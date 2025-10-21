"""Pydantic models for configuration management.

This module defines type-safe configuration models using Pydantic.
All configuration values are validated at load time, catching errors
before they reach runtime.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, Tuple


class LLMConfig(BaseModel):
    """LLM (Language Model) configuration."""
    
    enabled: bool = True
    host: str = "127.0.0.1"
    port: int = Field(8080, ge=1024, le=65535)
    timeout_s: int = Field(30, gt=0)
    max_tokens: int = Field(8192, gt=0)
    gpu_layers: int = Field(0, ge=0)
    
    @field_validator('host')
    @classmethod
    def validate_host(cls, v: str) -> str:
        """Validate host is not empty."""
        if not v or v.isspace():
            raise ValueError("Host cannot be empty")
        return v


class MCPConfig(BaseModel):
    """MCP (Model Context Protocol) configuration."""
    
    enabled: bool = True
    vault_path: Optional[str] = None
    server_path: str = "/usr/local/bin/mcp-obsidian"


class CacheConfig(BaseModel):
    """Cache configuration."""
    
    enabled: bool = False
    memory_mb: int = Field(256, gt=0)
    disk_mb: int = Field(100, gt=0)
    ttl_seconds: int = Field(3600, gt=0)


class PerformanceConfig(BaseModel):
    """Performance and resource management configuration."""
    
    profile: str = "standard"
    async_llm: bool = True
    max_workers: int = Field(2, gt=0)
    batch_size: int = Field(1, gt=0)


class AnalyticsConfig(BaseModel):
    """Usage analytics and telemetry configuration."""
    
    enabled: bool = False
    retention_days: int = Field(90, gt=0)
    export_to_cloud: bool = False


class GUIConfig(BaseModel):
    """GUI settings configuration."""
    
    theme: str = "system"
    window_size: Tuple[int, int] = (1000, 700)
    last_folder: Optional[str] = None


class TemplatesConfig(BaseModel):
    """Template management configuration."""
    
    search_paths: list[str] = Field(default_factory=lambda: ["~/.prompt-automation/prompts"])
    auto_reload: bool = True


class EspansoConfig(BaseModel):
    """Espanso integration configuration."""
    
    package_dir: str = "~/.config/espanso/match"
    auto_sync: bool = False


class FeaturesConfig(BaseModel):
    """Feature flags configuration."""
    
    mcp_integration: bool = True
    llm_generation: bool = True
    espanso_sync: bool = False
    template_management: bool = True
    command_palette: bool = True


class Config(BaseModel):
    """Root configuration model.
    
    This is the top-level configuration that contains all subsections.
    All fields have sensible defaults, making the config optional.
    """
    
    version: int = 3
    profile: str = "standard"
    
    llm: LLMConfig = Field(default_factory=LLMConfig)
    mcp: MCPConfig = Field(default_factory=MCPConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)
    analytics: AnalyticsConfig = Field(default_factory=AnalyticsConfig)
    gui: GUIConfig = Field(default_factory=GUIConfig)
    templates: TemplatesConfig = Field(default_factory=TemplatesConfig)
    espanso: EspansoConfig = Field(default_factory=EspansoConfig)
    features: FeaturesConfig = Field(default_factory=FeaturesConfig)
    
    model_config = ConfigDict(validate_assignment=True)
