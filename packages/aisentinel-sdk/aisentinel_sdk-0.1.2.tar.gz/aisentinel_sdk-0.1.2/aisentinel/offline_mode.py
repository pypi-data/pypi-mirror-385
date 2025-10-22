"""Offline mode detection utilities for the AISentinel SDK."""

from __future__ import annotations

import logging
import queue
import socket
import threading
import time
from dataclasses import dataclass
from typing import Callable, Optional

LOGGER = logging.getLogger(__name__)

ConnectivityChecker = Callable[[], bool]
QueuedOperation = Callable[[], None]


@dataclass
class OfflineTask:
    """Represents an operation queued while offline."""

    operation: QueuedOperation
    description: str


class OfflineModeManager:
    """Manage automatic online/offline detection and queued operations."""

    def __init__(
        self,
        check_interval: float = 30.0,
        connectivity_checker: Optional[ConnectivityChecker] = None,
    ) -> None:
        self._check_interval = check_interval
        self._connectivity_checker = connectivity_checker or self._default_checker
        self._queue: "queue.Queue[OfflineTask]" = queue.Queue()
        self._lock = threading.RLock()
        self._last_check: float = 0.0
        self._is_online: Optional[bool] = None

    def _default_checker(self) -> bool:
        try:
            with socket.create_connection(("8.8.8.8", 53), timeout=2):
                return True
        except OSError:
            return False

    def is_online(self, force_refresh: bool = False) -> bool:
        """Return whether the environment currently appears online."""
        with self._lock:
            now = time.time()
            if (
                force_refresh
                or self._is_online is None
                or (now - self._last_check) > self._check_interval
            ):
                result = self._connectivity_checker()
                if result and self._is_online is False:
                    LOGGER.info("Connectivity restored; processing offline queue")
                    self._drain_queue_async()
                self._is_online = result
                self._last_check = now
            return bool(self._is_online)

    def enqueue(self, operation: QueuedOperation, description: str = "") -> None:
        """Queue an operation to run when connectivity is restored."""
        self._queue.put(OfflineTask(operation=operation, description=description))
        LOGGER.debug("Queued offline operation: %s", description or operation)

    def _drain_queue_async(self) -> None:
        thread = threading.Thread(
            target=self.process_queue, name="aisentinel-offline-drain", daemon=True
        )
        thread.start()

    def process_queue(self) -> None:
        """Process queued operations synchronously if online."""
        if not self.is_online(force_refresh=True):
            LOGGER.debug("Skipping queue processing; still offline")
            return
        while not self._queue.empty():
            task = self._queue.get()
            try:
                LOGGER.debug(
                    "Executing queued operation: %s", task.description or task.operation
                )
                task.operation()
            except Exception:  # pragma: no cover - defensive logging
                LOGGER.exception(
                    "Queued offline operation failed: %s", task.description
                )
            finally:
                self._queue.task_done()

    def clear_queue(self) -> None:
        """Remove all queued operations without executing them."""
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except queue.Empty:  # pragma: no cover - compatibility
                break
            finally:
                self._queue.task_done()


__all__ = ["OfflineModeManager", "OfflineTask"]
