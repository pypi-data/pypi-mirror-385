"""Configuration for Langfuse export to local database.

This module provides configuration management for the analytics system,
supporting both SQLite (default) and PostgreSQL backends.

Example:
    Load configuration from environment:
    >>> config = ExportConfig.from_env()
    >>> print(config.db_url)
    'sqlite:///llm_metrics.db'

    Use PostgreSQL instead:
    >>> config = ExportConfig(
    ...     db_type="postgresql",
    ...     postgres_host="localhost",
    ...     postgres_user="llm_user",
    ...     postgres_password="secret"
    ... )
"""

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

from coffee_maker.config.manager import ConfigManager

load_dotenv()


@dataclass
class ExportConfig:
    """Configuration for Langfuse export.

    Attributes:
        langfuse_public_key: Langfuse public API key
        langfuse_secret_key: Langfuse secret API key
        langfuse_host: Langfuse host URL (default: https://cloud.langfuse.com)
        db_type: Database type ("sqlite" or "postgresql")
        sqlite_path: Path to SQLite database file (default: llm_metrics.db)
        postgres_host: PostgreSQL host (required if db_type="postgresql")
        postgres_port: PostgreSQL port (default: 5432)
        postgres_database: PostgreSQL database name
        postgres_user: PostgreSQL username
        postgres_password: PostgreSQL password
        export_batch_size: Number of records per batch (default: 1000)
        export_interval_minutes: Export interval for continuous mode (default: 30)
        lookback_hours: Hours to look back for initial export (default: 24)

    Example:
        >>> config = ExportConfig.from_env()
        >>> print(config.db_url)
        'sqlite:///llm_metrics.db'
    """

    # Langfuse credentials
    langfuse_public_key: str
    langfuse_secret_key: str
    langfuse_host: str = "https://cloud.langfuse.com"

    # Database configuration
    db_type: str = "sqlite"  # "sqlite" or "postgresql"
    sqlite_path: str = "llm_metrics.db"

    # PostgreSQL connection (only if db_type="postgresql")
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_database: str = "llm_metrics"
    postgres_user: Optional[str] = None
    postgres_password: Optional[str] = None

    # Export settings
    export_batch_size: int = 1000
    export_interval_minutes: int = 30
    lookback_hours: int = 24

    @classmethod
    def from_env(cls) -> "ExportConfig":
        """Load configuration from environment variables.

        Environment variables:
            LANGFUSE_PUBLIC_KEY: Langfuse public key (required)
            LANGFUSE_SECRET_KEY: Langfuse secret key (required)
            LANGFUSE_HOST: Langfuse host (optional)
            DB_TYPE: Database type - "sqlite" or "postgresql" (default: sqlite)
            SQLITE_PATH: SQLite database path (default: llm_metrics.db)
            POSTGRES_HOST: PostgreSQL host (required if DB_TYPE=postgresql)
            POSTGRES_PORT: PostgreSQL port (default: 5432)
            POSTGRES_DATABASE: PostgreSQL database name
            POSTGRES_USER: PostgreSQL username
            POSTGRES_PASSWORD: PostgreSQL password
            EXPORT_BATCH_SIZE: Batch size (default: 1000)
            EXPORT_INTERVAL_MINUTES: Export interval (default: 30)
            EXPORT_LOOKBACK_HOURS: Lookback hours (default: 24)

        Returns:
            ExportConfig instance with values from environment

        Raises:
            ValueError: If required environment variables are missing

        Example:
            >>> os.environ["LANGFUSE_PUBLIC_KEY"] = "pk-lf-xxx"
            >>> os.environ["LANGFUSE_SECRET_KEY"] = "sk-lf-xxx"
            >>> config = ExportConfig.from_env()
        """
        try:
            public_key = ConfigManager.get_langfuse_public_key(required=True)
            secret_key = ConfigManager.get_langfuse_secret_key(required=True)
        except Exception as e:
            raise ValueError(f"Langfuse keys must be set in environment: {e}")

        return cls(
            langfuse_public_key=public_key,
            langfuse_secret_key=secret_key,
            langfuse_host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
            db_type=os.getenv("DB_TYPE", "sqlite"),
            sqlite_path=os.getenv("SQLITE_PATH", "llm_metrics.db"),
            postgres_host=os.getenv("POSTGRES_HOST", "localhost"),
            postgres_port=int(os.getenv("POSTGRES_PORT", "5432")),
            postgres_database=os.getenv("POSTGRES_DATABASE", "llm_metrics"),
            postgres_user=os.getenv("POSTGRES_USER"),
            postgres_password=os.getenv("POSTGRES_PASSWORD"),
            export_batch_size=int(os.getenv("EXPORT_BATCH_SIZE", "1000")),
            export_interval_minutes=int(os.getenv("EXPORT_INTERVAL_MINUTES", "30")),
            lookback_hours=int(os.getenv("EXPORT_LOOKBACK_HOURS", "24")),
        )

    @property
    def db_url(self) -> str:
        """Get database connection URL.

        Returns:
            SQLAlchemy database URL

        Example:
            >>> config = ExportConfig(db_type="sqlite", sqlite_path="test.db")
            >>> config.db_url
            'sqlite:///test.db'

            >>> config = ExportConfig(
            ...     db_type="postgresql",
            ...     postgres_user="user",
            ...     postgres_password="pass",
            ...     postgres_host="localhost",
            ...     postgres_database="metrics"
            ... )
            >>> config.db_url
            'postgresql://user:pass@localhost:5432/metrics'
        """
        if self.db_type == "sqlite":
            return f"sqlite:///{self.sqlite_path}"
        elif self.db_type == "postgresql":
            if not self.postgres_user or not self.postgres_password:
                raise ValueError("postgres_user and postgres_password required for PostgreSQL")
            return (
                f"postgresql://{self.postgres_user}:{self.postgres_password}"
                f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_database}"
            )
        else:
            raise ValueError(f"Unsupported db_type: {self.db_type}")
