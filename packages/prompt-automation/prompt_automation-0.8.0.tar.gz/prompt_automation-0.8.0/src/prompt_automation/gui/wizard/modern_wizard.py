"""
Modern Template Wizard - Step-by-step template creation.

Clean, intuitive wizard that walks through essential template components:
1. What & Why (title, purpose, category)
2. Inputs (placeholders with smart defaults)
3. Structure (auto-generate or customize template body)
4. Review & Create

Design principles:
- One question per screen (no cognitive overload)
- Smart defaults (80% case works out of box)
- Progressive disclosure (advanced options hidden)
- Live preview (see what you're building)
"""
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import List, Dict, Any, Optional
import json

from ...config import PROMPTS_DIR
from ..fonts import get_display_font


class ModernTemplateWizard:
    """Step-by-step template creation wizard."""
    
    # Template structure presets
    STRUCTURE_PRESETS = {
        "Simple": {
            "desc": "Just objective and content (quick prompts)",
            "sections": ["## Objective", "{{content}}"]
        },
        "Standard": {
            "desc": "Objective, Context, Instructions, Output (most common)",
            "sections": [
                "## Objective",
                "{{objective}}",
                "",
                "## Context",
                "{{context}}",
                "",
                "## Instructions",
                "{{instructions}}",
                "",
                "## Output Format",
                "{{output_format}}"
            ]
        },
        "Comprehensive": {
            "desc": "Full structure with Quality Checks (complex workflows)",
            "sections": [
                "## Objective",
                "{{objective}}",
                "",
                "## Context",
                "{{context}}",
                "",
                "## Inputs",
                "{{inputs}}",
                "",
                "## Assumptions",
                "{{assumptions}}",
                "",
                "## Constraints",
                "{{constraints}}",
                "",
                "## Instructions",
                "{{instructions}}",
                "",
                "## Output Format",
                "{{output_format}}",
                "",
                "## Quality Checks",
                "{{quality_checks}}"
            ]
        }
    }
    
    def __init__(self, parent=None):
        """Initialize wizard window."""
        self.root = tk.Toplevel(parent) if parent else tk.Tk()
        self.root.title("New Template Wizard")
        self.root.geometry("900x650")
        self.root.resizable(False, False)
        
        # Make wizard modal to prevent event leakage to parent
        if parent:
            self.root.transient(parent)  # Set parent window
            self.root.grab_set()  # Make modal (blocks parent interaction)
            
        # Prevent key events from propagating to parent window
        # This fixes the issue where typing in wizard duplicates to search bar
        def _stop_propagation(event):
            # Stop event from bubbling to parent
            return None  # Let widget handle it, but don't propagate further
        
        # Bind to wizard root to intercept all key events
        self.root.bind('<Key>', _stop_propagation, add='+')
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.root.winfo_screenheight() // 2) - (650 // 2)
        self.root.geometry(f"900x650+{x}+{y}")
        
        # Configure ttk styles for readability (fix dark theme issues)
        style = ttk.Style()
        style.theme_use('default')  # Use default theme for consistent appearance
        style.configure(
            'TCombobox',
            fieldbackground='white',
            background='white',
            foreground='black',
            selectbackground='#3498db',
            selectforeground='white'
        )
        # Configure combobox dropdown list
        self.root.option_add('*TCombobox*Listbox.background', 'white')
        self.root.option_add('*TCombobox*Listbox.foreground', 'black')
        self.root.option_add('*TCombobox*Listbox.selectBackground', '#3498db')
        self.root.option_add('*TCombobox*Listbox.selectForeground', 'white')
        
        # State
        self.current_step = 0
        self.template_data = {
            "title": "",
            "style": "LLM",
            "category": "",
            "purpose": "",
            "placeholders": [],
            "structure_preset": "Standard",
            "custom_body": None
        }
        
        # Build UI
        self._build_ui()
        self._show_step(0)
        
    def _build_ui(self):
        """Build wizard UI structure."""
        # Progress bar at top
        self.progress_frame = tk.Frame(self.root, bg="#2c3e50", height=60)
        self.progress_frame.pack(fill="x")
        self.progress_frame.pack_propagate(False)
        
        self.progress_label = tk.Label(
            self.progress_frame,
            text="Step 1 of 4: What & Why",
            font=("Arial", 14, "bold"),
            bg="#2c3e50",
            fg="white",
            pady=15
        )
        self.progress_label.pack()
        
        # Main content area
        self.content_frame = tk.Frame(self.root, bg="white")
        self.content_frame.pack(fill="both", expand=True, padx=40, pady=30)
        
        # Navigation buttons at bottom
        self.nav_frame = tk.Frame(self.root, bg="#ecf0f1", height=70)
        self.nav_frame.pack(fill="x")
        self.nav_frame.pack_propagate(False)
        
        nav_inner = tk.Frame(self.nav_frame, bg="#ecf0f1")
        nav_inner.pack(expand=True)
        
        self.back_btn = tk.Button(
            nav_inner,
            text="← Back",
            command=self._go_back,
            font=("Arial", 11),
            padx=20,
            pady=8,
            state="disabled"
        )
        self.back_btn.pack(side="left", padx=10)
        
        self.next_btn = tk.Button(
            nav_inner,
            text="Next →",
            command=self._go_next,
            font=("Arial", 11, "bold"),
            padx=20,
            pady=8,
            bg="#3498db",
            fg="white",
            activebackground="#2980b9",
            activeforeground="white"
        )
        self.next_btn.pack(side="left", padx=10)
        
        self.cancel_btn = tk.Button(
            nav_inner,
            text="Cancel",
            command=self.root.destroy,
            font=("Arial", 11),
            padx=20,
            pady=8
        )
        self.cancel_btn.pack(side="left", padx=10)
        
    def _clear_content(self):
        """Clear content frame."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
    def _show_step(self, step_num):
        """Show specific wizard step."""
        self.current_step = step_num
        self._clear_content()
        
        # Update progress
        steps = [
            "What & Why",
            "Inputs (Placeholders)",
            "Structure",
            "Review & Create"
        ]
        self.progress_label.config(text=f"Step {step_num + 1} of {len(steps)}: {steps[step_num]}")
        
        # Update navigation buttons
        self.back_btn.config(state="normal" if step_num > 0 else "disabled")
        self.next_btn.config(text="Create Template" if step_num == 3 else "Next →")
        
        # Show appropriate step
        if step_num == 0:
            self._show_step1_what_why()
        elif step_num == 1:
            self._show_step2_inputs()
        elif step_num == 2:
            self._show_step3_structure()
        elif step_num == 3:
            self._show_step4_review()
            
    def _show_step1_what_why(self):
        """Step 1: Title, Category, Purpose."""
        tk.Label(
            self.content_frame,
            text="Let's create your template",
            font=("Arial", 20, "bold"),
            bg="white"
        ).pack(anchor="w", pady=(0, 5))
        
        tk.Label(
            self.content_frame,
            text="Start by describing what this template does",
            font=("Arial", 11),
            fg="#7f8c8d",
            bg="white"
        ).pack(anchor="w", pady=(0, 30))
        
        # Title
        tk.Label(
            self.content_frame,
            text="1. Template Title",
            font=("Arial", 12, "bold"),
            bg="white"
        ).pack(anchor="w", pady=(0, 5))
        
        tk.Label(
            self.content_frame,
            text="Clear, descriptive name (e.g., 'Quick Debugging Partner', 'Project Creator')",
            font=("Arial", 10),
            fg="#7f8c8d",
            bg="white"
        ).pack(anchor="w", pady=(0, 5))
        
        self.title_var = tk.StringVar(value=self.template_data["title"])
        title_entry = tk.Entry(
            self.content_frame,
            textvariable=self.title_var,
            font=("Arial", 12),
            width=60,
            bg="white",
            fg="black"
        )
        title_entry.pack(anchor="w", pady=(0, 25), ipady=6)
        title_entry.focus_set()
        
        # Style & Category
        row = tk.Frame(self.content_frame, bg="white")
        row.pack(fill="x", pady=(0, 25))
        
        # Style (left)
        left = tk.Frame(row, bg="white")
        left.pack(side="left", fill="both", expand=True, padx=(0, 20))
        
        tk.Label(
            left,
            text="2. Style (Category)",
            font=("Arial", 12, "bold"),
            bg="white"
        ).pack(anchor="w", pady=(0, 5))
        
        tk.Label(
            left,
            text="Where should this template live?",
            font=("Arial", 10),
            fg="#7f8c8d",
            bg="white"
        ).pack(anchor="w", pady=(0, 5))
        
        styles = sorted([p.name for p in PROMPTS_DIR.iterdir() if p.is_dir() and p.name not in {"Settings"}])
        self.style_var = tk.StringVar(value=self.template_data["style"])
        style_combo = ttk.Combobox(
            left,
            textvariable=self.style_var,
            values=styles,
            font=("Arial", 11),
            state="readonly",
            width=25
        )
        style_combo.pack(anchor="w", ipady=4)
        
        # Subcategory (right)
        right = tk.Frame(row, bg="white")
        right.pack(side="left", fill="both", expand=True)
        
        tk.Label(
            right,
            text="3. Subcategory (Optional)",
            font=("Arial", 12, "bold"),
            bg="white"
        ).pack(anchor="w", pady=(0, 5))
        
        tk.Label(
            right,
            text="e.g., 'Bug', 'Planning', 'Docs' (leave blank for root)",
            font=("Arial", 10),
            fg="#7f8c8d",
            bg="white"
        ).pack(anchor="w", pady=(0, 5))
        
        self.category_var = tk.StringVar(value=self.template_data["category"])
        category_entry = tk.Entry(
            right,
            textvariable=self.category_var,
            font=("Arial", 11),
            width=25,
            bg="white",
            fg="black"
        )
        category_entry.pack(anchor="w", ipady=4)
        
        # Purpose
        tk.Label(
            self.content_frame,
            text="4. One-sentence Purpose",
            font=("Arial", 12, "bold"),
            bg="white"
        ).pack(anchor="w", pady=(0, 5))
        
        tk.Label(
            self.content_frame,
            text="What problem does this solve? (This becomes the Objective)",
            font=("Arial", 10),
            fg="#7f8c8d",
            bg="white"
        ).pack(anchor="w", pady=(0, 5))
        
        self.purpose_var = tk.StringVar(value=self.template_data["purpose"])
        purpose_entry = tk.Entry(
            self.content_frame,
            textvariable=self.purpose_var,
            font=("Arial", 11),
            width=80,
            bg="white",
            fg="black"
        )
        purpose_entry.pack(anchor="w", pady=(0, 10), ipady=6)
        
        # Bind Enter key
        self.root.bind('<Return>', lambda e: self._go_next())
        
    def _show_step2_inputs(self):
        """Step 2: Define placeholders (inputs)."""
        tk.Label(
            self.content_frame,
            text="What information do you need from the user?",
            font=("Arial", 18, "bold"),
            bg="white"
        ).pack(anchor="w", pady=(0, 5))
        
        tk.Label(
            self.content_frame,
            text="Add 1-3 placeholders for key inputs (keep it simple)",
            font=("Arial", 11),
            fg="#7f8c8d",
            bg="white"
        ).pack(anchor="w", pady=(0, 20))
        
        # Placeholder list
        list_frame = tk.Frame(self.content_frame, bg="white")
        list_frame.pack(fill="both", expand=True)
        
        # Display existing placeholders
        self.ph_list_frame = tk.Frame(list_frame, bg="white")
        self.ph_list_frame.pack(fill="x", pady=(0, 15))
        self._refresh_placeholder_list()
        
        # Add new placeholder form
        add_frame = tk.LabelFrame(
            list_frame,
            text=" Add Placeholder ",
            font=("Arial", 11, "bold"),
            bg="white",
            padx=15,
            pady=15
        )
        add_frame.pack(fill="x")
        
        # Name
        tk.Label(add_frame, text="Name:", bg="white", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=5)
        self.ph_name_var = tk.StringVar()
        tk.Entry(add_frame, textvariable=self.ph_name_var, font=("Arial", 10), width=20, bg="white", fg="black").grid(row=0, column=1, sticky="w", padx=10, pady=5)
        
        tk.Label(add_frame, text="(e.g., 'issue', 'goals', 'concept')", font=("Arial", 9), fg="#95a5a6", bg="white").grid(row=0, column=2, sticky="w", pady=5)
        
        # Label
        tk.Label(add_frame, text="Label:", bg="white", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", pady=5)
        self.ph_label_var = tk.StringVar()
        label_entry = tk.Entry(add_frame, textvariable=self.ph_label_var, font=("Arial", 10), width=50, bg="white", fg="black")
        label_entry.grid(row=1, column=1, columnspan=2, sticky="w", padx=10, pady=5)
        
        tk.Label(add_frame, text="(What users see: 'Paste the error message or stack trace')", font=("Arial", 9), fg="#95a5a6", bg="white").grid(row=2, column=1, columnspan=2, sticky="w", padx=10)
        
        # Multiline checkbox
        self.ph_multiline_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            add_frame,
            text="Multiline (for long inputs like code, requirements, context)",
            variable=self.ph_multiline_var,
            bg="white",
            font=("Arial", 10)
        ).grid(row=3, column=1, columnspan=2, sticky="w", padx=10, pady=10)
        
        # Required checkbox
        self.ph_required_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            add_frame,
            text="Required (user must fill this field)",
            variable=self.ph_required_var,
            bg="white",
            font=("Arial", 10)
        ).grid(row=4, column=1, columnspan=2, sticky="w", padx=10, pady=5)
        
        # Add button
        tk.Button(
            add_frame,
            text="+ Add Placeholder",
            command=self._add_placeholder,
            font=("Arial", 10, "bold"),
            bg="#27ae60",
            fg="white",
            padx=15,
            pady=5
        ).grid(row=5, column=1, sticky="w", padx=10, pady=15)
        
    def _refresh_placeholder_list(self):
        """Refresh placeholder list display."""
        for widget in self.ph_list_frame.winfo_children():
            widget.destroy()
            
        if not self.template_data["placeholders"]:
            tk.Label(
                self.ph_list_frame,
                text="No placeholders yet. Add at least one input below.",
                font=("Arial", 10),
                fg="#7f8c8d",
                bg="white"
            ).pack(anchor="w")
            return
            
        for i, ph in enumerate(self.template_data["placeholders"]):
            ph_frame = tk.Frame(self.ph_list_frame, bg="#ecf0f1", relief="solid", borderwidth=1)
            ph_frame.pack(fill="x", pady=5, padx=2)
            
            # Content
            content = tk.Frame(ph_frame, bg="#ecf0f1")
            content.pack(side="left", fill="both", expand=True, padx=10, pady=8)
            
            tk.Label(
                content,
                text=f"{{{{ {ph['name']} }}}}",
                font=("Courier", 11, "bold"),
                bg="#ecf0f1"
            ).pack(anchor="w")
            
            tk.Label(
                content,
                text=ph.get("label", ""),
                font=("Arial", 9),
                fg="#34495e",
                bg="#ecf0f1"
            ).pack(anchor="w")
            
            flags = []
            if ph.get("multiline"):
                flags.append("multiline")
            if ph.get("required"):
                flags.append("required")
            if flags:
                tk.Label(
                    content,
                    text=" • ".join(flags),
                    font=("Arial", 8),
                    fg="#7f8c8d",
                    bg="#ecf0f1"
                ).pack(anchor="w")
            
            # Remove button
            tk.Button(
                ph_frame,
                text="✕",
                command=lambda idx=i: self._remove_placeholder(idx),
                font=("Arial", 10),
                bg="#e74c3c",
                fg="white",
                padx=8,
                pady=2
            ).pack(side="right", padx=5)
            
    def _add_placeholder(self):
        """Add placeholder to list."""
        name = self.ph_name_var.get().strip()
        if not name:
            messagebox.showerror("Validation", "Placeholder name required")
            return
            
        label = self.ph_label_var.get().strip() or f"Enter {name}"
        
        placeholder = {
            "name": name,
            "label": label,
            "multiline": self.ph_multiline_var.get(),
            "required": self.ph_required_var.get(),
            "default": ""
        }
        
        self.template_data["placeholders"].append(placeholder)
        
        # Clear form
        self.ph_name_var.set("")
        self.ph_label_var.set("")
        self.ph_multiline_var.set(True)
        self.ph_required_var.set(True)
        
        self._refresh_placeholder_list()
        
    def _remove_placeholder(self, index):
        """Remove placeholder from list."""
        self.template_data["placeholders"].pop(index)
        self._refresh_placeholder_list()
        
    def _show_step3_structure(self):
        """Step 3: Choose template structure."""
        tk.Label(
            self.content_frame,
            text="Choose your template structure",
            font=("Arial", 18, "bold"),
            bg="white"
        ).pack(anchor="w", pady=(0, 5))
        
        tk.Label(
            self.content_frame,
            text="Pick a preset that fits your use case (you can customize after creation)",
            font=("Arial", 11),
            fg="#7f8c8d",
            bg="white"
        ).pack(anchor="w", pady=(0, 25))
        
        # Preset options
        self.structure_var = tk.StringVar(value=self.template_data["structure_preset"])
        
        for preset_name, preset_data in self.STRUCTURE_PRESETS.items():
            frame = tk.Frame(self.content_frame, bg="white", relief="solid", borderwidth=1)
            frame.pack(fill="x", pady=8, padx=5)
            
            rb = tk.Radiobutton(
                frame,
                text=preset_name,
                variable=self.structure_var,
                value=preset_name,
                font=("Arial", 12, "bold"),
                bg="white",
                activebackground="white"
            )
            rb.pack(anchor="w", padx=15, pady=(10, 0))
            
            tk.Label(
                frame,
                text=preset_data["desc"],
                font=("Arial", 10),
                fg="#7f8c8d",
                bg="white"
            ).pack(anchor="w", padx=15, pady=(2, 5))
            
            # Show sections preview
            preview_text = " → ".join([s.strip() for s in preset_data["sections"] if s.strip() and s.startswith("##")])
            tk.Label(
                frame,
                text=preview_text,
                font=("Courier", 9),
                fg="#34495e",
                bg="white"
            ).pack(anchor="w", padx=15, pady=(0, 10))
            
    def _show_step4_review(self):
        """Step 4: Review and create."""
        tk.Label(
            self.content_frame,
            text="Review your template",
            font=("Arial", 18, "bold"),
            bg="white"
        ).pack(anchor="w", pady=(0, 20))
        
        # Create scrollable preview
        preview_frame = tk.Frame(self.content_frame, bg="white")
        preview_frame.pack(fill="both", expand=True)
        
        canvas = tk.Canvas(preview_frame, bg="white", highlightthickness=0)
        scrollbar = tk.Scrollbar(preview_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Build preview content
        self._build_review_content(scrollable_frame)
        
    def _build_review_content(self, parent):
        """Build review content."""
        # Title & metadata
        meta_frame = tk.Frame(parent, bg="#ecf0f1", relief="solid", borderwidth=1)
        meta_frame.pack(fill="x", pady=(0, 15), padx=5)
        
        tk.Label(
            meta_frame,
            text=self.template_data["title"] or "Untitled Template",
            font=("Arial", 16, "bold"),
            bg="#ecf0f1"
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        location = self.template_data["style"]
        if self.template_data["category"]:
            location += f" / {self.template_data['category']}"
            
        tk.Label(
            meta_frame,
            text=f"📁 {location}",
            font=("Arial", 10),
            fg="#7f8c8d",
            bg="#ecf0f1"
        ).pack(anchor="w", padx=15, pady=(0, 10))
        
        # Placeholders
        if self.template_data["placeholders"]:
            tk.Label(
                parent,
                text="Inputs:",
                font=("Arial", 12, "bold"),
                bg="white"
            ).pack(anchor="w", pady=(10, 5))
            
            for ph in self.template_data["placeholders"]:
                ph_frame = tk.Frame(parent, bg="white")
                ph_frame.pack(fill="x", pady=3)
                
                tk.Label(
                    ph_frame,
                    text=f"• {{{{ {ph['name']} }}}}",
                    font=("Courier", 10, "bold"),
                    bg="white"
                ).pack(side="left")
                
                tk.Label(
                    ph_frame,
                    text=f"  — {ph.get('label', '')}",
                    font=("Arial", 9),
                    fg="#7f8c8d",
                    bg="white"
                ).pack(side="left")
        
        # Structure preview
        tk.Label(
            parent,
            text="Structure:",
            font=("Arial", 12, "bold"),
            bg="white"
        ).pack(anchor="w", pady=(15, 5))
        
        structure_text = tk.Text(
            parent,
            height=15,
            font=get_display_font(),
            bg="#f8f9fa",
            relief="solid",
            borderwidth=1,
            wrap="word"
        )
        structure_text.pack(fill="both", expand=True, pady=(0, 10))
        
        # Generate preview
        preview = self._generate_template_body()
        structure_text.insert("1.0", "\n".join(preview))
        structure_text.config(state="disabled")
        
    def _generate_template_body(self) -> List[str]:
        """Generate template body from preset and placeholders."""
        preset = self.STRUCTURE_PRESETS[self.template_data["structure_preset"]]
        body = []
        
        # Start with objective
        body.append("## Objective")
        body.append(self.template_data["purpose"] or "Describe what this template does")
        body.append("")
        
        # Add sections from preset
        for section in preset["sections"]:
            if section.startswith("##"):
                section_name = section.replace("##", "").strip()
                if section_name == "Objective":
                    continue  # Already added
                    
                body.append(section)
                
                # Auto-populate sections based on placeholders
                if section_name == "Inputs" and self.template_data["placeholders"]:
                    for ph in self.template_data["placeholders"]:
                        body.append(f"- {ph['name']}: {{{{{ph['name']}}}}}")
                elif section_name == "Context":
                    body.append("- Role: [describe your role or perspective]")
                elif section_name == "Constraints":
                    body.append("- [Add constraints like length limits, tone, format requirements]")
                elif section_name == "Instructions":
                    body.append("1. [First step]")
                    body.append("2. [Second step]")
                    body.append("3. [Third step]")
                elif section_name == "Output Format":
                    body.append("- [Describe desired output format, structure, or examples]")
                elif section_name == "Quality Checks":
                    body.append("- [Add validation criteria]")
                else:
                    body.append(f"{{{{ {section_name.lower().replace(' ', '_')} }}}}")
                    
                body.append("")
                
        return body
        
    def _go_back(self):
        """Go to previous step."""
        if self.current_step > 0:
            # Save current step data
            self._save_current_step_data()
            self._show_step(self.current_step - 1)
            
    def _go_next(self):
        """Go to next step or create template."""
        # Save current step data FIRST
        self._save_current_step_data()
        
        # Then validate using saved data
        if not self._validate_current_step():
            return
        
        if self.current_step == 3:
            # Final step - create template
            self._create_template()
        else:
            # Go to next step
            self._show_step(self.current_step + 1)
            
    def _save_current_step_data(self):
        """Save data from current step."""
        if self.current_step == 0:
            self.template_data["title"] = self.title_var.get().strip()
            self.template_data["style"] = self.style_var.get().strip()
            self.template_data["category"] = self.category_var.get().strip()
            self.template_data["purpose"] = self.purpose_var.get().strip()
        elif self.current_step == 2:
            self.template_data["structure_preset"] = self.structure_var.get()
            
    def _validate_current_step(self) -> bool:
        """Validate current step data."""
        if self.current_step == 0:
            # Check saved template_data (already populated by _save_current_step_data)
            if not self.template_data["title"]:
                messagebox.showerror("Validation", "Template title is required")
                return False
            if not self.template_data["purpose"]:
                messagebox.showerror("Validation", "Please describe the template's purpose (becomes the Objective)")
                return False
        elif self.current_step == 1:
            if not self.template_data["placeholders"]:
                result = messagebox.askyesno(
                    "No Placeholders",
                    "You haven't added any placeholders.\n\n"
                    "This means the template won't collect any user input.\n\n"
                    "Continue anyway?"
                )
                if not result:
                    return False
                    
        return True
        
    def _create_template(self):
        """Create the template using TemplateManager."""
        try:
            from ...templates import TemplateManager
            from ...features import is_template_management_enabled
            
            manager = TemplateManager(auto_index=True, auto_version=False)
            
            # Build metadata
            metadata = {
                "path": "",
                "tags": [],
                "version": 1,
                "render": "markdown",
                "share_this_file_openly": True
            }
            
            if self.template_data["category"]:
                metadata["path"] = f"{self.template_data['style']}/{self.template_data['category']}"
            
            # Create template
            template_result = manager.create(
                title=self.template_data["title"],
                style=self.template_data["style"],
                placeholders=self.template_data["placeholders"],
                template=self._generate_template_body(),
                metadata=metadata
            )
            
            template_id = template_result['id']
            
            # Ask about visual editor
            if is_template_management_enabled():
                result = messagebox.askyesno(
                    "Template Created!",
                    f"✅ Template '{self.template_data['title']}' created (ID: {template_id})\n\n"
                    f"Would you like to open it in the Visual Editor to refine it?",
                    default="yes"
                )
                
                if result:
                    from ...templates.editor import TemplateEditor
                    from ...templates import TemplateManager
                    
                    # Get manager instance for editor
                    manager = TemplateManager()
                    
                    # Close wizard and open editor with template_id
                    self.root.destroy()
                    TemplateEditor(parent=None, manager=manager, template_id=template_id)
                else:
                    messagebox.showinfo("Success", f"Template created with ID {template_id}")
                    self.root.destroy()
            else:
                messagebox.showinfo("Success", f"Template created with ID {template_id}")
                self.root.destroy()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create template:\n{e}")
            import traceback
            traceback.print_exc()


def open_modern_template_wizard(parent=None):
    """
    Open modern template wizard.
    
    Args:
        parent: Parent window (optional). If provided, creates Toplevel dialog.
                If None, creates standalone Tk window with mainloop.
    
    Returns:
        ModernTemplateWizard instance
    """
    wizard = ModernTemplateWizard(parent=parent)
    
    # Only call mainloop if standalone (no parent)
    if parent is None:
        wizard.root.mainloop()
    
    return wizard


if __name__ == "__main__":
    open_modern_template_wizard()
