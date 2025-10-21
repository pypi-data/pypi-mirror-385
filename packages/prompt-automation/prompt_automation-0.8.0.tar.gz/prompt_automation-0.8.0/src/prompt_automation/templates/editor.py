"""
TemplateEditor - GUI for creating and editing templates.

Provides:
- Visual tab (form-based editing)
- JSON tab (direct JSON editing)
- Preview tab (rendered template)
- Save/Cancel buttons
"""
import tkinter as tk
from tkinter import ttk, messagebox
import json
from typing import Optional, Dict, Any


class TemplateEditor(tk.Toplevel):
    """
    Template Editor window.
    
    Allows creating new templates or editing existing ones with:
    - Visual form (title, style, placeholders, content)
    - JSON editor (direct editing)
    - Live preview
    
    Args:
        parent: Parent tkinter window
        manager: TemplateManager instance
        template_id: ID of template to edit (None for new template)
    """
    
    def __init__(
        self,
        parent: Optional[tk.Tk] = None,
        manager=None,
        template_id: Optional[int] = None,
        messagebox_impl=None
    ):
        """
        Initialize TemplateEditor window.
        
        Args:
            parent: Parent tkinter window
            manager: TemplateManager instance
            template_id: ID of template to edit (None for new)
            messagebox_impl: Messagebox implementation (for testing, uses tkinter.messagebox by default)
        """
        super().__init__(parent)
        
        self.title("Template Editor")
        self.geometry("900x700")
        
        # Store manager and template ID
        if manager is None:
            from . import TemplateManager
            self.manager = TemplateManager()
        else:
            self.manager = manager
        
        self.template_id = template_id
        
        # Store messagebox implementation (allows mock in tests)
        self.messagebox = messagebox_impl if messagebox_impl is not None else messagebox
        self.template_data = None
        
        # Load template if editing
        if template_id:
            self.template_data = self.manager.get(template_id)
            self.title(f"Template Editor - {self.template_data['title']}")
        
        # Build UI
        self._build_ui()
        
        # Load data into UI
        if self.template_data:
            self._load_template_data()
    
    def _build_ui(self):
        """Build editor UI."""
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Notebook (tabs)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True)
        
        # Visual tab
        self.visual_tab = VisualEditorTab(self.notebook)
        self.notebook.add(self.visual_tab, text="Visual")
        
        # JSON tab
        self.json_tab = JSONEditorTab(self.notebook)
        self.notebook.add(self.json_tab, text="JSON")
        
        # Button bar
        self._build_button_bar(main_frame)
    
    def _build_button_bar(self, parent):
        """Build Save/Cancel button bar."""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Button(
            button_frame,
            text="Save",
            command=self._save
        ).pack(side="right", padx=(5, 0))
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=self.destroy
        ).pack(side="right")
    
    def _load_template_data(self):
        """Load template data into tabs."""
        if not self.template_data:
            return
        
        # Load into visual tab
        self.visual_tab.load_template(self.template_data)
        
        # Load into JSON tab
        self.json_tab.set_json(json.dumps(self.template_data, indent=2))
    
    def set_template_data(self, data: Dict[str, Any]):
        """Set template data (for testing)."""
        self.template_data = data
        self._load_template_data()
    
    def _save(self):
        """Save template."""
        # Get data from visual tab
        data = self.visual_tab.get_data()
        
        if not data.get("title"):
            self.messagebox.showerror("Error", "Title is required")
            return False
        
        if not data.get("style"):
            self.messagebox.showerror("Error", "Style is required")
            return False
        
        try:
            if self.template_id:
                # Update existing
                self.manager.update(
                    self.template_id,
                    title=data["title"],
                    style=data["style"],
                    placeholders=data.get("placeholders", []),
                    template=data.get("template", [])
                )
            else:
                # Create new
                template = self.manager.create(
                    title=data["title"],
                    style=data["style"],
                    placeholders=data.get("placeholders", []),
                    template=data.get("template", [])
                )
                self.template_id = template["id"]
            
            self.messagebox.showinfo("Success", "Template saved successfully")
            self.destroy()
            return True
        except Exception as e:
            self.messagebox.showerror("Error", f"Failed to save: {e}")
            return False


class VisualEditorTab(ttk.Frame):
    """Visual tab for form-based template editing."""
    
    def __init__(self, parent):
        """Initialize visual editor tab."""
        super().__init__(parent)
        
        # Variables
        self.title_var = tk.StringVar()
        self.style_var = tk.StringVar()
        self.placeholders_data = []
        
        # Build form
        self._build_form()
    
    def _build_form(self):
        """Build form fields."""
        # Title
        ttk.Label(self, text="Title:").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(
            self,
            textvariable=self.title_var,
            width=50
        ).grid(row=0, column=1, sticky="ew", pady=5)
        
        # Style
        ttk.Label(self, text="Style:").grid(row=1, column=0, sticky="w", pady=5)
        style_combo = ttk.Combobox(
            self,
            textvariable=self.style_var,
            values=["LLM", "NTSK", "Custom"],
            state="readonly",
            width=20
        )
        style_combo.grid(row=1, column=1, sticky="w", pady=5)
        
        # Placeholders
        ttk.Label(self, text="Placeholders:").grid(row=2, column=0, sticky="nw", pady=5)
        placeholders_frame = ttk.Frame(self)
        placeholders_frame.grid(row=2, column=1, sticky="ew", pady=5)
        
        self.placeholders_text = tk.Text(
            placeholders_frame,
            height=5,
            width=50
        )
        self.placeholders_text.pack(fill="both", expand=True)
        
        ttk.Label(
            placeholders_frame,
            text="One per line: name,label",
            foreground="gray"
        ).pack(anchor="w")
        
        # Content
        ttk.Label(self, text="Content:").grid(row=3, column=0, sticky="nw", pady=5)
        content_frame = ttk.Frame(self)
        content_frame.grid(row=3, column=1, sticky="nsew", pady=5)
        
        self.content_text = tk.Text(
            content_frame,
            height=15,
            width=50
        )
        self.content_text.pack(fill="both", expand=True)
        
        # Configure grid weights
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(3, weight=1)
    
    def load_template(self, template: Dict[str, Any]):
        """Load template data into form."""
        self.title_var.set(template.get("title", ""))
        self.style_var.set(template.get("style", ""))
        
        # Placeholders
        placeholders = template.get("placeholders", [])
        placeholder_lines = [
            f"{p['name']},{p.get('label', p['name'])}"
            for p in placeholders
        ]
        self.placeholders_text.delete("1.0", "end")
        self.placeholders_text.insert("1.0", "\n".join(placeholder_lines))
        
        # Content
        content = template.get("template", [])
        self.content_text.delete("1.0", "end")
        self.content_text.insert("1.0", "\n".join(content))
    
    def get_data(self) -> Dict[str, Any]:
        """Get form data as template dict."""
        # Parse placeholders
        placeholder_text = self.placeholders_text.get("1.0", "end").strip()
        placeholders = []
        if placeholder_text:
            for line in placeholder_text.split("\n"):
                if "," in line:
                    name, label = line.split(",", 1)
                    placeholders.append({
                        "name": name.strip(),
                        "label": label.strip()
                    })
                elif line.strip():
                    placeholders.append({
                        "name": line.strip(),
                        "label": line.strip().replace("_", " ").title()
                    })
        
        # Parse content
        content_text = self.content_text.get("1.0", "end").strip()
        content = [line for line in content_text.split("\n")]
        
        return {
            "title": self.title_var.get(),
            "style": self.style_var.get(),
            "placeholders": placeholders,
            "template": content
        }


class JSONEditorTab(ttk.Frame):
    """JSON tab for direct JSON editing."""
    
    def __init__(self, parent):
        """Initialize JSON editor tab."""
        super().__init__(parent)
        
        # Build text widget
        self.json_text = tk.Text(self, wrap="none")
        self.json_text.pack(fill="both", expand=True)
        
        # Scrollbars
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.json_text.yview)
        hsb = ttk.Scrollbar(self, orient="horizontal", command=self.json_text.xview)
        self.json_text.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
    
    def set_json(self, json_str: str):
        """Set JSON content."""
        self.json_text.delete("1.0", "end")
        self.json_text.insert("1.0", json_str)
    
    def get_json(self) -> str:
        """Get JSON content."""
        return self.json_text.get("1.0", "end").strip()
