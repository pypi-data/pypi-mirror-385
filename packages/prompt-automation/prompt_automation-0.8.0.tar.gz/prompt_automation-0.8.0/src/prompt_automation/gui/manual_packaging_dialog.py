from __future__ import annotations

import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

from ..services.manual_packaging import ManualPackagingRequest, PackagingEvent, PackagingOrchestrator
from ..variables import storage


class ManualPackagingDialog:
    def __init__(self, root) -> None:
        self._root = root
        self._win = tk.Toplevel(root)
        self._win.title("Manual Packaging")
        self._win.geometry("720x520")
        self._win.transient(root)
        self._win.grab_set()
        self._orchestrator = PackagingOrchestrator()
        try:
            suggested = self._orchestrator.suggest_version()
        except Exception:
            suggested = ""
        self._running = False
        self._outcome = None
        self._thread: threading.Thread | None = None
        self._active_orchestrator: PackagingOrchestrator | None = None

        frame = ttk.Frame(self._win, padding=(12, 10))
        frame.pack(fill="both", expand=True)

        self._version_var = tk.StringVar(value=suggested)
        self._verbose_var = tk.BooleanVar(value=storage.get_manual_packaging_verbose_logs())
        self._dry_run_var = tk.BooleanVar(value=False)
        self._status_var = tk.StringVar(value="Idle")
        self._release_var = tk.StringVar(value="")

        top = ttk.LabelFrame(frame, text="Options")
        top.pack(fill="x")

        ttk.Label(top, text="Version tag (SemVer)").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self._version_entry = ttk.Entry(top, textvariable=self._version_var, width=24)
        self._version_entry.grid(row=0, column=1, sticky="w", padx=(0, 6), pady=4)

        ttk.Checkbutton(
            top,
            text="Verbose log streaming",
            variable=self._verbose_var,
            command=self._persist_verbose,
        ).grid(row=1, column=0, columnspan=2, sticky="w", padx=6)

        ttk.Checkbutton(
            top,
            text="Dry run (skip git + release)",
            variable=self._dry_run_var,
        ).grid(row=2, column=0, columnspan=2, sticky="w", padx=6, pady=(0, 4))

        ttk.Label(top, textvariable=self._status_var).grid(row=0, column=2, padx=6, sticky="e")

        log_frame = ttk.LabelFrame(frame, text="Log")
        log_frame.pack(fill="both", expand=True, pady=(10, 0))
        self._log = scrolledtext.ScrolledText(log_frame, wrap="word", height=18, state="disabled")
        self._log.pack(fill="both", expand=True)

        bottom = ttk.Frame(frame)
        bottom.pack(fill="x", pady=(8, 0))

        ttk.Label(bottom, textvariable=self._release_var, foreground="#00695c").pack(side="left", padx=(4, 0))

        self._start_btn = ttk.Button(bottom, text="Start", command=self._start)
        self._start_btn.pack(side="right")
        self._cancel_btn = ttk.Button(bottom, text="Cancel", command=self._cancel)
        self._cancel_btn.pack(side="right", padx=(0, 6))

        self._win.protocol("WM_DELETE_WINDOW", self._close)

    # --- actions -----------------------------------------------------
    def _persist_verbose(self) -> None:
        storage.set_manual_packaging_verbose_logs(self._verbose_var.get())

    def _start(self) -> None:
        if self._running:
            return
        version = self._version_var.get().strip() or None
        request = ManualPackagingRequest(
            version=version,
            verbose_logs=self._verbose_var.get(),
            dry_run=self._dry_run_var.get(),
        )
        self._set_running(True)
        self._append_log("Starting manual packaging...")
        self._status_var.set("Running")
        self._release_var.set("")
        orchestrator = PackagingOrchestrator(repo_root=getattr(self._orchestrator, "_repo_root", None))
        orchestrator.add_listener(lambda event: self._win.after(0, self._handle_event, event))
        self._active_orchestrator = orchestrator
        self._thread = threading.Thread(target=self._execute, args=(orchestrator, request), daemon=True)
        self._thread.start()

    def _execute(self, orchestrator: PackagingOrchestrator, request: ManualPackagingRequest) -> None:
        outcome = orchestrator.run(request)
        self._win.after(0, self._handle_outcome, outcome)

    def _handle_event(self, event: PackagingEvent) -> None:
        if event.kind == "log":
            self._append_log(event.message)
        if event.level == "error":
            self._status_var.set("Error")
        elif event.level == "warning" and not self._status_var.get().lower().startswith("error"):
            self._status_var.set("Warning")

    def _handle_outcome(self, outcome) -> None:
        self._set_running(False)
        self._outcome = outcome
        self._active_orchestrator = None
        if outcome.success:
            self._status_var.set("Complete")
            msg = "Manual packaging completed successfully."
            self._append_log(msg)
            if outcome.release_url:
                self._release_var.set(outcome.release_url)
        else:
            self._status_var.set("Failed")
            for err in outcome.errors:
                self._append_log(f"ERROR: {err}")
        if outcome.log_path:
            self._append_log(f"Log file: {outcome.log_path}")
        self._start_btn.configure(text="Close", command=self._close)
        self._cancel_btn.configure(text="View Log", command=lambda: self._show_log_path(outcome))

    def _show_log_path(self, outcome) -> None:
        if outcome and outcome.log_path:
            messagebox.showinfo("Manual Packaging", f"Log saved to:\n{outcome.log_path}")

    def _cancel(self) -> None:
        if self._running and self._thread and self._thread.is_alive():
            self._status_var.set("Cancelling…")
            try:
                if self._active_orchestrator:
                    self._active_orchestrator.cancel()
            except Exception:
                pass
        else:
            self._close()

    def _close(self) -> None:
        if self._running:
            messagebox.showwarning("Manual Packaging", "Packaging in progress; cancel first.")
            return
        self._win.grab_release()
        self._win.destroy()

    # --- helpers -----------------------------------------------------
    def _append_log(self, line: str) -> None:
        self._log.configure(state="normal")
        self._log.insert("end", line + "\n")
        self._log.see("end")
        self._log.configure(state="disabled")

    def _set_running(self, running: bool) -> None:
        self._running = running
        state = "disabled" if running else "normal"
        self._version_entry.configure(state=state)
        self._start_btn.configure(state="disabled" if running else "normal")
        self._cancel_btn.configure(text="Cancel" if running else "Close")


def open_manual_packaging_dialog(root) -> None:  # pragma: no cover - GUI glue
    ManualPackagingDialog(root)


__all__ = ["ManualPackagingDialog", "open_manual_packaging_dialog"]

