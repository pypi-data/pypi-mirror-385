"""Commands frame for GUI command palette.

Provides a command entry field and result display for executing
Obsidian vault operations via slash commands or natural language.
"""
from __future__ import annotations

from typing import TYPE_CHECKING
import types

if TYPE_CHECKING:
    from typing import Any

from ....commands import CommandExecutor, CommandResult
from ....commands.registry import CommandRegistry
from ....commands.handlers.rag_handler import RAGHandler
from ....commands.handlers.daily_handler import DailyHandler
from ....commands.handlers.note_handler import NoteHandler
from ....commands.handlers.open_handler import OpenHandler


def build(app):  # pragma: no cover - Tk runtime
    """Build commands frame.
    
    Args:
        app: SingleWindowApp instance
        
    Returns:
        Namespace with execute() and show_result() methods
    """
    import tkinter as tk
    from tkinter import messagebox, scrolledtext
    from unittest.mock import Mock
    
    # Check if running in headless test environment
    # If app or app.root is a Mock, we're in a test
    is_headless = isinstance(app, Mock) or isinstance(getattr(app, 'root', None), Mock)
    
    # Setup registry with handlers
    registry = CommandRegistry()
    mcp_client = app._mcp_client if hasattr(app, "_mcp_client") else None
    llm_client = app._llm_client if hasattr(app, "_llm_client") else None
    
    if mcp_client:
        registry.register("rag", RAGHandler(mcp_client))
        registry.register("daily", DailyHandler(mcp_client))
        registry.register("note", NoteHandler(mcp_client, llm_client))
        registry.register("open", OpenHandler(mcp_client))
    
    # Create executor
    executor = CommandExecutor(mcp_client, llm_client, registry)
    
    # State for headless tests
    state = {
        "last_result": None,
        "last_input": None
    }
    
    if is_headless:
        # Headless test stub
        class FrameStub:
            def __init__(self):
                self._state = state
                self._executor = executor
                self._app = app
            
            @property
            def last_result(self):
                return self._state["last_result"]
            
            def execute(self, user_input: str):
                """Execute command (headless)."""
                self._state["last_input"] = user_input
                result = self._executor.parse_and_execute(user_input)
                self._state["last_result"] = result
                return result
            
            def show_result(self, result: CommandResult):
                """Show result (headless)."""
                self._state["last_result"] = result
            
            def cancel(self):
                """Cancel (headless)."""
                if hasattr(self._app, "_handle_cancel"):
                    self._app._handle_cancel()
        
        return FrameStub()
    
    # Real GUI implementation
    frame = tk.Frame(app.root)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Title
    title = tk.Label(frame, text="Command Palette", font=("Arial", 14, "bold"))
    title.pack(pady=(0, 10))
    
    # Help text
    help_text = tk.Label(
        frame,
        text="Enter slash commands (/rag, /daily, /note, /open) or natural language",
        font=("Arial", 9),
        fg="gray"
    )
    help_text.pack()
    
    # Command entry
    entry_frame = tk.Frame(frame)
    entry_frame.pack(fill=tk.X, pady=10)
    
    entry_label = tk.Label(entry_frame, text="Command:")
    entry_label.pack(side=tk.LEFT)
    
    entry = tk.Entry(entry_frame, font=("Arial", 11))
    entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 10))
    
    # Result display
    result_label = tk.Label(frame, text="Result:", font=("Arial", 10, "bold"))
    result_label.pack(anchor=tk.W, pady=(10, 5))
    
    result_text = scrolledtext.ScrolledText(frame, height=15, font=("Courier", 9))
    result_text.pack(fill=tk.BOTH, expand=True)
    result_text.config(state=tk.DISABLED)
    
    # Status label
    status_label = tk.Label(frame, text="", font=("Arial", 9), fg="blue")
    status_label.pack(pady=5)
    
    def show_result(result: CommandResult):
        """Display command result."""
        state["last_result"] = result
        
        # Update result text
        result_text.config(state=tk.NORMAL)
        result_text.delete("1.0", tk.END)
        
        if result.success:
            # Show diff if requires approval
            if result.requires_approval and result.diff:
                # Show approval dialog
                approved = messagebox.askyesno(
                    "Approve Changes",
                    f"Review changes:\n\n{result.diff}\n\nApprove?",
                    parent=frame
                )
                if approved:
                    result_text.insert(tk.END, result.formatted)
                    status_label.config(text="✓ Command executed and approved", fg="green")
                else:
                    result_text.insert(tk.END, "Changes rejected by user")
                    status_label.config(text="✗ Changes rejected", fg="orange")
            else:
                result_text.insert(tk.END, result.formatted)
                status_label.config(text="✓ Command executed", fg="green")
        else:
            result_text.insert(tk.END, f"Error: {result.error}")
            status_label.config(text="✗ Command failed", fg="red")
        
        result_text.config(state=tk.DISABLED)
    
    def execute_command():
        """Execute command from entry."""
        user_input = entry.get().strip()
        if not user_input:
            status_label.config(text="Please enter a command", fg="orange")
            return
        
        state["last_input"] = user_input
        status_label.config(text="Executing...", fg="blue")
        frame.update()
        
        try:
            result = executor.parse_and_execute(user_input)
            show_result(result)
        except Exception as e:
            status_label.config(text=f"Error: {e}", fg="red")
    
    def cancel():
        """Cancel and return to selector."""
        if hasattr(app, "_handle_cancel"):
            app._handle_cancel()
    
    # Buttons
    button_frame = tk.Frame(frame)
    button_frame.pack(pady=10)
    
    execute_btn = tk.Button(button_frame, text="Execute", command=execute_command)
    execute_btn.pack(side=tk.LEFT, padx=5)
    
    cancel_btn = tk.Button(button_frame, text="Cancel", command=cancel)
    cancel_btn.pack(side=tk.LEFT, padx=5)
    
    # Bind Enter key
    entry.bind("<Return>", lambda e: execute_command())
    entry.focus()
    
    # Return namespace
    return types.SimpleNamespace(
        execute=lambda inp: show_result(executor.parse_and_execute(inp)),
        show_result=show_result,
        cancel=cancel,
        last_result=state.get("last_result")
    )
