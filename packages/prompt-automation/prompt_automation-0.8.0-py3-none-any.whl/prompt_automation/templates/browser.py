"""
TemplateBrowser - Main GUI window for template management.

Provides:
- Template grid with search/filter
- Folder tree navigation
- Preview panel
- Action buttons (New, Edit, Delete)
"""
import tkinter as tk
from tkinter import ttk
from typing import Optional


class TemplateBrowser(tk.Toplevel):
    """
    Template Browser window.
    
    Main window for browsing, searching, and managing templates.
    Displays templates in a grid with search, folder navigation,
    and preview panel.
    
    Args:
        parent: Parent tkinter window (optional)
        manager: TemplateManager instance (optional, will create if None)
    """
    
    def __init__(self, parent: Optional[tk.Tk] = None, manager=None):
        """Initialize TemplateBrowser window."""
        super().__init__(parent)
        
        self.title("Template Browser")
        self.geometry("1000x700")
        
        # Store manager
        if manager is None:
            from . import TemplateManager
            self.manager = TemplateManager()
        else:
            self.manager = manager
        
        # Variables
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search_changed)
        
        # Build UI
        self._build_ui()
        
        # Load templates
        self._load_templates()
    
    def _build_ui(self):
        """Build browser UI components."""
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Search bar at top
        self._build_search_bar(main_frame)
        
        # Toolbar with action buttons
        self._build_toolbar(main_frame)
        
        # Content area (grid + details)
        self._build_content_area(main_frame)
        
        # Status bar at bottom
        self._build_status_bar(main_frame)
    
    def _build_search_bar(self, parent):
        """Build search bar."""
        search_frame = ttk.Frame(parent)
        search_frame.pack(fill="x", pady=(0, 10))
        
        # Search label
        ttk.Label(search_frame, text="Search:").pack(side="left", padx=(0, 5))
        
        # Search entry
        search_entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            width=50
        )
        search_entry.pack(side="left", fill="x", expand=True)
        
        # Search hint
        ttk.Label(
            search_frame,
            text="(search by title, description, or tags)",
            foreground="gray"
        ).pack(side="left", padx=(10, 0))
    
    def _build_toolbar(self, parent):
        """Build toolbar with action buttons."""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill="x", pady=(0, 10))
        
        # Action buttons
        ttk.Button(
            toolbar,
            text="New Template",
            command=self._on_new_template
        ).pack(side="left", padx=(0, 5))
        
        ttk.Button(
            toolbar,
            text="Edit",
            command=self._on_edit_template
        ).pack(side="left", padx=(0, 5))
        
        ttk.Button(
            toolbar,
            text="Delete",
            command=self._on_delete_template
        ).pack(side="left", padx=(0, 5))
        
        # Separator
        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=10)
        
        # Import/Export
        ttk.Button(
            toolbar,
            text="Import",
            command=self._on_import
        ).pack(side="left", padx=(0, 5))
        
        ttk.Button(
            toolbar,
            text="Export",
            command=self._on_export
        ).pack(side="left")
    
    def _build_content_area(self, parent):
        """Build main content area (grid + details)."""
        content_frame = ttk.Frame(parent)
        content_frame.pack(fill="both", expand=True)
        
        # Template grid (Treeview)
        self._build_grid(content_frame)
    
    def _build_grid(self, parent):
        """Build template grid."""
        grid_frame = ttk.Frame(parent)
        grid_frame.pack(fill="both", expand=True)
        
        # Treeview with columns
        columns = ("id", "title", "style", "placeholders")
        self.grid_widget = ttk.Treeview(
            grid_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )
        
        # Column headings
        self.grid_widget.heading("id", text="ID")
        self.grid_widget.heading("title", text="Title")
        self.grid_widget.heading("style", text="Style")
        self.grid_widget.heading("placeholders", text="Placeholders")
        
        # Column widths
        self.grid_widget.column("id", width=80, anchor="center")
        self.grid_widget.column("title", width=300)
        self.grid_widget.column("style", width=100, anchor="center")
        self.grid_widget.column("placeholders", width=200)
        
        # Scrollbars
        vsb = ttk.Scrollbar(grid_frame, orient="vertical", command=self.grid_widget.yview)
        hsb = ttk.Scrollbar(grid_frame, orient="horizontal", command=self.grid_widget.xview)
        self.grid_widget.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout
        self.grid_widget.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        grid_frame.grid_rowconfigure(0, weight=1)
        grid_frame.grid_columnconfigure(0, weight=1)
        
        # Bind selection event
        self.grid_widget.bind("<<TreeviewSelect>>", self._on_template_selected)
    
    def _build_status_bar(self, parent):
        """Build status bar."""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill="x", pady=(10, 0))
        
        self.status_label = ttk.Label(
            status_frame,
            text="Ready",
            relief="sunken",
            anchor="w"
        )
        self.status_label.pack(fill="x")
    
    def _load_templates(self):
        """Load templates from manager into grid."""
        # Clear existing items
        for item in self.grid_widget.get_children():
            self.grid_widget.delete(item)
        
        # Load templates
        templates = self.manager.list_all()
        
        # Add to grid
        for template in templates:
            # Format placeholders
            placeholders_text = ", ".join(
                p.get("name", "") for p in template.get("placeholders", [])
            )
            
            self.grid_widget.insert(
                "",
                "end",
                values=(
                    template["id"],
                    template["title"],
                    template["style"],
                    placeholders_text
                )
            )
        
        # Update status
        self._update_status(f"Loaded {len(templates)} templates")
    
    def _on_search_changed(self, *args):
        """Handle search text change."""
        query = self.search_var.get().strip()
        
        if not query:
            # No search query - show all templates
            self._load_templates()
            return
        
        # Filter templates by search query
        self._filter_templates(query)
    
    def _filter_templates(self, query: str):
        """Filter templates based on search query."""
        # Clear grid
        for item in self.grid_widget.get_children():
            self.grid_widget.delete(item)
        
        # Get all templates
        templates = self.manager.list_all()
        
        # Simple text matching (TODO: use SearchEngine for FTS5)
        query_lower = query.lower()
        filtered = [
            t for t in templates
            if query_lower in t["title"].lower()
            or query_lower in t.get("style", "").lower()
        ]
        
        # Add filtered results to grid
        for template in filtered:
            placeholders_text = ", ".join(
                p.get("name", "") for p in template.get("placeholders", [])
            )
            
            self.grid_widget.insert(
                "",
                "end",
                values=(
                    template["id"],
                    template["title"],
                    template["style"],
                    placeholders_text
                )
            )
        
        # Update status
        self._update_status(f"Found {len(filtered)} templates matching '{query}'")
    
    def _update_status(self, message: str):
        """Update status bar message."""
        self.status_label.config(text=message)
    
    def _on_template_selected(self, event):
        """Handle template selection in grid."""
        selection = self.grid_widget.selection()
        if not selection:
            return
        
        # Get selected template ID
        item = self.grid_widget.item(selection[0])
        template_id = item["values"][0]
        
        # Update status
        self._update_status(f"Selected template {template_id}")
    
    # Action handlers (stubs for now)
    def _on_new_template(self):
        """Handle New Template button."""
        self._update_status("New Template (not yet implemented)")
    
    def _on_edit_template(self):
        """Handle Edit button."""
        selection = self.grid_widget.selection()
        if not selection:
            self._update_status("No template selected")
            return
        
        item = self.grid_widget.item(selection[0])
        template_id = item["values"][0]
        self._update_status(f"Edit template {template_id} (not yet implemented)")
    
    def _on_delete_template(self):
        """Handle Delete button."""
        selection = self.grid_widget.selection()
        if not selection:
            self._update_status("No template selected")
            return
        
        item = self.grid_widget.item(selection[0])
        template_id = item["values"][0]
        self._update_status(f"Delete template {template_id} (not yet implemented)")
    
    def _on_import(self):
        """Handle Import button."""
        self._update_status("Import (not yet implemented)")
    
    def _on_export(self):
        """Handle Export button."""
        self._update_status("Export (not yet implemented)")
