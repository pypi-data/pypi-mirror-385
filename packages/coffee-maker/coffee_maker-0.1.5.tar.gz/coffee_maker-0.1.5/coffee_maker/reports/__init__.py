"""Reports module for generating status reports and delivery summaries.

This module provides functionality for generating various reports including:
- Recent delivery summaries
- Upcoming deliverables calendar
- Estimation accuracy reports

Example:
    >>> from coffee_maker.reports.status_report_generator import StatusReportGenerator
    >>>
    >>> generator = StatusReportGenerator("docs/roadmap/ROADMAP.md")
    >>> summary = generator.format_delivery_summary()
    >>> print(summary)
"""

from coffee_maker.reports.status_report_generator import (
    StatusReportGenerator,
    StoryCompletion,
    UpcomingStory,
)

__all__ = ["StatusReportGenerator", "StoryCompletion", "UpcomingStory"]
