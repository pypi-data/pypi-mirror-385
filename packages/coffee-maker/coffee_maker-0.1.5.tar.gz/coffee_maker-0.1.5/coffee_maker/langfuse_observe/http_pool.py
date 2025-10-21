"""HTTP connection pooling for efficient API requests.

This module provides connection pooling to improve performance when making
multiple HTTP requests to LLM providers.
"""

import logging
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


class HTTPConnectionPool:
    """Manages HTTP connection pools for efficient API requests."""

    _instance: Optional["HTTPConnectionPool"] = None
    _sync_client: Optional[httpx.Client] = None
    _async_client: Optional[httpx.AsyncClient] = None
    _initialized: bool = False

    def __new__(cls, **kwargs):
        """Singleton pattern to ensure only one pool exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        max_connections: int = 100,
        max_keepalive_connections: int = 20,
        keepalive_expiry: float = 30.0,
        timeout: float = 60.0,
    ):
        """Initialize HTTP connection pool.

        Args:
            max_connections: Maximum number of connections in the pool
            max_keepalive_connections: Maximum number of keep-alive connections
            keepalive_expiry: Time in seconds to keep idle connections alive
            timeout: Request timeout in seconds
        """
        # Only initialize once (singleton pattern)
        if self._initialized:
            return

        self.max_connections = max_connections
        self.max_keepalive_connections = max_keepalive_connections
        self.keepalive_expiry = keepalive_expiry
        self.timeout = timeout
        self._initialized = True

        # Create connection limits
        limits = httpx.Limits(
            max_connections=max_connections,
            max_keepalive_connections=max_keepalive_connections,
            keepalive_expiry=keepalive_expiry,
        )

        # Create timeout configuration
        timeout_config = httpx.Timeout(timeout)

        # Initialize sync client
        self._sync_client = httpx.Client(limits=limits, timeout=timeout_config)

        # Initialize async client
        self._async_client = httpx.AsyncClient(limits=limits, timeout=timeout_config)

        logger.info(
            f"Initialized HTTP connection pool: "
            f"max_connections={max_connections}, "
            f"keepalive={max_keepalive_connections}, "
            f"timeout={timeout}s"
        )

    @classmethod
    def get_client(cls, **kwargs) -> httpx.Client:
        """Get the singleton sync HTTP client.

        Args:
            **kwargs: Optional initialization parameters (only used on first call)

        Returns:
            Configured httpx.Client instance
        """
        instance = cls(**kwargs)
        return instance._sync_client

    @classmethod
    def get_async_client(cls, **kwargs) -> httpx.AsyncClient:
        """Get the singleton async HTTP client.

        Args:
            **kwargs: Optional initialization parameters (only used on first call)

        Returns:
            Configured httpx.AsyncClient instance
        """
        instance = cls(**kwargs)
        return instance._async_client

    @classmethod
    def close(cls):
        """Close all HTTP clients and clean up resources."""
        instance = cls._instance
        if instance is None:
            return

        if instance._sync_client is not None:
            instance._sync_client.close()
            logger.info("Closed sync HTTP client")

        if instance._async_client is not None:
            # Note: async client needs to be closed with await
            logger.warning("Async HTTP client should be closed with 'await close_async()'")

        cls._sync_client = None
        cls._async_client = None
        cls._initialized = False
        cls._instance = None

    @classmethod
    async def close_async(cls):
        """Close all HTTP clients asynchronously."""
        instance = cls._instance
        if instance is None:
            return

        if instance._sync_client is not None:
            instance._sync_client.close()
            logger.info("Closed sync HTTP client")

        if instance._async_client is not None:
            await instance._async_client.aclose()
            logger.info("Closed async HTTP client")

        cls._sync_client = None
        cls._async_client = None
        cls._initialized = False
        cls._instance = None

    @classmethod
    def reset(cls):
        """Reset the singleton instance (useful for testing)."""
        cls.close()


# Convenience functions for direct access
def get_http_client(**kwargs) -> httpx.Client:
    """Get configured HTTP client with connection pooling.

    Args:
        **kwargs: Optional pool configuration

    Returns:
        httpx.Client with connection pooling

    Example:
        >>> client = get_http_client()
        >>> response = client.get("https://api.example.com/data")
    """
    return HTTPConnectionPool.get_client(**kwargs)


def get_async_http_client(**kwargs) -> httpx.AsyncClient:
    """Get configured async HTTP client with connection pooling.

    Args:
        **kwargs: Optional pool configuration

    Returns:
        httpx.AsyncClient with connection pooling

    Example:
        >>> client = get_async_http_client()
        >>> response = await client.get("https://api.example.com/data")
    """
    return HTTPConnectionPool.get_async_client(**kwargs)
