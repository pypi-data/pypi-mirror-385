"""Configuration profiles.

Profiles provide preset configurations for different use cases:
- lightweight: Minimal resource usage, features disabled
- standard: Balanced (default)
- performance: Maximum performance, GPU enabled, high concurrency
"""

PROFILES = {
    "lightweight": {
        "llm": {
            "enabled": False
        },
        "cache": {
            "enabled": False,
            "memory_mb": 64
        },
        "performance": {
            "max_workers": 1,
            "async_llm": False
        },
        "analytics": {
            "enabled": False
        }
    },
    "standard": {
        "llm": {
            "enabled": True,
            "gpu_layers": 0
        },
        "cache": {
            "enabled": True,
            "memory_mb": 256
        },
        "performance": {
            "max_workers": 2,
            "async_llm": True
        },
        "analytics": {
            "enabled": False
        }
    },
    "performance": {
        "llm": {
            "enabled": True,
            "gpu_layers": 32
        },
        "cache": {
            "enabled": True,
            "memory_mb": 512,
            "disk_mb": 200
        },
        "performance": {
            "profile": "performance",
            "max_workers": 4,
            "async_llm": True,
            "batch_size": 4
        },
        "analytics": {
            "enabled": True
        }
    }
}
