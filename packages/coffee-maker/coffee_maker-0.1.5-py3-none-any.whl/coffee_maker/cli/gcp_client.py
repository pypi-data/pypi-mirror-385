"""
GCP Daemon Client for project-manager CLI.

This module provides a client for interacting with the code_developer daemon
deployed on Google Cloud Platform.
"""

import logging
import os
from typing import Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class GCPDaemonClient:
    """Client for interacting with GCP-deployed code_developer daemon."""

    def __init__(self, api_url: str, api_key: Optional[str] = None):
        """
        Initialize GCP daemon client.

        Args:
            api_url: Base URL of the daemon API (e.g., https://code-developer-xxx.run.app)
            api_key: API key for authentication (optional if using gcloud auth)
        """
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key or os.getenv("COFFEE_MAKER_API_KEY")

        # Configure session with retries
        self.session = requests.Session()

        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=[
                "HEAD",
                "GET",
                "PUT",
                "DELETE",
                "OPTIONS",
                "TRACE",
                "POST",
            ],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Set authentication headers
        if self.api_key:
            self.session.headers["Authorization"] = f"Bearer {self.api_key}"

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """
        Make authenticated request to daemon API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., "/api/daemon/status")
            **kwargs: Additional request parameters

        Returns:
            Response JSON data

        Raises:
            requests.HTTPError: If request fails
        """
        url = f"{self.api_url}{endpoint}"
        logger.debug(f"{method} {url}")

        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()

        return response.json()

    def get_status(self) -> Dict:
        """
        Get current daemon status from GCP.

        Returns:
            Status information including:
            - status: running, stopped, error
            - current_priority: Priority being implemented
            - progress: Progress information
        """
        return self._request("GET", "/api/daemon/status")

    def start_daemon(self, priority: Optional[str] = None) -> Dict:
        """
        Start daemon implementation on GCP.

        Args:
            priority: Optional priority to implement (e.g., "PRIORITY 1")
                     If not specified, daemon will implement next planned priority

        Returns:
            Start confirmation
        """
        params = {"priority": priority} if priority else {}
        return self._request("POST", "/api/daemon/start", params=params)

    def stop_daemon(self) -> Dict:
        """
        Stop daemon on GCP.

        Returns:
            Stop confirmation
        """
        return self._request("POST", "/api/daemon/stop")

    def restart_daemon(self) -> Dict:
        """
        Restart daemon on GCP.

        Returns:
            Restart confirmation
        """
        return self._request("POST", "/api/daemon/restart")

    def stream_logs(self, follow: bool = True) -> None:
        """
        Stream logs from GCP daemon.

        Args:
            follow: If True, continuously stream logs (like tail -f)
        """
        endpoint = "/api/status/logs"
        url = f"{self.api_url}{endpoint}"

        try:
            with self.session.get(url, stream=True) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if line:
                        print(line.decode("utf-8"))
        except KeyboardInterrupt:
            logger.info("Log streaming interrupted")
        except Exception as e:
            logger.error(f"Error streaming logs: {e}")

    def get_roadmap(self) -> str:
        """
        Get ROADMAP.md content from GCP.

        Returns:
            ROADMAP.md content
        """
        response = self._request("GET", "/api/files/roadmap")
        return response["content"]

    def update_roadmap(self, content: str) -> Dict:
        """
        Update ROADMAP.md on GCP.

        Args:
            content: New ROADMAP.md content

        Returns:
            Update confirmation
        """
        return self._request("POST", "/api/files/roadmap", json={"content": content})

    def get_file(self, path: str) -> str:
        """
        Read project file from GCP.

        Args:
            path: File path relative to workspace root

        Returns:
            File content
        """
        response = self._request("GET", f"/api/files/{path}")
        return response["content"]

    def update_file(self, path: str, content: str) -> Dict:
        """
        Update project file on GCP.

        Args:
            path: File path relative to workspace root
            content: New file content

        Returns:
            Update confirmation
        """
        return self._request("PUT", f"/api/files/{path}", json={"content": content})

    def get_system_status(self) -> Dict:
        """
        Get comprehensive system status.

        Returns:
            System status including CPU, memory, disk usage
        """
        return self._request("GET", "/api/status")

    def get_metrics(self) -> Dict:
        """
        Get performance metrics.

        Returns:
            Metrics including task counts, costs, performance
        """
        return self._request("GET", "/api/status/metrics")

    def health_check(self) -> bool:
        """
        Check if daemon is healthy.

        Returns:
            True if healthy, False otherwise
        """
        try:
            response = self._request("GET", "/api/health")
            return response.get("status") == "healthy"
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False


def load_gcp_config() -> Optional[Dict]:
    """
    Load GCP configuration from ~/.config/coffee-maker/gcp.yaml

    Returns:
        GCP configuration dict or None if not found
    """
    import yaml
    from pathlib import Path

    config_path = Path.home() / ".config" / "coffee-maker" / "gcp.yaml"

    if not config_path.exists():
        return None

    with open(config_path) as f:
        config = yaml.safe_load(f)

    return config.get("gcp")


def get_gcp_client() -> Optional[GCPDaemonClient]:
    """
    Get configured GCP daemon client.

    Returns:
        GCPDaemonClient instance or None if not configured
    """
    config = load_gcp_config()

    if not config or not config.get("enabled"):
        return None

    api_url = config.get("api_url")
    api_key_env = config.get("api_key_env", "COFFEE_MAKER_API_KEY")
    api_key = os.getenv(api_key_env)

    if not api_url:
        logger.warning("GCP API URL not configured")
        return None

    return GCPDaemonClient(api_url, api_key)
