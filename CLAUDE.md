# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Internet speed testing tool with multiple interfaces: CLI, GUI (KivyMD), and KDE Plasma widget. Uses speedtest.net to measure download/upload speeds and ping latency. Includes scheduled testing, SQLite result storage, and data export capabilities.

## Quick Start

```bash
# Setup
make setup          # Create venv and install dependencies
make dev-setup      # Add pytest, black, flake8, mypy
make install        # Install executable scripts system-wide (requires sudo)
make install-user   # Install for current user only (~/.local/bin)

# Run
make run-cli        # CLI interface (direct Python)
make run-gui        # GUI interface (direct Python)
make run-scheduler  # Background scheduler (direct Python)

# After installation, you can also run:
speedtest-cli       # Installed CLI command
speedtest-gui       # Installed GUI command
speedtest-scheduler # Installed scheduler command

# Test & Quality
make test           # Quick functionality tests (test_installation.py --quick)
make test-full      # Complete test suite (test_installation.py)
make test-offline   # Tests without network (test_installation.py --no-network)
make lint           # Run flake8 (ignores E501, max-line-length=100)
make format         # Format with black (line-length=100)

# Direct test runs (after setup)
./speedtest_env/bin/python3 test_installation.py --quick
./speedtest_env/bin/python3 test_config_validation.py

# Maintenance
make update         # Update dependencies (reapplies Python 3.13 patch)
make backup         # Backup config and database
make restore        # Restore from latest backup
make clean          # Clean temporary files

# KDE Plasma Widget
make install-plasmoid   # Install KDE Plasma desktop widget
make uninstall-plasmoid # Uninstall Plasma widget
make restart-plasma     # Restart Plasma Shell
```

## Architecture

**Multi-Interface Architecture**: Business logic is separated from UI, allowing CLI, GUI, and scheduler to share the same testing engine.

### Core Flow
```
SpeedTestConfig → SpeedTestEngine → SpeedTestResult
                       ↓
      ┌────────────────┼────────────────┬────────────────┐
      ↓                ↓                ↓                ↓
   CLI (sp.py)    GUI (async)     Scheduler      KDE Widget (QML)
                      ↓                ↓                ↓
                Progress        TestResultStorage   Helper Script
                Callbacks           (SQLite)        (Python→DB)
```

### Key Modules

**speedtest_core.py** - Core business logic (UI-agnostic)
- `SpeedTestConfig`: Configuration with validation rules and file locking (Unix fcntl)
- `SpeedTestEngine`: Main engine with retry logic, connectivity checks, result validation
- `SpeedTestResult`: Result data class with warnings
- `AsyncSpeedTestRunner`: Threaded runner for GUI with cancellation support

**sp.py** - CLI frontend (lightweight wrapper)
- Delegates all logic to SpeedTestEngine
- Only handles `--create-config` flag and result display

**speedtest_gui.py** - KivyMD GUI
- Material Design interface with real-time progress
- Runs tests in background thread via AsyncSpeedTestRunner
- Uses progress callbacks and Kivy Clock for UI updates

**test_results_storage.py** - SQLite persistence
- WAL mode with busy timeout for concurrent access
- Indexed timestamp/date columns for performance
- Export to CSV/JSON, statistics queries

**scheduled_testing.py** - Background scheduler
- Monotonic time-based interval scheduling
- Graceful shutdown with signal handlers
- Persists results via TestResultStorage

**install.py** - Installation script
- Creates executable wrappers for CLI/GUI/scheduler
- Supports system-wide (/usr/local/bin) or user (~/.local/bin) installation
- Auto-creates venv, installs dependencies, applies Python 3.13 patch
- Platform-aware: detects Unix/Windows, adjusts paths accordingly

**uninstall.py** - Uninstallation script
- Removes installed executables
- Optionally removes config and database (--remove-all flag)

**config_validator.py** - Configuration schema validation
- Imports SpeedTestConfig.VALIDATION_RULES to stay in sync
- Validates types, ranges, and required fields
- Detects drift between schema and core config

**plasma-widget/** - KDE Plasma desktop widget
- **org.kde.plasma.speedtest/metadata.json**: Widget metadata and KDE integration
- **contents/ui/main.qml**: QML interface with full and compact representations
- **contents/code/speedtest_helper.py**: Python backend (gets DB results, runs tests, checks network)
- Communicates via JSON over PlasmaCore.DataSource executable engine
- Auto-refreshes every 30 seconds, one-click test execution
- Works in desktop or panel mode with tooltips

## Configuration System

Config loaded from `speedtest_config.json` (falls back to defaults if missing):
- Validation rules defined in `SpeedTestConfig.VALIDATION_RULES`
- Config must stay in sync with `config_validator.py` schema (uses import to avoid drift)
- File locking via `fcntl` on Unix (shared locks during reads)
- Create config: `python sp.py --create-config`

Key settings: timeouts, retry logic, validation thresholds (typical vs reasonable speeds/pings)

## Test Result Storage

All interfaces (CLI, GUI, scheduler) can persist results to SQLite database (`speedtest_history.db`):

**Database schema** (`test_results_storage.py`):
- Timestamps (indexed), download/upload speeds, ping, server info, validation status, warnings
- WAL journal mode for concurrent access
- Busy timeout: 5 seconds

**Export capabilities**:
- CSV: `TestResultStorage.export_to_csv(filename, days=None)`
- JSON: `TestResultStorage.export_to_json(filename, days=None)`
- Statistics: `get_statistics(days=None)` returns min/max/avg/median for speeds and ping

**Configuration** (`save_results_to_database`):
- Enabled by default (`true` in `speedtest_config.json`)
- When enabled, all successful test results are automatically saved to database
- CLI shows: "Result saved to database (ID: <record_id>)" after successful test
- GUI silently saves results (prints to console if KIVY_NO_CONSOLELOG is not set)
- Scheduler always saves results regardless of this setting

**Usage**:
- CLI: Results saved automatically after each successful test
- GUI: Results saved automatically in `handle_test_result()` after successful test
- Scheduler: Results saved via `TestResultStorage.save_result()` after each test
- Disable by setting `"save_results_to_database": false` in config file

## Dependencies

- **Python 3.8+**: Required by Pillow 12.0.0 and Kivy 2.3.1 (README mentions 3.6+ but this is outdated)
- **speedtest-cli 2.1.3**: Requires Python 3.13 patch via `fix_speedtest_py313.py`
- **Kivy 2.3.1 + KivyMD 1.2.0**: GUI framework (Material Design)
- **Pillow 12.0.0**: Image processing for Kivy (requires Python 3.8+)
- **SQLite3**: Built into Python, used for test result storage

## Critical Implementation Patterns

### Threading & Concurrency
- GUI runs tests in background via `AsyncSpeedTestRunner`
- Progress updates use bounded queues (maxsize=20) to prevent blocking
- Kivy Clock events schedule UI updates on main thread
- SQLite uses WAL mode + busy timeout (5s) for concurrent access

### Error Handling & Retries
- Retry logic: Fixed delay between attempts (consider exponential backoff in future)
- Cancellation: Returns invalid result; callers should check `is_valid`
- Network errors categorized: connectivity, timeout, validation failures
- Broad `AttributeError` catching for Python 3.13 fileno() issues

### Result Validation
- Two-tier thresholds: typical (warn) vs reasonable (error)
- Validates: speed units (bits→Mbps conversion), ping ranges, negative values
- Warnings attached to results for display in UI

### File Operations
- Config: fcntl shared locks on Unix (Windows msvcrt imported but not used)
- SQLite: WAL mode, indexed queries, connection reuse via context managers
- Exports: Handle newlines/encoding for cross-platform CSV/JSON

## Python 3.13 Compatibility Issue

**Problem**: speedtest-cli raises `AttributeError` on `sys.stderr.fileno()` in Kivy environments

**Automatic Fix**: The installer now automatically applies the patch during setup:
- `install.py` runs `fix_speedtest_py313.py` after installing dependencies
- `make setup` includes the patch step
- `make update` reapplies the patch after updating dependencies

**Manual Fix** (if needed): Run `python fix_speedtest_py313.py` in the venv

**GUI Workaround**: Sets `KIVY_NO_CONSOLELOG=1` to disable console logging

## Code Review Guidelines

This project includes custom code review configurations:

**For Continue CLI**: Use `/review` slash command
- Defined in `.continue/rules/review.md`
- Covers version compatibility, retry logic, concurrency, validation, and more
- Provides specific project-aware review criteria

**For Claude Code**: Use `python-code-reviewer` agent
- Defined in `.claude/agents/python-code-reviewer.md`
- Automatically invoked after significant code changes
- Multi-layered analysis with severity classification (CRITICAL → NICE TO HAVE)
- Checks functionality, correctness, security, performance, maintainability

### Key Review Focus Areas

Thread safety and concurrency:
- GUI callbacks and queue handling (AsyncSpeedTestRunner)
- Kivy Clock event scheduling and cleanup
- SQLite WAL mode and busy timeout handling

Configuration management:
- Consistency between `SpeedTestConfig.VALIDATION_RULES` and `config_validator.py`
- The validator imports VALIDATION_RULES to detect drift
- File locking: fcntl on Unix (shared locks), msvcrt on Windows (exclusive only)

Python 3.13 compatibility:
- Broad `AttributeError` catching for fileno() issues
- `KIVY_NO_CONSOLELOG=1` environment variable for GUI
- Automatic patch application via `fix_speedtest_py313.py`

Error handling patterns:
- Fixed retry delay (consider exponential backoff for improvements)
- Cancellation returns invalid result (callers check `is_valid`)
- Network error categorization (connectivity, timeout, validation)

Resource management:
- Connection cleanup (network sockets, file handles)
- Thread lifecycle (join with timeout, daemon threads)
- SQLite connection reuse via context managers
