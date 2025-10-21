"""Knowledge base for pre-answered feature implementation questions.

This module provides access to default answers for common questions that arise
during feature implementation (architecture, testing, GUI, rollout patterns).
Reduces human interruptions during Phase 1 (Pre-Flight) by providing
pre-configured answers with feature-specific override support.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

KB_FILE = Path(__file__).parent / "feature_qa.json"


def load_knowledge_base() -> Dict[str, Any]:
    """
    Load knowledge base from JSON file.
    
    Returns:
        Dict with default_answers and feature_specific_overrides.
        Returns empty structure on error (missing file, corrupt JSON, invalid schema).
        
    Example:
        >>> kb = load_knowledge_base()
        >>> kb["default_answers"]["architecture"]["max_loc_per_file"]
        400
    """
    try:
        if not KB_FILE.exists():
            logger.warning(f"Knowledge base not found: {KB_FILE}")
            return {"default_answers": {}, "feature_specific_overrides": {}}
        
        with open(KB_FILE) as f:
            data = json.load(f)
        
        # Validate schema
        if not _validate_kb_schema(data):
            logger.error("Knowledge base schema invalid")
            return {"default_answers": {}, "feature_specific_overrides": {}}
        
        logger.debug(f"Loaded knowledge base: {len(data['default_answers'])} categories")
        return data
        
    except json.JSONDecodeError as e:
        logger.error(f"Knowledge base JSON invalid: {e}")
        return {"default_answers": {}, "feature_specific_overrides": {}}
    except Exception as e:
        logger.error(f"Failed to load knowledge base: {e}")
        return {"default_answers": {}, "feature_specific_overrides": {}}


def _validate_kb_schema(data: Dict[str, Any]) -> bool:
    """
    Validate knowledge base has required structure.
    
    Args:
        data: Parsed JSON data
        
    Returns:
        True if schema valid, False otherwise
    """
    required_fields = ["version", "default_answers"]
    if not all(field in data for field in required_fields):
        return False
    
    # Check version compatibility
    if data["version"] != "1.0":
        logger.warning(f"Unknown KB version: {data['version']}")
    
    return True


def get_default_answer(
    category: str,
    key: str,
    feature_id: Optional[str] = None
) -> Any:
    """
    Get answer from knowledge base with feature-specific override support.
    
    Args:
        category: Category (architecture, testing, gui, rollout, etc.)
        key: Question key within category
        feature_id: Optional feature ID for override lookup
        
    Returns:
        Answer value or None if not found
        
    Example:
        >>> get_default_answer("testing", "framework")
        'pytest'
        >>> get_default_answer("architecture", "max_files", feature_id="workspace_context_gatherer")
        20
    """
    kb = load_knowledge_base()
    
    # Check feature-specific override first
    if feature_id and feature_id in kb.get("feature_specific_overrides", {}):
        if key in kb["feature_specific_overrides"][feature_id]:
            return kb["feature_specific_overrides"][feature_id][key]
    
    # Fall back to default answer
    return kb.get("default_answers", {}).get(category, {}).get(key)


def get_all_defaults(
    category: str,
    feature_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get all defaults for a category with feature overrides applied.
    
    Args:
        category: Category name
        feature_id: Optional feature ID for overrides
        
    Returns:
        Dict of key-value pairs with overrides applied
        
    Example:
        >>> defaults = get_all_defaults("architecture", feature_id="meta_prompt")
        >>> defaults["max_loc_per_file"]
        400
        >>> defaults["model_endpoint"]
        'http://127.0.0.1:8080'
    """
    kb = load_knowledge_base()
    defaults = kb.get("default_answers", {}).get(category, {}).copy()
    
    # Apply feature-specific overrides
    if feature_id and feature_id in kb.get("feature_specific_overrides", {}):
        overrides = kb["feature_specific_overrides"][feature_id]
        defaults.update(overrides)
    
    return defaults
