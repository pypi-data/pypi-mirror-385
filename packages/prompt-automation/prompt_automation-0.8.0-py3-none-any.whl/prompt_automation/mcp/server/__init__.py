"""MCP server entrypoint exposing the project planning tool."""
from __future__ import annotations

import json
import math
import random
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Optional, TextIO
from urllib import error as urllib_error
from urllib import request as urllib_request

from ... import features
from ...errorlog import get_logger
from ...renderer import load_template
from ...menus import (
    render_template as _render_template,
    suppress_mcp_project_execution,
)
from ..config import RetryPolicy
from . import note_schemas, note_tools, vault_paths
from ...config import PROMPTS_DIR, PROMPTS_SEARCH_PATHS
from ..observability.hooks import (
    global_state as observability_state,
    record_project_call_metric,
)

_log = get_logger(__name__)


TOOL_NAME = "pa.project.run"
_INPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "goals": {"type": "string"},
        "trace_id": {"type": "string"},
        "dry_run": {"type": "boolean"},
        "template": {"type": "object"},
        "template_metadata": {"type": "object"},
        "template_id": {"type": ["string", "number"]},
        "template_payload": {"type": "object"},
        "variables": {"type": "object"},
    },
    "additionalProperties": False,
}

_TEMPLATE_PATH = (
    PROMPTS_DIR
    / "LLM"
    / "Analysis"
    / "Planning"
    / "project_creator_then_assessor__id_13008.json"
)

_DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}

_RETRY_DELAY_SECONDS = 0.25
_PRIMARY_ENDPOINT = "http://127.0.0.1:8080/v1/models"
_FALLBACK_ENDPOINT = "http://127.0.0.1:8080/v1/chat/completions"
_MAX_TOKENS = 8192

DEFAULT_RETRY_POLICY = RetryPolicy(
    base_delay=_RETRY_DELAY_SECONDS,
    max_delay=_RETRY_DELAY_SECONDS * 2,
    jitter=0.0,
    max_attempts=5,
    max_duration=5.0,
)

_TEMPLATE_CACHE: Dict[str, Any] | None = None

_TEMPLATE_INDEX_BY_ID: Dict[Any, Dict[str, Any]] = {}
_TEMPLATE_INDEX_BY_PATH: Dict[str, Dict[str, Any]] = {}
_TEMPLATE_INDEX_SCANNED = False

_TEMPLATE_BY_REAL_PATH: Dict[Path, Dict[str, Any]] = {}
_METADATA_PATH_CACHE: Dict[str, Path] = {}

_GOALS_FALLBACK_TEXT = "Plan the project using the available context."


class InputValidationError(ValueError):
    """Raised when tool arguments fail schema validation."""


class ProjectExecutionCancelled(RuntimeError):
    """Raised when an MCP project execution is cancelled by the caller."""


def _normalize_metadata_path(value: str) -> str:
    cleaned = value.strip().replace("\\", "/")
    while cleaned.startswith("./"):
        cleaned = cleaned[2:]
    cleaned = cleaned.lstrip("/")
    return cleaned.lower()


def _iter_template_id_keys(value: Any) -> list[Any]:
    keys: list[Any] = []
    if isinstance(value, int):
        keys.append(value)
        keys.append(str(value))
    elif isinstance(value, str):
        stripped = value.strip()
        if stripped:
            keys.extend({stripped, value})
            if stripped.isdigit():
                keys.append(int(stripped))
    else:
        keys.append(value)
    seen: set[Any] = set()
    ordered: list[Any] = []
    for item in keys:
        if item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return ordered


def _register_template_index(template: Dict[str, Any], path: Path) -> None:
    global _TEMPLATE_INDEX_BY_ID, _TEMPLATE_INDEX_BY_PATH
    identifier = template.get("id")
    if identifier is not None:
        for key in _iter_template_id_keys(identifier):
            if key not in _TEMPLATE_INDEX_BY_ID:
                _TEMPLATE_INDEX_BY_ID[key] = template
    metadata = template.get("metadata") if isinstance(template.get("metadata"), dict) else {}
    if isinstance(metadata, dict):
        for hint_key in ("path", "relative_path", "relpath", "template_path"):
            raw = metadata.get(hint_key)
            if isinstance(raw, str) and raw.strip():
                normalized = _normalize_metadata_path(raw)
                if normalized:
                    if normalized not in _TEMPLATE_INDEX_BY_PATH:
                        _TEMPLATE_INDEX_BY_PATH[normalized] = template
                    _METADATA_PATH_CACHE.setdefault(normalized, path)
        history = metadata.get("path_history")
        if isinstance(history, list):
            for entry in history:
                if isinstance(entry, str) and entry.strip():
                    normalized = _normalize_metadata_path(entry)
                    if normalized:
                        if normalized not in _TEMPLATE_INDEX_BY_PATH:
                            _TEMPLATE_INDEX_BY_PATH[normalized] = template
                        _METADATA_PATH_CACHE.setdefault(normalized, path)
    try:
        relative = path.relative_to(PROMPTS_DIR).as_posix()
    except ValueError:
        relative = path.as_posix()
    normalized_relative = _normalize_metadata_path(relative)
    if normalized_relative:
        if normalized_relative not in _TEMPLATE_INDEX_BY_PATH:
            _TEMPLATE_INDEX_BY_PATH[normalized_relative] = template
        _METADATA_PATH_CACHE.setdefault(normalized_relative, path)


def _lookup_template_from_index(
    ids: list[Any], path_hints: list[str]
) -> Dict[str, Any] | None:
    for key in ids:
        for candidate in _iter_template_id_keys(key):
            template = _TEMPLATE_INDEX_BY_ID.get(candidate)
            if template is not None:
                return template
    for raw in path_hints:
        normalized = _normalize_metadata_path(raw)
        if not normalized:
            continue
        template = _TEMPLATE_INDEX_BY_PATH.get(normalized)
        if template is not None:
            return template
    return None


def _expand_metadata_hint_variants(raw: str) -> list[str]:
    normalized = raw.replace("\\", "/").strip()
    while normalized.startswith("./"):
        normalized = normalized[2:]
    normalized = normalized.lstrip("/")
    if not normalized:
        return []

    queue: list[str] = [normalized]
    seen: set[str] = set()
    variants: list[str] = []

    while queue:
        current = queue.pop(0)
        key = current.lower()
        if key in seen:
            continue
        seen.add(key)
        variants.append(current)

        if current.endswith(".json"):
            stem = current[: -len(".json")]
            if stem:
                queue.append(stem)
        else:
            queue.append(f"{current}.json")

        lower_current = key
        for prefix in ("styles/", "prompts/styles/", "prompts/"):
            if lower_current.startswith(prefix):
                remainder = current[len(prefix) :]
                if remainder:
                    queue.append(remainder)

    return variants


def _iter_metadata_candidate_paths(raw: str) -> list[Path]:
    variants = _expand_metadata_hint_variants(raw)
    if not variants:
        return []

    roots: list[Path] = []
    seen_roots: set[str] = set()
    for root in [PROMPTS_DIR, *PROMPTS_SEARCH_PATHS]:
        if not root:
            continue
        base = Path(root).expanduser()
        root_key = str(base)
        if root_key in seen_roots:
            continue
        seen_roots.add(root_key)
        roots.append(base)

    candidates: list[Path] = []
    seen: set[str] = set()
    for base in roots:
        for variant in variants:
            candidate = (base / variant).expanduser()
            key = str(candidate)
            if key in seen:
                continue
            seen.add(key)
            candidates.append(candidate)
    return candidates


def _resolve_template_by_metadata_hint(raw: str) -> Dict[str, Any] | None:
    cleaned = raw.strip()
    if not cleaned:
        return None

    normalized_hint = _normalize_metadata_path(cleaned)
    if normalized_hint:
        template = _TEMPLATE_INDEX_BY_PATH.get(normalized_hint)
        if template is not None:
            return template
        cached_path = _METADATA_PATH_CACHE.get(normalized_hint)
        if cached_path is not None:
            template = _load_template_and_register(cached_path)
            if template is not None:
                _TEMPLATE_INDEX_BY_PATH.setdefault(normalized_hint, template)
                return template
            _METADATA_PATH_CACHE.pop(normalized_hint, None)

    direct_candidate = Path(cleaned)
    template = _load_template_and_register(direct_candidate)
    if template is not None:
        if normalized_hint:
            try:
                resolved_direct = direct_candidate.expanduser().resolve()
            except Exception:
                resolved_direct = direct_candidate.expanduser()
            _METADATA_PATH_CACHE[normalized_hint] = resolved_direct
            _TEMPLATE_INDEX_BY_PATH.setdefault(normalized_hint, template)
        return template

    for candidate in _iter_metadata_candidate_paths(cleaned):
        template = _load_template_and_register(candidate)
        if template is None:
            continue
        if normalized_hint:
            try:
                resolved_candidate = candidate.resolve()
            except Exception:
                resolved_candidate = candidate
            _METADATA_PATH_CACHE[normalized_hint] = resolved_candidate
            _TEMPLATE_INDEX_BY_PATH.setdefault(normalized_hint, template)
        return template

    return None


def _load_template_and_register(path: Path) -> Dict[str, Any] | None:
    expanded = path.expanduser()
    try:
        resolved = expanded.resolve()
    except Exception:
        resolved = expanded

    for candidate in (resolved, expanded):
        cached = _TEMPLATE_BY_REAL_PATH.get(candidate)
        if cached is not None:
            return cached

    try:
        template = load_template(expanded)
    except FileNotFoundError:
        return None
    except Exception:
        return None

    try:
        resolved = expanded.resolve()
    except Exception:
        resolved = expanded

    _TEMPLATE_BY_REAL_PATH[resolved] = template
    if resolved != expanded:
        _TEMPLATE_BY_REAL_PATH[expanded] = template

    _register_template_index(template, resolved)
    return template


def _prime_template_indexes() -> None:
    global _TEMPLATE_INDEX_SCANNED
    if _TEMPLATE_INDEX_SCANNED:
        return
    try:
        iterator = PROMPTS_DIR.rglob("*.json") if PROMPTS_DIR.exists() else []
    except Exception:
        iterator = []
    for path in iterator:
        template = _load_template_and_register(path)
        if template is None:
            continue
    _TEMPLATE_INDEX_SCANNED = True


def _resolve_template_from_hints(
    template_metadata: Dict[str, Any] | None, template_id: str | int | None
) -> Dict[str, Any] | None:
    ids: list[Any] = []
    hints: list[str] = []
    if template_id is not None:
        ids.append(template_id)
    if isinstance(template_metadata, dict):
        meta_id = template_metadata.get("template_id")
        if meta_id is not None:
            ids.append(meta_id)
        for key in ("path", "relative_path", "relpath", "template_path"):
            raw = template_metadata.get(key)
            if isinstance(raw, str) and raw.strip():
                hints.append(raw)
        history = template_metadata.get("path_history")
        if isinstance(history, list):
            for entry in history:
                if isinstance(entry, str) and entry.strip():
                    hints.append(entry)

    candidate = _lookup_template_from_index(ids, hints)
    if candidate is not None:
        return candidate

    for raw in hints:
        template = _resolve_template_by_metadata_hint(raw)
        if template is not None:
            return template

    if not _TEMPLATE_INDEX_SCANNED:
        _prime_template_indexes()
        candidate = _lookup_template_from_index(ids, hints)
        if candidate is not None:
            return candidate

    return None


def _get_template(
    provided: Dict[str, Any] | None,
    template_metadata: Dict[str, Any] | None = None,
    template_id: str | int | None = None,
) -> Dict[str, Any]:
    if provided is not None:
        return provided
    resolved = _resolve_template_from_hints(template_metadata, template_id)
    if resolved is not None:
        return resolved
    global _TEMPLATE_CACHE
    if _TEMPLATE_CACHE is None:
        _TEMPLATE_CACHE = load_template(_TEMPLATE_PATH)
        _register_template_index(_TEMPLATE_CACHE, _TEMPLATE_PATH)
    return _TEMPLATE_CACHE


def _coerce_bool(value: Any) -> Optional[bool]:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        lower = value.strip().lower()
        if lower in {"1", "true", "yes", "on"}:
            return True
        if lower in {"0", "false", "no", "off"}:
            return False
    return None


def _normalize_json_like(value: Any, field_name: str, *, _seen: set[int] | None = None) -> Any:
    if _seen is None:
        _seen = set()

    def _inner(current: Any) -> Any:
        if isinstance(current, dict):
            obj_id = id(current)
            if obj_id in _seen:
                raise InputValidationError(f"'{field_name}' contains a recursive reference")
            _seen.add(obj_id)
            try:
                return {
                    str(key): _inner(item_value) for key, item_value in current.items()
                }
            finally:
                _seen.remove(obj_id)
        if isinstance(current, list):
            obj_id = id(current)
            if obj_id in _seen:
                raise InputValidationError(f"'{field_name}' contains a recursive reference")
            _seen.add(obj_id)
            try:
                return [_inner(item) for item in current]
            finally:
                _seen.remove(obj_id)
        if isinstance(current, float):
            if not math.isfinite(current):
                raise InputValidationError(
                    f"'{field_name}' contains a non-finite float value"
                )
            return float(current)
        if isinstance(current, (str, int, bool)) or current is None:
            return current
        raise InputValidationError(
            f"'{field_name}' contains unsupported value of type "
            f"{type(current).__name__}"
        )

    return _inner(value)


def _validate_arguments(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        raise InputValidationError("arguments must be a mapping")

    goals: str | None
    if "goals" in payload:
        raw_goals = payload.get("goals")
        if raw_goals is None:
            goals = None
        else:
            if isinstance(raw_goals, str):
                goals = raw_goals.strip()
            else:
                goals = str(raw_goals).strip()
    else:
        goals = None

    trace_id_raw = payload.get("trace_id")
    trace_id: str | None
    if trace_id_raw is None:
        trace_id = None
    else:
        trace_id = str(trace_id_raw).strip() or None

    dry_run_raw = payload.get("dry_run")
    dry_run = False
    if dry_run_raw is not None:
        coerced = _coerce_bool(dry_run_raw)
        if coerced is None:
            raise InputValidationError("'dry_run' must be boolean")
        dry_run = coerced

    template_metadata_raw = payload.get("template_metadata")
    if template_metadata_raw is None:
        template_metadata: Dict[str, Any] | None = None
    elif isinstance(template_metadata_raw, dict):
        template_metadata = _normalize_json_like(template_metadata_raw, "template_metadata")
    else:
        raise InputValidationError("'template_metadata' must be an object")

    variables_raw = payload.get("variables")
    if variables_raw is None:
        variables: Dict[str, Any] = {}
    elif isinstance(variables_raw, dict):
        variables = _normalize_json_like(variables_raw, "variables")
    else:
        raise InputValidationError("'variables' must be an object")

    template_payload_raw: Dict[str, Any] | None = None
    if "template_payload" in payload:
        candidate = payload.get("template_payload")
        if candidate is None:
            template_payload_raw = None
        elif isinstance(candidate, dict):
            template_payload_raw = candidate
        else:
            raise InputValidationError("'template_payload' must be an object")
    elif "template" in payload:
        candidate = payload.get("template")
        if candidate is None:
            template_payload_raw = None
        elif isinstance(candidate, dict):
            template_payload_raw = candidate
        else:
            raise InputValidationError("'template' must be an object")

    template_payload: Dict[str, Any] | None
    if template_payload_raw is None:
        template_payload = None
    else:
        template_payload = _normalize_json_like(template_payload_raw, "template_payload")

    template_id: str | int | None = None
    template_id_raw = payload.get("template_id")
    if template_id_raw is not None:
        if isinstance(template_id_raw, int):
            template_id = template_id_raw
        elif isinstance(template_id_raw, str):
            template_id = template_id_raw.strip()
            if not template_id:
                raise InputValidationError("'template_id' must be a non-empty string")
        else:
            raise InputValidationError("'template_id' must be a string or integer")

    if template_id is None and isinstance(template_payload, dict):
        candidate_id = template_payload.get("id")
        if isinstance(candidate_id, int):
            template_id = candidate_id
        elif isinstance(candidate_id, str) and candidate_id.strip():
            template_id = candidate_id.strip()

    return {
        "goals": goals,
        "trace_id": trace_id,
        "dry_run": dry_run,
        "template": template_payload,
        "template_metadata": template_metadata,
        "variables": variables,
        "template_id": template_id,
    }


def _render_prompt(
    goals: str | None,
    template_payload: Dict[str, Any] | None,
    variables: Dict[str, Any],
    template_metadata: Dict[str, Any] | None = None,
    template_id: str | int | None = None,
    *,
    resolved_template: Dict[str, Any] | None = None,
) -> str:
    source_template = (
        resolved_template
        if resolved_template is not None
        else _get_template(template_payload, template_metadata, template_id)
    )
    template = json.loads(json.dumps(source_template))
    context = json.loads(json.dumps(variables)) if variables else {}
    if goals is None:
        existing = context.get("goals")
        if isinstance(existing, str):
            effective_goals = existing
        elif existing is not None:
            effective_goals = str(existing)
        else:
            effective_goals = _GOALS_FALLBACK_TEXT
        context["goals"] = effective_goals
    else:
        context["goals"] = goals
    with suppress_mcp_project_execution():
        rendered, _ = _render_template(
            template,
            context,
            return_vars=True,
            skip_project_execution=True,
        )
    return rendered


def _request_payload(
    rendered_prompt: str,
    trace_id: str | None,
    dry_run: bool,
    template_payload: Dict[str, Any] | None,
    template_metadata: Dict[str, Any] | None,
    template_id: str | int | None,
    *,
    resolved_template: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    metadata: Dict[str, Any] = {}

    template_obj = resolved_template if resolved_template is not None else template_payload
    if isinstance(template_obj, dict):
        tmpl_meta = template_obj.get("metadata")
        if isinstance(tmpl_meta, dict):
            metadata.update(tmpl_meta)

    if template_metadata:
        metadata.update(template_metadata)

    if trace_id:
        metadata["trace_id"] = trace_id

    effective_template_id = template_id
    if effective_template_id is None and isinstance(template_obj, dict):
        derived_id = template_obj.get("id")
        if isinstance(derived_id, (int, str)) and str(derived_id).strip():
            effective_template_id = derived_id
    if effective_template_id is not None and "template_id" not in metadata:
        metadata["template_id"] = effective_template_id

    payload: Dict[str, Any] = {
        "model": "auto",
        "messages": [
            {
                "role": "system",
                "content": "You are Prompt Automation's project architect and assessor.",
            },
            {"role": "user", "content": rendered_prompt},
        ],
        "temperature": 0.1,
        "max_tokens": _MAX_TOKENS,
    }
    payload["metadata"] = metadata
    if dry_run:
        payload["dry_run"] = True
    return payload


def _extract_completion(payload: Dict[str, Any]) -> str:
    choices = payload.get("choices")
    if isinstance(choices, list) and choices:
        first = choices[0]
        if isinstance(first, dict):
            message = first.get("message")
            if isinstance(message, dict):
                content = message.get("content")
                if isinstance(content, str) and content.strip():
                    return content.strip()
            content = first.get("text")
            if isinstance(content, str) and content.strip():
                return content.strip()
    for key in ("output", "plan", "content"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    raise RuntimeError("completion payload did not contain any text output")


def _post_json(url: str, data: Dict[str, Any], trace_id: str | None) -> Dict[str, Any]:
    body = json.dumps(data, ensure_ascii=False).encode("utf-8")
    headers = dict(_DEFAULT_HEADERS)
    if trace_id:
        headers["X-Trace-Id"] = trace_id
    req = urllib_request.Request(url, data=body, headers=headers, method="POST")
    with urllib_request.urlopen(req, timeout=30) as resp:
        text = resp.read().decode("utf-8")
        return json.loads(text)


def _check_cancelled(should_cancel: Callable[[], bool] | None) -> bool:
    if should_cancel is None:
        return False
    try:
        return bool(should_cancel())
    except Exception:
        return False


def _sleep_with_cancellation(delay: float, should_cancel: Callable[[], bool] | None) -> None:
    if delay <= 0:
        return
    deadline = time.monotonic() + delay
    while True:
        if _check_cancelled(should_cancel):
            raise ProjectExecutionCancelled("cancelled")
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        time.sleep(min(remaining, 0.1))


def _attempt_endpoints(
    data: Dict[str, Any],
    trace_id: str | None,
    *,
    should_cancel: Callable[[], bool] | None = None,
    policy: RetryPolicy | None = None,
) -> str:
    endpoints = tuple(url for url in (_PRIMARY_ENDPOINT, _FALLBACK_ENDPOINT) if url)
    if not endpoints:
        raise RuntimeError("no endpoints configured")

    errors: list[str] = []
    policy = policy or DEFAULT_RETRY_POLICY
    attempts_per_endpoint: Dict[str, int] = {url: 0 for url in endpoints}
    total_attempts = 0
    disabled: set[str] = set()
    jitter_fn = random.uniform if policy.jitter > 0 else None
    configured_max_attempts = policy.max_attempts
    max_attempts = (
        None
        if configured_max_attempts is None
        else max(0, int(configured_max_attempts))
    )
    budget_start = time.monotonic()
    configured_max_duration = policy.max_duration
    deadline: float | None
    if configured_max_duration is None:
        deadline = None
    elif configured_max_duration > 0:
        deadline = budget_start + configured_max_duration
    else:
        deadline = budget_start
    budget_exhausted = False

    while True:
        if max_attempts is not None and total_attempts >= max_attempts:
            budget_exhausted = True
            break
        if deadline is not None and time.monotonic() >= deadline:
            budget_exhausted = True
            break
        progressed = False
        for url in endpoints:
            if url in disabled:
                continue
            if max_attempts is not None and total_attempts >= max_attempts:
                budget_exhausted = True
                break
            if deadline is not None and time.monotonic() >= deadline:
                budget_exhausted = True
                break
            progressed = True
            attempt = attempts_per_endpoint[url]
            attempt_index = attempt + 1
            if attempt > 0:
                delay = policy.delay_for_attempt(attempt, jitter_fn=jitter_fn)
                if deadline is not None and delay > 0:
                    remaining_budget = deadline - time.monotonic()
                    if remaining_budget <= 0:
                        budget_exhausted = True
                        break
                    delay = min(delay, max(0.0, remaining_budget))
                _sleep_with_cancellation(delay, should_cancel)
            if budget_exhausted:
                break
            if _check_cancelled(should_cancel):
                raise ProjectExecutionCancelled("cancelled")

            total_attempts += 1
            call_start = time.perf_counter()
            try:
                response = _post_json(url, data, trace_id)
            except (urllib_error.HTTPError, urllib_error.URLError) as exc:
                duration_ms = (time.perf_counter() - call_start) * 1000.0
                attempt_count = total_attempts
                message = f"{getattr(exc, 'code', 'error')}: {getattr(exc, 'reason', exc)}"
                errors.append(f"{url} attempt {attempt_index}: {message}")
                log_extra = {
                    "endpoint": url,
                    "attempt_index": attempt_index,
                    "attempt_count": attempt_count,
                    "duration_ms": duration_ms,
                    "error": str(exc),
                }
                should_disable = (
                    isinstance(exc, urllib_error.HTTPError)
                    and exc.code in {400, 401, 403}
                )
                next_delay_ms: float | None = None
                if not should_disable:
                    next_delay = policy.delay_for_attempt(attempt + 1)
                    if next_delay > 0:
                        next_delay_ms = next_delay * 1000.0
                        log_extra["next_delay_ms"] = next_delay_ms
                try:
                    _log.warning("mcp.project.call_failed", extra=log_extra)
                except Exception:
                    pass
                if should_disable:
                    disabled.add(url)
                attempts_per_endpoint[url] = attempt + 1
                if observability_state.metrics_enabled:
                    record_project_call_metric(
                        "mcp.project.call_failed",
                        duration_ms=duration_ms,
                        attempt_index=attempt_index,
                        attempt_count=attempt_count,
                        next_delay_ms=next_delay_ms,
                    )
                if _check_cancelled(should_cancel):
                    raise ProjectExecutionCancelled("cancelled")
                if max_attempts is not None and total_attempts >= max_attempts:
                    budget_exhausted = True
                    break
                if deadline is not None and time.monotonic() >= deadline:
                    budget_exhausted = True
                    break
            except Exception as exc:  # pragma: no cover - defensive guard
                duration_ms = (time.perf_counter() - call_start) * 1000.0
                errors.append(f"{url} attempt {attempt_index}: {exc}")
                log_extra = {
                    "endpoint": url,
                    "attempt_index": attempt_index,
                    "attempt_count": total_attempts,
                    "duration_ms": duration_ms,
                    "error": str(exc),
                }
                try:
                    _log.warning("mcp.project.call_failed", extra=log_extra)
                except Exception:
                    pass
                attempts_per_endpoint[url] = attempt + 1
                if observability_state.metrics_enabled:
                    record_project_call_metric(
                        "mcp.project.call_failed",
                        duration_ms=duration_ms,
                        attempt_index=attempt_index,
                        attempt_count=total_attempts,
                    )
                if _check_cancelled(should_cancel):
                    raise ProjectExecutionCancelled("cancelled")
                if max_attempts is not None and total_attempts >= max_attempts:
                    budget_exhausted = True
                    break
                if deadline is not None and time.monotonic() >= deadline:
                    budget_exhausted = True
                    break
            else:
                duration_ms = (time.perf_counter() - call_start) * 1000.0
                attempt_count = total_attempts
                try:
                    _log.info(
                        "mcp.project.call_succeeded",
                        extra={
                            "endpoint": url,
                            "attempt_index": attempt_index,
                            "attempt_count": attempt_count,
                            "duration_ms": duration_ms,
                        },
                    )
                except Exception:
                    pass
                if observability_state.metrics_enabled:
                    record_project_call_metric(
                        "mcp.project.call_succeeded",
                        duration_ms=duration_ms,
                        attempt_index=attempt_index,
                        attempt_count=attempt_count,
                    )
                return _extract_completion(response)
        if budget_exhausted:
            break
        if not progressed:
            break

    if budget_exhausted:
        elapsed = time.monotonic() - budget_start
        attempt_label = "attempt" if total_attempts == 1 else "attempts"
        message = f"retry budget exhausted after {total_attempts} {attempt_label}"
        details: list[str] = []
        if configured_max_attempts is not None:
            details.append(f"max_attempts={configured_max_attempts}")
        if configured_max_duration is not None:
            details.append(f"max_duration={configured_max_duration:.3f}s")
            message += f" over {elapsed:.2f}s"
        if details:
            message += f" ({', '.join(details)})"
        if errors:
            message += f"; {'; '.join(errors)}"
        raise RuntimeError(message)

    raise RuntimeError("; ".join(errors) if errors else "model invocation failed")


def execute_project(
    arguments: Dict[str, Any],
    *,
    should_cancel: Callable[[], bool] | None = None,
    retry_policy: RetryPolicy | None = None,
) -> str:
    """Execute the project planning workflow and return the completion text."""

    validated = _validate_arguments(arguments)
    resolved_template = _get_template(
        validated["template"],
        validated["template_metadata"],
        validated["template_id"],
    )
    rendered_prompt = _render_prompt(
        validated["goals"],
        validated["template"],
        validated["variables"],
        template_metadata=validated["template_metadata"],
        template_id=validated["template_id"],
        resolved_template=resolved_template,
    )
    payload = _request_payload(
        rendered_prompt,
        validated["trace_id"],
        validated["dry_run"],
        validated["template"],
        template_metadata=validated["template_metadata"],
        template_id=validated["template_id"],
        resolved_template=resolved_template,
    )
    plan = _attempt_endpoints(
        payload,
        validated["trace_id"],
        should_cancel=should_cancel,
        policy=retry_policy,
    )
    return plan


@dataclass
class JsonRpcResponse:
    id: Any
    result: Any | None = None
    error: Dict[str, Any] | None = None

    def as_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"jsonrpc": "2.0", "id": self.id}
        if self.error is not None:
            payload["error"] = self.error
        else:
            payload["result"] = self.result
        return payload


class ProjectServer:
    """Minimal JSON-RPC MCP server exposing ``pa.project.run``."""

    def __init__(self, reader: TextIO, writer: TextIO) -> None:
        self._reader = reader
        self._writer = writer

    def _write(self, payload: Dict[str, Any]) -> None:
        self._writer.write(json.dumps(payload, ensure_ascii=False) + "\n")
        self._writer.flush()

    def _respond(self, response: JsonRpcResponse) -> None:
        self._write(response.as_dict())

    def _handle_initialize(self, request_id: Any) -> None:
        result = {
            "name": "Prompt Automation MCP",
            "version": "1.0",
            "capabilities": [{"name": "tools", "version": "1"}],
            "tools": [
                {
                    "name": TOOL_NAME,
                    "description": "Generate a scoped project plan and assessment",
                    "input_schema": _INPUT_SCHEMA,
                }
            ],
        }
        if features.is_mcp_notes_enabled():
            result["tools"].extend(note_tools.iter_tool_descriptors())
        self._respond(JsonRpcResponse(id=request_id, result=result))

    def _handle_call_tool(self, request_id: Any, params: Dict[str, Any]) -> None:
        try:
            name = params.get("name")
            if name != TOOL_NAME:
                if not features.is_mcp_notes_enabled():
                    raise InputValidationError(f"unknown tool '{name}'")
                if name not in note_tools.TOOL_REGISTRY:
                    raise InputValidationError(f"unknown tool '{name}'")
                arguments = params.get("arguments") or {}
                handler = note_tools.TOOL_REGISTRY[name][0]
                result = handler(arguments)
            else:
                arguments = params.get("arguments") or {}
                plan = execute_project(arguments)
        except InputValidationError as exc:
            self._respond(
                JsonRpcResponse(
                    id=request_id,
                    error={"code": -32602, "message": str(exc)},
                )
            )
        except (note_tools.NoteToolError, vault_paths.VaultSecurityError, vault_paths.VaultResolutionError) as exc:
            self._respond(
                JsonRpcResponse(
                    id=request_id,
                    error={"code": -32602, "message": str(exc)},
                )
            )
        except Exception as exc:
            self._respond(
                JsonRpcResponse(
                    id=request_id,
                    error={"code": -32001, "message": str(exc)},
                )
            )
        else:
            if name == TOOL_NAME:
                self._respond(JsonRpcResponse(id=request_id, result={"plan": plan}))
            else:
                self._respond(JsonRpcResponse(id=request_id, result=result))

    def serve(self) -> None:
        for line in self._reader:
            if not line:
                break
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(payload, dict):
                continue
            method = payload.get("method")
            request_id = payload.get("id")
            if method == "initialize":
                self._handle_initialize(request_id)
            elif method == "callTool":
                params = payload.get("params")
                if not isinstance(params, dict):
                    params = {}
                self._handle_call_tool(request_id, params)
            else:
                self._respond(
                    JsonRpcResponse(
                        id=request_id,
                        error={"code": -32601, "message": f"unknown method '{method}'"},
                    )
                )


def run(reader: TextIO | None = None, writer: TextIO | None = None) -> None:
    """Entry point invoked by ``python -m prompt_automation.mcp.server``."""

    server = ProjectServer(reader or sys.stdin, writer or sys.stdout)
    server.serve()


if __name__ == "__main__":  # pragma: no cover - manual execution path
    run()


__all__ = [
    "execute_project",
    "run",
    "ProjectServer",
    "InputValidationError",
    "ProjectExecutionCancelled",
    "TOOL_NAME",
    "DEFAULT_RETRY_POLICY",
    "note_tools",
    "note_schemas",
    "vault_paths",
]

