"""Architect Skills Mixin - Adds proactive skills capabilities to ArchitectAgent.

This mixin extends ArchitectAgent with:
1. architecture-reuse-check skill (run before every spec)
2. proactive-refactoring-analysis skill (run weekly)
3. commit review capabilities (process commit_review_request messages)

Related ADRs:
    - ADR-010: Architect Commit Review and Skills Maintenance
    - ADR-011: Orchestrator-Based Commit Review (No Git Hooks)

Usage:
    class ArchitectAgent(ArchitectSkillsMixin, BaseAgent):
        pass
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ArchitectSkillsMixin:
    """Mixin adding proactive skills capabilities to ArchitectAgent.

    New Capabilities:
    1. Architecture Reuse Check (mandatory before specs)
    2. Proactive Refactoring Analysis (weekly automatic)
    3. Commit Review (process code_developer commits)

    Attributes:
        last_refactoring_analysis: Timestamp of last refactoring analysis
        refactoring_analysis_interval: Days between analyses (default: 7)
    """

    def __init__(self, *args, **kwargs):
        """Initialize mixin (call from ArchitectAgent.__init__)."""
        super().__init__(*args, **kwargs)

        # Refactoring analysis tracking
        self.refactoring_dir = Path("data/architect_status")
        self.refactoring_dir.mkdir(parents=True, exist_ok=True)

        self.last_refactoring_file = self.refactoring_dir / "last_refactoring_analysis.json"
        self.refactoring_analysis_interval = 7  # days

        logger.info("✅ ArchitectSkillsMixin initialized")

    def _enhanced_background_work(self):
        """Enhanced background work with skills integration.

        Call this instead of (or after) _do_background_work().

        Workflow:
        1. Check for commit review requests (PRIORITY: HIGH)
        2. Run weekly refactoring analysis (if Monday + >7 days)
        3. Original proactive spec creation
        """
        # Step 1: Process commit review requests (HIGHEST PRIORITY)
        self._process_commit_reviews()

        # Step 2: Run weekly refactoring analysis (if due)
        if self._should_run_refactoring_analysis():
            self._run_refactoring_analysis()

        # Step 3: Original background work (proactive spec creation)
        # Will be called by parent class

    def _process_commit_reviews(self):
        """Process commit review requests from code_developer.

        Messages format:
        {
            "type": "commit_review_request",
            "priority": "CRITICAL" or "NORMAL",
            "content": {
                "commit_sha": "a1b2c3d",
                "files_changed": ["file1.py", "file2.py"],
                "priority_name": "PRIORITY 10",
                "commit_message": "feat: ..."
            }
        }

        Processing:
        1. Read all commit_review_request messages
        2. Prioritize: CRITICAL first, then NORMAL
        3. Review up to 3 commits per iteration (prevent backlog)
        4. Generate feedback (tactical, learning, strategic)
        5. Route feedback to recipients
        """
        # Read commit review requests
        messages = self._read_messages(type_filter="commit_review_request")

        if not messages:
            return  # No reviews pending

        # Prioritize CRITICAL first
        critical = [m for m in messages if m.get("priority") == "CRITICAL"]
        normal = [m for m in messages if m.get("priority") == "NORMAL"]

        logger.info(f"📋 Commit reviews pending: {len(critical)} CRITICAL, {len(normal)} NORMAL")

        # Process CRITICAL reviews immediately (all of them)
        for message in critical:
            self._review_single_commit(message)

        # Process up to 3 NORMAL reviews per iteration (prevent queue buildup)
        for message in normal[:3]:
            self._review_single_commit(message)

        if len(normal) > 3:
            logger.info(f"⏳ {len(normal) - 3} NORMAL reviews queued for next iteration")

    def _review_single_commit(self, message: Dict):
        """Review a single commit and generate feedback.

        Args:
            message: commit_review_request message

        Steps:
        1. Extract commit info (SHA, files changed, etc.)
        2. Read git diff
        3. Analyze code quality (using LLM)
        4. Update Code Index (future: when skills implemented)
        5. Generate feedback (tactical, learning, strategic)
        6. Route feedback to appropriate recipients
        """
        content = message.get("content", {})
        commit_sha = content.get("commit_sha", "unknown")
        files_changed = content.get("files_changed", [])
        priority_name = content.get("priority_name", "unknown")

        logger.info(f"📋 Reviewing commit {commit_sha[:7]} ({priority_name})")

        # Update current task
        self.current_task = {
            "type": "commit_review",
            "commit_sha": commit_sha,
            "priority": priority_name,
            "started_at": datetime.now().isoformat(),
        }

        # Step 1: Read git diff
        try:
            diff = self.git.show(commit_sha)
            logger.info(f"✅ Git diff read ({len(diff)} chars)")
        except Exception as e:
            logger.error(f"❌ Failed to read git diff: {e}")
            return

        # Step 2: Analyze commit (using LLM)
        analysis = self._analyze_commit_quality(commit_sha, diff, files_changed, priority_name)

        if not analysis:
            logger.warning(f"⚠️  Commit analysis failed for {commit_sha[:7]}")
            return

        # Step 3: Generate and route feedback
        self._route_commit_feedback(commit_sha, analysis)

        logger.info(f"✅ Commit {commit_sha[:7]} reviewed successfully")

        # Update metrics
        self.metrics["commits_reviewed"] = self.metrics.get("commits_reviewed", 0) + 1

    def _analyze_commit_quality(
        self, commit_sha: str, diff: str, files_changed: List[str], priority_name: str
    ) -> Optional[Dict]:
        """Analyze commit quality using LLM.

        Args:
            commit_sha: Commit SHA
            diff: Git diff output
            files_changed: List of files changed
            priority_name: Priority name (e.g., "PRIORITY 10")

        Returns:
            Analysis dictionary with:
            - has_critical_issues: bool
            - has_bugs: bool
            - has_performance_issues: bool
            - has_new_patterns: bool
            - quality_score: int (0-100)
            - tactical_feedback: Dict (for code_developer)
            - learning_feedback: Dict (for reflector)
            - strategic_feedback: Dict (for project_manager)
        """
        # Build analysis prompt
        prompt = f"""Analyze this git commit for code quality issues and patterns.

Commit: {commit_sha[:7]}
Priority: {priority_name}
Files Changed: {', '.join(files_changed)}

Diff:
```
{diff[:5000]}  # Limit to first 5000 chars
```

Analyze for:
1. Critical issues (bugs, security vulnerabilities, spec deviations)
2. Performance issues
3. New patterns worth documenting
4. Refactoring opportunities

Output JSON:
{{
    "has_critical_issues": boolean,
    "has_bugs": boolean,
    "has_performance_issues": boolean,
    "has_new_patterns": boolean,
    "quality_score": integer (0-100),
    "tactical_feedback": {{
        "issues": [
            {{"severity": "CRITICAL|HIGH|MEDIUM", "description": "...", "fix": "..."}}
        ]
    }},
    "learning_feedback": {{
        "patterns": [
            {{"name": "...", "description": "...", "why_effective": "..."}}
        ]
    }},
    "strategic_feedback": {{
        "refactoring_needed": boolean,
        "description": "...",
        "effort_estimate": "..."
    }}
}}
"""

        # Execute LLM analysis
        from coffee_maker.autonomous.claude_cli_interface import ClaudeCLIInterface

        claude = ClaudeCLIInterface()

        try:
            result = claude.execute_prompt(prompt, timeout=600)
            if not result or not getattr(result, "success", False):
                logger.error("LLM analysis failed")
                return None

            # Parse JSON response
            response_text = getattr(result, "output", "")
            # Extract JSON from markdown code block if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]

            analysis = json.loads(response_text.strip())
            return analysis

        except Exception as e:
            logger.error(f"❌ Commit analysis error: {e}")
            return None

    def _route_commit_feedback(self, commit_sha: str, analysis: Dict):
        """Route commit feedback to appropriate recipients.

        Routing logic (from ADR-010):
        - CRITICAL bugs/security → code_developer (TACTICAL)
        - Spec deviation → code_developer (TACTICAL)
        - Refactoring needed → project_manager (STRATEGIC)
        - Effective pattern → reflector (LEARNING)

        Args:
            commit_sha: Commit SHA
            analysis: Analysis dictionary from _analyze_commit_quality
        """
        # Route 1: TACTICAL feedback to code_developer
        if analysis.get("has_critical_issues") or analysis.get("has_bugs"):
            tactical = analysis.get("tactical_feedback", {})
            if tactical.get("issues"):
                self._send_message(
                    "code_developer",
                    {
                        "type": "tactical_feedback",
                        "priority": "HIGH" if analysis.get("has_critical_issues") else "NORMAL",
                        "content": {
                            "commit_sha": commit_sha,
                            "issues": tactical["issues"],
                            "action_required": analysis.get("has_critical_issues", False),
                        },
                    },
                )
                logger.info(f"✉️  Sent tactical feedback to code_developer ({commit_sha[:7]})")

        # Route 2: LEARNING feedback to reflector
        if analysis.get("has_new_patterns"):
            learning = analysis.get("learning_feedback", {})
            if learning.get("patterns"):
                self._send_message(
                    "reflector",
                    {
                        "type": "learning_feedback",
                        "priority": "LOW",
                        "content": {
                            "commit_sha": commit_sha,
                            "patterns": learning["patterns"],
                        },
                    },
                )
                logger.info(f"✉️  Sent learning feedback to reflector ({commit_sha[:7]})")

        # Route 3: STRATEGIC feedback to project_manager
        strategic = analysis.get("strategic_feedback", {})
        if strategic.get("refactoring_needed"):
            self._send_message(
                "project_manager",
                {
                    "type": "strategic_feedback",
                    "priority": "MEDIUM",
                    "content": {
                        "commit_sha": commit_sha,
                        "refactoring": strategic,
                    },
                },
            )
            logger.info(f"✉️  Sent strategic feedback to project_manager ({commit_sha[:7]})")

    def _should_run_refactoring_analysis(self) -> bool:
        """Check if we should run weekly refactoring analysis.

        Criteria:
        - It's Monday (weekday == 0)
        - Last analysis was >7 days ago

        Returns:
            True if analysis should run
        """
        today = datetime.now()

        # Check if Monday
        if today.weekday() != 0:
            return False

        # Check last analysis time
        if not self.last_refactoring_file.exists():
            logger.info("📊 No previous refactoring analysis found - running first analysis")
            return True

        try:
            last_run_data = json.loads(self.last_refactoring_file.read_text())
            last_run_date = datetime.fromisoformat(last_run_data["timestamp"])

            days_since = (today - last_run_date).days

            if days_since >= self.refactoring_analysis_interval:
                logger.info(f"📊 Refactoring analysis due ({days_since} days since last run)")
                return True
            else:
                logger.info(f"⏳ Next refactoring analysis in {self.refactoring_analysis_interval - days_since} days")
                return False

        except Exception as e:
            logger.error(f"Error reading last refactoring analysis: {e}")
            return True  # Run analysis if can't read last run

    def _run_refactoring_analysis(self):
        """Run proactive refactoring analysis skill.

        Workflow:
        1. Load proactive-refactoring-analysis skill
        2. Execute skill with LLM (analyzes entire codebase)
        3. Generate synthetic report (1-2 pages)
        4. Save report to docs/architecture/
        5. Send report to project_manager
        6. Update last run timestamp

        Skill analyzes:
        - Code duplication (>20% duplicated blocks)
        - Large files (>500 LOC)
        - God classes (>15 methods)
        - Missing tests (coverage <80%)
        - TODO/FIXME comments
        - Technical debt indicators
        """
        logger.info("🔍 Running proactive refactoring analysis (weekly)...")

        # Update current task
        self.current_task = {
            "type": "refactoring_analysis",
            "started_at": datetime.now().isoformat(),
        }

        # Load skill
        from coffee_maker.autonomous.skill_loader import SkillNames, load_skill

        try:
            skill_prompt = load_skill(SkillNames.PROACTIVE_REFACTORING_ANALYSIS)
        except (AttributeError, FileNotFoundError) as e:
            logger.error(f"❌ Skill not available: {e}")
            logger.info("⏭️  Skipping refactoring analysis - skill not found")
            return

        # Execute skill with LLM
        from coffee_maker.autonomous.claude_cli_interface import ClaudeCLIInterface

        claude = ClaudeCLIInterface()

        try:
            result = claude.execute_prompt(skill_prompt, timeout=1800)  # 30 min timeout
            if not result or not getattr(result, "success", False):
                logger.error("Refactoring analysis failed")
                return

            report = getattr(result, "output", "")

        except Exception as e:
            logger.error(f"❌ Refactoring analysis error: {e}")
            return

        # Save report
        report_date = datetime.now().strftime("%Y%m%d")
        report_file = Path(f"docs/architecture/refactoring_analysis_{report_date}.md")
        report_file.write_text(report, encoding="utf-8")

        logger.info(f"✅ Refactoring analysis complete: {report_file}")

        # Extract summary and top priorities for message
        summary = self._extract_summary_from_report(report)
        top_priorities = self._extract_top_priorities_from_report(report)

        # Send report to project_manager
        self._send_message(
            "project_manager",
            {
                "type": "refactoring_analysis_report",
                "priority": "NORMAL",
                "content": {
                    "report_file": str(report_file),
                    "summary": summary,
                    "top_priorities": top_priorities,
                    "date": report_date,
                },
            },
        )

        logger.info("✉️  Sent refactoring analysis report to project_manager")

        # Update last run timestamp
        self.last_refactoring_file.write_text(
            json.dumps(
                {
                    "timestamp": datetime.now().isoformat(),
                    "report_file": str(report_file),
                },
                indent=2,
            )
        )

        # Update metrics
        self.metrics["refactoring_analyses_run"] = self.metrics.get("refactoring_analyses_run", 0) + 1

    def _extract_summary_from_report(self, report: str) -> str:
        """Extract executive summary from refactoring report.

        Args:
            report: Full report text

        Returns:
            Summary text (first few lines of executive summary)
        """
        # Simple extraction: find "Executive Summary" section
        if "Executive Summary" in report:
            lines = report.split("\n")
            in_summary = False
            summary_lines = []

            for line in lines:
                if "Executive Summary" in line:
                    in_summary = True
                    continue

                if in_summary:
                    if line.startswith("##") and "Executive Summary" not in line:
                        break  # Next section
                    summary_lines.append(line)

            return "\n".join(summary_lines[:10])  # First 10 lines of summary

        return "No summary available"

    def _extract_top_priorities_from_report(self, report: str) -> List[Dict]:
        """Extract top 3 refactoring priorities from report.

        Args:
            report: Full report text

        Returns:
            List of priority dictionaries
        """
        # Simple extraction: find "Top 3 Priorities" section
        priorities = []

        if "Top 3 Priorities" in report or "Top Priorities" in report:
            lines = report.split("\n")
            in_priorities = False
            current_priority = None

            for line in lines:
                if "Top 3 Priorities" in line or "Top Priorities" in line:
                    in_priorities = True
                    continue

                if in_priorities:
                    # Check for priority header (e.g., "### 1. Extract ConfigManager")
                    if line.startswith("###") and any(str(i) in line for i in [1, 2, 3]):
                        if current_priority:
                            priorities.append(current_priority)

                        current_priority = {
                            "title": line.replace("###", "").strip(),
                            "description": "",
                        }

                    elif current_priority and line.strip() and not line.startswith("#"):
                        current_priority["description"] += line + "\n"

                    # Stop after top 3
                    if len(priorities) >= 3:
                        break

            # Add last priority
            if current_priority and len(priorities) < 3:
                priorities.append(current_priority)

        return priorities[:3]

    def _run_architecture_reuse_check_before_spec(self, priority: Dict) -> str:
        """Run architecture-reuse-check skill before creating spec.

        This is MANDATORY before any technical specification creation.

        Args:
            priority: Priority dictionary

        Returns:
            Reuse analysis text to include in spec
        """
        logger.info("🔍 Running architecture-reuse-check skill (MANDATORY)...")

        try:
            # Load skill
            from coffee_maker.autonomous.skill_loader import SkillNames, load_skill

            priority_name = priority.get("name", "unknown")
            priority_content = priority.get("content", "")

            skill_prompt = load_skill(
                SkillNames.ARCHITECTURE_REUSE_CHECK,
                {
                    "PRIORITY_NAME": priority_name,
                    "PROBLEM_DESCRIPTION": priority_content[:1000],
                },
            )

            # Execute skill with LLM
            from coffee_maker.autonomous.claude_cli_interface import ClaudeCLIInterface

            claude = ClaudeCLIInterface()

            result = claude.execute_prompt(skill_prompt, timeout=600)
            if not result or not getattr(result, "success", False):
                logger.warning("Architecture reuse check failed - proceeding without it")
                return "## 🔍 Architecture Reuse Check\n\n⚠️  Skill execution failed\n"

            reuse_analysis = getattr(result, "output", "")
            logger.info("✅ Architecture reuse check complete")

            return reuse_analysis

        except (AttributeError, FileNotFoundError) as e:
            logger.warning(f"⚠️  architecture-reuse-check skill not found, proceeding without it: {e}")
            return "## 🔍 Architecture Reuse Check\n\n⚠️  Skill not yet implemented\n"
        except Exception as e:
            logger.error(f"❌ Architecture reuse check error: {e}")
            return "## 🔍 Architecture Reuse Check\n\n⚠️  Error running skill\n"
