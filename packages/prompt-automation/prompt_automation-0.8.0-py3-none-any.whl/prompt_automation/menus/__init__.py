"""Menu system with fzf and prompt_toolkit fallback."""
from __future__ import annotations

import re
from contextlib import contextmanager
from contextvars import ContextVar
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, TYPE_CHECKING

from ..config import PROMPTS_DIR, PROMPTS_SEARCH_PATHS
from ..services.exclusions import parse_exclusions
from ..renderer import (
    fill_placeholders,
    load_template,
    validate_template,
    read_file_safe,
    is_shareable,
    ensure_feature_flags,
)

if TYPE_CHECKING:
    from ..types import Template
from ..variables import (
    get_variables,
    ensure_template_global_snapshot,
    apply_template_global_overrides,
    get_global_reference_file,
)
from ..variables.hierarchy import GlobalVariableResolver

from .listing import list_styles, list_prompts
from .creation import (
    save_template,
    delete_template,
    add_style,
    delete_style,
    ensure_unique_ids,
    create_new_template,
)
from .picker import pick_style, pick_prompt

from .render_pipeline import (
    apply_defaults,
    apply_file_placeholders,
    apply_formatting,
    apply_global_placeholders,
    apply_markdown_rendering,
    apply_post_render,
)
from .. import parser_singlefield
from ..reminders import (
    extract_template_reminders,
    partition_placeholder_reminders,
)
from ..features import (
    is_mcp_server_enabled as _is_mcp_server_enabled,
    is_reminders_enabled as _reminders_enabled,
    is_reminders_timing_enabled as _rem_timing,
)
from ..errorlog import get_logger

_log = get_logger(__name__)


_MCP_PROJECT_EXECUTION_SUPPRESSED: ContextVar[bool] = ContextVar(
    "prompt_automation.menus._mcp_project_execution_suppressed", default=False
)

_MCP_PROJECT_CANCELLATION_CHECK: ContextVar[
    Callable[[], bool] | None
] = ContextVar(
    "prompt_automation.menus._mcp_project_cancellation_check",
    default=None,
)


@contextmanager
def suppress_mcp_project_execution() -> Iterator[None]:
    token = _MCP_PROJECT_EXECUTION_SUPPRESSED.set(True)
    try:
        yield
    finally:
        _MCP_PROJECT_EXECUTION_SUPPRESSED.reset(token)


@contextmanager
def provide_mcp_project_cancellation(
    check: Callable[[], bool] | None,
) -> Iterator[None]:
    token = _MCP_PROJECT_CANCELLATION_CHECK.set(check)
    try:
        yield
    finally:
        _MCP_PROJECT_CANCELLATION_CHECK.reset(token)


def _coerce_feature_flag(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "yes", "1", "on", "y", "enabled", "enable"}:
            return True
        if lowered in {"false", "no", "0", "off", "n", "disabled", "disable"}:
            return False
    return None


def _interpret_mcp_toggle(value: Any) -> bool | None:
    """Resolve whether a metadata value opts into or out of MCP execution."""

    direct = _coerce_feature_flag(value)
    if direct is not None:
        return direct

    if isinstance(value, dict):
        candidates: list[Any] = []
        for positive_key in ("enabled", "enable", "allow", "use"):
            if positive_key in value:
                candidates.append(value.get(positive_key))
        for negative_key in ("disabled", "disable", "opt_out", "opt-out", "deny"):
            if negative_key in value:
                decision = _coerce_feature_flag(value.get(negative_key))
                if decision is not None:
                    return not decision
        mode = value.get("mode")
        if isinstance(mode, str):
            lowered = mode.strip().lower()
            if lowered in {"enable", "enabled", "on"}:
                return True
            if lowered in {"disable", "disabled", "off"}:
                return False
        for candidate in candidates:
            decision = _coerce_feature_flag(candidate)
            if decision is not None:
                return decision
    return None


def _iter_mcp_metadata_candidates(meta: Dict[str, Any] | None) -> Iterator[Any]:
    if not isinstance(meta, dict):
        return iter(())

    def _generator() -> Iterator[Any]:
        for key in ("mcp_server", "mcp-server", "mcpServer"):
            if key in meta:
                yield meta.get(key)

        nested = meta.get("mcp")
        if isinstance(nested, dict):
            yield nested.get("server")

        for container_key in ("features", "feature_flags"):
            container = meta.get(container_key)
            if isinstance(container, dict):
                for key in ("mcp_server", "mcpserver", "mcp_server_enabled", "mcp_server_enable"):
                    if key in container:
                        yield container.get(key)

    return _generator()


def _supports_mcp_server(tmpl: "Template") -> bool:
    recognized_keys = (
        "mcp_server",
        "mcpserver",
        "mcp_server_enabled",
        "mcp_server_enable",
    )

    try:
        features = ensure_feature_flags(tmpl)
    except Exception:
        features = {}

    if isinstance(features, dict):
        for key in recognized_keys:
            decision = _interpret_mcp_toggle(features.get(key))
            if decision is True:
                return True
            if decision is False:
                return False

    meta = tmpl.get("metadata")
    if isinstance(meta, dict):
        for candidate in _iter_mcp_metadata_candidates(meta):
            decision = _interpret_mcp_toggle(candidate)
            if decision is True:
                return True
            if decision is False:
                return False

    # No explicit opt-out detected; templates are MCP-capable by default.
    return True

_UNRESOLVED_TOKEN_RE = re.compile(r"\{\{[^{}]+\}\}")


# --- Rendering -------------------------------------------------------------

def render_template(
    tmpl: "Template",
    values: Dict[str, Any] | None = None,
    *,
    return_vars: bool = False,
    skip_project_execution: bool = False,
) -> str | tuple[str, Dict[str, Any]]:
    """Render ``tmpl`` using provided ``values`` for placeholders."""

    placeholders = tmpl.get("placeholders", [])
    template_id = tmpl.get("id")

    meta = tmpl.get("metadata") if isinstance(tmpl.get("metadata"), dict) else {}
    exclude_globals: set[str] = parse_exclusions(meta.get("exclude_globals"))

    raw_globals = tmpl.get("global_placeholders", {})
    base_globals = dict(raw_globals) if isinstance(raw_globals, dict) else {}
    try:
        resolver = GlobalVariableResolver()
        globals_map = resolver.resolve(base_globals)
    except Exception:
        globals_map = base_globals
    tmpl["global_placeholders"] = globals_map
    if exclude_globals:
        for k in list(globals_map.keys()):
            if k in exclude_globals:
                globals_map.pop(k, None)
    if isinstance(template_id, int):
        ensure_template_global_snapshot(template_id, globals_map)
        snap_merged = apply_template_global_overrides(template_id, {})
        for k, v in snap_merged.items():
            if k in exclude_globals:
                continue
            if k == "reminders" and k not in globals_map:
                continue
            globals_map.setdefault(k, v)
        tmpl["global_placeholders"] = globals_map
    if values is None:
        # Compute reminders (non-invasive): attach a private key for CLI flow,
        # and pass template/global reminders via globals_map under a reserved key.
        if _reminders_enabled():
            try:
                import time
                t0 = time.perf_counter() if _rem_timing() else None
                tmpl_rem = extract_template_reminders(tmpl)
                ph_map = partition_placeholder_reminders(placeholders, tmpl_rem)
                # Attach sanitized per-placeholder reminders for CLI presentation
                for ph in placeholders:
                    if isinstance(ph, dict) and ph.get("name") in ph_map:
                        ph.setdefault("_reminders_inline", ph_map[ph["name"]])
                # Inject template reminders into globals map for CLI printing
                if tmpl_rem:
                    globals_map = dict(globals_map)
                    globals_map["__template_reminders"] = tmpl_rem
                # Observability: log counts without content
                try:
                    _log.info(
                        "reminders.summary",
                        extra={
                            "template": len(tmpl_rem),
                            "placeholder": sum(len(v) for v in ph_map.values()),
                        },
                    )
                    if t0 is not None:
                        dt_ms = int((time.perf_counter() - t0) * 1000)
                        _log.info("reminders.timing_ms", extra={"duration_ms": dt_ms})
                except Exception:
                    pass
            except Exception:
                pass
        raw_vars = get_variables(
            placeholders, template_id=template_id, globals_map=globals_map
        )
    else:
        raw_vars = dict(values)

    # If this template includes a single-field capture and a logic block, parse it
    try:
        if (
            isinstance(placeholders, list)
            and len(placeholders) == 1
            and placeholders[0].get("name") == "capture"
            and isinstance(tmpl.get("logic"), dict)
        ):
            capture_val = raw_vars.get("capture") or ""
            tz = tmpl.get("logic", {}).get("timezone")
            parsed = parser_singlefield.parse_capture(capture_val, timezone=tz)
            # Update raw_vars with parsed outputs so downstream pipeline sees them
            raw_vars.update(parsed)
    except Exception:
        pass

    vars = dict(raw_vars)

    context_path = raw_vars.get("context_append_file") or raw_vars.get("context_file")
    if not context_path:
        candidate = raw_vars.get("context")
        if isinstance(candidate, str) and Path(candidate).expanduser().is_file():
            context_path = candidate
    if context_path:
        vars["context"] = read_file_safe(str(context_path))
        raw_vars["context_append_file"] = str(context_path)

    apply_file_placeholders(tmpl, raw_vars, vars, placeholders)
    apply_defaults(raw_vars, vars, placeholders)
    apply_global_placeholders(tmpl, vars, exclude_globals)
    apply_formatting(vars, placeholders)
    # Convert markdown placeholders (e.g., reference_file) into sanitized HTML and wrappers
    try:
        apply_markdown_rendering(tmpl, vars, placeholders)
    except Exception:
        pass

    rendered = fill_placeholders(tmpl["template"], vars)
    rendered = apply_post_render(rendered, tmpl, placeholders, vars, exclude_globals)

    suppress_execution = skip_project_execution or _MCP_PROJECT_EXECUTION_SUPPRESSED.get(False)

    if (
        _is_mcp_server_enabled()
        and _supports_mcp_server(tmpl)
        and not suppress_execution
    ):
        goals_value = vars.get("goals")
        goals_clean = str(goals_value or "").strip()
        include_goals_argument = goals_value is not None
        try:
            from ..mcp.server import (
                ProjectExecutionCancelled,
                execute_project,
            )

            arguments: Dict[str, Any] = {}
            if include_goals_argument:
                arguments["goals"] = goals_clean
            if "trace_id" in vars:
                arguments["trace_id"] = vars["trace_id"]
            if "dry_run" in vars:
                arguments["dry_run"] = vars["dry_run"]

            template_payload: Dict[str, Any] | None
            try:
                template_payload = deepcopy(tmpl)
            except Exception:
                template_payload = dict(tmpl) if isinstance(tmpl, dict) else None

            if isinstance(template_payload, dict):
                arguments["template"] = template_payload

            template_identifier = tmpl.get("id") if isinstance(tmpl, dict) else None
            if isinstance(template_identifier, (str, int)):
                arguments["template_id"] = template_identifier

            metadata_obj = None
            if isinstance(template_payload, dict):
                metadata_obj = template_payload.get("metadata")
            if not isinstance(metadata_obj, dict) and isinstance(tmpl, dict):
                candidate_meta = tmpl.get("metadata")
                if isinstance(candidate_meta, dict):
                    metadata_obj = candidate_meta
            if isinstance(metadata_obj, dict):
                try:
                    arguments["template_metadata"] = deepcopy(metadata_obj)
                except Exception:
                    arguments["template_metadata"] = dict(metadata_obj)

            variables_payload = {
                key: value
                for key, value in vars.items()
                if key != "__mcp_plan__"
            }
            if variables_payload:
                try:
                    arguments["variables"] = deepcopy(variables_payload)
                except Exception:
                    arguments["variables"] = dict(variables_payload)
            cancellation_check = _MCP_PROJECT_CANCELLATION_CHECK.get(None)
            plan = execute_project(
                arguments,
                should_cancel=cancellation_check,
            )
            vars["__mcp_plan__"] = plan
            rendered = plan
        except ProjectExecutionCancelled:
            try:
                _log.info(
                    "mcp.render_template.cancelled",
                    extra={"template": tmpl.get("id")},
                )
            except Exception:
                pass
            raise
        except Exception as exc:
            try:
                _log.warning(
                    "mcp.render_template.fallback",
                    extra={"template": tmpl.get("id"), "error": str(exc)},
                )
            except Exception:
                pass

    # Fallback: if logic-driven tokens still present, attempt late parse & substitution
    if (
        isinstance(tmpl.get("logic"), dict)
        and isinstance(placeholders, list)
        and len(placeholders) == 1
        and placeholders[0].get("name") == "capture"
    and ("{{title}}" in rendered or "{{priority}}" in rendered or "{{due_display}}" in rendered or "{{acceptance_final}}" in rendered)
    ):
        try:
            capture_val = raw_vars.get("capture") or ""
            tz = tmpl.get("logic", {}).get("timezone")
            parsed_late = parser_singlefield.parse_capture(capture_val, timezone=tz)
            repl_map = {
                "{{title}}": parsed_late.get("title", ""),
                "{{priority}}": parsed_late.get("priority", ""),
                "{{due_display}}": parsed_late.get("due_display", ""),
                "{{acceptance_final}}": parsed_late.get("acceptance_final", ""),
            }
            for token, val in repl_map.items():
                rendered = rendered.replace(token, val)
        except Exception:
            pass

    rendered = _UNRESOLVED_TOKEN_RE.sub("", rendered)

    if return_vars:
        return rendered, vars
    return rendered


__all__ = [
    "list_styles",
    "list_prompts",
    "pick_style",
    "pick_prompt",
    "render_template",
    "suppress_mcp_project_execution",
    "provide_mcp_project_cancellation",
    "save_template",
    "delete_template",
    "add_style",
    "delete_style",
    "ensure_unique_ids",
    "create_new_template",
    "PROMPTS_DIR",
    "PROMPTS_SEARCH_PATHS",
    "load_template",
]
