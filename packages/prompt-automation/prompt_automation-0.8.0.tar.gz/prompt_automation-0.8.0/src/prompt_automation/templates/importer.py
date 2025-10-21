"""
TemplateImporter - Import/export templates to/from external JSON files.

Provides functionality to import templates from external sources
and export templates for sharing or backup.
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional

from . import TemplateManager
from .validator import TemplateValidator


class TemplateImporter:
    """Import and export templates."""
    
    def __init__(self, manager: TemplateManager):
        """
        Initialize importer.
        
        Args:
            manager: TemplateManager instance
        """
        self.manager = manager
        self.validator = TemplateValidator()
    
    def import_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Import template from JSON file.
        
        Args:
            file_path: Path to JSON file
        
        Returns:
            Imported template data
        
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If JSON is invalid or template is invalid
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Load JSON
        try:
            content = file_path.read_text()
            template = json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")
        
        # Validate template
        if not self.validator.validate(template):
            errors = "\n".join(self.validator.get_errors())
            raise ValueError(f"Invalid template:\n{errors}")
        
        # Create template via manager (unpack dict to kwargs)
        created = self.manager.create(
            title=template["title"],
            style=template["style"],
            placeholders=template.get("placeholders", []),
            template=template["template"],
            metadata=template.get("metadata")
        )
        return created
    
    def export_file(self, template_id: int, file_path: Path) -> None:
        """
        Export template to JSON file.
        
        Args:
            template_id: Template ID to export
            file_path: Destination path
        
        Raises:
            ValueError: If template not found
        """
        template = self.manager.get(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")
        
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write JSON with formatting
        content = json.dumps(template, indent=2)
        file_path.write_text(content)
    
    def import_directory(self, dir_path: Path) -> Dict[str, Any]:
        """
        Import all JSON templates from directory.
        
        Args:
            dir_path: Directory containing JSON files
        
        Returns:
            Dict with 'imported', 'failed', and 'errors' lists
        """
        if not dir_path.is_dir():
            raise ValueError(f"Not a directory: {dir_path}")
        
        results = {
            "imported": [],
            "failed": [],
            "errors": []
        }
        
        for json_file in dir_path.glob("*.json"):
            try:
                template = self.import_file(json_file)
                results["imported"].append({
                    "file": str(json_file),
                    "id": template["id"],
                    "title": template["title"]
                })
            except (FileNotFoundError, ValueError) as e:
                results["failed"].append(str(json_file))
                results["errors"].append(str(e))
        
        return results
    
    def export_directory(self, template_ids: list, dir_path: Path) -> Dict[str, Any]:
        """
        Export multiple templates to directory.
        
        Args:
            template_ids: List of template IDs
            dir_path: Destination directory
        
        Returns:
            Dict with 'exported', 'failed', and 'errors' lists
        """
        dir_path.mkdir(parents=True, exist_ok=True)
        
        results = {
            "exported": [],
            "failed": [],
            "errors": []
        }
        
        for template_id in template_ids:
            try:
                template = self.manager.get(template_id)
                if not template:
                    raise ValueError(f"Template not found: {template_id}")
                
                # Sanitize filename from title
                safe_title = "".join(c for c in template["title"] if c.isalnum() or c in " _-")
                filename = f"{template_id}_{safe_title[:50]}.json"
                file_path = dir_path / filename
                
                self.export_file(template_id, file_path)
                results["exported"].append({
                    "id": template_id,
                    "file": str(file_path)
                })
            except ValueError as e:
                results["failed"].append(template_id)
                results["errors"].append(str(e))
        
        return results
