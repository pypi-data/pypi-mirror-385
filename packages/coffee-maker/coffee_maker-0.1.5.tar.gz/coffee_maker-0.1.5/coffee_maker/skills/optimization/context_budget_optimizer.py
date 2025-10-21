"""Context Budget Optimizer - Prevents CFR-007 violations.

This module provides utilities for monitoring and optimizing context budget
usage to ensure compliance with CFR-007 (30% of 200K token budget = 60K limit).

Key Classes:
    - TokenCounter: Accurate token counting using tiktoken
    - FilePrioritizer: Smart file ranking by relevance
    - ContextBudgetOptimizer: Main optimization engine
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


@dataclass
class FileInfo:
    """Information about a file for budget analysis."""

    path: str
    size_bytes: int
    estimated_tokens: int
    lines: int
    category: str  # "high", "medium", "low" priority


class TokenCounter:
    """Accurate token counting using tiktoken.

    This class provides reliable token counting for context budget calculations.
    Falls back to approximation if tiktoken is not available.
    """

    def __init__(self):
        """Initialize token counter with tiktoken encoding."""
        try:
            import tiktoken

            self.encoding = tiktoken.get_encoding("cl100k_base")  # GPT-3.5/4 encoding
            self.has_tiktoken = True
        except ImportError:
            logger.warning("tiktoken not available, using approximate counting")
            self.encoding = None
            self.has_tiktoken = False

    def count_tokens(self, text: str) -> int:
        """Count tokens in text.

        Args:
            text: Text to count tokens for

        Returns:
            Number of tokens
        """
        if self.has_tiktoken and self.encoding:
            return len(self.encoding.encode(text))
        else:
            # Rough approximation: 1 token ≈ 4 characters
            return len(text) // 4

    def count_file_tokens(self, file_path: str) -> Tuple[int, int]:
        """Count tokens in file.

        Args:
            file_path: Path to file

        Returns:
            Tuple of (tokens, lines)
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                lines = len(content.splitlines())
                tokens = self.count_tokens(content)
                return tokens, lines
        except Exception as e:
            logger.warning(f"Could not read {file_path}: {e}")
            return 0, 0


class FilePrioritizer:
    """Smart file prioritization by relevance to task.

    Files are categorized into high, medium, and low priority based on
    their relevance to typical agent tasks.
    """

    PRIORITY_PATTERNS = {
        "high": [
            "ROADMAP.md",
            "CLAUDE.md",
            "SPEC-",
            "GUIDELINE-",
            "specification",
            "requirements",
        ],
        "medium": ["ADR-", "architecture", "design", "patterns"],
        "low": [
            "historical",
            "archived",
            "examples",
            "deprecated",
            "_deprecated",
        ],
    }

    @classmethod
    def categorize_file(cls, file_path: str, task_description: str = "") -> str:
        """Categorize file priority.

        Args:
            file_path: Path to file
            task_description: Optional task description for context

        Returns:
            Priority category: "high", "medium", or "low"
        """
        lower_path = file_path.lower()

        # Check low priority first (most specific)
        for pattern in cls.PRIORITY_PATTERNS["low"]:
            if pattern.lower() in lower_path:
                return "low"

        # Check high priority
        for pattern in cls.PRIORITY_PATTERNS["high"]:
            if pattern.lower() in lower_path:
                return "high"

        # Check medium priority
        for pattern in cls.PRIORITY_PATTERNS["medium"]:
            if pattern.lower() in lower_path:
                return "medium"

        # Default: medium
        return "medium"


class ContextBudgetOptimizer:
    """Main context budget optimizer engine.

    Analyzes proposed files and provides optimization recommendations
    to ensure context budget compliance with CFR-007.

    Attributes:
        TOTAL_BUDGET: Total available context tokens (200K)
        CFR_007_THRESHOLD: CFR-007 compliance threshold (30%)
        BUDGET_LIMIT: Maximum tokens to use (60K)
    """

    TOTAL_BUDGET = 200_000  # tokens
    CFR_007_THRESHOLD = 0.30  # 30% of total budget
    BUDGET_LIMIT = int(TOTAL_BUDGET * CFR_007_THRESHOLD)  # 60,000 tokens

    def __init__(self):
        """Initialize optimizer."""
        self.token_counter = TokenCounter()
        self.project_root = Path.cwd()

    def analyze_files(self, file_paths: List[str]) -> Dict:
        """Analyze list of files for budget compliance.

        Args:
            file_paths: List of file paths to analyze

        Returns:
            Dict containing analysis results and statistics
        """
        files_info = []
        total_tokens = 0

        for file_path in file_paths:
            # Handle both absolute and relative paths
            if Path(file_path).is_absolute():
                full_path = Path(file_path)
            else:
                full_path = self.project_root / file_path

            if full_path.exists():
                tokens, lines = self.token_counter.count_file_tokens(str(full_path))
                size_bytes = full_path.stat().st_size
                category = FilePrioritizer.categorize_file(file_path)

                file_info = FileInfo(
                    path=file_path,
                    size_bytes=size_bytes,
                    estimated_tokens=tokens,
                    lines=lines,
                    category=category,
                )
                files_info.append(file_info)
                total_tokens += tokens
            else:
                logger.warning(f"File not found: {file_path}")

        # Sort by category (high, medium, low)
        priority_order = {"high": 0, "medium": 1, "low": 2}
        files_info.sort(key=lambda f: priority_order[f.category])

        return {
            "files": files_info,
            "total_tokens": total_tokens,
            "budget_limit": self.BUDGET_LIMIT,
            "exceeds_budget": total_tokens > self.BUDGET_LIMIT,
            "excess_tokens": max(0, total_tokens - self.BUDGET_LIMIT),
        }

    def generate_recommendations(self, analysis: Dict) -> List[Dict]:
        """Generate optimization recommendations.

        Args:
            analysis: Analysis dict from analyze_files()

        Returns:
            List of recommendation dicts with action and details
        """
        recommendations = []
        total_tokens = analysis["total_tokens"]
        budget_limit = analysis["budget_limit"]

        if total_tokens <= budget_limit:
            return [
                {
                    "action": "no_optimization_needed",
                    "message": f"Current context ({total_tokens:,} tokens) is within budget ({budget_limit:,} tokens)",
                }
            ]

        excess_tokens = total_tokens - budget_limit
        savings_needed = excess_tokens + 5000  # Buffer

        # Recommendation 1: Summarize large high-priority files
        large_files = [f for f in analysis["files"] if f.estimated_tokens > 5000]
        for file_info in large_files:
            if file_info.category == "high":
                # Estimate 90% reduction for large files
                potential_savings = int(file_info.estimated_tokens * 0.9)
                if potential_savings >= savings_needed:
                    recommendations.append(
                        {
                            "priority": 1,
                            "action": "summarize",
                            "file": file_info.path,
                            "reduction": potential_savings,
                            "new_token_count": int(file_info.estimated_tokens * 0.1),
                            "description": f"Summarize {file_info.path} ({file_info.lines:,} lines → ~500 lines)",
                            "estimated_time": "2-3 min",
                        }
                    )
                    savings_needed -= potential_savings
                    if savings_needed <= 0:
                        break

        # Recommendation 2: Load medium priority files partially
        for file_info in analysis["files"]:
            if file_info.category == "medium" and file_info.estimated_tokens > 3000:
                potential_savings = int(file_info.estimated_tokens * 0.5)
                if potential_savings >= savings_needed:
                    recommendations.append(
                        {
                            "priority": 2,
                            "action": "partial_load",
                            "file": file_info.path,
                            "reduction": potential_savings,
                            "description": f"Load {file_info.path} partially (first 200 lines only)",
                            "estimated_time": "1 min",
                        }
                    )
                    savings_needed -= potential_savings
                    if savings_needed <= 0:
                        break

        # Recommendation 3: Defer low-priority files
        low_priority_files = [f for f in analysis["files"] if f.category == "low"]
        for file_info in low_priority_files:
            if savings_needed > 0:
                recommendations.append(
                    {
                        "priority": 3,
                        "action": "defer",
                        "file": file_info.path,
                        "reduction": file_info.estimated_tokens,
                        "description": f"Defer {file_info.path} to follow-up task",
                        "estimated_time": "0 min",
                    }
                )
                savings_needed -= file_info.estimated_tokens
                if savings_needed <= 0:
                    break

        return recommendations

    def generate_report(
        self,
        agent: str,
        task: str,
        analysis: Dict,
        recommendations: List[Dict],
    ) -> str:
        """Generate human-readable optimization report.

        Args:
            agent: Agent name
            task: Task description
            analysis: Analysis dict from analyze_files()
            recommendations: Recommendations list

        Returns:
            Formatted report string
        """
        report = f"""
CONTEXT BUDGET ANALYSIS REPORT
==============================

Agent: {agent}
Task: {task}

BUDGET INFORMATION
==================
Total Budget: {self.TOTAL_BUDGET:,} tokens
CFR-007 Threshold: {self.BUDGET_LIMIT:,} tokens (30%)
Current Usage: {analysis['total_tokens']:,} tokens ({analysis['total_tokens'] / self.BUDGET_LIMIT * 100:.1f}%)
Status: {"✅ WITHIN BUDGET" if not analysis['exceeds_budget'] else "❌ EXCEEDS BUDGET"}

PROPOSED FILES ({analysis['total_tokens']:,} tokens)
==============================
"""
        for file_info in analysis["files"]:
            report += f"{file_info.path}: {file_info.estimated_tokens:,} tokens\n"

        report += f"\nRECOMMENDATIONS\n"
        report += "===============\n"
        for i, rec in enumerate(recommendations, 1):
            if rec["action"] == "no_optimization_needed":
                report += f"✅ {rec['message']}\n"
            else:
                report += f"\n{i}. {rec['description']}\n"
                if "reduction" in rec:
                    report += f"   Reduction: {rec['reduction']:,} tokens\n"
                report += f"   Time: {rec['estimated_time']}\n"

        return report
