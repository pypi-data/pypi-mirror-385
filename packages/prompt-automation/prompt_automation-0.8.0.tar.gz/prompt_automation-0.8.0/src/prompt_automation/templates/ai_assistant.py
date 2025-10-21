"""
AIAssistant - Lightweight text analysis for template creation.

Provides simple placeholder extraction and structure inference
without requiring full LLM or MCP integration.
"""
import re
from typing import List, Dict, Any


class AIAssistant:
    """Lightweight AI assistant for template creation."""
    
    @staticmethod
    def extract_placeholders(text: str) -> List[Dict[str, str]]:
        """
        Extract {{placeholders}} from text.
        
        Args:
            text: Text containing {{placeholder}} markers
        
        Returns:
            List of placeholder dicts with 'name' and 'label'
        """
        # Pattern matches {{word}}
        pattern = r'\{\{(\w+)\}\}'
        matches = re.findall(pattern, text)
        
        # Remove duplicates while preserving order
        seen = set()
        placeholders = []
        for name in matches:
            if name not in seen:
                seen.add(name)
                # Generate label from name (replace underscores, title case)
                label = name.replace("_", " ").title()
                placeholders.append({
                    "name": name,
                    "label": label
                })
        
        return placeholders
    
    @staticmethod
    def infer_structure(text: str) -> Dict[str, Any]:
        """
        Infer template structure from free-form text.
        
        Looks for patterns like:
        Title: ...
        Description: ...
        Content: ...
        
        Args:
            text: Free-form text with potential structure
        
        Returns:
            Dict with inferred fields
        """
        lines = text.strip().split("\n")
        structure = {}
        
        content_lines = []
        in_content = False
        
        for line in lines:
            if line.startswith("Title:"):
                structure["title"] = line.replace("Title:", "").strip()
            elif line.startswith("Description:"):
                structure["description"] = line.replace("Description:", "").strip()
            elif line.startswith("Content:"):
                in_content = True
            elif in_content:
                content_lines.append(line)
        
        if content_lines:
            structure["content"] = "\n".join(content_lines)
        
        return structure
