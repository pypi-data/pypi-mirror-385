"""Background validation service producing auto-repair suggestions."""

from __future__ import annotations

import json
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional

from ..config import PROMPTS_DIR
from ..errorlog import get_logger
from ..renderer import load_template, validate_template
from .cache.manager import ensure_cache_subdir, validate_cache_path

_log = get_logger(__name__)

REQUIRED_TEMPLATE_KEYS = {"id", "title", "style", "template", "placeholders"}


@dataclass
class ValidationSummary:
    total_templates: int
    invalid_templates: int
    messages: List[dict]


class BackgroundValidator:
    def __init__(
        self,
        root: Path | None = None,
        *,
        interval_seconds: float = 30.0,
        cache_root: Path | None = None,
        time_fn: callable | None = None,
    ) -> None:
        self.root = (root or PROMPTS_DIR).resolve()
        self.interval = float(interval_seconds)
        self.cache_root = (cache_root or Path("cache")).resolve()
        self._clock = time_fn or time.perf_counter
        self._log_dir = ensure_cache_subdir(self.cache_root, "validation")
        self._log_path = validate_cache_path(
            self._log_dir, self._log_dir / "repair-suggestions.log"
        )
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    # ------------------------------------------------------------------
    def start(self) -> None:
        with self._lock:
            if self._thread and self._thread.is_alive():
                return
            self._stop_event.clear()
            self._thread = threading.Thread(
                target=self._worker, name="background-validator", daemon=True
            )
            self._thread.start()

    def stop(self) -> None:
        with self._lock:
            if not self._thread:
                return
            self._stop_event.set()
            thread = self._thread
        if thread and thread.is_alive():
            thread.join()

    # ------------------------------------------------------------------
    def run_once(self) -> ValidationSummary:
        messages: List[dict] = []
        total = 0
        invalid = 0
        for path in self._iter_templates():
            total += 1
            suggestion = self._validate_template(path)
            if suggestion is None:
                continue
            invalid += 1
            messages.append(suggestion)
        if messages:
            self._append_log(messages)
        summary = ValidationSummary(
            total_templates=total, invalid_templates=invalid, messages=messages
        )
        try:
            _log.info(
                "%s",
                {
                    "event": "background_validator.run_once",
                    "total": total,
                    "invalid": invalid,
                },
            )
        except Exception:  # pragma: no cover - logging safety
            pass
        return summary

    # ------------------------------------------------------------------
    def _iter_templates(self) -> Iterable[Path]:
        for path in sorted(self.root.rglob("*.json")):
            if path.name.lower() == "settings.json" and path.parent.name == "Settings":
                continue
            yield path

    def _validate_template(self, path: Path) -> Optional[dict]:
        try:
            data = load_template(path)
        except Exception as exc:
            return {
                "path": path.relative_to(self.root).as_posix(),
                "reason": "unreadable",
                "detail": str(exc),
            }
        missing = sorted(k for k in REQUIRED_TEMPLATE_KEYS if k not in data)
        if missing:
            return {
                "path": path.relative_to(self.root).as_posix(),
                "reason": "missing_keys",
                "missing": missing,
            }
        if not validate_template(data):
            return {
                "path": path.relative_to(self.root).as_posix(),
                "reason": "schema_validation_failed",
            }
        return None

    def _append_log(self, messages: List[dict]) -> None:
        payload = {"event": "validation.repair_suggestions", "entries": messages}
        serialized = json.dumps(payload, ensure_ascii=False)
        try:
            with self._log_path.open("a", encoding="utf-8") as fh:
                fh.write(serialized + "\n")
        except Exception:
            pass

    def _worker(self) -> None:
        while not self._stop_event.is_set():
            try:
                self.run_once()
            except Exception:
                try:
                    _log.warning("background_validator.error", exc_info=True)
                except Exception:
                    pass
            self._stop_event.wait(self.interval)


__all__ = ["BackgroundValidator", "ValidationSummary"]
