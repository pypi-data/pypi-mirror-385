"""Background template validation utilities."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Optional
import threading

from concurrent.futures import ThreadPoolExecutor


Callback = Callable[["TemplateValidationResult"], None]
Loader = Callable[[Path], Any]
ValidatorFn = Callable[[Any], bool]
Notifier = Callable[[Callable[[], None]], None]


@dataclass(frozen=True)
class TemplateValidationResult:
    path: Path
    valid: bool
    error: Optional[str] = None


class TemplateValidator:
    """Validate templates asynchronously when selections change."""

    def __init__(
        self,
        *,
        loader: Loader,
        validator: ValidatorFn,
        executor: ThreadPoolExecutor | None = None,
        notifier: Notifier | None = None,
    ) -> None:
        self._loader = loader
        self._validator = validator
        self._executor = executor or ThreadPoolExecutor(max_workers=1)
        self._owns_executor = executor is None
        self._notifier = notifier or (lambda fn: fn())
        self._lock = threading.Lock()
        self._seq = 0
        self._latest = 0
        self._closed = False

    def enqueue(
        self,
        path: Path | str,
        *,
        template: Any | None,
        callback: Callback | None = None,
    ) -> None:
        """Schedule validation for *path* and call *callback* with the result."""

        if self._closed:
            return
        path = Path(path)
        with self._lock:
            self._seq += 1
            seq = self._seq
            self._latest = seq

        def _task() -> TemplateValidationResult:
            data = template
            if data is None:
                try:
                    data = self._loader(path)
                except Exception as exc:
                    return TemplateValidationResult(path=path, valid=False, error=str(exc))
            try:
                valid = bool(self._validator(data))
            except Exception as exc:
                return TemplateValidationResult(path=path, valid=False, error=str(exc))
            if valid:
                return TemplateValidationResult(path=path, valid=True, error=None)
            return TemplateValidationResult(path=path, valid=False, error="Template validation failed")

        future = self._executor.submit(_task)

        def _on_done(fut):
            try:
                result = fut.result()
            except Exception as exc:
                result = TemplateValidationResult(path=path, valid=False, error=str(exc))
            with self._lock:
                if seq != self._latest:
                    return
            if callback is None:
                return

            def _deliver() -> None:
                try:
                    callback(result)
                except Exception:
                    pass

            self._notifier(_deliver)

        try:
            future.add_done_callback(_on_done)
        except Exception:
            # Fallback to synchronous execution if futures unavailable
            _on_done(future)

    def close(self) -> None:
        with self._lock:
            self._closed = True
        if self._owns_executor:
            try:
                self._executor.shutdown(wait=False)
            except Exception:
                pass


__all__ = ["TemplateValidator", "TemplateValidationResult"]
