"""
TemplateValidator - JSON schema validation for template data.

Validates template structure against defined schema to ensure
consistency and catch errors early.
"""
from typing import Dict, Any, List, Optional


class TemplateValidator:
    """Validates template data against schema."""
    
    # JSON schema for template validation
    SCHEMA = {
        "required": ["id", "title", "style", "template"],
        "properties": {
            "id": {"type": "integer", "minimum": 10000},
            "title": {"type": "string", "minLength": 1},
            "style": {"type": "string", "enum": ["LLM", "Copilot", "General", "Code"]},
            "template": {"type": "array", "minItems": 1},
            "placeholders": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["name", "label"],
                    "properties": {
                        "name": {"type": "string"},
                        "label": {"type": "string"}
                    }
                }
            },
            "description": {"type": "string"},
            "metadata": {"type": "object"}
        }
    }
    
    def __init__(self):
        """Initialize validator."""
        self.errors: List[str] = []
    
    def validate(self, template: Dict[str, Any]) -> bool:
        """
        Validate template against schema.
        
        Args:
            template: Template data to validate
        
        Returns:
            True if valid, False otherwise
        """
        self.errors = []
        
        # Check required fields
        for field in self.SCHEMA["required"]:
            if field not in template:
                self.errors.append(f"Missing required field: {field}")
        
        if self.errors:
            return False
        
        # Validate field types
        props = self.SCHEMA["properties"]
        
        # ID validation
        if not isinstance(template["id"], int):
            self.errors.append("Field 'id' must be an integer")
        elif template["id"] < props["id"]["minimum"]:
            self.errors.append(f"Field 'id' must be >= {props['id']['minimum']}")
        
        # Title validation
        if not isinstance(template["title"], str):
            self.errors.append("Field 'title' must be a string")
        elif len(template["title"]) < props["title"]["minLength"]:
            self.errors.append("Field 'title' cannot be empty")
        
        # Style validation
        if not isinstance(template["style"], str):
            self.errors.append("Field 'style' must be a string")
        elif template["style"] not in props["style"]["enum"]:
            valid_styles = ", ".join(props["style"]["enum"])
            self.errors.append(f"Field 'style' must be one of: {valid_styles}")
        
        # Template validation
        if not isinstance(template["template"], list):
            self.errors.append("Field 'template' must be an array")
        elif len(template["template"]) < props["template"]["minItems"]:
            self.errors.append("Field 'template' cannot be empty")
        
        # Optional placeholders validation
        if "placeholders" in template:
            if not isinstance(template["placeholders"], list):
                self.errors.append("Field 'placeholders' must be an array")
            else:
                for i, placeholder in enumerate(template["placeholders"]):
                    if not isinstance(placeholder, dict):
                        self.errors.append(f"Placeholder {i} must be an object")
                        continue
                    
                    if "name" not in placeholder:
                        self.errors.append(f"Placeholder {i} missing 'name'")
                    elif not isinstance(placeholder["name"], str):
                        self.errors.append(f"Placeholder {i} 'name' must be string")
                    
                    if "label" not in placeholder:
                        self.errors.append(f"Placeholder {i} missing 'label'")
                    elif not isinstance(placeholder["label"], str):
                        self.errors.append(f"Placeholder {i} 'label' must be string")
        
        return len(self.errors) == 0
    
    def get_errors(self) -> List[str]:
        """Get validation errors from last validate() call."""
        return self.errors
