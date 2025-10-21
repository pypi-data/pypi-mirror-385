"""Hierarchical variable management modal for the GUI."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

from ..features import is_variable_hierarchy_enabled
from ..errorlog import get_logger
from ..variables.hierarchy.resolver import (
    EspansoDiscoveryAdapter,
    GlobalVariableResolver,
    RepoEspansoDiscoveryAdapter,
    StubEspansoDiscoveryAdapter,
)
from ..variables.hierarchy.storage import HierarchicalVariableStore
from ..variables.inventory import (
    VariableInventory,
    coerce_variable_value,
    parse_variable_path,
)

_log = get_logger(__name__)


Translator = Callable[[str], str]
StoreFactory = Callable[[], HierarchicalVariableStore]
InventoryFactory = Callable[[HierarchicalVariableStore], VariableInventory]


def _locate_doc(filename: str) -> Path | None:
    base = Path(__file__).resolve()
    for parent in base.parents:
        candidate = parent / "docs" / filename
        if candidate.exists():
            return candidate
    return None


_VARIABLE_DOC = _locate_doc("VARIABLE_WORKFLOW.md")


def _load_variables_doc() -> tuple[str | None, str | None]:
    if _VARIABLE_DOC is None:
        return None, None
    try:
        return _VARIABLE_DOC.read_text(encoding="utf-8"), str(_VARIABLE_DOC)
    except Exception:
        return None, str(_VARIABLE_DOC)


@dataclass(frozen=True)
class VariableEntry:
    """Presentation model describing a variable row in the modal."""

    path: str
    display_value: str
    raw_value: Any
    source: str
    is_espanso: bool
    example: str

    def matches(self, needle: str) -> bool:
        haystack = f"{self.path}\n{self.display_value}".lower()
        return needle in haystack


class VariableModalController:
    """Encapsulates CRUD operations and filtering for the modal."""

    def __init__(
        self,
        *,
        resolver: GlobalVariableResolver,
        store_factory: StoreFactory,
        adapter: EspansoDiscoveryAdapter,
        translator: Translator | None = None,
        inventory_factory: InventoryFactory | None = None,
    ) -> None:
        self._resolver = resolver
        self._store = store_factory()
        inv_factory = inventory_factory or VariableInventory
        self._inventory = inv_factory(self._store)
        self._adapter = adapter
        self._ = translator or (lambda msg: msg)
        self._entries: list[VariableEntry] = []
        self._entry_index: dict[str, VariableEntry] = {}
        self._search_term = ""
        self.refresh()

    # Public API -----------------------------------------------------
    def refresh(self) -> None:
        namespace = self._store.export_namespace("globals")
        resolved = self._resolver.resolve()
        espanso = self._safe_collect_espanso()
        entries = list(_build_entries(namespace, resolved, espanso))
        entries.sort(key=lambda item: item.path)
        self._entries = entries
        self._entry_index = {entry.path: entry for entry in entries}

    def set_search(self, text: str) -> None:
        self._search_term = text.strip().lower()

    def filtered_entries(self) -> list[VariableEntry]:
        if not self._search_term:
            return list(self._entries)
        return [e for e in self._entries if e.matches(self._search_term)]

    def create_variable(self, dotted_path: str, value: Any) -> VariableEntry:
        tokens = parse_variable_path(dotted_path)
        if not tokens:
            raise ValueError(self._("A variable path is required."))
        if _is_espanso(tokens):
            raise ValueError(self._("Espanso variables are read-only."))
        payload = coerce_variable_value(value)
        self._inventory.set_global(tokens, payload)
        self.refresh()
        return self._entry_index[".".join(tokens)]

    def update_variable(self, dotted_path: str, value: Any) -> VariableEntry:
        tokens = parse_variable_path(dotted_path)
        entry = self._entry_index.get(".".join(tokens))
        if entry is None:
            raise ValueError(self._("Unknown variable."))
        if entry.is_espanso:
            raise ValueError(self._("Espanso variables are read-only."))
        payload = coerce_variable_value(value)
        self._inventory.set_global(tokens, payload)
        self.refresh()
        return self._entry_index[".".join(tokens)]

    def delete_variable(self, dotted_path: str) -> bool:
        tokens = parse_variable_path(dotted_path)
        entry = self._entry_index.get(".".join(tokens))
        if entry is None:
            return False
        if entry.is_espanso:
            raise ValueError(self._("Espanso variables are read-only."))
        removed = self._inventory.delete_global(tokens)
        self.refresh()
        return removed

    # Internal helpers -----------------------------------------------
    def _safe_collect_espanso(self) -> Mapping[str, Any]:
        try:
            payload = self._adapter.collect()
            if isinstance(payload, Mapping):
                return payload
        except Exception as exc:  # pragma: no cover - defensive
            try:
                _log.error("variable_modal.espanso_error", extra={"error": str(exc)})
            except Exception:
                pass
        return {}


def open_variable_modal(
    root,
    *,
    ui_factory: Callable[..., Any] | None = None,
    translator: Translator | None = None,
    resolver: GlobalVariableResolver | None = None,
    store_factory: StoreFactory | None = None,
    adapter: EspansoDiscoveryAdapter | None = None,
):  # pragma: no cover - GUI heavy
    """Open the variable management modal if the hierarchy feature is enabled."""

    if not is_variable_hierarchy_enabled():
        return None

    _ = translator or (lambda msg: msg)
    adapter = adapter or RepoEspansoDiscoveryAdapter()
    store_factory = store_factory or HierarchicalVariableStore
    resolver = resolver or GlobalVariableResolver(adapter=adapter)
    controller = VariableModalController(
        resolver=resolver,
        store_factory=store_factory,
        adapter=adapter,
        translator=_ ,
    )
    factory = ui_factory or _default_ui_factory
    try:
        return factory(root, controller, _)
    except TypeError:
        return factory(root, controller)


class _VariableEditorDialog:  # pragma: no cover - GUI heavy
    def __init__(
        self,
        root,
        translator: Translator,
        *,
        title: str,
        initial_path: str = "",
        initial_value: str = "",
        allow_path_edit: bool = True,
    ) -> None:
        import tkinter as tk
        from tkinter import messagebox

        self._root = root
        self._ = translator or (lambda msg: msg)
        self._messagebox = messagebox
        self._title = title
        self._initial_path = initial_path
        self._initial_value = initial_value
        self._allow_path_edit = allow_path_edit
        self._result: tuple[str, str] | None = None

        self._window = tk.Toplevel(root)
        self._window.title(self._(title))
        self._window.transient(root)
        self._window.grab_set()
        self._window.resizable(True, True)
        self._window.minsize(420, 320)

        frame = tk.Frame(self._window, padx=12, pady=10)
        frame.pack(fill="both", expand=True)

        self._path_var = tk.StringVar(value=initial_path)
        tk.Label(frame, text=self._("Variable name"), anchor="w").pack(anchor="w")
        entry = tk.Entry(frame, textvariable=self._path_var)
        entry.pack(fill="x", pady=(0, 6))
        if not allow_path_edit:
            entry.configure(state="disabled")

        tk.Label(frame, text=self._("Value"), anchor="w").pack(anchor="w")
        self._text = tk.Text(frame, height=12, wrap="word")
        self._text.pack(fill="both", expand=True)
        if initial_value:
            self._text.insert("1.0", initial_value)

        btns = tk.Frame(frame)
        btns.pack(fill="x", pady=(10, 0))

        cancel_btn = tk.Button(btns, text=self._("Cancel"), command=self._cancel)
        cancel_btn.pack(side="right")
        save_btn = tk.Button(btns, text=self._("Save"), command=self._submit)
        save_btn.pack(side="right", padx=(0, 6))

        entry.focus_set()
        root.wait_window(self._window)

    def result(self) -> tuple[str, str] | None:
        return self._result

    def _submit(self) -> None:
        path = self._path_var.get().strip()
        if not path:
            self._messagebox.showerror(self._("Variables"), self._("Variable name is required."), parent=self._window)
            return
        value = self._text.get("1.0", "end-1c")
        self._result = (path, value)
        self._window.destroy()

    def _cancel(self) -> None:
        self._window.destroy()


class _ModalView:  # pragma: no cover - GUI heavy
    def __init__(self, root, controller: VariableModalController, translator: Translator) -> None:
        import tkinter as tk
        from tkinter import messagebox, simpledialog

        self._tk = tk
        self._messagebox = messagebox
        self._simpledialog = simpledialog
        self._root = root
        self._ = translator or (lambda msg: msg)
        self.controller = controller
        self.window = tk.Toplevel(root)
        self._rows: list[VariableEntry] = []
        self._wrap_targets: list[Any] = []
        self._build_structure()
        self._bind_handlers()
        self.refresh()

    def _build_structure(self) -> None:
        tk = self._tk
        win = self.window
        win.title(self._("Variables"))
        win.geometry("720x520")
        win.transient(self._root)
        win.grab_set()
        win.resizable(True, True)
        win.minsize(640, 440)
        win.focus_set()

        frame = tk.Frame(win, padx=12, pady=10)
        frame.pack(fill="both", expand=True)
        self._frame = frame

        self._search_var = tk.StringVar(value="")
        tk.Label(frame, text=self._("Search")).pack(anchor="w")
        self._search_entry = tk.Entry(frame, textvariable=self._search_var)
        self._search_entry.pack(fill="x")
        self._search_entry.focus_set()

        self._listbox = tk.Listbox(frame, activestyle="dotbox", exportselection=False)
        self._listbox.pack(fill="both", expand=True, pady=(8, 8))

        self._example_label = tk.Label(frame, text="", anchor="w", justify="left", wraplength=680)
        self._example_label.pack(fill="x", pady=(0, 6))

        self._status_label = tk.Label(frame, text="", anchor="w", justify="left", wraplength=680)
        self._status_label.pack(fill="x")

        self._wrap_targets = [self._example_label, self._status_label]

        button_bar = tk.Frame(frame)
        button_bar.pack(fill="x", pady=(6, 0))
        tk.Button(button_bar, text=self._("Create"), command=self._create_entry).pack(side="left", padx=4)
        tk.Button(button_bar, text=self._("Edit"), command=self._edit_entry).pack(side="left", padx=4)
        tk.Button(button_bar, text=self._("Delete"), command=self._delete_entry).pack(side="left", padx=4)
        tk.Button(button_bar, text=self._("Help"), command=self._open_help).pack(side="right", padx=(0, 6))
        tk.Button(button_bar, text=self._("Close"), command=self.window.destroy).pack(side="right")

    def _bind_handlers(self) -> None:
        self._listbox.bind("<<ListboxSelect>>", self._update_example)
        self._search_entry.bind("<KeyRelease>", self._on_search)
        self.window.bind("<Configure>", self._on_resize)

    def refresh(self) -> None:
        tk = self._tk
        self._rows = self.controller.filtered_entries()
        self._listbox.delete(0, tk.END)
        espanso_tag = f"[{self._('Espanso')}] "
        for row in self._rows:
            prefix = espanso_tag if row.is_espanso else ""
            display = f"{prefix}{row.path} — {row.display_value}"
            self._listbox.insert(tk.END, display)
        count_text = self._("{count} variables").format(count=len(self._rows))
        self._status_label.configure(text=count_text)
        if self._rows:
            first = self._rows[0]
            usage = self._("Usage: {placeholder}").format(placeholder=f"{{{{{first.path}}}}}")
            value_prefix = self._("Value:")
            value_block = self._format_editor_value(first.raw_value)
            self._example_label.configure(text=f"{usage}\n{value_prefix}\n{value_block}")
        else:
            self._example_label.configure(text="")

    def _on_search(self, *_args) -> None:
        self.controller.set_search(self._search_var.get())
        self.refresh()

    def _selected_entry(self) -> VariableEntry | None:
        selection = self._listbox.curselection()
        if not selection:
            return None
        index = selection[0]
        if 0 <= index < len(self._rows):
            return self._rows[index]
        return None

    def _update_example(self, _event=None) -> None:
        entry = self._selected_entry()
        if not entry:
            return
        usage = self._("Usage: {placeholder}").format(placeholder=f"{{{{{entry.path}}}}}")
        value_prefix = self._("Value:")
        value_block = self._format_editor_value(entry.raw_value)
        text = f"{usage}\n{value_prefix}\n{value_block}"
        self._example_label.configure(text=text)

    def _open_help(self) -> None:
        import tkinter as tk
        from tkinter import messagebox, scrolledtext

        content, doc_path = _load_variables_doc()
        if content is None:
            fallback = [
                self._("Documentation not found."),
                "",
                self._("Expected file:"),
            ]
            if doc_path:
                fallback.append(doc_path)
            else:
                fallback.append("docs/VARIABLE_WORKFLOW.md")
            content = "\n".join(fallback)
        try:
            win = tk.Toplevel(self.window)
            win.title(self._("Variable Workflow Guide"))
            win.geometry("780x560")
            win.transient(self.window)
            win.resizable(True, True)
            win.minsize(520, 360)
            text = scrolledtext.ScrolledText(win, wrap="word")
            text.pack(fill="both", expand=True)
            text.insert("1.0", content)
            text.configure(state="disabled")
            tk.Button(win, text=self._("Close"), command=win.destroy).pack(side="bottom", pady=6)
        except Exception as exc:  # pragma: no cover - defensive
            try:
                messagebox.showerror(self._("Variables"), str(exc), parent=self.window)
            except Exception:
                pass

    def _create_entry(self) -> None:
        dialog = _VariableEditorDialog(
            self._root,
            self._,
            title="Create variable",
            allow_path_edit=True,
        )
        result = dialog.result()
        if not result:
            return
        path, value = result
        try:
            self.controller.create_variable(path, value)
        except ValueError as exc:
            self._messagebox.showerror(self._("Variables"), str(exc), parent=self.window)
        self.refresh()

    def _edit_entry(self) -> None:
        entry = self._selected_entry()
        if not entry:
            self._messagebox.showinfo(self._("Variables"), self._("Select a variable to edit."), parent=self.window)
            return
        if entry.is_espanso:
            self._messagebox.showwarning(self._("Variables"), self._("Espanso variables cannot be edited."), parent=self.window)
            return
        dialog = _VariableEditorDialog(
            self._root,
            self._,
            title="Edit variable",
            initial_path=entry.path,
            initial_value=self._format_editor_value(entry.raw_value),
            allow_path_edit=False,
        )
        result = dialog.result()
        if not result:
            return
        _path, value = result
        try:
            self.controller.update_variable(entry.path, value)
        except ValueError as exc:
            self._messagebox.showerror(self._("Variables"), str(exc), parent=self.window)
        self.refresh()

    def _delete_entry(self) -> None:
        entry = self._selected_entry()
        if not entry:
            self._messagebox.showinfo(self._("Variables"), self._("Select a variable to delete."), parent=self.window)
            return
        if entry.is_espanso:
            self._messagebox.showwarning(self._("Variables"), self._("Espanso variables cannot be removed."), parent=self.window)
            return
        confirm = self._messagebox.askyesno(
            self._("Variables"),
            self._("Delete {path}?").format(path=entry.path),
            parent=self.window,
        )
        if not confirm:
            return
        try:
            self.controller.delete_variable(entry.path)
        except ValueError as exc:
            self._messagebox.showerror(self._("Variables"), str(exc), parent=self.window)
        self.refresh()

    def _on_resize(self, event) -> None:
        width = getattr(event, "width", 0)
        if width <= 1:
            return
        wrap = max(width - 48, 320)
        for widget in self._wrap_targets:
            try:
                widget.configure(wraplength=wrap)
            except Exception:
                pass

    def _format_editor_value(self, value: Any) -> str:
        if isinstance(value, str):
            return value
        try:
            return json.dumps(value, indent=2, ensure_ascii=False)
        except Exception:
            return str(value)


def _default_ui_factory(root, controller: VariableModalController, translator: Translator):  # pragma: no cover - GUI heavy
    return _ModalView(root, controller, translator).window


# Pure helper utilities ---------------------------------------------
def _build_entries(
    namespace: Mapping[str, Any] | Sequence[Any] | None,
    resolved: Mapping[str, Any],
    espanso: Mapping[str, Any],
) -> Iterable[VariableEntry]:
    resolved = resolved or {}
    for path, value in _flatten_mapping(namespace, include_parent=False):
        dot = ".".join(path)
        resolved_value = _lookup(resolved, path)
        yield VariableEntry(
            path=dot,
            display_value=_format_value(resolved_value if resolved_value is not None else value),
            raw_value=resolved_value if resolved_value is not None else value,
            source="custom",
            is_espanso=False,
            example=f"{{{{{dot}}}}}",
        )
    for path, value in _flatten_mapping(espanso, include_parent=True):
        dot = ".".join(path)
        yield VariableEntry(
            path=dot,
            display_value=_format_value(value),
            raw_value=value,
            source="espanso",
            is_espanso=True,
            example=f"{{{{{dot}}}}}",
        )


def _flatten_mapping(
    data: Any,
    prefix: tuple[str, ...] = (),
    *,
    include_parent: bool,
) -> Iterable[tuple[tuple[str, ...], Any]]:
    if isinstance(data, Mapping):
        if not data and prefix:
            yield prefix, {}
        for key, value in data.items():
            new_prefix = prefix + (str(key),)
            if isinstance(value, Mapping):
                if include_parent:
                    yield new_prefix, value
                yield from _flatten_mapping(value, new_prefix, include_parent=include_parent)
            else:
                yield new_prefix, value
    else:
        yield prefix, data


def _lookup(mapping: Mapping[str, Any], path: Sequence[str]) -> Any:
    node: Any = mapping
    for segment in path:
        if isinstance(node, Mapping) and segment in node:
            node = node[segment]
        else:
            return None
    return node


def _is_espanso(tokens: Sequence[str]) -> bool:
    return bool(tokens and tokens[0] == "__espanso__")


def _format_value(value: Any) -> str:
    if isinstance(value, str):
        trimmed = value.strip()
        return trimmed if len(trimmed) <= 80 else trimmed[:77] + "…"
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    except TypeError:
        return str(value)


__all__ = [
    "VariableEntry",
    "VariableModalController",
    "open_variable_modal",
]
