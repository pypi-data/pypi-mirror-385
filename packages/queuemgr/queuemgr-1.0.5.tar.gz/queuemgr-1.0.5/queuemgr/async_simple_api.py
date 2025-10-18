"""
AsyncIO-compatible Simple API for the queue system.

This module provides asyncio-compatible versions of the simple API
that work correctly in asyncio applications and web servers.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

import asyncio
import atexit
import signal
import sys
from typing import Dict, Any, Optional, Type, List
from contextlib import asynccontextmanager

from .async_process_manager import AsyncProcessManager, async_queue_system
from .jobs.base import QueueJobBase
from queuemgr.exceptions import ProcessControlError


class AsyncQueueSystem:
    """
    AsyncIO-compatible simple API for the queue system.

    Provides a high-level interface that automatically manages the process
    manager and handles cleanup, designed to work with asyncio applications.
    """

    def __init__(
        self,
        registry_path: str = "queuemgr_registry.jsonl",
        shutdown_timeout: float = 30.0,
    ):
        """
        Initialize the async queue system.

        Args:
            registry_path: Path to the registry file.
            shutdown_timeout: Timeout for graceful shutdown.
        """
        self.registry_path = registry_path
        self.shutdown_timeout = shutdown_timeout
        self._manager: Optional[AsyncProcessManager] = None
        self._is_initialized = False

    async def start(self) -> None:
        """
        Start the async queue system.

        Raises:
            ProcessControlError: If the system is already running or fails to start.
        """
        if self._is_initialized:
            raise ProcessControlError(
                "system", "start", "Queue system is already running"
            )

        try:
            from .process_config import ProcessManagerConfig
            config = ProcessManagerConfig(
                registry_path=self.registry_path,
                shutdown_timeout=self.shutdown_timeout
            )
            self._manager = AsyncProcessManager(config)
            await self._manager.start()
            self._is_initialized = True
        except Exception as e:
            raise ProcessControlError("system", "start", f"Failed to start system: {e}")

    async def stop(self) -> None:
        """
        Stop the async queue system.

        Raises:
            ProcessControlError: If the system is not running or fails to stop.
        """
        if not self._is_initialized:
            return

        try:
            if self._manager:
                await self._manager.stop()
            self._is_initialized = False
        except Exception as e:
            raise ProcessControlError("system", "stop", f"Failed to stop system: {e}")

    def is_running(self) -> bool:
        """
        Check if the queue system is running.

        Returns:
            True if the system is running, False otherwise.
        """
        return (
            self._is_initialized
            and self._manager is not None
            and self._manager.is_running()
        )

    async def add_job(
        self, job_class: Type[QueueJobBase], job_id: str, params: Dict[str, Any]
    ) -> None:
        """
        Add a job to the queue.

        Args:
            job_class: Job class to instantiate.
            job_id: Unique job identifier.
            params: Job parameters.

        Raises:
            ProcessControlError: If the system is not running or command fails.
        """
        if not self.is_running():
            raise ProcessControlError(
                "system", "add_job", "Queue system is not running"
            )

        await self._manager.add_job(job_class, job_id, params)

    async def start_job(self, job_id: str) -> None:
        """
        Start a job.

        Args:
            job_id: Job identifier.

        Raises:
            ProcessControlError: If the system is not running or command fails.
        """
        if not self.is_running():
            raise ProcessControlError(
                "system", "start_job", "Queue system is not running"
            )

        await self._manager.start_job(job_id)

    async def stop_job(self, job_id: str) -> None:
        """
        Stop a job.

        Args:
            job_id: Job identifier.

        Raises:
            ProcessControlError: If the system is not running or command fails.
        """
        if not self.is_running():
            raise ProcessControlError(
                "system", "stop_job", "Queue system is not running"
            )

        await self._manager.stop_job(job_id)

    async def delete_job(self, job_id: str, force: bool = False) -> None:
        """
        Delete a job.

        Args:
            job_id: Job identifier.
            force: Force deletion even if job is running.

        Raises:
            ProcessControlError: If the system is not running or command fails.
        """
        if not self.is_running():
            raise ProcessControlError(
                "system", "delete_job", "Queue system is not running"
            )

        await self._manager.delete_job(job_id, force)

    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get job status.

        Args:
            job_id: Job identifier.

        Returns:
            Job status information.

        Raises:
            ProcessControlError: If the system is not running or command fails.
        """
        if not self.is_running():
            raise ProcessControlError(
                "system", "get_job_status", "Queue system is not running"
            )

        return await self._manager.get_job_status(job_id)

    async def list_jobs(self) -> List[Dict[str, Any]]:
        """
        List all jobs.

        Returns:
            List of job information.

        Raises:
            ProcessControlError: If the system is not running or command fails.
        """
        if not self.is_running():
            raise ProcessControlError(
                "system", "list_jobs", "Queue system is not running"
            )

        return await self._manager.list_jobs()


@asynccontextmanager
async def async_queue_system_context(
    registry_path: str = "queuemgr_registry.jsonl",
    shutdown_timeout: float = 30.0,
):
    """
    AsyncIO-compatible context manager for the queue system.

    Args:
        registry_path: Path to the registry file.
        shutdown_timeout: Timeout for graceful shutdown.

    Yields:
        AsyncQueueSystem: The async queue system instance.

    Example:
        ```python
        async with async_queue_system_context() as queue:
            await queue.add_job(MyJob, "job1", {"param": "value"})
            await queue.start_job("job1")
            status = await queue.get_job_status("job1")
        ```
    """
    queue_system = AsyncQueueSystem(registry_path, shutdown_timeout)

    try:
        await queue_system.start()
        yield queue_system
    finally:
        await queue_system.stop()


# Global async queue system instance for convenience
_global_async_queue: Optional[AsyncQueueSystem] = None


async def get_global_async_queue() -> AsyncQueueSystem:
    """
    Get the global async queue system instance.

    Returns:
        The global async queue system instance.

    Raises:
        ProcessControlError: If the global queue system is not initialized.
    """
    global _global_async_queue

    if _global_async_queue is None:
        _global_async_queue = AsyncQueueSystem()
        await _global_async_queue.start()

    return _global_async_queue


async def shutdown_global_async_queue() -> None:
    """
    Shutdown the global async queue system.

    This function should be called during application shutdown.
    """
    global _global_async_queue

    if _global_async_queue is not None:
        await _global_async_queue.stop()
        _global_async_queue = None


# Register cleanup function
async def _cleanup_handler():
    """Cleanup handler for graceful shutdown."""
    await shutdown_global_async_queue()


# Register cleanup for different signal types
def _setup_async_cleanup():
    """Setup async cleanup handlers."""
    try:
        # Only register if we're in the main thread
        if hasattr(signal, "SIGTERM"):
            signal.signal(
                signal.SIGTERM, lambda s, f: asyncio.create_task(_cleanup_handler())
            )
        if hasattr(signal, "SIGINT"):
            signal.signal(
                signal.SIGINT, lambda s, f: asyncio.create_task(_cleanup_handler())
            )
    except ValueError:
        # Signals can only be registered in the main thread
        # This is expected in some contexts, so we ignore the error
        pass


# Setup cleanup on module import
_setup_async_cleanup()
