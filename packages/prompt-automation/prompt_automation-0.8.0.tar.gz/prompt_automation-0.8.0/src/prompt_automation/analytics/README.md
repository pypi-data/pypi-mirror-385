# Analytics Module

This module provides comprehensive usage analytics and telemetry for prompt-automation.

## Features

- **Event Logging**: Track templates, LLM calls, MCP operations, errors, and resource usage
- **Privacy Controls**: SHA256 hashing, prompt preview, stack trace sanitization, opt-out support
- **Local Storage**: SQLite database with WAL mode, auto-rotation at 100MB, 30-day retention
- **Queries**: Top templates, cache hit rate, errors, resource trends, latency percentiles
- **Self-Instrumentation Exclusion**: Analytics doesn't track itself (prevents recursion)

## Quick Start

```python
from prompt_automation.analytics import Analytics

# Create analytics instance
analytics = Analytics()

# Log events
analytics.log_template_render(13008, "Project Creator", 125, False)
analytics.log_llm_call("prompt", "qwen-7b", 1250, 100, 200)
analytics.log_mcp_call("obsidian_search", 350, True, "success")

# Query data
top_templates = analytics.get_top_templates(limit=10)
cache_rate = analytics.get_cache_hit_rate(hours=24)
errors = analytics.get_recent_errors(limit=100)
```

## Opt-Out

Analytics is **enabled by default** (opt-out model). To disable:

```bash
export PA_ANALYTICS_ENABLED=false
```

Or in Python:
```python
import os
os.environ["PA_ANALYTICS_ENABLED"] = "false"
```

## Privacy

All analytics data is privacy-aware:

- **Prompts**: Hashed with SHA256, only first 50 chars stored as preview
- **Variables**: Hashed before storage
- **Stack traces**: User paths sanitized
- **No PII**: No personally identifiable information stored

## Database

- **Location**: `~/.prompt-automation/analytics.db`
- **Max size**: 100MB (configurable)
- **Rotation**: Automatic at 110% of max size
- **Backups**: Compressed (gzip) in `~/.prompt-automation/analytics-backups/`
- **Retention**: 30 days of data

## API Reference

### Analytics Class

```python
Analytics(db_path=None, max_size_mb=100)
```

#### Event Logging Methods

- `log_template_render(template_id, template_title, duration_ms, cache_hit, variables=None)`
- `log_llm_call(prompt, model, duration_ms, tokens_input, tokens_output, device=None, cache_hit=False)`
- `log_mcp_call(tool, duration_ms, cache_hit, status)`
- `log_error(error, context=None)`
- `log_resource_usage(cpu_percent, ram_used_mb, ram_percent, gpu_available=False, ...)`

#### Query Methods

- `get_top_templates(limit=10, hours=24)` → List[Dict]
- `get_cache_hit_rate(hours=24)` → float (0.0-1.0)
- `get_recent_errors(limit=100, hours=24)` → List[Dict]
- `get_resource_usage(hours=1)` → List[Dict]
- `get_latency_percentiles(event_type="llm_call", hours=24)` → Dict[str, float]
- `get_event_count_by_type(hours=24)` → Dict[str, int]

#### Utility Methods

- `is_enabled()` → bool
- `clear_all_data()` → None
- `export_data()` → Dict
- `close()` → None

## Performance

- **Write latency**: <5ms (batched, async)
- **Query latency**: <10ms (indexed)
- **CPU overhead**: <1%
- **DB size growth**: ~1MB/1000 events

## Testing

Run all analytics tests:

```bash
pytest tests/analytics/ -v
```

Expected: 40 tests passing

## Demo

See `scripts/demo_analytics.py` for a comprehensive demonstration of all features.

## Architecture

The module consists of:

- `database.py`: SQLite interface with WAL mode and rotation
- `logger.py`: Event logging with batching and self-instrumentation exclusion
- `privacy.py`: Hashing, sanitization, and opt-out controls
- `queries.py`: Common queries and reporting
- `__init__.py`: Main orchestrator

## Self-Instrumentation Exclusion

Analytics operations are **not tracked** to prevent recursion and noise:

- Event types starting with `analytics_`
- Operations from module `prompt_automation.analytics`
- This ensures analytics observes the application, not itself

## Next Steps

To integrate analytics into the application:

1. Add analytics calls to template rendering
2. Add analytics calls to LLM execution
3. Add analytics calls to MCP operations
4. Add resource monitoring daemon
5. Create CLI dashboard (see `analytics_feat_02.md`)

## Related Files

- `docs/agentic_feature_implementation/21_usage_analytics_telemetry/feature_spec.md`
- `docs/agentic_feature_implementation/21_usage_analytics_telemetry/implementation_summary.md`
- `tests/analytics/` - Test suite
- `scripts/demo_analytics.py` - Demo script
