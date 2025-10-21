# restart_mcp_server.py
import logging
import socket
import sys
import time
from multiprocessing import Process  # Import the Process class
from typing import Callable, Optional

import psutil

# --- Logging Configuration when used as a function and not a class ---
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
LOGGER = logging.getLogger(__name__)

# Timing constants (in seconds)
PORT_RELEASE_WAIT_SECONDS = 1.0
"""Time to wait for OS to release port after killing process."""

SERVER_POLL_INTERVAL_SECONDS = 0.5
"""Interval between server readiness checks."""

DEFAULT_SERVER_TIMEOUT_SECONDS = 10
"""Default timeout for waiting for server to become ready."""


def kill_process_on_port(port: int, logger=LOGGER):
    """Kills a process that is listening on the specified port."""
    logger.info(f"Searching for a process on port {port}...")
    existing_process = find_process_on_port(port)

    if existing_process:
        logger.info(f"Found existing server with PID: {existing_process.pid}. Terminating it.")
        try:
            existing_process.terminate()
            existing_process.wait(timeout=3)
        except psutil.TimeoutExpired:
            logger.info("Process did not terminate gracefully. Forcing shutdown (SIGKILL)...")
            existing_process.kill()
        except psutil.NoSuchProcess:
            logger.info("Process already terminated before we could kill it.")

        logger.info("Giving the OS a moment to release the port...")
        time.sleep(PORT_RELEASE_WAIT_SECONDS)
    else:
        logger.info(f"No existing server found on port {port}.")


def run_daemon(function_to_run: Callable, port: int, logger=LOGGER):
    """
    Finds and kills an existing server process on the specified port,
    then starts a new one as a background daemon using multiprocessing.
    """

    kill_process_on_port(port)

    # Start the new server process in the background
    logger.info(f"Starting new server by calling the start_server() function in a new process...")

    # Create a new Process object.
    # The 'target' is the function you want to run in the new process.
    server_process = Process(target=function_to_run, daemon=True)

    # Start the process. This will execute the start_server function.
    server_process.start()

    wait_for_server_ready("127.0.0.1", port)
    logger.info(f"Server started successfully in the background with PID: {server_process.pid}.")
    print("Note: Since this is a daemon process, it will exit when this main script exits.")


def wait_for_server_ready(host: str, port: int, timeout: int = DEFAULT_SERVER_TIMEOUT_SECONDS) -> bool:
    """
    Waits for a network server to become available on a specific host and port.

    Args:
        host (str): The server host (e.g., '127.0.0.1').
        port (int): The server port.
        timeout (int): The maximum time to wait in seconds.

    Returns:
        bool: True if the server is ready, False if the timeout is reached.
    """
    start_time = time.monotonic()
    while time.monotonic() - start_time < timeout:
        try:
            with socket.create_connection((host, port), timeout=1):
                LOGGER.info(f"Server on port {port} is ready!")
                return True
        except (socket.timeout, ConnectionRefusedError):
            # Server is not ready yet, wait a bit before retrying
            time.sleep(SERVER_POLL_INTERVAL_SECONDS)
    LOGGER.error(f"Server on port {port} did not become ready within {timeout} seconds.")
    return False


def find_process_on_port(port: int) -> Optional[psutil.Process]:
    """
    Finds a process that is listening on the specified port.
    This version gracefully handles AccessDenied errors when scanning processes.
    """
    # Iterate through all running processes
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            # Get the connections for the current process
            for conn in proc.net_connections(kind="inet"):
                # Check if the connection matches the port and is in a listening state
                if conn.laddr.port == port and conn.status == psutil.CONN_LISTEN:
                    return proc  # Found the process!
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            # This can happen if the process terminates while we're inspecting it,
            # or if we don't have permission to access its details (the core issue).
            # We simply ignore it and continue to the next process.
            continue
    return None  # No process found on the specified port


class DeamonProcessOnPortHandler:
    def __init__(self, port: int, function_to_run: Callable):
        self.port = port
        self.function_to_run = function_to_run
        logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger(f"DeamonProcessOnPortHandler.{function_to_run}")

    def run_daemon(self):
        run_daemon(self.function_to_run, self.port, self.logger)

    def kill_process_on_port(self):
        kill_process_on_port(self.port, self.logger)
