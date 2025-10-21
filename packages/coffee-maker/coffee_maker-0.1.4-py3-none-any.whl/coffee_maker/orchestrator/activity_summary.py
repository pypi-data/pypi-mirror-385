"""Activity and Progress Summary Generator.

This module implements the activity-summary skill for the orchestrator.
It generates comprehensive reports of development activity, progress, and agent status.

Related:
    .claude/skills/orchestrator/activity-summary/SKILL.md - Skill documentation
"""

import json
import re
import subprocess
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from coffee_maker.cli.notifications import NotificationDB


def get_recent_commits(hours: int = 6) -> List[Dict]:
    """Get commits from last N hours.

    Args:
        hours: Number of hours to look back

    Returns:
        List of commit dictionaries with hash, date, subject, priority
    """
    since = datetime.now() - timedelta(hours=hours)
    since_str = since.strftime("%Y-%m-%d %H:%M:%S")

    cmd = f'git log --since="{since_str}" --pretty=format:"%h|%ai|%s" --no-merges'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    commits = []
    for line in result.stdout.split("\n"):
        if not line:
            continue

        parts = line.split("|", 2)
        if len(parts) < 3:
            continue

        hash_val, date, subject = parts

        # Extract US/PRIORITY from commit
        us_match = re.search(r"(US-\d+|PRIORITY \d+)", subject)

        commits.append(
            {
                "hash": hash_val,
                "date": date,
                "subject": subject,
                "priority": us_match.group(1) if us_match else None,
            }
        )

    return commits


def group_commits_by_priority(commits: List[Dict]) -> Dict[str, List[Dict]]:
    """Group commits by their priority.

    Args:
        commits: List of commit dictionaries

    Returns:
        Dictionary mapping priority -> list of commits
    """
    by_priority = defaultdict(list)

    for commit in commits:
        priority = commit["priority"] or "Other"
        by_priority[priority].append(commit)

    return dict(by_priority)


def find_completed_priorities(commits: List[Dict]) -> List[str]:
    """Find priorities that were marked complete in commits.

    Args:
        commits: List of commit dictionaries

    Returns:
        List of priority names that were completed
    """
    completed = []

    for commit in commits:
        # Look for completion patterns
        if re.search(r"(complete|implement|feat).*US-\d+", commit["subject"], re.I):
            if commit["priority"]:
                completed.append(commit["priority"])

    return list(set(completed))


def get_running_agents() -> List[Dict]:
    """Get all currently running agents.

    Returns:
        List of agent dictionaries with type, pid, priority, command
    """
    agents = []

    cmd = 'ps aux | grep -E "(code_developer|architect|code-reviewer|project_manager|orchestrator)" | grep python | grep -v grep'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    for line in result.stdout.split("\n"):
        if not line:
            continue

        parts = line.split()
        if len(parts) < 11:
            continue

        pid = int(parts[1])
        cmd_line = " ".join(parts[10:])

        agent_type = None
        priority = None

        if "code_developer" in cmd_line or "daemon" in cmd_line:
            agent_type = "code_developer"
            priority_match = re.search(r"--priority[= ](\d+)", cmd_line)
            if priority_match:
                priority = priority_match.group(1)
        elif "architect" in cmd_line:
            agent_type = "architect"
        elif "code-reviewer" in cmd_line:
            agent_type = "code-reviewer"
        elif "project_manager" in cmd_line:
            agent_type = "project_manager"
        elif "orchestrator" in cmd_line:
            agent_type = "orchestrator"

        if agent_type:
            agents.append({"type": agent_type, "pid": pid, "priority": priority, "command": cmd_line})

    return agents


def get_agent_status_from_files() -> Dict[str, Dict]:
    """Read agent status from status files.

    Returns all status files, categorized by whether the process is still running.

    Returns:
        Dictionary with 'active' and 'recent_issues' keys containing agent statuses
    """
    from datetime import datetime, timedelta
    import os

    status_dir = Path("data/agent_status")
    active_agents = {}
    recent_issues = {}

    if not status_dir.exists():
        return {"active": active_agents, "recent_issues": recent_issues}

    for status_file in status_dir.glob("*.json"):
        try:
            status = json.loads(status_file.read_text())
            agent_type = status.get("agent_type", status_file.stem)

            # Check if PID is still running
            pid = status.get("pid")
            if pid:
                try:
                    os.kill(pid, 0)  # Signal 0 checks if process exists
                    # Process exists - this is an active agent
                    active_agents[agent_type] = status
                except (OSError, ProcessLookupError):
                    # Process doesn't exist - check if it's a recent issue
                    last_heartbeat = status.get("last_heartbeat")
                    if last_heartbeat:
                        try:
                            heartbeat_time = datetime.fromisoformat(last_heartbeat)
                            age = datetime.now() - heartbeat_time

                            # Show errors/crashes from last 24 hours
                            if age < timedelta(hours=24):
                                recent_issues[agent_type] = status
                        except Exception:
                            pass
            else:
                # No PID - might be old format, skip
                pass

        except Exception:
            continue

    return {"active": active_agents, "recent_issues": recent_issues}


def get_active_worktrees() -> List[Dict]:
    """Get all active git worktrees.

    Returns:
        List of worktree dictionaries with path, branch, commit
    """
    cmd = "git worktree list --porcelain"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    worktrees = []
    current_wt = {}

    for line in result.stdout.split("\n"):
        if line.startswith("worktree "):
            if current_wt:
                worktrees.append(current_wt)
            current_wt = {"path": line.split(" ", 1)[1]}
        elif line.startswith("branch "):
            current_wt["branch"] = line.split(" ", 1)[1]
        elif line.startswith("HEAD "):
            current_wt["commit"] = line.split(" ", 1)[1]

    if current_wt:
        worktrees.append(current_wt)

    # Filter out main worktree
    return [wt for wt in worktrees if "-wt" in wt.get("path", "")]


def get_worktree_commits(worktree_path: str, hours: int = 6) -> List[Dict]:
    """Get commits from a specific worktree directory.

    Args:
        worktree_path: Path to worktree directory
        hours: Number of hours to look back

    Returns:
        List of commit dictionaries with hash, date, subject
    """
    import os

    if not os.path.exists(worktree_path):
        return []

    since = datetime.now() - timedelta(hours=hours)
    since_str = since.strftime("%Y-%m-%d %H:%M:%S")

    cmd = f'cd "{worktree_path}" && git log --since="{since_str}" --pretty=format:"%h|%ai|%s" --no-merges'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    commits = []
    for line in result.stdout.split("\n"):
        if not line:
            continue

        parts = line.split("|", 2)
        if len(parts) < 3:
            continue

        hash_val, date, subject = parts

        # Extract US/PRIORITY from commit
        us_match = re.search(r"(US-\d+|PRIORITY \d+)", subject)

        commits.append(
            {"hash": hash_val, "date": date, "subject": subject, "priority": us_match.group(1) if us_match else None}
        )

    return commits


def analyze_worktree_activity(worktree: Dict, hours: int = 6) -> Dict:
    """Analyze what work was done in a worktree.

    Args:
        worktree: Worktree dictionary with path, branch, commit
        hours: Number of hours to look back

    Returns:
        Dictionary with commits, priority, file_stats, summary
    """

    worktree_path = worktree.get("path", "")
    branch = worktree.get("branch", "unknown")

    # Extract priority number from path (e.g., "wt038" -> "038")
    priority_match = re.search(r"wt(\d+)", worktree_path)
    priority_num = priority_match.group(1) if priority_match else "?"

    # Get commits from this worktree
    commits = get_worktree_commits(worktree_path, hours=hours)

    # Get file stats (what changed in this worktree since it was created)
    # Find the base commit (where this worktree branched from)
    base_cmd = f'cd "{worktree_path}" && git merge-base HEAD roadmap'
    base_result = subprocess.run(base_cmd, shell=True, capture_output=True, text=True)
    base_commit = base_result.stdout.strip() if base_result.returncode == 0 else None

    file_stats = {"files_changed": 0, "insertions": 0, "deletions": 0}

    if base_commit:
        stat_cmd = f'cd "{worktree_path}" && git diff {base_commit}..HEAD --shortstat'
        stat_result = subprocess.run(stat_cmd, shell=True, capture_output=True, text=True)

        if stat_result.returncode == 0:
            # Parse output like: "3 files changed, 2981 insertions(+), 12 deletions(-)"
            stat_match = re.search(r"(\d+) files? changed", stat_result.stdout)
            if stat_match:
                file_stats["files_changed"] = int(stat_match.group(1))

            ins_match = re.search(r"(\d+) insertions?", stat_result.stdout)
            if ins_match:
                file_stats["insertions"] = int(ins_match.group(1))

            del_match = re.search(r"(\d+) deletions?", stat_result.stdout)
            if del_match:
                file_stats["deletions"] = int(del_match.group(1))

    # Determine summary
    summary = "No activity"
    if commits:
        if len(commits) == 1 and "End of iteration" in commits[0]["subject"]:
            summary = "Completed (checkpoint only)"
        else:
            summary = f"{len(commits)} commit(s)"

    return {
        "path": worktree_path,
        "branch": branch,
        "priority": f"US-{priority_num}" if priority_num.isdigit() else f"Priority {priority_num}",
        "commits": commits,
        "file_stats": file_stats,
        "summary": summary,
    }


def get_planned_priorities(roadmap_path: Path, limit: int = 5) -> List[Dict]:
    """Get next N planned priorities from ROADMAP.

    Args:
        roadmap_path: Path to ROADMAP.md
        limit: Maximum number of priorities to return

    Returns:
        List of priority dictionaries with name, title, status
    """
    if not roadmap_path.exists():
        return []

    content = roadmap_path.read_text()
    planned = []

    priority_pattern = r"##\s+(US-\d+|PRIORITY \d+):\s+(.+?)$"
    status_pattern = r"\*\*Status\*\*:\s*(.+?)$"

    lines = content.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i]

        priority_match = re.match(priority_pattern, line)
        if priority_match:
            priority_name = priority_match.group(1)
            priority_title = priority_match.group(2)

            # Look ahead for status
            for j in range(i + 1, min(i + 10, len(lines))):
                status_match = re.match(status_pattern, lines[j])
                if status_match:
                    status = status_match.group(1)

                    if "PLANNED" in status.upper() or "📝" in status:
                        planned.append({"name": priority_name, "title": priority_title, "status": status})

                        if len(planned) >= limit:
                            return planned
                    break

        i += 1

    return planned


def generate_summary_report(
    completed_work: Dict, current_work: Dict, upcoming_work: List[Dict], time_window: int = 6
) -> str:
    """Generate human-readable summary report.

    Args:
        completed_work: Dictionary with completed priorities and commits
        current_work: Dictionary with running agents, statuses, worktrees
        upcoming_work: List of upcoming planned priorities
        time_window: Hours covered by this report

    Returns:
        Formatted markdown report
    """
    report = f"""# Development Activity Report
**Period**: Last {time_window} hours
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## ✅ Completed Work

"""

    # Completed priorities
    if completed_work.get("completed_priorities"):
        report += "### Priorities Completed:\n"
        for priority in completed_work["completed_priorities"]:
            commits = completed_work["commits_by_priority"].get(priority, [])
            report += f"- **{priority}**: {len(commits)} commit(s)\n"
            for commit in commits[:3]:  # Show first 3 commits
                report += f"  - `{commit['hash']}` {commit['subject']}\n"
        report += "\n"
    else:
        report += "_No priorities completed in this period_\n\n"

    # All commits
    total_commits = len(completed_work.get("all_commits", []))
    report += f"**Total Commits**: {total_commits}\n\n"

    if total_commits > 0:
        report += "### Recent Commits:\n"
        for commit in completed_work["all_commits"][:10]:
            report += f"- `{commit['hash']}` {commit['subject']} _{commit['date']}_\n"
        report += "\n"

    report += "---\n\n"

    # Current work
    report += "## 🚀 Current Work in Progress\n\n"

    running_agents = current_work.get("running_agents", [])
    if running_agents:
        report += f"**Active Agents**: {len(running_agents)}\n\n"

        # Group by type
        by_type = defaultdict(list)
        for agent in running_agents:
            by_type[agent["type"]].append(agent)

        for agent_type, agents in by_type.items():
            report += f"### {agent_type.replace('_', ' ').title()} ({len(agents)})\n"
            for agent in agents:
                priority_str = f" - Priority {agent['priority']}" if agent["priority"] else ""
                report += f"- PID {agent['pid']}{priority_str}\n"
            report += "\n"
    else:
        report += "_No agents currently running_\n\n"

    # Worktrees with detailed activity
    worktree_activities = current_work.get("worktree_activities", [])
    if worktree_activities:
        report += f"**Active Worktrees**: {len(worktree_activities)}\n\n"
        for wt_activity in worktree_activities:
            priority = wt_activity.get("priority", "Unknown")
            branch = wt_activity.get("branch", "unknown")
            path = wt_activity.get("path", "")
            summary = wt_activity.get("summary", "No activity")
            commits = wt_activity.get("commits", [])
            file_stats = wt_activity.get("file_stats", {})

            report += f"### {priority}: {summary}\n"
            report += f"- Branch: `{branch}`\n"
            report += f"- Path: `{path}`\n"

            # File statistics
            files_changed = file_stats.get("files_changed", 0)
            insertions = file_stats.get("insertions", 0)
            deletions = file_stats.get("deletions", 0)

            if files_changed > 0:
                report += f"- Changes: {files_changed} files, +{insertions}/-{deletions} lines\n"

            # Show commits (excluding "End of iteration" checkpoints)
            real_commits = [c for c in commits if "End of iteration" not in c.get("subject", "")]
            if real_commits:
                report += f"- Commits:\n"
                for commit in real_commits[:5]:  # Show max 5 commits
                    subject = commit.get("subject", "")
                    hash_val = commit.get("hash", "")
                    # Truncate long subjects
                    if len(subject) > 80:
                        subject = subject[:77] + "..."
                    report += f"  - `{hash_val}` {subject}\n"

            report += "\n"
    else:
        # Fallback to simple worktree list if detailed analysis not available
        worktrees = current_work.get("worktrees", [])
        if worktrees:
            report += f"**Active Worktrees**: {len(worktrees)}\n\n"
            for wt in worktrees:
                branch = wt.get("branch", "unknown")
                path = wt.get("path", "")
                priority = re.search(r"wt(\d+)", path)
                priority_num = priority.group(1) if priority else "?"
                report += f"- Priority {priority_num}: `{branch}` at `{path}`\n"
            report += "\n"

    # Agent status details (active agents only)
    agent_statuses = current_work.get("agent_statuses", {})
    active_statuses = agent_statuses.get("active", {}) if isinstance(agent_statuses, dict) else agent_statuses
    if active_statuses:
        report += "### Agent Status Details:\n\n"
        for agent_type, status in active_statuses.items():
            state = status.get("state", "unknown")
            task = status.get("current_task", {})
            health = status.get("health", "unknown")

            report += f"**{agent_type}**: {state} ({health})\n"
            if task:
                task_type = task.get("type", "unknown")
                task_priority = task.get("priority", task.get("title", ""))
                report += f"  - Task: {task_type}"
                if task_priority:
                    report += f" ({task_priority})"
                report += "\n"
            report += "\n"

    # Recent agent issues (crashes, errors from last 24h)
    recent_issues = agent_statuses.get("recent_issues", {}) if isinstance(agent_statuses, dict) else {}
    if recent_issues:
        report += "### ⚠️  Recent Agent Issues (Last 24 Hours):\n\n"
        for agent_type, status in recent_issues.items():
            state = status.get("state", "unknown")
            health = status.get("health", "unknown")
            error = status.get("error", "No error details")
            last_heartbeat = status.get("last_heartbeat", "unknown")
            stopped_at = status.get("stopped_at", last_heartbeat)

            report += f"**{agent_type}**: {state} ({health})\n"
            report += f"  - Last seen: {stopped_at}\n"
            if error:
                # Truncate long errors
                error_msg = error if len(error) < 100 else error[:97] + "..."
                report += f"  - Error: {error_msg}\n"
            report += "\n"

    report += "---\n\n"

    # Upcoming work
    report += "## 📋 Upcoming Work\n\n"

    if upcoming_work:
        report += f"**Next {len(upcoming_work)} Priorities**:\n\n"
        for i, priority in enumerate(upcoming_work, 1):
            report += f"{i}. **{priority['name']}**: {priority['title']}\n"
            report += f"   Status: {priority['status']}\n"
        report += "\n"
    else:
        report += "_No planned priorities found_\n\n"

    report += "---\n\n"

    # Summary statistics
    report += "## 📊 Summary Statistics\n\n"
    report += f"- Commits in period: {total_commits}\n"
    report += f"- Active agents: {len(running_agents)}\n"

    # Count worktrees from either worktree_activities or fallback to worktrees list
    wt_count = len(worktree_activities) if worktree_activities else len(current_work.get("worktrees", []))
    report += f"- Parallel worktrees: {wt_count}\n"
    report += f"- Completed priorities: {len(completed_work.get('completed_priorities', []))}\n"
    report += f"- Upcoming priorities: {len(upcoming_work)}\n"

    return report


def save_report(report: str, timestamp: Optional[datetime] = None) -> Path:
    """Save report to evidence directory.

    Args:
        report: Report content (markdown)
        timestamp: Timestamp for filename (default: now)

    Returns:
        Path where report was saved
    """
    if timestamp is None:
        timestamp = datetime.now()

    evidence_dir = Path("evidence")
    evidence_dir.mkdir(exist_ok=True)

    filename = f"activity-summary-{timestamp.strftime('%Y%m%d-%H%M%S')}.md"
    report_path = evidence_dir / filename
    report_path.write_text(report)

    return report_path


def create_summary_notification(report: str, report_path: Path):
    """Create notification with summary.

    Args:
        report: Full report content
        report_path: Path where report was saved
    """
    # Extract key stats for notification
    stats_match = re.search(r"- Commits in period: (\d+)", report)
    commits = stats_match.group(1) if stats_match else "0"

    agents_match = re.search(r"- Active agents: (\d+)", report)
    agents = agents_match.group(1) if agents_match else "0"

    completed_match = re.search(r"- Completed priorities: (\d+)", report)
    completed = completed_match.group(1) if completed_match else "0"

    worktrees_match = re.search(r"- Parallel worktrees: (\d+)", report)
    worktrees = worktrees_match.group(1) if worktrees_match else "0"

    # Create concise notification
    title = "Development Activity Summary"
    message = f"""Activity report generated:

✅ Completed: {completed} priorities
🚀 Active: {agents} agents running
🌿 Worktrees: {worktrees} parallel executions
📝 Commits: {commits}

Full report: {report_path}"""

    notifications = NotificationDB()
    notifications.create_notification(
        type="activity_summary",
        title=title,
        message=message.strip(),
        priority="normal",
        sound=False,  # CFR-009: No sound for background reports
        agent_id="orchestrator",
    )


def generate_activity_summary(time_window: int = 6, save_to_file: bool = True) -> str:
    """Generate complete activity summary.

    This is the main entry point for the activity-summary skill.

    Args:
        time_window: Hours to look back
        save_to_file: Whether to save report to evidence/ directory

    Returns:
        Formatted summary report
    """
    # Step 1: Collect data
    commits = get_recent_commits(hours=time_window)
    running_agents = get_running_agents()
    agent_statuses = get_agent_status_from_files()
    worktrees = get_active_worktrees()

    # Step 1b: Analyze worktree activity (detailed commits and stats)
    worktree_activities = []
    for worktree in worktrees:
        activity = analyze_worktree_activity(worktree, hours=time_window)
        worktree_activities.append(activity)

    # Step 2: Analyze completed work
    commits_by_priority = group_commits_by_priority(commits)
    completed_priorities = find_completed_priorities(commits)

    completed_work = {
        "all_commits": commits,
        "commits_by_priority": commits_by_priority,
        "completed_priorities": completed_priorities,
    }

    # Step 3: Analyze current work
    current_work = {
        "running_agents": running_agents,
        "agent_statuses": agent_statuses,
        "worktrees": worktrees,
        "worktree_activities": worktree_activities,
    }

    # Step 4: Get upcoming work
    roadmap_path = Path("docs/roadmap/ROADMAP.md")
    upcoming_work = get_planned_priorities(roadmap_path, limit=5)

    # Step 5: Generate report
    report = generate_summary_report(
        completed_work=completed_work, current_work=current_work, upcoming_work=upcoming_work, time_window=time_window
    )

    # Step 6: Save and notify
    if save_to_file:
        timestamp = datetime.now()
        report_path = save_report(report, timestamp)
        create_summary_notification(report, report_path)

    return report
