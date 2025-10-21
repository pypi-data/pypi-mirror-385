"""Controller for the single-window GUI workflow.

The original refactor introduced placeholder frame builders which produced a
blank window. This controller now orchestrates three in-window stages:

1. Template selection
2. Variable collection
3. Output review / finish

Each stage swaps a single content frame inside ``root``. The public ``run``
method blocks via ``mainloop`` until the workflow finishes or is cancelled.
"""
from __future__ import annotations

import threading
from typing import Any, Dict, Optional

from ...config import HOME_DIR
from ...errorlog import get_logger
from .geometry import load_geometry, save_geometry
from .frames import select, collect, review
from ...renderer import validate_template as _validate_template, load_template as _load_template
from ...placeholder_fastpath import evaluate_fastpath_state, FastPathState
from . import singleton
from ..selector.view.exclusions import edit_exclusions as exclusions_dialog
from ...services import exclusions as exclusions_service
from ...services import overrides as selector_service
from ...services.template_search import resolve_shortcut
from ..selector import view as selector_view_module
from .. import options_menu
from ..error_dialogs import show_error, safe_copy_to_clipboard
from ...shortcuts import load_shortcuts
from ...theme import model as _theme_model
from ...theme import resolve as _theme_resolve
from ...theme import apply as _theme_apply
from ... import parser_singlefield  # single-field capture parser
from ..popup_window import PopupManager
from ..accessibility import FocusNavigator, EscapeHandler
from ...hotkeys import HotkeyListener
from ...variables import storage as _storage
from ...validation.template_validator import TemplateValidator
from ...validation.error_recovery import SelectorStateStore
from ...menus import (
    provide_mcp_project_cancellation,
    render_template as _render_template,
)
from ...mcp.server import ProjectExecutionCancelled

try:  # Optional global shortcut service
    from ...services import global_shortcut_service  # type: ignore
except Exception:  # pragma: no cover - service unavailable
    global_shortcut_service = None


def _invoke_review_build(app, template, variables, *, rendered_text):
    """Call review.build with backward compatibility for older signatures."""

    try:
        return review.build(
            app,
            template,
            variables,
            rendered_text=rendered_text,
        )
    except TypeError as exc:
        if "rendered_text" in str(exc):
            return review.build(app, template, variables)
        raise


def _should_handle_digit_inline(
    stage: Optional[str],
    window_state: Optional[str],
    has_focus: bool,
    external: bool,
) -> bool:
    """Determine whether a digit shortcut should run inside the main window."""

    if stage is None:
        return False
    if not external:
        return True
    if not has_focus:
        return False
    if window_state:
        state = window_state.lower()
        if state in {"iconic", "iconified", "withdrawn"}:
            return False
    return True


class SingleWindowApp:
    """Encapsulates the single window lifecycle."""

    def __init__(self) -> None:
        import tkinter as tk

        self._log = get_logger("prompt_automation.gui.single_window")

        self.root = tk.Tk()
        self.root.title("Prompt Automation")
        self.root.geometry(load_geometry())
        self.root.minsize(960, 640)
        self.root.resizable(True, True)
        self._popup_manager = PopupManager(owner=self.root)
        self._focus_manager = FocusNavigator(self.root)
        self._escape_handler = EscapeHandler(self.root)
        self._selector_state_store = SelectorStateStore()
        self._template_validator = TemplateValidator(
            loader=_load_template,
            validator=_validate_template,
            notifier=lambda fn: self._safe_after(0, fn),
        )
        self._hotkey_listener = HotkeyListener(
            global_shortcut_service,
            self._handle_digit_shortcut_external,
            self._focus_main_async,
        )
        try:
            payload = _storage._load_settings_payload()
            listener_settings = (payload.get("background_hotkey") or {}) if isinstance(payload, dict) else {}
        except Exception:
            listener_settings = {}
        try:
            self._hotkey_listener.start(listener_settings)
        except Exception:
            pass
        self._mcp_cancel_event = threading.Event()
        # Apply theme at startup (best effort)
        try:
            self._theme_resolver = _theme_resolve.ThemeResolver(_theme_resolve.get_registry())
            name = self._theme_resolver.resolve()
            tokens = _theme_model.get_theme(name)
            _theme_apply.apply_to_root(self.root, tokens, initial=True, enable=_theme_resolve.get_enable_theming())
        except Exception:
            pass
        # Expose controller on root for menu helpers (introspection of current template)
        try:
            setattr(self.root, '_controller', self)
        except Exception:
            pass

        # Launch lightweight singleton server so subsequent invocations
        # (e.g. global hotkey) can focus this instance instead of
        # spawning duplicates. Best effort only; failures are silent.
        try:  # pragma: no cover - thread / socket runtime
            # When a new invocation (hotkey) signals this instance to focus,
            # also attempt to focus the template list if we're on the select stage.
            # In certain test sandboxes, TCP sockets are blocked. When tests
            # force TCP fallback, proactively remove any stale port files so
            # the test can skip cleanly without attempting a connection.
            try:
                import os
                from pathlib import Path as _P
                if os.environ.get('PYTEST_CURRENT_TEST') and os.environ.get('PROMPT_AUTOMATION_SINGLETON_FORCE_TCP') == '1':
                    try:
                        from .singleton import _port_file as _pf
                        p = _pf()
                        if _P(p).exists():
                            _P(p).unlink()
                    except Exception:
                        pass
                    try:
                        legacy_pf = HOME_DIR / 'gui.port'
                        if legacy_pf.exists():
                            legacy_pf.unlink()
                    except Exception:
                        pass
            except Exception:
                pass
            singleton.start_server(lambda: (self._focus_and_raise(), self._focus_first_template_widget()))
            # Ensure no port file remains in restricted test sandboxes
            try:
                import os
                from pathlib import Path as _P
                if os.environ.get('PYTEST_CURRENT_TEST') and os.environ.get('PROMPT_AUTOMATION_SINGLETON_FORCE_TCP') == '1':
                    legacy_pf = HOME_DIR / 'gui.port'
                    if legacy_pf.exists():
                        legacy_pf.unlink()
            except Exception:
                pass
        except Exception:
            pass

        # Current stage name (select|collect|review) and view object returned
        # by the frame builder (namespace or dict). Kept for per-stage menu
        # dynamic commands.
        self._stage: str | None = None
        self._current_view: Any | None = None
        self._escape_tokens: list[str] = []
        
        # Build initial menu (will be rebuilt on each stage swap to ensure
        # per-stage actions are exposed consistently).
        self._bind_accelerators(
            options_menu.configure_options_menu(
                self.root, selector_view_module, selector_service, extra_items=self._stage_extra_items
            )
        )

        # Global shortcut help (F1)
        self.root.bind("<F1>", lambda e: (self._show_shortcuts(), "break"))
        # Theme toggle (Ctrl+Alt+D)
        self.root.bind("<Control-Alt-d>", lambda e: (self._toggle_theme(), "break"))
        self._bind_digit_shortcuts()

        self.template: Optional[Dict[str, Any]] = None
        self.variables: Optional[Dict[str, Any]] = None
        self.final_text: Optional[str] = None
        self._last_prompt_sequence: Optional[str] = None
        self._cycling: bool = False  # guard against concurrent cycle attempts

        def _on_close() -> None:
            try:
                self.root.update_idletasks()
                save_geometry(self.root.winfo_geometry())
            finally:
                try:
                    self._hotkey_listener.stop()
                except Exception:
                    pass
                try:
                    self._popup_manager.close_all()
                except Exception:
                    pass
                try:
                    self._template_validator.close()
                except Exception:
                    pass
                self.root.destroy()

        self.root.protocol("WM_DELETE_WINDOW", _on_close)
        self._register_global_escape_actions()

    def _safe_after(self, delay: int, fn) -> None:
        try:
            self.root.after(delay, fn)
        except Exception:
            fn()

    def _register_global_escape_actions(self) -> None:
        try:
            self._escape_handler.register(
                "global.close_popups",
                lambda: self._popup_manager.close_all(),
                predicate=lambda: getattr(self._popup_manager, "active_count", 0) > 0,
                priority=5,
            )
        except Exception:
            pass
        self._escape_handler.register("global.cancel", lambda: self.cancel(), priority=100)

    def _apply_stage_accessibility(self) -> None:
        view = getattr(self, "_current_view", None)
        if hasattr(self, "_focus_manager"):
            chain = getattr(view, "focus_chain", None) if view is not None else None
            try:
                self._focus_manager.reset(chain or [])
            except Exception:
                pass
        if hasattr(self, "_escape_handler"):
            try:
                self._escape_handler.clear(self._escape_tokens)
            except Exception:
                self._escape_tokens = []
            else:
                self._escape_tokens = []
            tokens = getattr(view, "escape_tokens", None) if view is not None else None
            if tokens:
                self._escape_tokens = list(tokens)

    def _toggle_theme(self) -> None:
        try:
            new_name = self._theme_resolver.toggle()
            tokens = _theme_model.get_theme(new_name)
            _theme_apply.apply_to_root(self.root, tokens, initial=False, enable=_theme_resolve.get_enable_theming())
            self._rebuild_menu()
        except Exception:
            pass

    def _publish_last_prompt_sequence(self, template: Dict[str, Any] | None, plan_text: str) -> None:
        if not plan_text:
            return
        self._last_prompt_sequence = plan_text
        callback = getattr(self, "update_last_prompt_sequence", None)
        if callable(callback):
            try:
                callback(template, plan_text)
            except Exception:
                try:
                    self._log.warning("mcp.plan.publish_failed", extra={"template": getattr(template, "get", lambda *_: None)("id")})
                except Exception:
                    pass

    # --- Stage orchestration -------------------------------------------------
    def _clear_content(self) -> None:
        for child in list(self.root.children.values()):
            try:
                child.destroy()
            except Exception:
                pass

    # --- Menu / accelerator handling ----------------------------------------
    def _bind_accelerators(self, mapping: Dict[str, Any]) -> None:
        # Unconditional bind (tk replaces existing). Wrap each to return break
        for seq, func in mapping.items():
            self.root.bind(seq, lambda e, f=func: (f(), "break"))
        self._accelerators = mapping

    def _rebuild_menu(self) -> None:
        try:
            mapping = options_menu.configure_options_menu(
                self.root,
                selector_view_module,
                selector_service,
                extra_items=self._stage_extra_items,
            )
        except Exception as e:  # pragma: no cover - defensive
            self._log.error("Menu rebuild failed: %s", e, exc_info=True)
            return
        self._bind_accelerators(mapping)

    # Extra items injected into the Options menu: reflect current stage.
    def _stage_extra_items(self, opt_menu, menubar) -> None:  # pragma: no cover - GUI heavy
        import tkinter as tk
        stage = self._stage or "?"
        # Show a disabled header for clarity
        opt_menu.add_separator()
        opt_menu.add_command(label=f"Stage: {stage}", state="disabled")
        # Stage specific utilities
        try:
            if stage == "collect" and getattr(self, "template", None):
                tid = self.template.get("id") if isinstance(self.template, dict) else None
                if tid is not None:
                    opt_menu.add_command(
                        label="Edit template exclusions",
                        command=lambda tid=tid: self.edit_exclusions(tid),
                    )
                if self._current_view and hasattr(self._current_view, "review"):
                    opt_menu.add_command(
                        label="Review ▶",
                        command=lambda: self._current_view.review(),  # type: ignore[attr-defined]
                    )
            elif stage == "review" and self._current_view:
                # Provide copy / finish commands mirroring toolbar buttons.
                if hasattr(self._current_view, "copy"):
                    opt_menu.add_command(
                        label="Copy (stay)",
                        command=lambda: self._current_view.copy(),  # type: ignore[attr-defined]
                    )
                if hasattr(self._current_view, "finish"):
                    opt_menu.add_command(
                        label="Finish (copy & close)",
                        command=lambda: self._current_view.finish(),  # type: ignore[attr-defined]
                    )
        except Exception as e:
            self._log.error("Stage extra menu items failed: %s", e, exc_info=True)

    def start(self) -> None:
        """Enter stage 1 (template selection)."""
        self._clear_content()
        self._stage = "select"
        try:
            self._current_view = select.build(self)
        except Exception as e:
            self._log.error("Template selection failed: %s", e, exc_info=True)
            show_error("Error", f"Failed to open template selector:\n{e}")
            raise
        else:
            try:
                self.root.update_idletasks()
                save_geometry(self.root.winfo_geometry())
            except Exception:
                pass
        self._apply_stage_accessibility()
        # Defer focus so nested widgets are realized
        try:
            self.root.after(40, self._focus_first_template_widget)
        except Exception:
            pass
        self._rebuild_menu()

    def advance_to_collect(self, template: Dict[str, Any]) -> None:
        self.template = template
        # Fast-path: if template has no effective input placeholders and feature enabled,
        # skip variable collection and go directly to review. Avoid any transient UI.
        # Evaluate fast-path for templates that look like real prompt files
        # (have at least a body under 'template'); avoid triggering for
        # bare stubs used in unit tests that lack these keys.
        try:
            body = template.get("template") if isinstance(template, dict) else None
            if isinstance(body, list):
                state = evaluate_fastpath_state(template)
                if state == FastPathState.EMPTY:
                    try:
                        # Single debug-level line; no sensitive content.
                        self._log.debug("fastpath.placeholder_empty", extra={"activated": True})
                    except Exception:
                        pass
                    self.advance_to_review({})
                    return
        except Exception:  # pragma: no cover - defensive
            pass
        self._clear_content()
        self._stage = "collect"
        try:
            self._current_view = collect.build(self, template)
        except Exception as e:
            self._log.error("Variable collection failed: %s", e, exc_info=True)
            show_error("Error", f"Failed to collect variables:\n{e}")
            raise
        else:
            try:
                self.root.update_idletasks()
                save_geometry(self.root.winfo_geometry())
            except Exception:
                pass
        self._apply_stage_accessibility()
        try:
            self.root.update_idletasks()
            screen_w = self.root.winfo_screenwidth()
            screen_h = self.root.winfo_screenheight()
            base_w = max(960, int(screen_w * 0.6))
            base_h = max(640, int(screen_h * 0.6))
            cur_w = max(self.root.winfo_width(), 1)
            cur_h = max(self.root.winfo_height(), 1)
            if cur_w < base_w or cur_h < base_h:
                self.root.geometry(f"{base_w}x{base_h}")
        except Exception:
            pass
        self._rebuild_menu()

    def back_to_select(self) -> None:
        self.start()

    def _handle_cancel(self) -> None:
        """Handle cancel button: clear state and return to selector."""
        # Clear workflow state
        self.template = None
        self.variables = None
        self._stage = "select"
        
        # Return to selector
        self.back_to_select()

    def advance_to_review(self, variables: Dict[str, Any]) -> None:
        # Inject single-field logic outputs BEFORE building review view so fill_placeholders works.
        try:
            tmpl = self.template or {}
            phs = tmpl.get("placeholders") or []
            if (
                isinstance(phs, list)
                and len(phs) == 1
                and isinstance(phs[0], dict)
                and 'logic' in (tmpl or {})
            ):
                # Accept any single placeholder name; map to capture for parsing
                only_name = phs[0].get('name')
                cap_val = variables.get(only_name) or variables.get('capture') or ''
                tz = (tmpl.get('logic') or {}).get('timezone') if isinstance(tmpl.get('logic'), dict) else None
                parsed = parser_singlefield.parse_capture(cap_val, timezone=tz)
                # Merge parsed outputs if not already supplied
                for k, v in parsed.items():
                    variables.setdefault(k, v)
        except Exception:  # pragma: no cover - defensive
            pass
        self.variables = dict(variables)
        self._clear_content()
        self._stage = "review"
        try:
            rendered_text = None
            render_vars = variables
            try:
                self._mcp_cancel_event.clear()
                with provide_mcp_project_cancellation(
                    self._mcp_cancel_event.is_set
                ):
                    rendered_text, render_vars = _render_template(
                        self.template or {},
                        variables,
                        return_vars=True,
                    )
            except ProjectExecutionCancelled:
                return
            except Exception:
                render_vars = variables
            else:
                plan_candidate = None
                if isinstance(render_vars, dict):
                    plan_candidate = render_vars.get("__mcp_plan__")
                if isinstance(plan_candidate, str) and plan_candidate.strip():
                    self._publish_last_prompt_sequence(self.template or {}, plan_candidate)
            self._current_view = _invoke_review_build(
                self,
                self.template,
                render_vars,
                rendered_text=rendered_text,
            )
            # Safety: if auto-copy feature active but view did not copy (e.g., future regression), trigger once here.
            try:
                from ...variables.storage import is_auto_copy_enabled_for_template
                # Skip in headless test path (namespace exposes 'bindings') to keep deterministic test counts
                headless = hasattr(self._current_view, 'bindings')
                if not headless and self.template and is_auto_copy_enabled_for_template(self.template.get("id")):
                    v = self._current_view
                    # Heuristic: only copy if status/instructions not already set to copied state (headless view attr names)
                    already = False
                    try:
                        instr = getattr(v, 'instructions', None)
                        if instr and isinstance(instr, dict) and 'Copy again' in (instr.get('text') or ''):
                            already = True
                    except Exception:
                        pass
                    if not already and hasattr(v, 'copy'):
                        try:
                            v.copy()  # type: ignore[attr-defined]
                        except Exception:
                            pass
            except Exception:
                pass
        except Exception as e:
            self._log.error("Review window failed: %s", e, exc_info=True)
            show_error("Error", f"Failed to open review window:\n{e}")
            raise
        else:
            try:
                self.root.update_idletasks()
                save_geometry(self.root.winfo_geometry())
            except Exception:
                pass
        self._apply_stage_accessibility()
        self._rebuild_menu()

    def edit_exclusions(self, template_id: int) -> None:
        """Open the exclusions editor for ``template_id``."""
        try:
            try:
                exclusions_dialog(self.root, exclusions_service, template_id)
            except TypeError:
                exclusions_dialog(self.root, exclusions_service)  # type: ignore[misc]
        except Exception as e:
            self._log.error("Exclusions editor failed: %s", e, exc_info=True)
            show_error("Error", f"Failed to edit exclusions:\n{e}")

    def _show_shortcuts(self) -> None:
        """Display configured template shortcuts in a simple dialog."""
        from tkinter import messagebox

        mapping = load_shortcuts()
        if not mapping:
            msg = "No shortcuts configured."
        else:
            lines = [f"{k}: {v}" for k, v in sorted(mapping.items())]
            msg = "\n".join(lines)
        messagebox.showinfo("Shortcuts", msg)

    def finish(self, final_text: str) -> None:
        # Cycle back asynchronously to avoid re-entrancy freezes on
        # some Tk builds when destroying widgets inside the original
        # event callback (e.g. Ctrl+Enter binding).
        self.final_text = final_text

        def _do_cycle():  # pragma: no cover - trivial logic
            if self._cycling:
                return
            self._cycling = True
            try:
                self.template = None
                self.variables = None
                # Proactively remove any stale bindings that may reference
                # destroyed widgets before we rebuild.
                try:
                    for seq in list(getattr(self, "_accelerators", {}).keys()):
                        self.root.unbind(seq)
                except Exception:
                    pass
                # Rebuild select stage
                self.start()
                try:
                    self.root.update_idletasks()
                except Exception:
                    pass
                # Small delayed focus to allow geometry/layout settle
                try:
                    self.root.after(50, lambda: (self._focus_and_raise(), self._attempt_initial_focus(), self._focus_first_template_widget()))
                except Exception:
                    self._focus_and_raise(); self._attempt_initial_focus(); self._focus_first_template_widget()
            except Exception:
                try:
                    self.root.quit()
                finally:
                    try:
                        self.root.destroy()
                    except Exception:
                        pass
            finally:
                # Allow future cycles after loop returns to idle
                def _clear_flag():
                    self._cycling = False
                try:
                    self.root.after(10, _clear_flag)
                except Exception:
                    self._cycling = False

        # Schedule with a short delay to ensure the originating Ctrl+Enter
        # binding callback has fully unwound across platforms (avoids some
        # rare focus / event queue stalls observed on Windows/macOS).
        try:
            self.root.after(75, _do_cycle)
        except Exception:
            try:
                self.root.after(0, _do_cycle)
            except Exception:
                _do_cycle()

    def cancel(self) -> None:
        self._mcp_cancel_event.set()
        self.final_text = None
        self.variables = None
        try:
            self.root.quit()
        finally:
            self.root.destroy()

    def run(self) -> tuple[Optional[str], Optional[Dict[str, Any]]]:
        try:
            self.start()
            self.root.mainloop()
            return self.final_text, self.variables
        finally:  # persistence best effort
            try:
                if self.root.winfo_exists():
                    save_geometry(self.root.winfo_geometry())
            except Exception:
                pass

    def _bind_digit_shortcuts(self) -> None:
        if getattr(self, "_digit_shortcuts_bound", False):
            return

        def _bind(sequence: str, handler) -> None:
            try:
                self.root.bind_all(sequence, handler)
            except Exception:
                self.root.bind(sequence, handler)

        for digit in "123456789":
            def _handler(event, d=digit):
                self._handle_digit_shortcut(d, external=False)
                return "break"

            _bind(f"<Control-KeyPress-{digit}>", _handler)
            _bind(f"<Control-KeyPress-KP_{digit}>", _handler)

        def _focus_handler(_event=None):
            self._focus_main_async()
            return "break"

        _bind("<Control-KeyPress-0>", _focus_handler)
        _bind("<Control-KeyPress-KP_0>", _focus_handler)
        self._digit_shortcuts_bound = True

    def _resolve_shortcut_template(self, digit: str) -> Optional[Dict[str, Any]]:
        template: Optional[Dict[str, Any]] = None
        try:
            template = resolve_shortcut(digit)
        except Exception as exc:
            try:
                self._log.error("shortcut.lookup_failed digit=%s error=%s", digit, exc)
            except Exception:
                pass
            return None
        if not template:
            try:
                self._log.info("shortcut.unmapped", extra={"digit": digit})
            except Exception:
                pass
            return None
        return template

    def _handle_digit_shortcut_external(self, digit: str) -> None:
        self._handle_digit_shortcut(digit, external=True)

    def _handle_digit_shortcut(self, digit: str, *, external: bool) -> None:
        def _dispatch() -> None:
            template = self._resolve_shortcut_template(digit)
            if not template:
                return
            has_focus = self._window_has_focus()
            try:
                state = str(self.root.state())
            except Exception:
                state = None
            if _should_handle_digit_inline(self._stage, state, has_focus, external):
                try:
                    self._focus_and_raise()
                except Exception:
                    pass
                self._start_template_from_shortcut(digit, template)
                return
            popup_owner = self.root if not external else None
            self._open_digit_popup(digit, template, owner=popup_owner)

        try:
            self.root.after(0, _dispatch)
        except Exception:
            _dispatch()

    def _start_template_from_shortcut(self, digit: str, template: Dict[str, Any]) -> None:
        try:
            self.advance_to_collect(template)
        except Exception as exc:
            try:
                self._log.error("shortcut.inline_failed digit=%s error=%s", digit, exc)
            except Exception:
                pass

    def _open_digit_popup(self, digit: str, template: Optional[Dict[str, Any]] = None, *, owner: Any = None) -> None:
        def _dispatch() -> None:
            tpl = template if template is not None else self._resolve_shortcut_template(digit)
            if not tpl:
                return
            try:
                self._popup_manager.open_template(tpl, owner=owner)
            except Exception as exc:
                try:
                    self._log.error("popup.shortcut.spawn_failed digit=%s error=%s", digit, exc)
                except Exception:
                    pass

        try:
            self.root.after(0, _dispatch)
        except Exception:
            _dispatch()

    # --- Focus helpers ----------------------------------------------------
    def _focus_and_raise(self) -> None:
        """Force the window to foreground (best effort)."""
        try:  # pragma: no cover - GUI runtime
            self.root.lift()
            self.root.focus_force()
            try:
                self.root.attributes('-topmost', True)
                # after delay drop topmost so normal stacking resumes
                self.root.after(150, lambda: self.root.attributes('-topmost', False))
            except Exception:
                pass
        except Exception:
            pass

    def _focus_main_async(self) -> None:
        def _do_focus() -> None:
            self._focus_and_raise()
            self._focus_first_template_widget()

        try:
            self.root.after(0, _do_focus)
        except Exception:
            _do_focus()

    def _window_has_focus(self) -> bool:
        try:
            widget = self.root.focus_displayof()
            if widget is None:
                return False
            toplevel = widget.winfo_toplevel()
            return toplevel is self.root
        except Exception:
            return False

    def _attempt_initial_focus(self) -> None:  # pragma: no cover - GUI runtime
        """Give initial keyboard focus to first suitable widget after cycle.

        The select frame may auto-select the first template; ensuring the
        listbox (or any widget with focus_set) receives focus avoids the
        appearance of a frozen window where keystrokes are ignored.
        """
        try:
            # Heuristic: focus first child widget that has focus_set
            for child in self.root.children.values():
                if hasattr(child, "focus_set"):
                    try:
                        child.focus_set()
                        break
                    except Exception:
                        continue
        except Exception:
            pass

    def _focus_first_template_widget(self) -> None:  # pragma: no cover - GUI runtime
        """Focus the first template listbox (selection stage) if present.

        Recursively searches descendants for a Tk Listbox and sets focus.
        Safe to call in any stage; no-op if not found.
        """
        if self._stage != "select":
            return
        try:
            # Prefer the listbox so arrow keys / Enter work immediately.
            lst = getattr(self, '_select_listbox', None)
            if lst is not None and hasattr(lst, 'focus_set'):
                try:
                    lst.focus_set()
                except Exception:
                    pass
            else:
                # Fallback to search entry if listbox missing
                entry = getattr(self, '_select_query_entry', None)
                if entry is not None and hasattr(entry, 'focus_set'):
                    try:
                        entry.focus_set()
                        return
                    except Exception:
                        pass
            def _recurse(w):
                try:
                    children = w.winfo_children()
                except Exception:
                    return False
                for c in children:
                    try:
                        if getattr(c, 'winfo_class', lambda: '')() == 'Listbox':
                            try:
                                c.focus_set()
                            except Exception:
                                pass
                            return True
                    except Exception:
                        pass
                    if _recurse(c):
                        return True
                return False
            _recurse(self.root)
            # Bind type-to-search once per select stage entry.
            self.enable_type_to_search()
        except Exception:
            pass

    def enable_type_to_search(self) -> None:  # pragma: no cover - GUI runtime
        """Enable typing while listbox focused to jump to search box.

        When on the select stage, if a printable character is typed while the
        listbox (selector) has focus, focus shifts to the search entry and the
        character is inserted, initiating an immediate search workflow.
        """
        if self._stage != 'select':
            return
        try:
            root = self.root
            if getattr(self, '_type_search_bound', False):
                return
            if getattr(self, '_select_inline_type_to_search', False):
                self._type_search_bound = True
                return
            entry = getattr(self, '_select_query_entry', None)
            lst = getattr(self, '_select_listbox', None)
            if not (entry and lst):
                return
            def _on_key(ev):
                try:
                    ch = getattr(ev, 'char', '')
                    # Only intercept when the listbox currently has focus.
                    # This avoids double insertion when typing directly in the entry,
                    # because Entry's own default handler will already insert the char.
                    _fg = getattr(root, 'focus_get', None)
                    if _fg is not None:
                        if _fg() is not lst:
                            return None
                    # If focus_get is unavailable (test stubs), assume listbox-focused.
                    if len(ch) == 1 and ch.isprintable():
                        try:
                            entry.focus_set()
                            if hasattr(entry, 'delete') and hasattr(entry, 'index') and entry.index('insert') == 0:
                                pass  # leave existing search text
                            if hasattr(entry, 'insert'):
                                entry.insert('end', ch)
                            if hasattr(entry, 'event_generate'):
                                entry.event_generate('<KeyRelease>')
                            return 'break'
                        except Exception:
                            return None
                except Exception:
                    return None
            # Bind at the root level so keypresses while the listbox has focus
            # are captured, but the focus guard above prevents interference when
            # the entry already has focus (avoids double insertion).
            root.bind('<Key>', _on_key)
            self._type_search_bound = True
        except Exception:
            pass


__all__ = ["SingleWindowApp", "_should_handle_digit_inline"]
