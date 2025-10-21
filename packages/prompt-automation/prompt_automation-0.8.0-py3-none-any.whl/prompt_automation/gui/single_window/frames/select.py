"""Template selection frame with hierarchical browse and search."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

from ....config import PROMPTS_DIR
from ....errorlog import get_logger
from ....renderer import load_template
from ....services.template_search import list_templates, resolve_shortcut
from ....services.hierarchy import TemplateHierarchyScanner, HierarchyNode
from ....features import is_hierarchy_enabled
from ....services import multi_select as multi_select_service
from ....shortcuts import load_shortcuts
from ....validation.template_validator import TemplateValidationResult
from ....validation.error_recovery import SelectorState, SelectorStateStore
from ...components import shortcut_mapper as shortcut_mapper_component
from ...constants import INSTR_SELECT_SHORTCUTS
from ..tree_helpers import find_node_for, build_browse_items, flatten_matches
from ..selector_state import load_expanded, save_expanded


_log = get_logger(__name__)


def _canon_rel(rel: str | Path) -> str:
    parts = [p for p in Path(rel).parts if p]
    return "/".join(parts)


def toggle_folder_state(expanded: set[str], rel: str) -> None:
    """Toggle the canonical relative folder path in ``expanded``."""
    rel_norm = _canon_rel(rel)
    if not rel_norm:
        return
    if rel_norm in expanded:
        expanded.remove(rel_norm)
    else:
        expanded.add(rel_norm)


@dataclass
class FocusAction:
    target: str
    consume: bool = False


class SearchFocusController:
    """Derive focus routing between listbox and search entry."""

    _CONTROL_MASK = 0x0004
    _ARROW_KEYS = {
        "Up",
        "Down",
        "Left",
        "Right",
        "Prior",
        "Next",
        "Home",
        "End",
    }

    def __init__(self) -> None:
        self._last_target = "list"

    def decide_focus(self, current: str, event: Any) -> FocusAction:
        char = getattr(event, "char", "") or ""
        keysym = getattr(event, "keysym", "") or ""
        state = getattr(event, "state", 0) or 0

        if keysym in self._ARROW_KEYS:
            self._last_target = "list"
            return FocusAction(target="list", consume=False)

        printable = bool(char and char.isprintable())
        control = bool(state & self._CONTROL_MASK)

        if printable and not control:
            self._last_target = "search"
            consume = current != "search"
            return FocusAction(target="search", consume=consume)

        if current == "search":
            self._last_target = "search"
            return FocusAction(target="search", consume=False)

        self._last_target = current or "list"
        return FocusAction(target=self._last_target, consume=False)


def _normalized_key(event: Any) -> str:
    key = getattr(event, "char", "") or ""
    if key:
        return key
    keysym = getattr(event, "keysym", "") or ""
    if keysym.startswith("KP_") and len(keysym) == 4 and keysym[-1].isdigit():
        return keysym[-1]
    if keysym.isdigit():
        return keysym
    return key


def build(app) -> Any:  # pragma: no cover - Tk runtime
    import tkinter as tk
    import types

    # Headless test stub: if core widgets missing, return a lightweight object
    if not hasattr(tk, "Listbox"):
        state: Dict[str, Any] = {
            "recursive": True,
            "query": "",
            "paths": list_templates("", True),
            "selected": [],
            "preview": "",
            "expanded": set(),
        }
        instr = {"text": INSTR_SELECT_SHORTCUTS}

        def _refresh() -> None:
            state["paths"] = list_templates(state["query"], state["recursive"])
            state["preview"] = ""

        def search(query: str):
            state["query"] = query
            _refresh()
            return state["paths"]

        def toggle_recursive():
            state["recursive"] = not state["recursive"]
            _refresh()
            return state["recursive"]

        def activate_shortcut(key: str):
            tmpl = resolve_shortcut(str(key))
            if tmpl:
                app.advance_to_collect(tmpl)

        def activate_index(n: int):
            if 1 <= n <= len(state["paths"]):
                tmpl = load_template(state["paths"][n - 1])
                app.advance_to_collect(tmpl)

        def _set_preview(path: Path) -> None:
            try:
                tmpl = load_template(path)
                state["preview"] = "\n".join(tmpl.get("template", []))
            except Exception as e:
                state["preview"] = f"Error: {e}"

        def select(indices):
            state["selected"] = []
            if indices:
                idx_paths = [
                    state["paths"][i] for i in indices if i < len(state["paths"])
                ]
                for p in idx_paths:
                    try:
                        state["selected"].append(load_template(p))
                    except Exception:
                        pass
                _set_preview(idx_paths[0])
            else:
                state["preview"] = ""

        def combine():
            tmpl = multi_select_service.merge_templates(state["selected"])
            if tmpl:
                app.advance_to_collect(tmpl)
            return tmpl

        def toggle_folder(rel: str):
            toggle_folder_state(state["expanded"], rel)
            return sorted(state["expanded"])

        return types.SimpleNamespace(
            search=search,
            toggle_recursive=toggle_recursive,
            activate_shortcut=activate_shortcut,
            activate_index=activate_index,
            select=select,
            combine=combine,
            toggle_folder=toggle_folder,
            state=state,
            instructions=instr,
            escape_tokens=[],
            focus_chain=[],
        )

    frame = tk.Frame(app.root)
    frame.pack(fill="both", expand=True)

    state_store = getattr(app, "_selector_state_store", None)

    def _sanitize_state(state: SelectorState) -> SelectorState:
        cwd_candidate = _canon_rel(state.cwd_rel) if state.cwd_rel else ""
        if cwd_candidate and not (PROMPTS_DIR / cwd_candidate).is_dir():
            cwd_candidate = ""
        valid_expanded = set()
        for rel in state.expanded:
            rel_norm = _canon_rel(rel)
            if rel_norm and (PROMPTS_DIR / rel_norm).is_dir():
                valid_expanded.add(rel_norm)
        return SelectorState(cwd_rel=cwd_candidate, query=state.query, expanded=valid_expanded)

    if isinstance(state_store, SelectorStateStore):
        try:
            saved_state = _sanitize_state(state_store.load())
        except Exception:
            saved_state = SelectorState()
    else:
        saved_state = _sanitize_state(SelectorState(expanded=set(load_expanded())))

    tk.Label(frame, text="Select Template", font=("Arial", 14, "bold")).pack(pady=(12, 4))
    tk.Label(frame, text=INSTR_SELECT_SHORTCUTS, anchor="w", fg="#444").pack(
        fill="x", padx=12
    )

    search_bar = tk.Frame(frame)
    search_bar.pack(fill="x", padx=12)
    query = tk.StringVar(value=saved_state.query)
    entry = tk.Entry(search_bar, textvariable=query)
    entry.pack(side="left", fill="x", expand=True)
    recursive_var = tk.BooleanVar(value=True)

    main = tk.Frame(frame)
    main.pack(fill="both", expand=True)

    list_container = tk.Frame(main)
    list_container.pack(side="left", fill="both", expand=True, padx=(12, 0), pady=8)
    try:
        list_container.grid_rowconfigure(0, weight=1)
        list_container.grid_columnconfigure(0, weight=1)
    except Exception:
        pass

    listbox = tk.Listbox(list_container, activestyle="dotbox", selectmode="extended")
    scrollbar = tk.Scrollbar(list_container, orient="vertical", command=listbox.yview)
    scroll_x = tk.Scrollbar(list_container, orient="horizontal", command=listbox.xview)
    listbox.config(yscrollcommand=scrollbar.set, xscrollcommand=scroll_x.set)

    try:
        listbox.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")
    except Exception:
        listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="left", fill="y")
        scroll_x.pack(side="top", fill="x")

    preview = tk.Text(main, wrap="word", height=10, state="disabled")
    preview.pack(side="left", fill="both", expand=True, padx=(0, 12), pady=8)

    # Map listbox indices to either a template path or a folder rel
    item_map: Dict[int, Dict[str, Any]] = {}
    hier_mode = False
    cwd_rel = _canon_rel(saved_state.cwd_rel) if saved_state else ""
    scanner: TemplateHierarchyScanner | None = None

    # Enable hierarchical mode only in real Tk runtime to keep test stubs' flat expectations intact
    if is_hierarchy_enabled() and hasattr(tk, "TkVersion"):
        hier_mode = True
        scanner = TemplateHierarchyScanner()

    def _refresh_hier(*_):
        nonlocal cwd_rel, reselect_after_refresh
        assert scanner is not None
        node = find_node_for(scanner.scan(), cwd_rel)
        listbox.delete(0, "end")
        item_map.clear()
        q = query.get().strip().lower()
        # Global search mode: when user types, show matching templates anywhere recursively
        if q:
            rows = flatten_matches(scanner.list_flat(), q)
            for idx, (text, meta) in enumerate(rows):
                listbox.insert("end", text)
                item_map[idx] = meta
            _set_status_base(f"{len(rows)} results")
            if not listbox.curselection() and listbox.size() > 0:
                _select_index(0)
            update_preview()
            return
        # Browsing mode (no query): folders first, then templates of cwd
        idx = 0
        if cwd_rel:
            listbox.insert("end", ".. (up)")
            item_map[idx] = {"type": "up"}
            idx += 1
        # Inline browse rows with expansion support
        rows = build_browse_items(node, cwd_rel, expanded)
        for text, meta in rows:
            listbox.insert("end", text)
            item_map[idx] = meta
            idx += 1
        _set_status_base(f"{idx} items  ·  {cwd_rel or '/'}")
        target = reselect_after_refresh
        reselect_after_refresh = None
        if not _restore_selection(target):
            _ensure_default_selection()
        update_preview()

    def _refresh_flat(*_):
        paths = list_templates(query.get(), recursive_var.get())
        listbox.delete(0, "end")
        item_map.clear()
        for idx, p in enumerate(paths):
            rel = p.relative_to(PROMPTS_DIR)
            listbox.insert("end", str(rel))
            item_map[idx] = {"type": "template", "path": p}
        _set_status_base(f"{len(paths)} templates")
        if listbox.size() > 0 and not listbox.curselection():
            _select_index(0)
        update_preview()

    def refresh(*_):
        _refresh_shortcut_display()
        if hier_mode:
            _refresh_hier()
        else:
            _refresh_flat()

    def _on_query_change(_event=None):
        refresh()
        _set_validation_message("")
        _persist_state()

    btn_bar = tk.Frame(frame)
    btn_bar.pack(fill="x", pady=(0, 8))

    status = tk.StringVar(value="")
    status_base = {"text": ""}
    validation_note = {"text": ""}

    def _update_status_label() -> None:
        parts = [status_base["text"]]
        note = validation_note["text"]
        if note:
            parts.append(note)
        text = "  ·  ".join([p for p in parts if p])
        status.set(text)

    def _set_status_base(text: str) -> None:
        status_base["text"] = text or ""
        _update_status_label()

    def _set_validation_message(text: str) -> None:
        validation_note["text"] = text or ""
        _update_status_label()

    tk.Label(btn_bar, textvariable=status, anchor="w").pack(side="left", padx=12)

    # Folder expansion state (relative paths from cwd)
    expanded: set[str] = set(saved_state.expanded) if hier_mode else set()
    reselect_after_refresh: str | None = None

    focus_controller = SearchFocusController()

    def _persist_state() -> None:
        if isinstance(state_store, SelectorStateStore):
            try:
                state_store.save(
                    SelectorState(
                        cwd_rel=cwd_rel if hier_mode else "",
                        query=query.get(),
                        expanded=set(expanded) if hier_mode else set(),
                    )
                )
            except Exception:
                pass
        else:
            try:
                save_expanded(expanded)
            except Exception:
                pass

    validator = getattr(app, "_template_validator", None)
    def _on_validation_result(result: TemplateValidationResult) -> None:
        if result.valid:
            _set_validation_message("Template valid")
        else:
            err = result.error or "Template validation failed"
            _set_validation_message(f"Invalid template: {err}")

    def _queue_validation(path: Path, data: Dict[str, Any]) -> None:
        if validator is None:
            return
        _set_validation_message("Validating…")
        try:
            validator.enqueue(path, template=data, callback=_on_validation_result)
        except Exception:
            pass

    def _select_index(idx: int) -> None:
        listbox.selection_clear(0, "end")
        listbox.selection_set(idx)
        listbox.activate(idx)
        try:
            listbox.see(idx)
        except Exception:
            pass

    def _restore_selection(target_rel: str | None) -> bool:
        if not target_rel:
            return False
        target_norm = _canon_rel(target_rel)
        for idx, meta in item_map.items():
            if meta.get("type") == "folder" and _canon_rel(meta.get("rel", "")) == target_norm:
                _select_index(idx)
                return True
        return False

    def _ensure_default_selection() -> None:
        if listbox.size() == 0:
            return
        if listbox.curselection():
            return
        idx = 0
        if hier_mode and not query.get().strip() and cwd_rel and listbox.size() > 1:
            idx = 1
        _select_index(idx)

    def _current_focus() -> str:
        try:
            widget = app.root.focus_get()
        except Exception:
            widget = None
        if widget is entry:
            return "search"
        if widget is listbox:
            return "list"
        return "other"

    def _nearest_index(event) -> int | None:
        try:
            return listbox.nearest(getattr(event, "y", 0))
        except Exception:
            sel = listbox.curselection()
            if sel:
                return sel[0]
            return None

    def _current_selection_index() -> int | None:
        sel = listbox.curselection()
        if sel:
            return sel[0]
        return None

    def _toggle_expand_current() -> str:
        nonlocal reselect_after_refresh
        sel = listbox.curselection()
        if not sel:
            return "break"
        item = item_map.get(sel[0])
        if not item or item.get("type") != "folder":
            return "break"
        rel = item.get("rel", "")
        toggle_folder_state(expanded, rel)
        reselect_after_refresh = rel
        refresh(); _persist_state()
        return "break"

    def proceed(event=None):
        nonlocal cwd_rel
        sel = listbox.curselection()
        if not sel:
            _set_status_base("Select a template first")
            _set_validation_message("")
            return "break"
        item = item_map.get(sel[0])
        if not item:
            return "break"
        if item.get("type") == "folder":
            # navigate into
            cwd_rel = item.get("rel", "")
            refresh()
            _persist_state()
            return "break"
        if item.get("type") == "up":
            cwd_rel = _canon_rel(Path(cwd_rel).parent if cwd_rel else "")
            refresh()
            _persist_state()
            return "break"
        try:
            data = load_template(item["path"])  # type: ignore[index]
        except Exception as e:  # pragma: no cover - runtime
            _set_status_base(f"Failed: {e}")
            _set_validation_message("")
            return "break"
        app.advance_to_collect(data)
        return "break"

    def _nav_up(event=None):
        nonlocal cwd_rel, reselect_after_refresh
        # Only navigate up in hierarchical mode with no active query
        if not hier_mode or query.get().strip():
            return None
        if not cwd_rel:
            return None
        target_rel = cwd_rel
        cwd_rel = _canon_rel(Path(cwd_rel).parent)
        reselect_after_refresh = target_rel
        refresh()
        _persist_state()
        return "break"

    def _clear_search_action() -> str:
        if not query.get().strip():
            return "break"
        query.set("")
        refresh()
        _set_validation_message("")
        _persist_state()
        return "break"

    def combine_action(event=None):
        sel = listbox.curselection()
        # Only count template selections
        chosen = [item_map[i] for i in sel if item_map.get(i, {}).get("type") == "template"]
        if len(chosen) < 2:
            _set_status_base("Select at least two templates")
            return "break"
        loaded = [load_template(it["path"]) for it in chosen]
        tmpl = multi_select_service.merge_templates(loaded)
        if tmpl:
            app.advance_to_collect(tmpl)
        else:
            _set_status_base("Failed to combine")
        return "break"

    def _activate_from_entry(event=None):
        if listbox.size() == 0:
            _set_status_base("No templates available")
            return "break"
        sel = listbox.curselection()
        if not sel:
            idx = 0
            if hier_mode and not query.get().strip() and cwd_rel and listbox.size() > 1:
                idx = 1
            _select_index(idx)
        return proceed()

    shortcuts_current = load_shortcuts()

    def _resolve_shortcut_meta(rel: str) -> Dict[str, Any]:
        try:
            data = load_template(PROMPTS_DIR / rel)
            title = data.get("title") or Path(rel).stem
        except Exception:
            title = Path(rel).stem
        return {"title": str(title), "path": rel}

    shortcut_model = shortcut_mapper_component.ShortcutMapperModel(
        shortcuts_current,
        resolver=_resolve_shortcut_meta,
    )

    def _activate_digit_from_mapper(digit: str) -> None:
        if not digit:
            return
        tmpl = resolve_shortcut(digit)
        if tmpl:
            app.advance_to_collect(tmpl)
            return
        if digit.isdigit() and digit != "0":
            idx = int(digit) - 1
            if 0 <= idx < listbox.size():
                listbox.selection_clear(0, "end")
                listbox.selection_set(idx)
                listbox.activate(idx)
                proceed()

    LabelFrame = getattr(tk, "LabelFrame", None)
    if LabelFrame is not None:
        mapper_container = LabelFrame(frame, text="Digit Shortcuts")
    else:
        mapper_container = tk.Frame(frame)
    mapper_container.pack(fill="x", padx=12, pady=(0, 8))
    if LabelFrame is None:
        tk.Label(mapper_container, text="Digit Shortcuts", anchor="w", font=("Arial", 10, "bold")).pack(
            fill="x", pady=(0, 2)
        )
    mapper_ns = shortcut_mapper_component.build_shortcut_mapper(
        mapper_container,
        shortcut_model,
        on_activate=_activate_digit_from_mapper,
    )
    mapper_widget = getattr(mapper_ns, "widget", None)
    if mapper_widget is not None:
        mapper_widget.pack(fill="x", expand=True)

    def _refresh_shortcut_display() -> None:
        nonlocal shortcuts_current
        try:
            mapping = load_shortcuts()
        except Exception:
            return
        if mapping != shortcuts_current:
            shortcuts_current = mapping
            try:
                mapper_ns.update(mapping)
            except Exception:
                pass

    escape_tokens: list[str] = []
    handler = getattr(app, "_escape_handler", None)
    if handler is not None:
        try:
            handler.register(
                "select.clear_search",
                _clear_search_action,
                predicate=lambda: bool(query.get().strip()),
                priority=10,
            )
            escape_tokens.append("select.clear_search")
        except Exception:
            pass
        if hier_mode:
            try:
                handler.register(
                    "select.nav_up",
                    lambda: _nav_up(),
                    predicate=lambda: bool(not query.get().strip() and cwd_rel),
                    priority=30,
                )
                escape_tokens.append("select.nav_up")
            except Exception:
                pass

    next_btn = tk.Button(btn_bar, text="Next ▶", command=proceed)
    next_btn.pack(side="right", padx=4)
    combine_btn = tk.Button(btn_bar, text="Combine ▶", command=combine_action)
    combine_btn.pack(side="right", padx=4)
    # Hide recursive toggle in hierarchical mode (not applicable)
    recursive_check = None
    if not hier_mode:
        recursive_check = tk.Checkbutton(
            btn_bar,
            text="Recursive Search",
            variable=recursive_var,
            command=lambda: refresh(),
        )
        recursive_check.pack(side="right", padx=8)

    entry.bind("<KeyRelease>", _on_query_change)
    entry.bind("<Return>", _activate_from_entry)
    entry.bind("<KP_Enter>", _activate_from_entry)
    listbox.bind("<Return>", proceed)
    listbox.bind("<Control-Return>", lambda e: _toggle_expand_current())
    listbox.bind("<BackSpace>", _nav_up)
    listbox.bind("<<ListboxSelect>>", lambda e: update_preview())

    def _toggle_folder_by_index(idx: int) -> str:
        nonlocal reselect_after_refresh
        item = item_map.get(idx)
        if not item or item.get("type") != "folder":
            return "break"
        rel = item.get("rel", "")
        toggle_folder_state(expanded, rel)
        reselect_after_refresh = rel
        refresh(); _persist_state()
        return "break"

    def _on_double_click(event):  # pragma: no cover - Tk runtime
        idx = _nearest_index(event)
        if idx is None:
            return "break"
        item = item_map.get(idx)
        if not item:
            return "break"
        if item.get("type") == "folder":
            return _toggle_folder_by_index(idx)
        if item.get("type") == "template":
            listbox.selection_clear(0, "end")
            listbox.selection_set(idx)
            listbox.activate(idx)
            proceed()
            return "break"
        if item.get("type") == "up":
            return _nav_up()
        return "break"

    def _on_ctrl_click(event):  # pragma: no cover - Tk runtime
        idx = _nearest_index(event)
        if idx is None:
            return None
        item = item_map.get(idx)
        if not item or item.get("type") != "folder":
            return None
        return _toggle_folder_by_index(idx)

    listbox.bind("<Double-Button-1>", _on_double_click)
    listbox.bind("<Control-Button-1>", _on_ctrl_click)
    listbox.bind("<Command-Button-1>", _on_ctrl_click)

    def _first_child_index(idx: int) -> int | None:
        next_idx = idx + 1
        if next_idx < listbox.size():
            return next_idx
        return None

    def _handle_right_arrow(idx: int | None) -> str | None:
        nonlocal reselect_after_refresh
        if idx is None:
            return "break"
        item = item_map.get(idx)
        if not item:
            return "break"
        if item.get("type") == "folder":
            rel = item.get("rel", "")
            rel_norm = _canon_rel(rel)
            if rel_norm not in expanded:
                toggle_folder_state(expanded, rel)
                reselect_after_refresh = rel
                refresh(); _persist_state()
                return "break"
            child_idx = _first_child_index(idx)
            if child_idx is not None:
                _select_index(child_idx)
                update_preview()
            return "break"
        if item.get("type") == "up":
            return _nav_up()
        return "break"

    def _handle_left_arrow(idx: int | None) -> str | None:
        nonlocal reselect_after_refresh
        if idx is None:
            return "break"
        item = item_map.get(idx)
        if not item:
            return "break"
        if item.get("type") == "folder":
            rel = item.get("rel", "")
            rel_norm = _canon_rel(rel)
            if rel_norm in expanded:
                expanded.discard(rel_norm)
                reselect_after_refresh = rel
                refresh(); _persist_state()
                return "break"
            return _nav_up()
        return _nav_up()

    def on_key(event):
        # Only suppress/ignore digits when actively inside a template
        # (collect/review stages). When stage is unknown (e.g., standalone
        # selector usage), allow digits to function normally.
        try:
            st = getattr(app, '_stage', 'select')
            if st in ('collect', 'review'):
                return None
        except Exception:
            pass

        keysym = getattr(event, "keysym", "")
        if hier_mode and not query.get().strip():
            idx = _current_selection_index()
            if keysym in {"Right", "KP_Right"}:
                return _handle_right_arrow(idx)
            if keysym in {"Left", "KP_Left"}:
                return _handle_left_arrow(idx)

        key = _normalized_key(event)
        if key:
            tmpl = resolve_shortcut(key)
            if tmpl:
                app.advance_to_collect(tmpl)
                return "break"
            if key.isdigit() and key != "0":
                idx = int(key) - 1
                if 0 <= idx < listbox.size():
                    listbox.selection_clear(0, "end")
                    listbox.selection_set(idx)
                    listbox.activate(idx)
                    proceed()
                    return "break"

        current = _current_focus()
        decision = focus_controller.decide_focus(current, event)

        if decision.target == "search" and current != "search":
            try:
                entry.focus_set()
            except Exception:
                pass
        if decision.consume and decision.target == "search":
            char = getattr(event, "char", "")
            if char:
                try:
                    entry.icursor("end")
                    entry.insert("end", char)
                    query.set(entry.get())
                except Exception:
                    pass
            refresh()
            return "break"

        if decision.target == "list" and current != "list":
            try:
                listbox.focus_set()
            except Exception:
                pass
            if listbox.size() == 0:
                return "break"
            sel = listbox.curselection()
            idx = sel[0] if sel else 0
            keysym = getattr(event, "keysym", "")
            if keysym == "Up":
                idx = max(idx - 1, 0)
            elif keysym == "Down":
                idx = min(idx + 1, listbox.size() - 1)
            listbox.selection_clear(0, "end")
            listbox.selection_set(idx)
            listbox.activate(idx)
            update_preview()
            return "break"

    frame.bind_all("<Key>", on_key)

    def update_preview():
        sel = listbox.curselection()
        preview.config(state="normal")
        preview.delete("1.0", "end")
        if not sel:
            preview.config(state="disabled")
            _set_validation_message("")
            return
        item = item_map.get(sel[0])
        if not item or item.get("type") != "template":
            preview.config(state="disabled")
            _set_validation_message("")
            return
        try:
            tmpl = load_template(item["path"])  # type: ignore[index]
            lines = tmpl.get("template", [])
            preview.insert("1.0", "\n".join(lines))
            _queue_validation(item["path"], tmpl)
        except Exception as e:  # pragma: no cover - runtime
            preview.insert("1.0", f"Error: {e}")
            _set_validation_message(f"Invalid template: {e}")
        preview.config(state="disabled")

    refresh()
    # Expose search entry on app for focus preference when snapping back
    try:
        setattr(app, '_select_query_entry', entry)
        setattr(app, '_select_listbox', listbox)
        setattr(app, '_select_status_var', status)
        setattr(app, '_select_inline_type_to_search', True)
    except Exception:
        pass
    if item_map:
        _ensure_default_selection()
        listbox.focus_set()
        update_preview()

    focus_chain = [entry, listbox]
    if mapper_widget is not None:
        focus_chain.append(mapper_widget)
    if not hier_mode and recursive_check is not None:
        focus_chain.append(recursive_check)
    focus_chain.extend([combine_btn, next_btn])

    return types.SimpleNamespace(
        frame=frame,
        focus_chain=[w for w in focus_chain if w is not None],
        escape_tokens=escape_tokens,
        status_var=status,
    )


__all__ = ["build", "SearchFocusController", "FocusAction", "toggle_folder_state"]
