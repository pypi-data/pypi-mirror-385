# Changelog

## [0.8.0] - 2025-10-20

### Added
- **Feature 16: Template Management System** - Complete template lifecycle management with visual workflows and AI assistance. Transforms template authoring from manual JSON editing to guided creation with real-time validation.
  - **TemplateManager**: CRUD operations with automatic ID assignment, folder management, atomic file writes (245 LOC)
  - **SearchEngine**: SQLite FTS5 full-text search across title/content/tags with BM25 ranking, <100ms for 1000+ templates (187 LOC)
  - **VersionManager**: Last 10 versions per template with one-click rollback and metadata tracking (156 LOC)
  - **AIValidator**: Real-time schema validation, placeholder extraction, import/export for sharing (134 LOC)
  - **TemplateBrowser GUI**: Grid view with real-time search, toolbar (New/Edit/Delete/Import/Export), context menu (423 LOC)
  - **TemplateEditor GUI**: Dual tabs (Visual forms + JSON editor) with bidirectional sync and save validation (512 LOC)
  - **ModernTemplateWizard GUI**: 4-step guided creation (What & Why → Inputs → Structure → Review) with AI-assisted placeholder extraction and structure presets (918 LOC)
  - **Hotkey integration**: Ctrl+Shift+J opens wizard (Windows + WSL2)
  - **Options menu entries**: "Browse Templates" and "New Template Wizard"
  - **79 tests** (100% passing): 7 manager, 9 search, 8 versions, 8 validator, 10 browser, 8 editor, 23 wizard, 6 integration
  - **Implementation**: 1600 LOC across 10 modules, ≥85% coverage, 5-day effort

### Fixed
- Modal wizard prevents event leakage to parent window (grab_set + transient)
- Dark theme readability with white backgrounds on all text fields
- Template editor constructor compatibility (template_id parameter)

### Known Limitations
- Style dropdown in wizard requires mouse click (keyboard shortcuts deferred to minor feature)
- See `docs/agentic_feature_implementation/minor_features/keyboard_accessible_dropdown.md` for future fix

## Unreleased
- **Feature 014 COMPLETE**: Command Palette - Universal command executor for Obsidian vault operations via slash commands or natural language. **Core capabilities**: (1) Slash commands `/rag` (search vault), `/daily` (append to daily note), `/note` (create note), `/open` (open in Obsidian), (2) Natural language interpretation via Qwen LLM (e.g., "find notes about testing" → `/rag testing`), (3) Diff generation using `difflib.unified_diff` for write operations with approval flow, (4) Approval dialogs (CLI interactive prompt, GUI modal) before executing changes, (5) LLM location suggestions for `/note` command with "Notes/" fallback, (6) Thread-safe CommandRegistry with `threading.Lock`, (7) Graceful degradation (works without LLM, MCP client placeholder for future integration). **GUI**: New CommandFrame (Frame 4) with command entry field, scrolled result display, approval modal for diffs, Cancel button. **CLI**: New `--execute <command>` flag runs commands directly (e.g., `prompt-automation --execute "/rag test"`). **Implementation**: 1,350 LOC across 12 modules (CommandExecutor 87 LOC, CommandParser 209 LOC with shlex.split, CommandRegistry 61 LOC, 4 handlers 513 LOC, LLM client 138 LOC, GUI frame 202 LOC, CLI integration 67 LOC), 89 tests (100% passing in 0.6s), zero regressions. **Architecture**: Layered design (GUI/CLI → Executor → Parser → Registry → Handlers → MCP/LLM), synchronous API (matches existing MCP client). **Patterns Applied**: Pattern 7 (Search with Fallback Chain), Pattern 8 (AST-based code analysis), Pattern 10 (Atomic State Persistence), Pattern 12 (Hybrid Strategy with Fallback Chain). **Known Limitations**: MCP client integration pending (Feature 01 dependency), handlers use `None` placeholder with TODO comments. **Documentation**: Complete implementation summary (≤500 words), context summary (≤200 words), manual test guide (17 test scenarios across 5 suites), plan/tasks breakdown in `docs/agentic_feature_implementation/14_command_palette/`. Developed using strict TDD methodology (RED → GREEN → REFACTOR) with automated 3-phase workflow. **Status**: Implementation complete 2025-10-17, ready for archival.
- **Feature 005 COMPLETE**: Validation Runner - Automated validation system that executes all quality checks (pytest, coverage, lint, file/function size limits) for feature branches. **Core capabilities**: (1) Pytest execution with 5-minute timeout and retry logic for flaky tests, (2) Coverage validation with ≥85% threshold parsing from JSON reports, (3) Lint checks using flake8 (required) and pylint (optional), (4) File size validation (≤400 LOC per file), (5) Function size validation (≤75 LOC per function using AST parsing), (6) Parallel execution using ThreadPoolExecutor for concurrent checks, (7) Structured results dict with all_passed flag and detailed messages. **CLI**: New `--validate` flag runs complete validation suite with formatted output (e.g., `prompt-automation --validate --branch feature/my-branch`). Exit code 0 (pass) or 1 (fail). **Implementation**: 469 LOC across 5 validation modules (test_executor.py 75 LOC, coverage_checker.py 62 LOC, lint_checker.py 100 LOC, size_checker.py 89 LOC, runner.py 143 LOC), 38 tests (100% passing in 0.25s), zero regressions (695/695 tests pass). CLI integration adds +75 LOC to controller.py. **Performance**: Validation tests run in <1 second. Parallel execution reduces total check time significantly. **Patterns Applied**: Pattern 8 (AST-based code analysis for accurate function LOC), Pattern 9 (ThreadPoolExecutor for parallel execution). **Bug Fixes**: Fixed critical recursive pytest execution bug causing indefinite hangs (test mocking issue), fixed 6 test regressions from background hotkey disable. **Documentation**: Complete implementation summary, manual test guide, plan/tasks breakdown in `_archive/2025-10-04_feature_05_validation_runner/`. Developed using strict TDD methodology (RED → GREEN → REFACTOR) with automated 3-phase workflow. **Status**: Production-ready, archived 2025-10-04.
- **Feature 004 REJECTED**: Feature Pattern Templates - Rejected due to low priority and uncertain ROI. Existing resources (AGENTS.md patterns, Knowledge Base, existing code examples) already provide sufficient guidance. Maintenance burden not justified by unclear benefit. Archived to `_archive/04_feature_patterns/` for potential future reconsideration if clear need emerges.
- **Feature 003 COMPLETE**: Knowledge Base - Pre-answered questions system storing default answers to common feature implementation questions. **Core capabilities**: (1) Default answers by category (architecture, testing, gui, rollout, performance, security) sourced from AGENTS.md, (2) Feature-specific overrides for per-feature customization (meta_prompt, workspace_context_gatherer, copilot_agent), (3) Graceful error handling with fallback to empty dict on missing/corrupt JSON, (4) JSON schema validation (version 1.0) with backward compatibility warnings, (5) CLI inspection via `--show-defaults <category|all>` command, (6) Python API: `get_default_answer(category, key, feature_id)` and `get_all_defaults(category, feature_id)`. **CLI**: New `--show-defaults` flag displays KB contents as JSON (e.g., `prompt-automation --show-defaults testing`). **Implementation**: 147 LOC loader module, 62 LOC JSON data file, 140 LOC tests (10 tests, 100% passing), CLI integration in controller.py. All file sizes ≤400 LOC. Zero regressions (666/671 tests pass, 5 pre-existing failures unrelated to feature). **Performance**: KB loads in <10ms, <1MB memory footprint, no external dependencies (pure stdlib). **Architecture**: Simple loader pattern with feature override precedence, quarterly review schedule for defaults alignment. **Documentation**: README.md updated with usage examples, implementation summary in `docs/agentic_feature_implementation/03_knowledge_base/implementation_summary.md`. Developed using strict TDD methodology (RED → GREEN → REFACTOR) with automated 3-phase workflow. **Integration**: Ready for meta-prompt system (Feature 16) to use in Phase 1 question pre-answering. **Status**: Implementation complete, all 10 acceptance criteria met, ready for archival.
- **Feature 001 COMPLETE**: Workspace Context Gatherer - Intelligent workspace analysis system that provides LLM-ready context for feature implementation. **Core capabilities**: (1) Keyword extraction from feature specs with stop word filtering (max 10 keywords), (2) Codebase search using fallback chain (ripgrep → git-grep → pathlib) with timeout handling, (3) AST-based workspace indexing for Python files (functions, classes, imports), JSON/Markdown parsing, (4) Optional Obsidian MCP integration (feature-flagged, default OFF via `PA_WORKSPACE_CONTEXT_OBSIDIAN_ENABLED`), (5) AGENTS.md constraint extraction with section headers, (6) Related test discovery matching feature keywords, (7) Context formatting as structured Markdown. **CLI**: New `--index-workspace` flag builds and saves workspace index to `.prompt-automation-index.json` (typical output: "✅ Indexed 245 files"). **Implementation**: 745 LOC (search.py 141 LOC, indexer.py 270 LOC, context_gatherer.py 331 LOC), 43 tests (40 workspace + 3 CLI, all passing), 1 skipped (ripgrep not installed). All file sizes ≤400 LOC. Zero regressions (656/661 tests pass, 5 pre-existing failures unrelated to feature). **Performance**: Context gathering <5 seconds validated. **Architecture**: 3-module design with Pattern 7 (Search with Fallback Chain), Pattern 8 (AST-Based Code Analysis). **Documentation**: Inline docstrings, task breakdown in `docs/agentic_feature_implementation/01_workspace_context_gatherer/tasks.md`. Developed using strict TDD methodology (RED → GREEN → REFACTOR) with automated 3-phase workflow. **Status**: Implementation complete, pending manual testing and archival.
- **Feature 000 COMPLETE**: Smart Settings & Config Management system providing unified configuration with hot-reload, profiles, and environment overrides. **Backend**: ConfigManager singleton with type-safe Pydantic validation (10 models), atomic file writes with backup, 300ms debounced hot-reload, and 3 profiles (lightweight/standard/performance). Configuration file: `~/.prompt-automation/config.json`. Environment variables: `PA_*` prefix (e.g., `PA_LLM__PORT=9090`). **GUI**: New Configuration Manager panel (Options → Configuration Manager...) provides visual settings discovery, automatic file creation, profile switching (radio buttons), hot-reload toggle, validation with error messages, env var override display (blue labels), Save/Reset/Open File actions. All settings organized by category tabs (LLM, Cache, Performance, Analytics, Features). **Implementation**: 766 LOC backend + 306 LOC GUI, 69 tests (100% passing), zero regressions (612/614 total tests pass, 2 pre-existing failures). **Documentation**: `docs/CONFIGURATION.md`, `docs/CONFIG_MIGRATION.md`. Replaces Feature 15 (Unified Settings System). Foundational infrastructure for Features 16-22. Developed using TDD with automated workflow (Phase 1 Discovery → Phase 2 TDD Implementation → Phase 3 Archival). **Status**: Production-ready, archived 2025-10-03.
- **UX improvement**: Added Python Environment Info dialog to Help menu (Help → Python Environment Info...). Displays Python executable, version, sys.path, pydantic availability, and ConfigManager status in scrollable window. User-triggered only (silent by default), preventing automatic popups and desktop glitching. Implementation: 75 LOC new dialog module, +11 LOC menu integration, removed standalone test script. Documentation: `docs/PYTHON_ENV_INFO_DIALOG.md`.
- **Bug fix**: Fixed universal GUI toggle persistence issue where checkboxes would flash checked then immediately revert to unchecked state. Root cause: tkinter BooleanVar/StringVar objects were being garbage collected, causing widgets to lose variable bindings. Solution: Store all GUI variables as window/frame attributes to maintain strong Python references. Affects all settings panels (Options → Settings, Options → Configuration Manager). Implementation: +15 LOC across settings_panel.py and config_manager_panel.py, 4 new tests for toggle persistence, 587/587 tests passing. Documentation: `docs/GUI_TOGGLE_PERSISTENCE_FIX.md`. Developed using TDD methodology.
- Added cancel button functionality to single-window GUI workflow: Users can now abort from Variables or Review stages and return to template selector. Cancel button clears all workflow state (template, variables, stage) to prevent stale data. Implementation: ~18 LOC added across controller and frame builders, 5 new tests, zero regressions (507/507 tests pass). Feature developed using Test-Driven Development with automated workflow system (Phase 1: Discovery → Phase 2: TDD Implementation → Phase 3: Archival).
- Added `obsidian_notes_tools_enabled` global placeholder (default `true`) as the kill switch for Obsidian notes tooling; set to `false` in packaged globals or overrides to pause the integrations across CLI, GUI, and MCP during rollback.
- Clarified MCP template search resolution: metadata paths now iterate `PROMPTS_SEARCH_PATHS`, documenting that packaged prompts under `src/prompt_automation/prompts/...` resolve automatically.
- Prepared hierarchical variable management for rollout: added end-to-end acceptance coverage for migration, resolver, GUI CRUD, and Espanso tagging; documented release procedures and troubleshooting in `docs/hierarchical_variable_storage.md`; recorded performance metrics confirming we remain below the 50 ms render budget with <5% P95 regression headroom.
- Added MCP integration documentation covering the fake Qwen stub, MCP server launch, JSON-RPC validation steps, and llama.cpp model placement in `docs/MCP_INTEGRATION.md`; linked the guide from installation scripts, README, settings UI, and manual validation checklists.

## 0.6.7 - 2025-09-17
- (no changes yet)

## 0.6.6 - 2025-09-17
- Added: Manual packaging wizard accessible from the GUI (Options → Packaging). The dialog runs the test suite, executes the existing packagers, tags the repo, and uploads installers to GitHub releases. Preferences for verbose logging persist to `Settings/settings.json`, and a new background service streams structured logs to `~/.prompt-automation/logs/manual-packaging-*.log`. Documentation lives in `docs/MANUAL_PACKAGING.md`.
- Added: Experimental native installer tooling under `packagers/` with Windows (PyInstaller) and macOS (py2app + `hdiutil`) builds. New CLI (`python packagers/build_all.py`) orchestrates artifact creation, enforces the 350-line helper limit, and documents manual verification steps in `docs/PACKAGING.md`. GitHub Actions now runs a dry-run on push and exposes manual jobs for platform packaging once runners are provisioned.
- Bug fix: stabilize CLI fallback for file placeholders with invalid pre‑supplied paths and no template binding; initialize labels early to prevent crashes and allow deterministic skip (None) without repeated prompts.
- Added: Placeholder-empty fast-path in single-window GUI. When a template has no effective input placeholders (placeholders missing/`null`/`[]` or only reminder/link/invalid specs), the app bypasses the variable collection stage and opens the final output view directly. Outputs render with the same pipeline as the normal review stage and auto-copy behavior remains unchanged. Observability: one debug log line (`fastpath.placeholder_empty`) emitted on activation (no template content logged). Kill-switch: set `PROMPT_AUTOMATION_DISABLE_PLACEHOLDER_FASTPATH=1` or add `"disable_placeholder_fastpath": true` to `Settings/settings.json` to disable. Backward compatible: templates with placeholders are unaffected.
- Added: Recent history for executed templates (last 5, persisted in `~/.prompt-automation/recent-history.json`). New Options → Recent history panel lists newest→oldest with preview and Copy action. Feature flag `PROMPT_AUTOMATION_HISTORY` (and `Settings/settings.json: recent_history_enabled`) controls enablement; default enabled. Redaction hook via `PROMPT_AUTOMATION_HISTORY_REDACTION_PATTERNS` or `recent_history_redaction_patterns` in settings. Purge behavior when disabled via `PROMPT_AUTOMATION_HISTORY_PURGE_ON_DISABLE` or `recent_history_purge_on_disable`. Defensive parsing, atomic writes, and corruption quarantine. No changes to existing flows besides post-success appends.
- Added: Optional hierarchical template browsing behind a feature flag. A new scanner (`TemplateHierarchyScanner`) renders physical on‑disk folders as a tree with caching and safe defaults. CRUD operations (`TemplateFSService`) provide create/rename/move/delete for folders and templates with path sandboxing and name validation. CLI gains `--tree` (and `--flat`) modifiers for `--list`. Observability: structured INFO logs for scan and CRUD events. Backward‑compatible: flat listing and public APIs unchanged by default.
- Added: CLI name filtering via `--filter <pattern>` for both flat and tree listings, allowing quick narrowing of templates and folders.
 - Added: Read‑only “reminders” support at template root and placeholder level. Inline reminder text renders beneath inputs in the single‑window GUI, with a collapsible panel presenting template/global reminders. CLI prints template/global reminders once before the first prompt and placeholder reminders before each query. Feature flag `PROMPT_AUTOMATION_REMINDERS` (and `Settings/settings.json: reminders_enabled`) controls enablement; default is enabled. Observability: single `reminders.summary` log per template summarizing counts.
- Single-window GUI: restored bullet/checklist auto-formatting for multiline placeholders via lightweight key bindings.
- Reference file picker now renders only when a `reference_file` placeholder exists and appears inline beneath it (no global toolbar clutter).
- Improved accessibility: focus changes auto-scroll to reveal the focused input; added debug logs for bullet insertion, inline ref picker instantiation, and scroll adjustments.
- Added feature flag `PA_DISABLE_SINGLE_WINDOW_FORMATTING_FIX=1` to temporarily disable the new formatting/scroll and revert to legacy global picker layout.
- Added Dark Mode & theming infrastructure:
  - New `dark` theme with accessible palette (AA contrast).
  - Runtime toggle `Ctrl+Alt+D` with persistence.
  - CLI override `--theme=<light|dark|system>` and `--persist-theme`.
  - Safe defaults: light remains unchanged; disable via `enable_theming=false`.
  - Minimal Tk-based applier (no heavy deps) + ANSI formatter for CLI headings.
  - Extension guide for registering additional themes.
- Unified single-window UI now matches legacy feature set and is the default
  experience. Set `PROMPT_AUTOMATION_FORCE_LEGACY=1` to restore the old
  multi-window dialogs.
- Removed experimental `PROMPT_AUTOMATION_SINGLE_WINDOW` toggle.
- Documented modular service layer (`template_search`, `multi_select`,
  `variable_form`, `overrides`, `exclusions`).

## 0.4.4 - 2025-08-18
Comprehensive GUI refactor + quality-of-life enhancements, consolidating prior selector modernization and adding new safety / clarity features.

### Highlights
- Unified single-window workflow (`gui/single_window.py`): persistent root window orchestrating selection → (optional combined multi-select preview) → variable collection → inline review with geometry persistence.
- Centralized Options menu (`gui/options_menu.py`) shared between embedded selector and single-window, eliminating duplicated menu construction logic.
- Inline reference file viewer for `reference_file` placeholder (markdown-ish rendering, truncation for large files, copy/reset/refresh controls & rich keybindings).
- Multi-select synthetic template preview stage: after Finish Multi, users see a read-only combined template before placeholder prompts begin (increases safety & orientation for large batch operations).
- Append targets preview: Review stage toolbar button opens read-only inspectors for each `append_file` / `*_append_file` target before commit.
- Conditional Copy Paths button: Appears in review only when any `*_path` tokens are present in the variable map (avoids UI noise).
- New recursion toggle hotkey (Ctrl+L) for fast recursive / non-recursive search switching without leaving the keyboard.
- Geometry persistence (`~/.prompt-automation/gui-settings.json`) ensures window position/size consistency across runs.

### Hotkey & Selector Improvements (carried forward into 0.4.x)
- Enhanced global hotkey system: GUI-first launch with terminal fallback across Windows (AutoHotkey), Linux (espanso / .desktop fallback), and macOS (AppleScript) with dependency validation.
- Interactive `--assign-hotkey` command + per-user hotkey mapping file.
- Added `--update` command to refresh hotkey configuration / verify dependencies.
- Numeric shortcut management & renumber dialog; digits 0–9 open mapped templates instantly.
- Preview toggle (Ctrl+P) reuses an existing preview window rather than spawning multiples.

### Selector & Navigation
- Modular selector (`gui/selector/`) replaces monolith; legacy wrapper retained for backward import stability.
- Hierarchical folder navigation with breadcrumb and Backspace up-navigation.
- Recursive full-content AND-token search (path, title, placeholder names, body) with live incremental filtering; non-recursive mode toggle + keyboard focus retention.
- Quick keyboard accelerators: `s` focus search, Enter open/select, arrow key navigation, Ctrl+P preview, Ctrl+L recursion toggle.
- Multi-select synthesis produces an id = -1 ephemeral template (original sources untouched).

### Placeholders & Overrides
- Multi-file placeholder system: independent persistence (`path` + `skip`) per (template, placeholder name) mirrored to `prompts/styles/Settings/settings.json`.
- Manage Overrides dialog for inspecting/removing persisted file paths & simple value overrides.
- Inline `reference_file` viewer supersedes legacy modal; other file placeholders still use modal flow (future extensibility path).
- Optional `append_file` / `*_append_file` targets append rendered output post-confirmation; preview added this release for transparency.
- Conditional injection of `*_path` tokens only when referenced in template body to keep variable map lean.

### Review & Output
- Single-window inline review frame: edit rendered text directly; Ctrl+Enter to finish & paste; Ctrl+Shift+C copy without closing; Esc cancel.
- Append targets preview & Copy Paths buttons enhance auditability before finalizing.
- Automatic clipboard copy & paste keystroke emission (with fallback to copy-only on failure).

### Documentation Updates
- HOTKEYS.md: Added Ctrl+L toggle, multi-select preview stage, append targets preview, conditional Copy Paths description.
- CODEBASE_REFERENCE.md: Added `options_menu.py`, expanded single-window architecture, updated feature matrix, toolbar notes.
- VARIABLES_REFERENCE.md: Documented append targets preview & conditional Copy Paths; clarified inline `reference_file` behavior.
- CHANGELOG now reflects 0.4.4 unified release (previous “Unreleased” content incorporated here).

### Internal / Architecture
- Introduced `options_menu.configure_options_menu()` for DRY menu creation & accelerator binding mapping.
- Added multi-stage orchestration within `SingleWindowApp` with explicit stage swapping helper `_swap_stage()`.
- Title wrap-length auto-adjust bound to `<Configure>` events for responsive UX.
- Centralized geometry save/load helpers with defensive IO handling.
- Guarded fallbacks to legacy multi-window path if single-window initialization fails.

### Migration / Upgrade Notes
- No breaking template schema changes. Existing templates & overrides remain compatible.
- Legacy modal `reference_file` viewer still available for non-single-window flows; inline path is automatic in single-window mode.
- If you previously scripted selector menu modifications, update integrations to use `configure_options_menu` rather than manual `tk.Menu` mutation.
- Duplicate 0.2.1 entries in historical section left untouched (will be rationalized in a future housekeeping release).

### Testing & Stability
- Existing 22 test cases pass (no regressions introduced by refactor).
- GUI code paths wrapped in defensive try/except blocks; failures fall back to legacy flows where practical.

### Future Considerations (Not Yet Implemented)
- Optional inline mode for additional file placeholders.
- Filter / transform pipeline (e.g. length, case, diff) for future placeholder post-processing.
- Lightweight plugin hook for augmenting Options menu via `extra_items` callback.

## 0.2.1 - 2025-08-01
- Enhanced cross-platform compatibility for WSL2/Windows environments
- Fixed Unicode character encoding issues in PowerShell scripts  
- Improved WSL path detection and temporary file handling
- Enhanced prompts directory resolution with multiple fallback locations
- Updated all installation scripts for better cross-platform support
- Fixed package distribution to include prompts directory in all installations
- Added comprehensive error handling for missing prompts directory
- Made Windows keyboard library optional to prevent system hook errors
- Improved error handling for keyboard library failures with PowerShell fallback

## 0.2.1 - 2024-05-01
- Documentation overhaul with install instructions, template management guide and advanced configuration.
- `PROMPT_AUTOMATION_PROMPTS` and `PROMPT_AUTOMATION_DB` environment variables allow custom locations for templates and usage log.
