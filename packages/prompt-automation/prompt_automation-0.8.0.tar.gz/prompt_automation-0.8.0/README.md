# prompt-automation

`prompt-automation` is a keyboard-driven prompt launcher for teams that rely on shared templates. Press one hotkey to open the selector, fill placeholders with guardrails, and copy a final response.

## Key capabilities
- Single-window workflow that combines template browsing, variable collection, and review.
- New Template Wizard and hierarchical folder support to organize large prompt libraries.
- Snapshot-aware globals plus reminders to keep safety guidance consistent across templates.
- Espanso sync tooling that validates snippets, mirrors files, and restarts the espanso service for you.

## Installation
### Quick install scripts
Use the provided scripts when you want an end-to-end setup that installs dependencies and assigns the default hotkey.

- **Windows**
  ```powershell
  install\install.ps1
  ```
- **macOS / Linux / WSL2**
  ```bash
  bash install/install.sh
  ```

After installation, follow the [MCP Integration Guide](docs/MCP_INTEGRATION.md)
if you plan to exercise the MCP planning stub or a local Qwen deployment.

### pip / pipx packages
Prefer a Python package manager? Install the published package and run the CLI directly.

```bash
pipx install prompt-automation
# or
python -m pip install prompt-automation
```

### Native installers (preview)
Want a packaged executable or `.dmg` instead of running the scripts directly? Use the packaging CLI to orchestrate the builds.

```
python -m pip install -e .[packaging]
python packagers/build_all.py --dry-run  # prints planned commands
python packagers/build_all.py            # builds Windows + macOS artifacts
```

Artifacts are written to `dist/packagers/<os>/...` and the workflow is documented in [docs/PACKAGING.md](docs/PACKAGING.md).

Prefer a guided experience? The in-app wizard under **Options → Packaging → Manual packaging** walks through tests, packaging, tagging, and GitHub release upload. See [docs/MANUAL_PACKAGING.md](docs/MANUAL_PACKAGING.md) for screenshots and troubleshooting tips.

### WSL2 Installation (Windows users)
If you're developing in WSL2 and want a global keyboard hotkey to launch the GUI from Windows:

#### Prerequisites
- **WSL2 with Ubuntu** (or compatible distro) - [WSL2 Setup Guide](docs/WSL2_SETUP_GUIDE.md)
- **Python 3.12.3+** in WSL2 - `python3 --version`
- **AutoHotkey v2.0** on Windows - [Download](https://www.autohotkey.com/)

#### Installation Steps

1. **Install in WSL2**
   ```bash
   cd ~/prompt-automation
   pipx install -e .
   ```

2. **Assign hotkey** (default: Ctrl+Shift+J)
   ```bash
   prompt-automation --assign-hotkey
   ```
   When prompted, enter: `ctrl+shift+j` (or your preferred hotkey)

3. **Verify installation**
   - Press **Ctrl+Shift+J** (Windows-wide hotkey)
   - GUI should launch from WSL2
   - Check AutoHotkey tray icon (system tray, right side of taskbar)

#### How it works
- `--assign-hotkey` auto-detects WSL2 environment
- Generates AutoHotkey v2 script in Windows Startup folder
- Script launches `wsl.exe -d {distro} prompt-automation --gui`
- Hotkey works system-wide (any Windows application)

#### Troubleshooting

**Issue**: Nothing happens when pressing hotkey
- Check WSL2 is running: `wsl.exe --status` (in PowerShell)
- Verify AutoHotkey is installed: Look for tray icon
- Check script exists: `C:\Users\{username}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\prompt-automation.ahk`
- Re-run: `prompt-automation --assign-hotkey` to regenerate script

**Issue**: GUI launches but immediately closes
- Test directly: `prompt-automation --gui` (in WSL2)
- Check logs: `tail -f ~/.prompt-automation/logs/error.log`
- Verify dependencies: `pipx inject prompt-automation ".[tests]"`

**Issue**: AutoHotkey not installed
- Download from [autohotkey.com](https://www.autohotkey.com/)
- Install **v2.0** (64-bit recommended)
- After install, re-run: `prompt-automation --assign-hotkey`

**Full details**: See [WSL2 Setup Guide](docs/WSL2_SETUP_GUIDE.md) for advanced configuration.

### Developer setup
For editable installs that auto-configure development flags:

- **Windows**: `install/install-dev.ps1`
- **macOS / Linux / WSL2**:
  ```bash
  pipx install --editable .
  pipx inject prompt-automation ".[tests]"
  ```
  or `python -m pip install --user -e '.[tests]'`

After installation restart your terminal so `pipx` is on your `PATH`. The GUI depends on Tkinter; Debian/Ubuntu users may need `sudo apt install python3-tk`.

## Quickstart
1. Launch the app with **Ctrl+Shift+J** or run `prompt-automation` (aliases: `prompt_automation`, `pa`).
2. Browse or search for a template. Hierarchical navigation is available when enabled.
3. Fill in placeholders. Leave a field blank to fall back to defaults or remove the line entirely.
4. Review the rendered output, then press **Ctrl+Enter** to copy and close or **Ctrl+Shift+C** to copy without closing.
5. Need a new shortcut? Run `prompt-automation --assign-hotkey` to rebind the global hotkey.

Ready to validate the MCP bridge? The [MCP Integration Guide](docs/MCP_INTEGRATION.md)
covers enabling the toggle, starting the stub, and running JSON-RPC checks end-to-end.

More GUI shortcuts and CLI options live in [Single Window Keyboard Shortcuts](docs/SINGLE_WINDOW_KB.md) and [Hotkeys](docs/HOTKEYS.md).

## Automated feature development workflow

**Want to implement features using an AI-guided workflow?** This project includes a complete 3-phase system that automates feature implementation from discovery to archival.

### Quick Start

```bash
# Phase 1: Auto-discover next feature and generate approval spec
./scripts/feature_workflow_copilot.sh

# Phase 2: AI implements using TDD (after Phase 1 approval)
./scripts/feature_workflow_copilot.sh --phase 2 {feature_id}

# Phase 3: Archive and update docs (after manual testing)
./scripts/feature_workflow_copilot.sh --phase 3 {feature_id}
```

### What it does

- **Phase 1**: Discovers next unarchived feature, extracts Definition of Done, assesses risks, generates approval spec
- **Phase 2**: Implements feature using TDD (RED → GREEN → REFACTOR), validates coverage (≥85%), generates manual test guide
- **Phase 3**: Moves feature to archive, updates all documentation, gathers workflow feedback, suggests next feature

### Human checkpoints

- ⏸️ **After Phase 1**: Choose implementation path (AI direct or meta-prompt)
- ⏸️ **After Phase 2**: Perform manual testing before archival

### Complete documentation

- 📖 **[Complete Workflow Guide](docs/agentic_feature_implementation/WORKFLOW_COMPLETE_GUIDE.md)** - Step-by-step "dumb steps" instructions (start here!)
- 📚 **[Feature Index & Roadmap](docs/agentic_feature_implementation/README.md)** - All available features and system overview
- 🔧 **[Technical Reference](docs/agentic_feature_implementation/AUTOMATED_WORKFLOW_GUIDE.md)** - Phase details, state management, troubleshooting

All workflow state is version-controlled in `docs/agentic_feature_implementation/{NN}_{feature_name}/workflow_state_phase*.json` for cross-device portability. Completed features are archived in `docs/agentic_feature_implementation/_archive/` with context summaries for future features.

## Espanso integration
`prompt-automation` keeps the versioned espanso package under `espanso-package/` as the source of truth. Use the app, CLI, or helper scripts to generate matches, validate them, and mirror the results into your espanso installation.

| Command or flag | Purpose |
| --- | --- |
| `prompt-automation --espanso-sync` | Generate snippets, validate, mirror to the espanso directory, install/update the package, and restart espanso. |
| `prompt-automation --espanso-sync --git-branch <name>` | Override the git branch when installing from a repository. |
| `scripts/espanso.sh sync` | Run the sync pipeline from a shell script (respects the same environment variables). |
| `PA_SKIP_INSTALL=1 scripts/espanso.sh sync` | Dry-run: generate, validate, and mirror without installing or restarting espanso. |
| `scripts/espanso.sh lint` | Validate YAML matches and check for duplicate triggers. |
| `prompt-automation --espanso-clean` | Backup and remove local espanso match files managed by this project. |
| `prompt-automation --espanso-clean-deep` | Extend clean-up to uninstall legacy/conflicting packages. |
| `prompt-automation --espanso-clean-list` | Show which files would be touched without making changes. |

Detailed workflows, CI notes, and packaging guidance are documented in [ESPANSO_PACKAGE.md](docs/ESPANSO_PACKAGE.md) and [ESPANSO_FIRST_RUN.md](docs/ESPANSO_FIRST_RUN.md).

## Template authoring
Templates live under `src/prompt_automation/prompts/`. Start with the New Template Wizard or create JSON manually. For directory conventions, metadata flags, multi-file placeholders, and override sync behavior, read the [Template Authoring and Management guide](docs/TEMPLATES.md).

Additional references:
- [Variable Workflow Guide](docs/VARIABLE_WORKFLOW.md) walks through creating, editing, and removing globals plus their espanso integration.
- [Variables & Globals Reference](docs/VARIABLES_REFERENCE.md) explains placeholder schema, persistence, and formatting helpers.
- [Hierarchical Variable Management](docs/hierarchical_variable_storage.md) covers migration behavior, GUI CRUD, Espanso
  integration, performance guardrails, and release/rollback procedures.
- [Reminders Schema and Usage](docs/REMINDERS.md) covers instructional text blocks and feature flags.
- [Theme Extension Guide](docs/THEME_EXTENSION_GUIDE.md) describes how to customize the Tk theme system.

## Troubleshooting and maintenance
- `prompt-automation --troubleshoot` prints log locations, override files, and environment details.
- [Installation Troubleshooting](docs/INSTALLATION_TROUBLESHOOTING.md) covers platform-specific installer issues.
- [Python Troubleshooting](docs/PYTHON_TROUBLESHOOTING.md) helps resolve interpreter or dependency problems.
- [Hotkeys](docs/HOTKEYS.md) walks through repairing or manually configuring shortcuts.
- [Uninstall](docs/UNINSTALL.md) lists CLI flags and exit codes for the built-in uninstaller.

For espanso-specific checks see [ESPANSO_REMOTE_FIRST.md](docs/ESPANSO_REMOTE_FIRST.md) and the scripts in `scripts/`.

## Configuration Management

**Feature 000: Smart Settings & Config Management** provides a unified configuration system with GUI and API access.

**Key Capabilities**:
- **GUI Access**: Visual settings discovery and configuration (Options → Configuration Manager...)
- **Single config file**: `~/.prompt-automation/config.json` replaces scattered settings
- **Hot-reload**: Changes apply instantly without restart (300ms debounce)
- **Profiles**: Switch between lightweight/standard/performance presets
- **Type-safe**: Pydantic validation prevents invalid configurations
- **Environment overrides**: Use `PA_*` env vars for deployment flexibility

**GUI Quick Start** (Recommended):
1. Launch: `prompt-automation`
2. Click: **Options** → **Configuration Manager...**
3. Browse settings by category (LLM, Cache, Performance, Analytics, Features)
4. Edit values, switch profiles, enable hot-reload
5. Click **Save** to persist changes

**API Quick Start** (Advanced):
```python
from prompt_automation.settings import ConfigManager

config = ConfigManager()

# Read settings
llm_port = config.get("llm.port", default=8080)

# Update settings
config.set("cache.memory_mb", 512)
config.save()

# Switch profile
config.switch_profile("performance")

# Enable hot-reload
config.enable_hot_reload()
```

**Documentation**: See [Configuration Guide](docs/CONFIGURATION.md) and [Migration Guide](docs/CONFIG_MIGRATION.md) for full details.

## Knowledge Base

**Feature 003: Pre-Answered Questions Knowledge Base** provides default answers to common feature implementation questions, reducing human interruptions during automated workflows.

**Key Capabilities**:
- **Default answers by category**: Architecture, testing, GUI, rollout, performance, security
- **Feature-specific overrides**: Per-feature customization (e.g., meta-prompt model endpoint)
- **JSON validation**: Schema validation on load with graceful fallback
- **CLI inspection**: View defaults via `--show-defaults` command
- **Versioned schema**: Support for future migrations

**CLI Quick Start**:
```bash
# Show all default answers
prompt-automation --show-defaults all

# Show specific category
prompt-automation --show-defaults testing
# Output: {
#   "framework": "pytest",
#   "coverage_target": 85,
#   "require_unit_tests": true,
#   ...
# }

# Show architecture defaults
prompt-automation --show-defaults architecture
```

**API Quick Start**:
```python
from prompt_automation.knowledge import get_default_answer, get_all_defaults

# Get single default answer
framework = get_default_answer("testing", "framework")
print(framework)  # "pytest"

# Get answer with feature-specific override
timeout = get_default_answer("testing", "timeout_seconds", feature_id="copilot_agent")
print(timeout)  # 300

# Get all defaults for a category (with overrides applied)
defaults = get_all_defaults("architecture", feature_id="meta_prompt")
print(defaults["max_loc_per_file"])  # 400
print(defaults["model_endpoint"])  # "http://127.0.0.1:8080" (override)
```

**Default Categories**:
- **architecture**: Style, LOC limits, naming conventions, folder structure
- **testing**: Framework, coverage target, TDD requirements, test runtime limits
- **gui**: Framework (tkinter), pattern (single_window), CLI backport policy
- **rollout**: Feature flags, observability, rollback plans, kill switches
- **performance**: Latency targets, memory limits, CPU cores, measurement requirements
- **security**: Secrets handling, privilege levels, input validation

**Knowledge Base Location**: `src/prompt_automation/knowledge/feature_qa.json`

**Integration**: Meta-prompt system (future) will use these defaults during Phase 1 (Pre-Flight) to automatically answer common questions before prompting the user.

## Workspace Context Gathering

**Feature 001: Workspace Context Gatherer** provides intelligent workspace analysis for feature implementation, generating LLM-ready context from your codebase.

**Key Capabilities**:
- **Keyword extraction**: Analyzes feature specs, removes stop words, extracts top 10 relevant keywords
- **Codebase search**: Multi-strategy search with automatic fallback (ripgrep → git-grep → pathlib)
- **AST-based indexing**: Parses Python files for functions, classes, imports (no regex fragility)
- **Workspace indexing**: Builds searchable index of Python/JSON/Markdown files
- **Constraint extraction**: Pulls relevant sections from `AGENTS.md` for context
- **Test discovery**: Finds related test files matching feature keywords
- **Obsidian integration**: Optional MCP bridge to search Obsidian notes (feature-flagged)

**CLI Quick Start**:
```bash
# Build workspace index
prompt-automation --index-workspace
# Output: ✅ Indexed 245 files
#         ✅ Index saved to: /path/to/.prompt-automation-index.json

# Use in Python
from prompt_automation.workspace.context_gatherer import ContextGatherer

gatherer = ContextGatherer()
context = gatherer.gather_for_feature(
    feature_id="workspace-context-gatherer",
    feature_title="Workspace Context Gatherer",
    spec_text="Implement intelligent workspace analysis..."
)
print(context)  # Markdown-formatted context
```

**Configuration**:
```bash
# Enable Obsidian MCP integration (default: OFF)
export PA_WORKSPACE_CONTEXT_OBSIDIAN_ENABLED=1

# Or via config.json
{
  "features": {
    "workspace_context_obsidian": true
  }
}
```

**Performance**: Context gathering completes in <5 seconds for typical workspaces (500-1000 files).

**Architecture**: Uses Pattern 7 (Search with Fallback Chain) and Pattern 8 (AST-Based Code Analysis) from `AGENTS.md`.

## Performance & Observability (Features 18-21)

Version 3.0 will introduce additional performance and observability features:

### Feature 18: Reserved for future use

### Feature 19: Caching System (Planned)
Intelligent caching to eliminate redundant LLM calls and speed up repeated operations.

See [Feature 18 Spec](docs/agentic_feature_implementation/18_smart_settings_config/feature_spec.md) for details.

---

### Feature 19: Multi-Tier Caching System
Intelligent 3-tier caching (Memory/Disk/GPU) reduces redundant operations by 80-90%.

**Key Capabilities**:
- **L1 (Memory)**: LRU cache, <5ms lookups, 256MB default
- **L2 (Disk)**: Persistent cache with compression, <50ms lookups, survives restarts
- **L3 (GPU VRAM)**: Model weights cached (optional, if GPU available)
- **Semantic deduplication**: Similar prompts share cache (90%+ accuracy)
- **Auto-eviction**: Memory-safe, no OOM crashes

**Performance Impact**:
- Template loads: **40x faster** (200ms → <5ms)
- LLM calls: **50-500x faster** (5s → <10ms cached)
- Cache hit rate: **80-90%** for typical workloads

**Quick Start**:
```bash
# View cache statistics
prompt-automation cache stats

# Clear cache
prompt-automation cache clear

# Warm cache with top templates
prompt-automation cache warm
```

See [Feature 19 Spec](docs/agentic_feature_implementation/19_multi_tier_caching/feature_spec.md) for details.

---

### Feature 20: Performance & Resource Manager
Async LLM inference, GPU utilization, and dynamic resource management prevent bottlenecks.

**Key Capabilities**:
- **Async LLM calls**: Non-blocking GUI, stays responsive during inference
- **GPU auto-detection**: CUDA, ROCm, MPS (Apple Silicon) with CPU fallback
- **Connection pooling**: Reuse HTTP connections (50%+ faster)
- **Request batching**: 10+ prompts → 1 batch (30%+ throughput gain)
- **Resource monitoring**: Real-time CPU/RAM/GPU/VRAM tracking
- **Dynamic throttling**: Auto-reduce load when resources constrained
- **Docker optimized**: Multi-stage builds, GPU passthrough, <500MB images

**Performance Targets**:
- LLM latency: **<500ms** (GPU), **<2s** (CPU)
- GPU utilization: **80%+** when available
- Memory usage: **≤512MB** (performance), **≤256MB** (standard), **≤64MB** (minimal)

**Quick Start**:
```bash
# View resource usage
prompt-automation metrics

# Check GPU status
prompt-automation gpu-info

# Enable/disable GPU
prompt-automation config set performance.gpu_enabled true
```

See [Feature 20 Spec](docs/agentic_feature_implementation/20_performance_resource_manager/feature_spec.md) for details.

---

### Feature 21: Usage Analytics & Telemetry
Track usage patterns, performance metrics, and errors for data-driven optimization.

**Key Capabilities**:
- **Usage tracking**: Templates, prompts, MCP calls (100% coverage)
- **Performance metrics**: Latency (P50/P95/P99), cache hit rates, throughput
- **Error tracking**: Exceptions with full context and stack traces
- **Resource metrics**: Time-series CPU/RAM/GPU data (1 Hz sampling)
- **Local SQLite DB**: Max 100MB, auto-rotate to archives
- **Privacy-first**: Prompts hashed (SHA256), opt-out available, no PII
- **CLI dashboard**: View insights without leaving terminal

**Quick Start**:
```bash
# View analytics summary
prompt-automation analytics summary

# Top templates (last 24 hours)
prompt-automation analytics top-templates

# Recent errors
prompt-automation analytics errors --limit 20

# Resource usage over time
prompt-automation analytics resources --hours 1

# Export data (JSON)
prompt-automation analytics export --output analytics.json

# Clear all analytics data
prompt-automation analytics clear --confirm

# Opt-out of analytics
prompt-automation config set analytics.enabled false
```

See [Feature 21 Spec](docs/agentic_feature_implementation/21_usage_analytics_telemetry/feature_spec.md) for details.

---

### Recommended Feature Enablement Order

When enabling performance and observability features, follow this order to measure before optimizing:

**1. Feature 18 (Smart Settings) - Foundational** ✅
```bash
# Enable first: All other features depend on this
prompt-automation config set-profile standard
```
**Why First**: Unified configuration system required by all other features. Establishes baseline settings.

**2. Feature 21 (Analytics) - Measure Baseline** 📊
```bash
# Enable second: Measure current performance before optimizing
prompt-automation config set analytics.enabled true
prompt-automation analytics summary
```
**Why Second**: Establish performance baseline. Metrics guide which optimizations are needed.

**Key Questions to Answer**:
- What templates are used most? (Focus caching here)
- Where are latency bottlenecks? (LLM calls? Template parsing? MCP requests?)
- What's the cache hit rate? (Is caching even needed?)
- Are resources constrained? (Is GPU/memory optimization needed?)

**3. Feature 22 (MCP Router) - Only If Multi-Server** 🔀
```bash
# Enable third: Only if using 2+ MCP servers
prompt-automation config set mcp.router.enabled true
```
**Why Third**: Most users have single MCP server (Obsidian OR LiteLLM, not both). Enable only if metrics show need for multi-server routing.

**Skip If**: Using only one MCP server (Feature 22 adds complexity without benefit)

**4. Feature 19 (Caching) - If Latency Detected** ⚡
```bash
# Enable fourth: Only if Feature 21 metrics show high latency
prompt-automation config set cache.enabled true
prompt-automation cache stats
```
**Why Fourth**: Caching adds memory overhead and complexity. Only enable if analytics (Feature 21) shows:
- LLM latency >2s (Feature 19 reduces to <10ms)
- Template parsing >50ms (Feature 19 reduces to <5ms)
- Repeated prompts >10% of workload (Feature 19 deduplicates)

**Skip If**: Latency is already acceptable (<500ms P95) or workload is unique prompts (cache won't help)

**5. Feature 20 (Performance Manager) - If Resource Constrained** 🔥
```bash
# Enable fifth: Only if Feature 21 shows resource issues
prompt-automation config set performance.gpu_enabled true
prompt-automation gpu-info
```
**Why Fifth**: GPU optimization, batching, and async inference add complexity. Only enable if analytics shows:
- CPU utilization >80% (Feature 20 adds GPU acceleration)
- Memory usage near limits (Feature 20 adds dynamic throttling)
- GUI freezing during LLM calls (Feature 20 adds async inference)

**Skip If**: Resources are sufficient (single-threaded workload, low memory usage, fast CPU inference)

**Summary**:
```
Enablement Order: 18 → 21 → [22 if multi-server] → [19 if latency] → [20 if constrained]
Core Pattern: Measure (21) before optimizing (19/20)
Key Insight: Not all users need all features. Enable based on metrics, not assumptions.
```

**Feature Flags** (gradual rollout):
```yaml
# ~/.prompt-automation/settings.yaml
features:
  smart_settings: true         # Feature 18: Always enable
  analytics: true              # Feature 21: Enable for measurement
  mcp_router: false            # Feature 22: Opt-in (multi-server only)
  multi_tier_cache: false      # Feature 19: Opt-in (latency issues)
  performance_manager: false   # Feature 20: Opt-in (resource issues)
```

---

### Integration & Configuration

All features work together seamlessly. Configuration example:

```json
{
  "profile": "performance",
  "cache": {
    "enabled": true,
    "l1_size_mb": 256,
    "l2_size_mb": 200,
    "use_semantic_hash": true
  },
  "performance": {
    "gpu_enabled": true,
    "max_concurrent_requests": 10,
    "batch_size": 10
  },
  "analytics": {
    "enabled": true,
    "hash_prompts": true
  }
}
```

**Complete Documentation**:
- [Features 18-21 Integration Guide](docs/agentic_feature_implementation/FEATURES_18_21_INTEGRATION.md) - How features interact
- [Optimization Roadmap](docs/agentic_feature_implementation/OPTIMIZATION_ROADMAP.md) - Implementation timeline (12 days)

**Expected Impact**: 10-500x performance improvement, zero OOM crashes, comprehensive observability.

---

## MCP Router & Multi-Server Integration (Feature 22)

Version 3.1 introduces a **universal MCP gateway** that aggregates tools from multiple MCP servers (LiteLLM Gateway, Obsidian MCP, llama.cpp bridges, custom servers) and routes tool calls automatically based on namespace.

### What is the MCP Router?

The MCP Router provides server-agnostic integration: add new MCP servers by editing a config file only—**no code changes required**. It normalizes different transport protocols (HTTP, stdio, gRPC) and provides automatic fallback, namespace isolation, and hot-reload capabilities.

**Benefits**:
- **Zero coupling**: Application code doesn't depend on specific servers
- **Multi-server aggregation**: 100+ tools from 3+ servers in a single interface
- **Namespace isolation**: No tool name collisions (`obsidian.search`, `llm.generate`)
- **Automatic fallback**: Resilient to server failures (llama.cpp → LiteLLM)
- **Hot-reload registry**: Add/remove servers without restart
- **Protocol-agnostic**: HTTP, stdio, gRPC all work identically

### Quick Start

**1. Enable MCP Router**:
```bash
# Via CLI
prompt-automation config set mcp_router_enabled true

# Or edit ~/.prompt-automation/settings.json
{
  "mcp_router_enabled": true,
  "mcp_router_config_path": "~/.prompt-automation/mcp/servers.json"
}
```

**2. Configure Servers**:

Create `~/.prompt-automation/mcp/servers.json`:
```json
{
  "version": "1.0",
  "servers": [
    {
      "id": "litellm-gateway",
      "name": "LiteLLM MCP Gateway",
      "enabled": true,
      "transport": "http",
      "endpoint": "http://localhost:8080/mcp",
      "namespace": "llm",
      "priority": 10,
      "fallback": "llama-cpp-local",
      "capabilities": ["generate", "embed", "chat"]
    },
    {
      "id": "obsidian-mcp",
      "name": "Obsidian MCP",
      "enabled": true,
      "transport": "stdio",
      "command": "node",
      "args": ["/path/to/obsidian-mcp/index.js"],
      "namespace": "obsidian",
      "priority": 5,
      "capabilities": ["search_notes", "create_note"]
    }
  ]
}
```

**3. List Available Tools**:
```bash
# All servers
prompt-automation mcp list-servers
# Output:
# LiteLLM MCP Gateway (healthy, priority 10, 25 tools)
# Obsidian MCP (healthy, priority 5, 12 tools)

# All tools
prompt-automation mcp list-tools

# Filter by namespace
prompt-automation mcp list-tools --namespace obsidian
# Output:
# obsidian.search_notes - Search Obsidian vault for notes
# obsidian.create_note - Create a new note in vault
```

**4. Call Tools**:
```bash
# Search Obsidian vault
prompt-automation mcp call obsidian.search_notes \
  --arguments '{"query": "python", "limit": 5}'

# Generate text with LLM (with automatic fallback)
prompt-automation mcp call llm.generate \
  --arguments '{"prompt": "Explain asyncio", "max_tokens": 100}'
```

**5. Health Check**:
```bash
prompt-automation mcp health
# Output:
# litellm-gateway: healthy (uptime: 3600s)
# obsidian-mcp: healthy (uptime: 3600s)
```

**6. Hot-Reload (No Restart)**:
```bash
# Edit servers.json (add new server, change priority, etc.)
vim ~/.prompt-automation/mcp/servers.json

# Reload configuration
prompt-automation mcp reload-registry

# Verify changes
prompt-automation mcp list-servers
```

### Integration with Existing Features

- **Feature 13 (Meta-Prompt)**: Automatically routes LLM calls through the router
- **Feature 14 (Command Palette)**: Exposes all router tools in the UI
- **Features 18-21**: Router integrates with config, caching, performance, and analytics

**Example (Meta-Prompt with Fallback)**:
```bash
# Primary LLM server down? Router automatically uses fallback
prompt-automation render --template-id 13008 --variable goals="Create FastAPI app"

# Router logs:
# [INFO] Primary server litellm-gateway unavailable
# [INFO] Routing to fallback server llama-cpp-local
# [INFO] Tool call succeeded (latency: 500ms)
```

### Adding Custom Servers

See **[MCP Router Developer Guide](docs/agentic_feature_implementation/22_mcp_router_gateway/MCP_ROUTER_GUIDE.md)** for:
- Implementing the universal MCP contract (JSON-RPC 2.0)
- Creating protocol adapters (HTTP, stdio, gRPC)
- Testing integration
- Auto-discovery patterns

**Minimal Example**:
```python
# my_mcp_server.py
from flask import Flask, jsonify
app = Flask(__name__)

@app.route("/mcp/v1/discover", methods=["POST"])
def discover():
    return jsonify({
        "jsonrpc": "2.0",
        "result": {
            "name": "my-server",
            "tools": [{
                "name": "my_tool",
                "namespace": "custom",
                "inputSchema": {"type": "object"},
                "outputSchema": {"type": "object"}
            }]
        },
        "id": 1
    })

if __name__ == "__main__":
    app.run(port=9000)
```

Add to registry → reload → done!

**Complete Documentation**:
- [MCP Integration Guide](docs/MCP_INTEGRATION.md) - Setup, configuration, troubleshooting
- [MCP Router Developer Guide](docs/agentic_feature_implementation/22_mcp_router_gateway/MCP_ROUTER_GUIDE.md) - Adding new servers
- [Feature 22 Spec](docs/agentic_feature_implementation/22_mcp_router_gateway/feature_spec.md) - Architecture and implementation plan

---

## Contributing and support
- Review [CONTRIBUTING.md](CONTRIBUTING.md) and [CODEBASE_REFERENCE.md](docs/CODEBASE_REFERENCE.md) before submitting a change.
- Run `pytest -q` to verify the test suite.
- Report bugs or request features via GitHub issues.

`prompt-automation` is licensed under the MIT License. See [LICENSE](LICENSE) for details.
