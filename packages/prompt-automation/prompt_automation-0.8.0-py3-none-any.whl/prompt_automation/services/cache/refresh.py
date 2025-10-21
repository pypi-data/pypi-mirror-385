"""Background cache refresh service (Feature 24: Local Cache)."""

from __future__ import annotations

import socket
import threading
import time
from typing import Callable, Optional

from prompt_automation.errorlog import get_logger

_log = get_logger(__name__)


class BackgroundRefreshService:
    """Background service for periodic cache refresh.
    
    Monitors network connectivity and refreshes cache when online.
    Runs in a separate daemon thread to avoid blocking main app.
    """

    def __init__(
        self,
        refresh_callback: Callable[[], None],
        interval_seconds: int = 300,  # 5 minutes default
        max_stale_age_seconds: int = 86400,  # 1 day default
    ) -> None:
        """Initialize background refresh service.
        
        Args:
            refresh_callback: Function to call for refresh (no args)
            interval_seconds: Refresh interval in seconds (default 5 min)
            max_stale_age_seconds: Max age for stale data (default 1 day)
        """
        self.refresh_callback = refresh_callback
        self.interval_seconds = interval_seconds
        self.max_stale_age_seconds = max_stale_age_seconds
        
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._running = False

    def start(self) -> None:
        """Start background refresh service."""
        if self._running:
            _log.debug("refresh_service_already_running")
            return
        
        self._stop_event.clear()
        self._running = True
        
        # Start daemon thread (exits when main app exits)
        self._thread = threading.Thread(
            target=self._refresh_loop,
            daemon=True,
            name="cache-refresh"
        )
        self._thread.start()
        
        _log.debug(
            "refresh_service_started interval_seconds=%d",
            self.interval_seconds
        )

    def stop(self) -> None:
        """Stop background refresh service."""
        if not self._running:
            return
        
        self._stop_event.set()
        self._running = False
        
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        
        _log.debug("refresh_service_stopped")

    def _refresh_loop(self) -> None:
        """Main refresh loop (runs in background thread)."""
        while not self._stop_event.is_set():
            try:
                # Check if online before refreshing
                if self._is_online():
                    _log.debug("refresh_started")
                    try:
                        self.refresh_callback()
                        _log.debug("refresh_completed")
                    except Exception as e:
                        _log.error("refresh_failed error=%s", e)
                else:
                    _log.debug("refresh_skipped_offline")
                
            except Exception as e:
                _log.error("refresh_loop_error error=%s", e)
            
            # Wait for next interval (or stop event)
            self._stop_event.wait(timeout=self.interval_seconds)

    def _is_online(self) -> bool:
        """Check if internet connection is available.
        
        Uses DNS query to Google's DNS server (8.8.8.8:53) as a simple
        connectivity test. This is a lightweight check that doesn't
        make HTTP requests.
        
        Returns:
            True if online, False otherwise
        """
        try:
            # Try to connect to Google DNS (port 53)
            # Timeout after 3 seconds
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            return False


__all__ = ["BackgroundRefreshService"]
