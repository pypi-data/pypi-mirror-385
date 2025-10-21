"""Multi-Model Code Review Agent.

This module provides a multi-model code review system that analyzes code
from multiple perspectives using different LLMs:
- Bug detection (GPT-4)
- Architecture review (Claude)
- Performance analysis (Gemini)
- Security audit (specialized model)

Usage:
    from coffee_maker.code_reviewer import MultiModelCodeReviewer

    reviewer = MultiModelCodeReviewer()
    report = reviewer.review_file("path/to/file.py")
    report.save_html("review_report.html")
"""

from typing import List

from coffee_maker.code_reviewer.reviewer import MultiModelCodeReviewer

__all__: List[str] = ["MultiModelCodeReviewer"]
