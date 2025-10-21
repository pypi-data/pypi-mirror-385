"""Analytics and observability for LLM operations.

This module provides comprehensive analytics capabilities for Coffee Maker Agent:

- **Langfuse Export**: Export traces to local SQLite database (native sqlite3)
- **Performance Metrics**: Analyze LLM, prompt, and agent performance
- **Cost Tracking**: Detailed cost analytics and optimization insights
- **Rate Limiting**: Multi-process safe rate limit counters

Key Components:
    - LangfuseExporter: Export Langfuse data to local database (sqlite3)
    - PerformanceAnalyzer: Analyze LLM and prompt performance (sqlite3)
    - Models: Dataclass-based models for traces, generations, spans

Example:
    Export Langfuse data to SQLite:
    >>> from coffee_maker.langfuse_observe.analytics import LangfuseExporter
    >>> from coffee_maker.langfuse_observe.analytics.config import ExportConfig
    >>>
    >>> config = ExportConfig.from_env()
    >>> exporter = LangfuseExporter(config)
    >>> exporter.setup_database()
    >>> stats = exporter.export_traces()
    >>> print(f"Exported {stats['generations']} generations")

    Analyze LLM performance:
    >>> from coffee_maker.langfuse_observe.analytics import PerformanceAnalyzer
    >>>
    >>> analyzer = PerformanceAnalyzer("llm_metrics.db")
    >>> perf = analyzer.get_llm_performance(days=7)
    >>> print(f"Average latency: {perf['avg_latency_ms']:.0f}ms")

See Also:
    - :class:`LangfuseExporter`: Main export functionality
    - :class:`PerformanceAnalyzer`: Performance analysis
    - :mod:`coffee_maker.langfuse_observe.analytics.models_sqlite`: Data models
"""

from typing import List

from coffee_maker.langfuse_observe.analytics.config import ExportConfig
from coffee_maker.langfuse_observe.analytics.exporter_sqlite import LangfuseExporter
from coffee_maker.langfuse_observe.analytics.analyzer_sqlite import PerformanceAnalyzer

__all__: List[str] = [
    "LangfuseExporter",
    "PerformanceAnalyzer",
    "ExportConfig",
]
