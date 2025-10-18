"""
Core ProcManager functionality.

This module contains the core ProcManager class that manages
the queue system in a separate process.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

import json
import signal
import time
from multiprocessing import Process
from typing import Dict, Any, Optional
from pathlib import Path

from .queue.job_queue import JobQueue
from .core.registry import JsonlRegistry
from .core.exceptions import ProcessControlError
from .proc_config import ProcManagerConfig


class ProcManager:
    """
    High-level process manager using /proc filesystem.

    Manages the entire queue system in a separate process with automatic
    cleanup and graceful shutdown using Linux /proc filesystem.
    """

    def __init__(self, config: Optional[ProcManagerConfig] = None):
        """
        Initialize the process manager.

        Args:
            config: Configuration for the process manager.
        """
        self.config = config or ProcManagerConfig()
        self._proc_dir = Path(self.config.proc_dir)
        self._process: Optional[Process] = None
        self._running = False

    def start(self, registry_path: str = None, proc_dir: str = None) -> None:
        """
        Start the manager process.

        Args:
            registry_path: Path to registry file.
            proc_dir: Directory for /proc files.

        Raises:
            ProcessControlError: If start fails.
        """
        if self._running:
            raise ProcessControlError(
                "manager", "start", "Process manager is already running"
            )

        # Update config if provided
        if registry_path:
            self.config.registry_path = registry_path
        if proc_dir:
            self.config.proc_dir = proc_dir
            self._proc_dir = Path(proc_dir)

        try:
            # Create proc directory
            self._proc_dir.mkdir(parents=True, exist_ok=True)

            # Start manager process
            self._process = Process(
                target=self._manager_process, args=(self.config,), name="QueueManager"
            )
            self._process.start()

            # Wait for ready signal
            self._wait_for_ready()

            self._running = True

        except (OSError, IOError, ValueError, TimeoutError) as e:
            self.stop()
            raise ProcessControlError(
                "manager", "start", f"Failed to start manager: {e}"
            )

    def stop(self, timeout: float = None) -> None:
        """
        Stop the manager process.

        Args:
            timeout: Maximum time to wait for shutdown.

        Raises:
            ProcessControlError: If stop fails.
        """
        if not self._running:
            raise ProcessControlError("manager", "stop", "Manager is not running")

        try:
            # Send shutdown command
            self._send_command("shutdown", {})

            # Wait for process to finish
            if self._process:
                self._process.join(timeout=timeout or self.config.shutdown_timeout)

            # Cleanup
            self._cleanup()

        except (OSError, IOError, ValueError, TimeoutError) as e:
            raise ProcessControlError("manager", "stop", f"Failed to stop manager: {e}")

        finally:
            self._running = False

    def is_running(self) -> bool:
        """
        Check if manager is running.

        Returns:
            True if running, False otherwise.
        """
        return self._running and self._process is not None and self._process.is_alive()

    def add_job(self, job_class: type, job_id: str, params: Dict[str, Any]) -> None:
        """
        Add a job to the queue.

        Args:
            job_class: Job class to instantiate.
            job_id: Unique job identifier.
            params: Job parameters.

        Raises:
            ProcessControlError: If add fails.
        """
        if not self.is_running():
            raise ProcessControlError(
                "manager", "operation", Exception("Manager is not running")
            )

        self._send_command(
            "add_job",
            {
                "job_class_name": job_class.__name__,
                "job_class_module": job_class.__module__,
                "job_id": job_id,
                "params": params,
            },
        )

    def start_job(self, job_id: str) -> None:
        """
        Start a job.

        Args:
            job_id: Job identifier.

        Raises:
            ProcessControlError: If start fails.
        """
        if not self.is_running():
            raise ProcessControlError(
                "manager", "operation", Exception("Manager is not running")
            )

        self._send_command("start_job", {"job_id": job_id})

    def stop_job(self, job_id: str) -> None:
        """
        Stop a job.

        Args:
            job_id: Job identifier.

        Raises:
            ProcessControlError: If stop fails.
        """
        if not self.is_running():
            raise ProcessControlError(
                "manager", "operation", Exception("Manager is not running")
            )

        self._send_command("stop_job", {"job_id": job_id})

    def delete_job(self, job_id: str) -> None:
        """
        Delete a job.

        Args:
            job_id: Job identifier.

        Raises:
            ProcessControlError: If delete fails.
        """
        if not self.is_running():
            raise ProcessControlError(
                "manager", "operation", Exception("Manager is not running")
            )

        self._send_command("delete_job", {"job_id": job_id})

    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get the status of a specific job.

        Args:
            job_id: Job identifier.

        Returns:
            Job status information.

        Raises:
            ProcessControlError: If operation fails.
        """
        if not self.is_running():
            raise ProcessControlError(
                "manager", "operation", Exception("Manager is not running")
            )

        result = self._send_command("get_job_status", {"job_id": job_id})
        return result if isinstance(result, dict) else {}

    def list_jobs(self) -> list:
        """
        List all jobs.

        Returns:
            List of job information.

        Raises:
            ProcessControlError: If operation fails.
        """
        if not self.is_running():
            raise ProcessControlError(
                "manager", "operation", Exception("Manager is not running")
            )

        result = self._send_command("list_jobs", {})
        return result if isinstance(result, list) else []

    def _send_command(self, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send a command to the manager process via /proc."""
        try:
            # Write command to command file
            command_file = self._proc_dir / "command"
            with open(command_file, "w") as f:
                json.dump({"command": command, "params": params}, f)

            # Wait for response
            response_file = self._proc_dir / "response"
            timeout = 30.0
            start_time = time.time()

            while not response_file.exists():
                if time.time() - start_time > timeout:
                    raise ProcessControlError("manager", "command", "Command timeout")
                time.sleep(0.1)

            # Read response
            with open(response_file, "r") as f:
                response = json.load(f)

            # Clean up response file
            response_file.unlink()

            return response

        except (OSError, IOError, ValueError, TimeoutError) as e:
            raise ProcessControlError("manager", "command", f"Command failed: {e}")

    def _wait_for_ready(self) -> None:
        """Wait for manager process to be ready."""
        ready_file = self._proc_dir / "ready"
        start_time = time.time()

        while not ready_file.exists():
            if time.time() - start_time > 30.0:
                raise ProcessControlError(
                    "manager",
                    "initialization",
                    "Manager failed to initialize within timeout",
                )
            time.sleep(0.1)

    def _cleanup(self) -> None:
        """Clean up proc directory."""
        try:
            if self._proc_dir.exists():
                for file in self._proc_dir.glob("*"):
                    file.unlink()
                self._proc_dir.rmdir()
        except (OSError, IOError):
            pass  # Ignore cleanup errors

    @staticmethod
    def _manager_process(config: ProcManagerConfig) -> None:
        """Manager process entry point."""
        try:
            # Setup signal handlers
            signal.signal(signal.SIGTERM, lambda s, f: None)
            signal.signal(signal.SIGINT, lambda s, f: None)

            # Initialize queue system
            registry = JsonlRegistry(config.registry_path)
            queue = JobQueue(registry=registry)

            # Create proc directory
            proc_dir = Path(config.proc_dir)
            proc_dir.mkdir(parents=True, exist_ok=True)

            # Create ready file
            ready_file = proc_dir / "ready"
            ready_file.touch()

            # Main loop
            while True:
                try:
                    # Check for commands
                    command_file = proc_dir / "command"
                    if command_file.exists():
                        # Read command
                        with open(command_file, "r") as f:
                            command_data = json.load(f)

                        # Process command
                        response = ProcManager._process_command(
                            queue, command_data["command"], command_data["params"]
                        )

                        # Write response
                        response_file = proc_dir / "response"
                        with open(response_file, "w") as f:
                            json.dump(response, f)

                        # Clean up command file
                        command_file.unlink()

                    time.sleep(0.1)

                except (OSError, IOError, ValueError, TimeoutError):
                    break

        except (OSError, IOError, ValueError, TimeoutError):
            pass

        finally:
            # Cleanup
            try:
                if proc_dir.exists():
                    for file in proc_dir.glob("*"):
                        file.unlink()
            except (OSError, IOError):
                pass

    @staticmethod
    def _process_command(
        queue: JobQueue, command: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process a command from the manager."""
        try:
            if command == "add_job":
                # Import job class
                job_class_name = params["job_class_name"]
                job_class_module = params["job_class_module"]

                module = __import__(job_class_module, fromlist=[job_class_name])
                job_class = getattr(module, job_class_name)

                queue.add_job(job_class, params["job_id"], params["params"])
                return {"status": "success"}

            elif command == "start_job":
                queue.start_job(params["job_id"])
                return {"status": "success"}

            elif command == "stop_job":
                queue.stop_job(params["job_id"])
                return {"status": "success"}

            elif command == "delete_job":
                queue.delete_job(params["job_id"])
                return {"status": "success"}

            elif command == "get_job_status":
                status = queue.get_job_status(params["job_id"])
                return {"status": "success", "result": status}

            elif command == "list_jobs":
                jobs = queue.list_jobs()
                return {"status": "success", "result": jobs}

            elif command == "shutdown":
                queue.shutdown()
                return {"status": "shutdown"}

            else:
                return {"status": "error", "error": f"Unknown command: {command}"}
        except (OSError, IOError, ValueError, TimeoutError) as e:
            return {"status": "error", "error": str(e)}
