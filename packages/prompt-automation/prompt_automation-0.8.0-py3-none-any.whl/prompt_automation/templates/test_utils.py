"""
Test utilities for template GUI components.

Provides mock implementations of tkinter dialogs to prevent
manual intervention during automated testing.
"""
from typing import Optional, Any


class MockMessageBox:
    """
    Mock implementation of tkinter.messagebox for testing.
    
    Records all dialog calls without displaying actual popups.
    Allows tests to verify error handling without blocking.
    """
    
    def __init__(self):
        """Initialize mock with empty call history."""
        self.calls = []
    
    def showerror(self, title: str, message: str) -> None:
        """Mock showerror - records call without showing popup."""
        self.calls.append({
            "type": "error",
            "title": title,
            "message": message
        })
    
    def showinfo(self, title: str, message: str) -> None:
        """Mock showinfo - records call without showing popup."""
        self.calls.append({
            "type": "info",
            "title": title,
            "message": message
        })
    
    def showwarning(self, title: str, message: str) -> None:
        """Mock showwarning - records call without showing popup."""
        self.calls.append({
            "type": "warning",
            "title": title,
            "message": message
        })
    
    def askyesno(self, title: str, message: str) -> bool:
        """Mock askyesno - records call and returns True."""
        self.calls.append({
            "type": "yesno",
            "title": title,
            "message": message
        })
        return True  # Default to "Yes"
    
    def askokcancel(self, title: str, message: str) -> bool:
        """Mock askokcancel - records call and returns True."""
        self.calls.append({
            "type": "okcancel",
            "title": title,
            "message": message
        })
        return True  # Default to "OK"
    
    def reset(self) -> None:
        """Clear call history."""
        self.calls = []
    
    def get_last_call(self) -> Optional[dict]:
        """Get most recent dialog call."""
        return self.calls[-1] if self.calls else None
    
    def get_calls_by_type(self, call_type: str) -> list:
        """Get all calls of specific type (error/info/warning/yesno/okcancel)."""
        return [c for c in self.calls if c["type"] == call_type]


class MockFileDialog:
    """
    Mock implementation of tkinter.filedialog for testing.
    
    Returns predetermined paths without showing file picker.
    """
    
    def __init__(self, default_path: Optional[str] = None):
        """
        Initialize mock file dialog.
        
        Args:
            default_path: Path to return from dialogs (None = user cancelled)
        """
        self.default_path = default_path
        self.calls = []
    
    def askopenfilename(self, **kwargs) -> str:
        """Mock askopenfilename - returns default_path."""
        self.calls.append({
            "type": "open",
            "kwargs": kwargs
        })
        return self.default_path or ""
    
    def asksaveasfilename(self, **kwargs) -> str:
        """Mock asksaveasfilename - returns default_path."""
        self.calls.append({
            "type": "save",
            "kwargs": kwargs
        })
        return self.default_path or ""
    
    def askdirectory(self, **kwargs) -> str:
        """Mock askdirectory - returns default_path."""
        self.calls.append({
            "type": "directory",
            "kwargs": kwargs
        })
        return self.default_path or ""
    
    def reset(self) -> None:
        """Clear call history."""
        self.calls = []
