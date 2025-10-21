"""File watcher for configuration hot-reload."""

import logging
import time
from pathlib import Path
from typing import Callable, Optional

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

logger = logging.getLogger(__name__)


class ConfigFileWatcher:
    """Watch configuration file for changes and trigger reload."""

    def __init__(
        self,
        config_path: Path,
        on_change: Callable[[], None],
        debounce_seconds: float = 0.3,
    ):
        """
        Initialize file watcher.

        Args:
            config_path: Path to configuration file to watch
            on_change: Callback to invoke when file changes
            debounce_seconds: Minimum time between reload triggers (default: 300ms)
        """
        self.config_path = config_path.resolve()
        self.on_change = on_change
        self.debounce_seconds = debounce_seconds
        self._observer: Optional[Observer] = None
        self._last_reload_time: float = 0.0

    def start(self) -> None:
        """Start watching for file changes."""
        if self._observer is not None:
            logger.warning("Watcher already started")
            return

        # Create event handler
        handler = _ConfigFileEventHandler(
            config_path=self.config_path,
            on_change=self._debounced_reload,
        )

        # Create and start observer
        self._observer = Observer()
        watch_dir = self.config_path.parent
        self._observer.schedule(handler, str(watch_dir), recursive=False)
        self._observer.start()

        logger.info(f"Started watching {self.config_path}")

    def stop(self) -> None:
        """Stop watching for file changes."""
        if self._observer is None:
            logger.warning("Watcher not started")
            return

        self._observer.stop()
        self._observer.join(timeout=2.0)
        self._observer = None

        logger.info(f"Stopped watching {self.config_path}")

    def _debounced_reload(self) -> None:
        """Reload with debouncing to avoid excessive reloads."""
        now = time.time()
        time_since_last = now - self._last_reload_time

        if time_since_last < self.debounce_seconds:
            logger.debug(
                f"Skipping reload (debounce: {time_since_last:.3f}s < "
                f"{self.debounce_seconds}s)"
            )
            return

        self._last_reload_time = now
        logger.info("Triggering config reload")

        try:
            self.on_change()
        except Exception as e:
            logger.error(f"Error during config reload: {e}", exc_info=True)


class _ConfigFileEventHandler(FileSystemEventHandler):
    """Internal event handler for watchdog."""

    def __init__(self, config_path: Path, on_change: Callable[[], None]):
        super().__init__()
        self.config_path = config_path
        self.on_change = on_change

    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file modification events."""
        if event.is_directory:
            return

        # Check if the modified file is our config file
        event_path = Path(event.src_path).resolve()
        if event_path == self.config_path:
            logger.debug(f"Config file modified: {event_path}")
            self.on_change()

    def on_created(self, event: FileSystemEvent) -> None:
        """Handle file creation events (config file restored)."""
        if event.is_directory:
            return

        event_path = Path(event.src_path).resolve()
        if event_path == self.config_path:
            logger.debug(f"Config file created: {event_path}")
            self.on_change()
