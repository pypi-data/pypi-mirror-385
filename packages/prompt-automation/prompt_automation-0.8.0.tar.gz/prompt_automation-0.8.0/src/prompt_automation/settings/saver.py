"""Configuration saver with atomic writes.

Ensures config files are never corrupted by using:
- Atomic writes (temp file → rename)
- Backup creation before overwrite
- Proper file permissions (user-only)
"""

import json
import shutil
from pathlib import Path

from .models import Config


class Saver:
    """Save configuration atomically to prevent corruption."""
    
    def __init__(self, config_path: Path):
        """Initialize saver with config file path.
        
        Args:
            config_path: Path to config.json file
        """
        self.config_path = Path(config_path)
    
    def save(self, config: Config) -> None:
        """Save config atomically with backup.
        
        Process:
        1. Write to temp file
        2. Create backup of existing file
        3. Atomic rename (temp → config.json)
        4. Set permissions (user-only: 0o600)
        
        Args:
            config: Config instance to save
            
        Raises:
            IOError: If save fails
        """
        # Ensure directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        temp_path = Path(str(self.config_path) + '.tmp')
        backup_path = Path(str(self.config_path) + '.bak')
        
        try:
            # 1. Write to temp file
            with open(temp_path, 'w') as f:
                json.dump(config.model_dump(), f, indent=2)
            
            # 2. Backup existing config (if exists)
            if self.config_path.exists():
                shutil.copy2(self.config_path, backup_path)
            
            # 3. Atomic rename (use replace for Windows compatibility)
            temp_path.replace(self.config_path)
            
            # 4. Set permissions (user read/write only)
            self.config_path.chmod(0o600)
        
        except Exception as e:
            # Cleanup temp file on error
            if temp_path.exists():
                temp_path.unlink()
            raise IOError(f"Failed to save config: {e}") from e
