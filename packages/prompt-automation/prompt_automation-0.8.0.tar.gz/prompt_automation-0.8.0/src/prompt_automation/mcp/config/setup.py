"""Cross-platform MCP configuration setup wizard."""

import json
import logging
import platform
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Import validation functions for cross-platform safety
try:
    from ...platform_utils import validate_path_accessible, detect_environment
    _HAS_VALIDATION = True
except ImportError:
    # Fallback if validation not available (shouldn't happen in normal operation)
    _HAS_VALIDATION = False


def get_default_registry_path() -> Path:
    """
    Get default MCP registry path.
    
    Uses platform-aware home directory resolution to handle WSL2/Windows correctly.
    
    Returns:
        Path to mcp-registry.json in the appropriate .prompt-automation directory
    """
    try:
        from ...platform_utils import get_app_home
        return get_app_home() / "mcp-registry.json"
    except ImportError:
        # Fallback if platform_utils not available
        return Path.home() / ".prompt-automation" / "mcp-registry.json"


def detect_platform() -> str:
    """
    Detect current platform.
    
    Returns:
        'windows', 'linux', or 'darwin' (Mac)
    """
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    elif system == "darwin":
        return "darwin"
    else:
        return "linux"


def normalize_vault_path(path_str: str, target_platform: Optional[str] = None) -> str:
    """
    Normalize vault path for target platform.
    
    Args:
        path_str: Input path (can be Windows, Linux, or Mac format)
        target_platform: Target platform ('windows', 'linux', 'darwin'), 
                        or None to use current platform
    
    Returns:
        Normalized path string for target platform
    
    Examples:
        >>> normalize_vault_path("C:\\Users\\Name\\Vault", "linux")
        "/mnt/c/Users/Name/Vault"
        
        >>> normalize_vault_path("/home/user/vault", "windows")
        "C:\\\\home\\\\user\\\\vault"  # WSL path conversion
    """
    platform_type = target_platform or detect_platform()
    
    # Convert to Path object for normalization
    try:
        p = Path(path_str)
        
        # If on Windows and path starts with drive letter
        if platform_type == "windows":
            # Ensure Windows-style backslashes
            return str(p).replace("/", "\\")
        else:
            # Linux/Mac: forward slashes
            # If input was Windows path (C:\...), convert to WSL2 format
            if len(path_str) >= 3 and path_str[1] == ":" and path_str[2] in ("/", "\\"):
                drive_letter = path_str[0].lower()
                rest_of_path = path_str[3:].replace("\\", "/")
                return f"/mnt/{drive_letter}/{rest_of_path}"
            else:
                return str(p).replace("\\", "/")
    
    except Exception as e:
        logger.warning(f"Path normalization failed: {e}, using original: {path_str}")
        return path_str


def create_obsidian_provider_config(
    vault_path: str,
    server_command: Optional[list] = None,
    provider_id: str = "obsidian"
) -> Dict[str, Any]:
    """
    Create Obsidian MCP provider configuration.
    
    Args:
        vault_path: Path to Obsidian vault
        server_command: Command to launch MCP server 
                       (default: auto-detect npx or node)
        provider_id: Provider identifier (default: "obsidian")
    
    Returns:
        Provider config dict
    """
    # Normalize vault path for current platform
    normalized_vault = normalize_vault_path(vault_path)
    
    # Default server command (tries npx first, falls back to node)
    if server_command is None:
        # Try to find MCP server installation
        # Priority: npx (global install) > local node_modules > bundled
        server_command = [
            "npx",
            "-y",
            "@modelcontextprotocol/server-obsidian"
        ]
    
    return {
        "id": provider_id,
        "transport": "stdio",
        "command": server_command,
        "consent_required": False,
        "metadata": {
            "vault_path": normalized_vault,
            "platform": detect_platform(),
            "configured_at": platform.node()  # Hostname for tracking
        }
    }


def load_or_create_registry(registry_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load existing registry or create new one.
    
    Args:
        registry_path: Path to registry file (default: ~/.prompt-automation/mcp-registry.json)
    
    Returns:
        Registry dict
    """
    path = registry_path or get_default_registry_path()
    
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception as e:
            logger.warning(f"Failed to load existing registry: {e}, creating new")
    
    # Create new registry
    return {"providers": []}


def add_or_update_provider(
    registry: Dict[str, Any],
    provider_config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Add or update provider in registry.
    
    Args:
        registry: Registry dict
        provider_config: Provider config to add/update
    
    Returns:
        Updated registry
    """
    providers = registry.get("providers", [])
    provider_id = provider_config["id"]
    
    # Find existing provider with same ID
    existing_index = None
    for i, p in enumerate(providers):
        if p.get("id") == provider_id:
            existing_index = i
            break
    
    if existing_index is not None:
        # Update existing
        providers[existing_index] = provider_config
        logger.info(f"Updated existing provider: {provider_id}")
    else:
        # Add new
        providers.append(provider_config)
        logger.info(f"Added new provider: {provider_id}")
    
    registry["providers"] = providers
    return registry


def save_registry(registry: Dict[str, Any], registry_path: Optional[Path] = None) -> Path:
    """
    Save registry to disk.
    
    Args:
        registry: Registry dict
        registry_path: Path to save to (default: ~/.prompt-automation/mcp-registry.json)
    
    Returns:
        Path where registry was saved
        
    Raises:
        RuntimeError: If path validation fails (cross-platform accessibility issue)
    """
    path = registry_path or get_default_registry_path()
    
    # Validate path accessibility before attempting write
    if _HAS_VALIDATION:
        result = validate_path_accessible(path.parent, check_writable=True)
        if not result.success:
            env = detect_environment()
            error_msg = (
                f"Cannot write MCP registry to {path}: {result.error}\n"
                f"Current environment: {env}\n"
                f"Suggestion: {result.message}"
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    # Ensure directory exists
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write with pretty formatting
    path.write_text(json.dumps(registry, indent=2))
    logger.info(f"Saved MCP registry to: {path}")
    
    return path


def setup_obsidian_mcp(
    vault_path: str,
    server_command: Optional[list] = None,
    registry_path: Optional[Path] = None,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Setup Obsidian MCP integration.
    
    Args:
        vault_path: Path to Obsidian vault (any platform format)
        server_command: Custom MCP server command (default: ["prompt-automation", "mcp-server"])
        registry_path: Custom registry path (default: ~/.prompt-automation/mcp-registry.json)
        dry_run: Show what would be configured without saving
        
    Returns:
        {
            "success": bool,
            "registry_path": str,
            "vault_path": str,
            "platform": str,
            "message": str
        }
    """
    import socket
    
    # Detect platform and normalize vault path
    current_platform = detect_platform()
    normalized_vault_path = normalize_vault_path(vault_path, current_platform)
    
    # Default to built-in MCP server (platform-specific command)
    if server_command is None:
        if current_platform == "windows":
            server_command = ["prompt-automation-mcp-server"]
        else:
            # WSL2 or Linux: Try to use Windows executable via PATH
            # (requires Windows PATH in WSL2's PATH environment)
            server_command = ["prompt-automation-mcp-server.exe"]
    
    # Validate vault path exists
    if not Path(normalized_vault_path).exists():
        return {
            "success": False,
            "registry_path": str(registry_path or get_default_registry_path()),
            "vault_path": normalized_vault_path,
            "platform": current_platform,
            "message": f"Vault path does not exist: {normalized_vault_path}"
        }
    
    # Get hostname for metadata
    hostname = socket.gethostname()
    
    # Create provider configuration
    provider = {
        "id": "obsidian",
        "transport": "stdio",
        "command": server_command,
        "consent_required": False,
        "metadata": {
            "vault_path": normalized_vault_path,
            "platform": current_platform,
            "configured_at": hostname
        }
    }
    
    # Create or update registry
    path = registry_path or get_default_registry_path()
    
    # Load existing registry if it exists
    if path.exists():
        try:
            existing_registry = json.loads(path.read_text())
            providers = existing_registry.get("providers", [])
            
            # Update existing obsidian provider or add new one
            updated = False
            for i, p in enumerate(providers):
                if p.get("id") == "obsidian":
                    providers[i] = provider
                    updated = True
                    break
            
            if not updated:
                providers.append(provider)
            
            registry = {"providers": providers}
        except json.JSONDecodeError:
            # If registry is corrupted, start fresh
            registry = {"providers": [provider]}
    else:
        registry = {"providers": [provider]}
    
    if dry_run:
        return {
            "success": True,
            "registry_path": str(path),
            "vault_path": normalized_vault_path,
            "platform": current_platform,
            "message": "Dry run - configuration not saved",
            "registry_preview": registry,
            "provider_id": "obsidian"
        }
    
    # Save registry
    saved_path = save_registry(registry, path)
    
    return {
        "success": True,
        "registry_path": str(path),
        "saved_to": str(saved_path),
        "vault_path": normalized_vault_path,
        "platform": current_platform,
        "message": f"Configuration saved successfully",
        "provider_id": "obsidian"
    }


def validate_obsidian_setup(registry_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Validate Obsidian MCP setup.
    
    Args:
        registry_path: Path to registry file
    
    Returns:
        Validation results dict
    """
    path = registry_path or get_default_registry_path()
    
    results = {
        "registry_exists": path.exists(),
        "registry_path": str(path),
        "providers": [],
        "errors": []
    }
    
    if not path.exists():
        results["errors"].append(f"Registry file not found: {path}")
        return results
    
    try:
        registry = json.loads(path.read_text())
        providers = registry.get("providers", [])
        
        for provider in providers:
            provider_id = provider.get("id", "unknown")
            vault_path = provider.get("metadata", {}).get("vault_path")
            
            validation = {
                "id": provider_id,
                "vault_path": vault_path,
                "vault_exists": False,
                "command": provider.get("command", [])
            }
            
            # Check if vault path exists
            if vault_path:
                try:
                    vault_exists = Path(vault_path).exists()
                    validation["vault_exists"] = vault_exists
                    if not vault_exists:
                        results["errors"].append(
                            f"Vault path does not exist: {vault_path}"
                        )
                except Exception as e:
                    results["errors"].append(
                        f"Failed to check vault path: {e}"
                    )
            
            results["providers"].append(validation)
    
    except Exception as e:
        results["errors"].append(f"Failed to parse registry: {e}")
    
    results["valid"] = len(results["errors"]) == 0
    return results


if __name__ == "__main__":
    # CLI test
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python setup.py <vault_path>")
        sys.exit(1)
    
    vault_path = sys.argv[1]
    result = setup_obsidian_mcp(vault_path, dry_run=True)
    
    print("\n📋 Setup Preview:")
    print(json.dumps(result, indent=2))
    
    print("\n✅ Run without --dry-run to save configuration")
