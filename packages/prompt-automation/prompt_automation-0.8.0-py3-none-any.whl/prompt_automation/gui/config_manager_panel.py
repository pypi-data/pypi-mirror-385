"""GUI panel for ConfigManager - Visual settings discovery and configuration."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import Any

from ..errorlog import get_logger

_log = get_logger(__name__)

# Try to import ConfigManager, gracefully handle missing dependencies
try:
    from ..settings import ConfigManager
    _CONFIGMANAGER_AVAILABLE = True
except ImportError as e:
    _log.error("ConfigManager unavailable: %s", e)
    _CONFIGMANAGER_AVAILABLE = False
    _CONFIGMANAGER_ERROR = str(e)


def open_config_manager_panel(root) -> None:  # pragma: no cover - GUI heavy
    """
    Open ConfigManager panel window.
    
    Provides visual interface for:
    - Settings discovery (all available configuration options)
    - Profile switching (lightweight/standard/performance)
    - Hot-reload toggle
    - Automatic config file creation
    """
    _log.info("Opening Configuration Manager panel...")
    
    # Check if ConfigManager is available
    if not _CONFIGMANAGER_AVAILABLE:
        error_msg = (
            "Configuration Manager requires 'pydantic' package.\n\n"
            f"Error: {_CONFIGMANAGER_ERROR}\n\n"
            "To fix this, run:\n"
            "  pip install pydantic>=2.0.0 watchdog>=3.0.0\n\n"
            "Or reinstall prompt-automation with:\n"
            "  pip install -e ."
        )
        _log.error("ConfigManager unavailable: %s", _CONFIGMANAGER_ERROR)
        messagebox.showerror("Missing Dependency", error_msg)
        return
    
    try:
        win = tk.Toplevel(root)
        win.title("Configuration Manager")
        win.geometry("700x600")
        
        # Ensure window is visible and on top
        win.lift()
        win.focus_force()
        
        # Prevent keyboard events from propagating to parent
        win.grab_set()
        
        _log.info("Configuration Manager window created")
    except Exception as e:
        _log.error("Failed to create Configuration Manager window: %s", e, exc_info=True)
        raise
    
    # Get ConfigManager instance and RELOAD to get latest values
    config_mgr = ConfigManager()
    config_mgr.load()  # Force reload from disk to get current state
    config_path = config_mgr.config_path
    if not config_path.exists():
        try:
            config_mgr.save()
            _log.info("Created config file at %s", config_path)
        except Exception as e:
            _log.error("Failed to create config file: %s", e)
            messagebox.showerror("Error", f"Failed to create config file: {e}")
            win.destroy()
            return
    
    # Status bar at top
    status_frame = tk.Frame(win)
    status_frame.pack(fill="x", padx=8, pady=(8, 0))
    
    tk.Label(
        status_frame,
        text=f"Config file: {config_path}",
        font=("TkDefaultFont", 9),
        fg="gray"
    ).pack(side="left")
    
    # Profile selection
    profile_frame = tk.LabelFrame(win, text="Profile", padx=8, pady=8)
    profile_frame.pack(fill="x", padx=8, pady=8)
    
    profiles = {
        "lightweight": "Minimal features, low resource usage",
        "standard": "Balanced features and performance (default)",
        "performance": "All features enabled, maximum performance"
    }
    
    # Detect current profile based on settings
    current_profile = tk.StringVar(value="standard")
    
    for profile, description in profiles.items():
        rb = tk.Radiobutton(
            profile_frame,
            text=profile.capitalize(),
            variable=current_profile,
            value=profile
        )
        rb.pack(anchor="w")
        tk.Label(
            profile_frame,
            text=f"  {description}",
            font=("TkDefaultFont", 9),
            fg="gray"
        ).pack(anchor="w", padx=(20, 0))
    
    def _switch_profile():
        try:
            profile = current_profile.get()
            config_mgr.switch_profile(profile)
            config_mgr.save()
            messagebox.showinfo("Success", f"Switched to {profile} profile")
            _refresh_ui()
        except Exception as e:
            _log.error("Failed to switch profile: %s", e)
            messagebox.showerror("Error", f"Failed to switch profile: {e}")
    
    tk.Button(
        profile_frame,
        text="Apply Profile",
        command=_switch_profile
    ).pack(anchor="e", pady=(8, 0))
    
    # Settings tabs
    notebook = ttk.Notebook(win)
    notebook.pack(fill="both", expand=True, padx=8, pady=8)
    
    # Create tabs for each config section
    tabs = {}
    sections = {
        "llm": ("LLM", ["enabled", "host", "port", "timeout_s", "max_tokens", "gpu_layers"]),
        "cache": ("Cache", ["enabled", "memory_mb", "disk_mb", "ttl_seconds"]),
        "performance": ("Performance", ["profile", "async_llm", "max_workers", "batch_size"]),
        "analytics": ("Analytics", ["enabled", "retention_days", "export_to_cloud"]),
        "features": ("Features", ["mcp_integration", "llm_generation", "espanso_sync", "template_management", "command_palette"]),
    }
    
    for section_key, (section_name, fields) in sections.items():
        frame = tk.Frame(notebook)
        notebook.add(frame, text=section_name)
        tabs[section_key] = frame
        
        # Add scrollable canvas
        canvas = tk.Canvas(frame)
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e, c=canvas: c.configure(scrollregion=c.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Populate fields
        _populate_section(scrollable_frame, section_key, fields, config_mgr)
    
    # Hot-reload toggle
    hotreload_frame = tk.Frame(win)
    hotreload_frame.pack(fill="x", padx=8, pady=(0, 8))
    
    # Read current hot-reload state from ConfigManager
    is_hotreload_enabled = config_mgr._watcher is not None if hasattr(config_mgr, '_watcher') else False
    hotreload_var = tk.BooleanVar(value=is_hotreload_enabled)
    # Keep variable alive
    win._hotreload_var = hotreload_var  # type: ignore
    
    def _toggle_hotreload():
        try:
            new_value = hotreload_var.get()
            _log.info(f">>> Hot-reload toggle clicked: {new_value}")
            
            # Simply enable or disable - don't save (hot-reload is runtime state, not config)
            if new_value:
                config_mgr.enable_hot_reload()
                _log.info(">>> Hot-reload enabled")
            else:
                config_mgr.disable_hot_reload()
                _log.info(">>> Hot-reload disabled")
            
            # Ensure UI reflects the actual state
            actual_state = config_mgr._watcher is not None if hasattr(config_mgr, '_watcher') else False
            if actual_state != new_value:
                _log.warning(f">>> Hot-reload state mismatch! UI: {new_value}, Actual: {actual_state}")
                hotreload_var.set(actual_state)
            
            _log.info(f">>> Hot-reload toggle complete: UI={hotreload_var.get()}, Actual={actual_state}")
        except Exception as e:
            _log.error(">>> Hot-reload toggle error: %s", e, exc_info=True)
            # Reset checkbox to previous state
            hotreload_var.set(not new_value)
            messagebox.showerror("Error", f"Failed to toggle hot-reload: {e}")
    
    tk.Checkbutton(
        hotreload_frame,
        text="Enable hot-reload (auto-reload on file changes)",
        variable=hotreload_var,
        command=_toggle_hotreload
    ).pack(side="left")
    
    # Action buttons
    button_frame = tk.Frame(win)
    button_frame.pack(fill="x", padx=8, pady=(0, 8))
    
    def _save_config():
        try:
            config_mgr.save()
            messagebox.showinfo("Success", "Configuration saved")
        except Exception as e:
            _log.error("Failed to save config: %s", e)
            messagebox.showerror("Error", f"Failed to save config: {e}")
    
    def _reset_defaults():
        if messagebox.askyesno("Confirm", "Reset all settings to defaults?"):
            try:
                config_path.unlink(missing_ok=True)
                # Force reload
                ConfigManager._instance = None
                config_mgr = ConfigManager()
                config_mgr.save()
                messagebox.showinfo("Success", "Reset to defaults")
                win.destroy()
            except Exception as e:
                _log.error("Failed to reset config: %s", e)
                messagebox.showerror("Error", f"Failed to reset config: {e}")
    
    def _open_file():
        try:
            import subprocess
            import platform
            
            if platform.system() == "Windows":
                subprocess.run(["notepad", str(config_path)])
            elif platform.system() == "Darwin":
                subprocess.run(["open", str(config_path)])
            else:
                subprocess.run(["xdg-open", str(config_path)])
        except Exception as e:
            _log.error("Failed to open config file: %s", e)
            messagebox.showerror("Error", f"Failed to open config file: {e}")
    
    def _refresh_ui():
        """Refresh UI to reflect current config state."""
        win.destroy()
        open_config_manager_panel(root)
    
    tk.Button(button_frame, text="Save", command=_save_config, width=10).pack(side="left", padx=(0, 4))
    tk.Button(button_frame, text="Reset to Defaults", command=_reset_defaults).pack(side="left", padx=4)
    tk.Button(button_frame, text="Open File", command=_open_file).pack(side="left", padx=4)
    tk.Button(button_frame, text="Close", command=win.destroy, width=10).pack(side="right")


def _populate_section(frame: tk.Frame, section_key: str, fields: list[str], config_mgr: ConfigManager) -> None:
    """Populate a configuration section with field widgets."""
    # Store all variables on the frame to prevent garbage collection
    if not hasattr(frame, '_config_vars'):
        frame._config_vars = {}  # type: ignore
    
    for field in fields:
        try:
            config_key = f"{section_key}.{field}"
            _log.info(f"Creating widget for {config_key}")
            current_value = config_mgr.get(config_key)
            _log.info(f"  Current value: {current_value} (type: {type(current_value).__name__})")
            
            # Create field frame
            field_frame = tk.Frame(frame)
            field_frame.pack(fill="x", padx=8, pady=4)
            
            # Label
            tk.Label(
                field_frame,
                text=field.replace("_", " ").title() + ":",
                width=20,
                anchor="w"
            ).pack(side="left")
            
            # Input widget based on type
            if isinstance(current_value, bool):
                var = tk.BooleanVar(value=current_value)
                # Keep variable alive
                frame._config_vars[config_key] = var  # type: ignore
                
                def _make_bool_handler(key: str, v: tk.BooleanVar):
                    """Create boolean change handler with proper closure."""
                    def handler():
                        try:
                            new_val = v.get()
                            _log.info(f">>> HANDLER CALLED: Config bool changed: {key} = {new_val}")
                            
                            # Temporarily disable hot-reload to prevent circular reload
                            was_hotreload_enabled = config_mgr._watcher is not None if hasattr(config_mgr, '_watcher') else False
                            if was_hotreload_enabled:
                                config_mgr.disable_hot_reload()
                            
                            try:
                                config_mgr.set(key, new_val)
                                config_mgr.save()
                                _log.info(f">>> SAVE COMPLETE: Config saved: {key} = {new_val}")
                            finally:
                                # Re-enable hot-reload if it was enabled
                                if was_hotreload_enabled:
                                    config_mgr.enable_hot_reload()
                        except Exception as e:
                            _log.error(f">>> HANDLER ERROR: Failed to set {key}: {e}", exc_info=True)
                            # Reset checkbox to previous state
                            v.set(not new_val)
                            messagebox.showerror("Error", f"Invalid value: {e}")
                    return handler
                
                handler_func = _make_bool_handler(config_key, var)
                _log.info(f"  Creating checkbox with handler for {config_key}")
                widget = tk.Checkbutton(
                    field_frame, 
                    variable=var,
                    command=handler_func
                )
                widget.pack(side="left")
                _log.info(f"  ✓ Checkbox created and packed for {config_key}")
                
            elif isinstance(current_value, (int, float)):
                var = tk.StringVar(value=str(current_value))
                # Keep variable alive
                frame._config_vars[config_key] = var  # type: ignore
                entry = tk.Entry(field_frame, textvariable=var, width=15)
                entry.pack(side="left")
                
                # Prevent key events from propagating to parent window
                entry.bind("<Key>", lambda e: "break" if e.keysym not in ["Tab", "Return", "Escape"] else None)
                
                def _on_change_number(event=None, key=config_key, v=var, cur_val=current_value):
                    try:
                        # Temporarily disable hot-reload to prevent circular reload
                        was_hotreload_enabled = config_mgr._watcher is not None if hasattr(config_mgr, '_watcher') else False
                        if was_hotreload_enabled:
                            config_mgr.disable_hot_reload()
                        
                        try:
                            value = v.get()
                            if isinstance(cur_val, int):
                                config_mgr.set(key, int(value))
                            else:
                                config_mgr.set(key, float(value))
                            config_mgr.save()
                        finally:
                            # Re-enable hot-reload if it was enabled
                            if was_hotreload_enabled:
                                config_mgr.enable_hot_reload()
                    except ValueError as ve:
                        messagebox.showerror("Error", f"Invalid number: {v.get()}")
                    except Exception as e:
                        _log.error(f"Failed to set {key}: {e}")
                        messagebox.showerror("Error", f"Invalid value: {e}")
                
                entry.bind("<FocusOut>", _on_change_number)
                entry.bind("<Return>", _on_change_number)
                
            else:  # String
                var = tk.StringVar(value=str(current_value))
                # Keep variable alive
                frame._config_vars[config_key] = var  # type: ignore
                entry = tk.Entry(field_frame, textvariable=var, width=30)
                entry.pack(side="left")
                
                # Prevent key events from propagating to parent window
                entry.bind("<Key>", lambda e: "break" if e.keysym not in ["Tab", "Return", "Escape"] else None)
                
                def _on_change_str(event=None, key=config_key, v=var):
                    try:
                        # Temporarily disable hot-reload to prevent circular reload
                        was_hotreload_enabled = config_mgr._watcher is not None if hasattr(config_mgr, '_watcher') else False
                        if was_hotreload_enabled:
                            config_mgr.disable_hot_reload()
                        
                        try:
                            config_mgr.set(key, v.get())
                            config_mgr.save()
                        finally:
                            # Re-enable hot-reload if it was enabled
                            if was_hotreload_enabled:
                                config_mgr.enable_hot_reload()
                    except Exception as e:
                        _log.error(f"Failed to set {key}: {e}")
                        messagebox.showerror("Error", f"Invalid value: {e}")
                
                entry.bind("<FocusOut>", _on_change_str)
                entry.bind("<Return>", _on_change_str)
            
            # Show current env var override if exists
            env_var = f"PA_{section_key.upper()}__{field.upper()}"
            import os
            if env_var in os.environ:
                tk.Label(
                    field_frame,
                    text=f"(env: {env_var})",
                    font=("TkDefaultFont", 8),
                    fg="blue"
                ).pack(side="left", padx=(4, 0))
                
        except Exception as e:
            _log.error(f"Failed to populate field {section_key}.{field}: {e}")


__all__ = ["open_config_manager_panel"]
