"""Python environment diagnostic dialog for troubleshooting."""
from __future__ import annotations

import sys
import tkinter as tk
from tkinter import scrolledtext

from ..errorlog import get_logger

_log = get_logger(__name__)


def show_python_environment_info(root) -> None:  # pragma: no cover - GUI heavy
    """Display Python environment information for troubleshooting.
    
    Shows:
    - Python executable path
    - Python version
    - sys.path entries
    - pydantic availability
    - ConfigManager availability
    """
    _log.info("Opening Python Environment Info dialog")
    
    win = tk.Toplevel(root)
    win.title("Python Environment Info")
    win.geometry("800x600")
    
    text = scrolledtext.ScrolledText(win, wrap=tk.WORD, font=("Courier", 10))
    text.pack(fill="both", expand=True, padx=10, pady=10)
    
    info = []
    info.append("=== Python Environment ===\n")
    info.append(f"Python executable: {sys.executable}\n")
    info.append(f"Python version: {sys.version}\n")
    info.append(f"\n=== sys.path (first 10) ===\n")
    for i, path in enumerate(sys.path[:10], 1):
        info.append(f"{i}. {path}\n")
    
    info.append(f"\n=== Testing pydantic import ===\n")
    try:
        import pydantic
        info.append(f"✓ pydantic version: {pydantic.__version__}\n")
        info.append(f"✓ pydantic location: {pydantic.__file__}\n")
    except ImportError as e:
        info.append(f"✗ pydantic import failed: {e}\n")
    
    info.append(f"\n=== Testing prompt_automation.settings import ===\n")
    try:
        from ...settings import ConfigManager
        info.append(f"✓ ConfigManager imported successfully\n")
        config = ConfigManager()
        info.append(f"✓ ConfigManager instance created\n")
    except Exception as e:
        info.append(f"✗ ConfigManager import failed: {e}\n")
        import traceback
        info.append(traceback.format_exc())
    
    text.insert("1.0", "".join(info))
    text.config(state="disabled")
    
    # Close button
    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=10)
    
    tk.Button(
        btn_frame,
        text="Close",
        command=win.destroy,
        padx=20,
        pady=10
    ).pack()


__all__ = ["show_python_environment_info"]
