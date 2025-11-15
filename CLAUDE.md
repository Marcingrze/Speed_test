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
- Monotonic time-based interval scheduling with event-based waiting
- Graceful shutdown with signal handlers (SIGINT, SIGTERM)
- Persists results via TestResultStorage
- Constants: `OVERDUE_YIELD_SECONDS = 0.1`, `MAX_SLEEP_SECONDS = 60`
- Uses `threading.Event.wait()` for responsive shutdown (not fixed sleep)

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
- Auto-refreshes every 30 seconds, one-click "Run Speed Test" button
- Background test execution with visual feedback (spinner, notifications)
- Automatic result detection when test completes (checks every 5s, max 2 minutes)
- Desktop notifications for test start, completion, and errors
- Works in desktop or panel mode with dynamic tooltips and busy indicator

## Configuration System

Config loaded from `speedtest_config.json` (falls back to defaults if missing):
- Validation rules defined in `SpeedTestConfig.VALIDATION_RULES`
- `config_validator.py` uses lazy schema building from VALIDATION_RULES (no drift possible)
- Schema types auto-detected from `DEFAULT_CONFIG` values
- File locking via `fcntl` on Unix (shared locks during reads)
- Create config: `python sp.py --create-config`

Key settings: timeouts, retry logic, validation thresholds (typical vs reasonable speeds/pings)

**Important**: `config_validator.py` dynamically builds its schema from `SpeedTestConfig.VALIDATION_RULES` at runtime, ensuring they never drift out of sync. Add new validated fields to `VALIDATION_RULES` in `speedtest_core.py` and they automatically appear in the validator.

## Test Result Storage

All interfaces (CLI, GUI, scheduler, Plasma widget) share a unified SQLite database for test results.

**Database location**:
- **Unified path**: `~/.local/share/speedtest/speedtest_history.db`
- Directory created automatically on first use
- All components use the same centralized database via `TestResultStorage.get_default_db_path()`

**Database schema** (`test_results_storage.py`):
- `id` (INTEGER): Auto-incremented primary key
- `timestamp` (REAL): Unix timestamp (system time when test was executed)
- `download_mbps` (REAL): Download speed in Mbps
- `upload_mbps` (REAL): Upload speed in Mbps
- `ping_ms` (REAL): Latency in milliseconds
- `server_info` (TEXT): Speed test server information
- `is_valid` (BOOLEAN): Result validation status
- `warnings` (TEXT): JSON array of warnings (if any)
- `test_date` (TEXT): ISO 8601 formatted date/time (e.g., "2025-11-15T13:48:11.601623")
- Indexes on `timestamp` and `test_date` for performance
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
- Plasma widget: Reads latest results from shared database via `get_last_result()`
- Disable saving by setting `"save_results_to_database": false` in config file

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
- GUI cleanup uses class-level atexit flag to prevent duplicate registrations
- Thread join timeout capped at 30s to prevent UI blocking (daemon threads clean up)

### Error Handling & Retries
- Retry logic: Fixed delay between attempts (consider exponential backoff in future)
- Cancellation: Returns invalid result; callers should check `is_valid`
- Network errors categorized: connectivity, timeout, validation failures
- Broad `AttributeError` catching for Python 3.13 fileno() issues

### Result Validation
- Two-tier thresholds: typical (warn) vs reasonable (error)
- Validates: speed units (bits→Mbps conversion), ping ranges, negative values
- Warnings attached to results for display in UI
- Widget cache (`update_widget_cache()`) validates `result.is_valid` before caching
- Invalid results are never cached to prevent misleading widget displays

### File Operations
- Config: fcntl shared locks on Unix (Windows msvcrt imported but not used)
- SQLite: WAL mode, indexed queries, connection reuse via context managers
- SQLite connection initialization uses temp variable + `isolation_level=None` for atomicity
- Exports: Handle newlines/encoding for cross-platform CSV/JSON
- Database files (`*.db`, `*.db-shm`, `*.db-wal`) excluded from git via .gitignore

## Python 3.13 Compatibility Issue

**Problem**: speedtest-cli raises `AttributeError` on `sys.stderr.fileno()` in Kivy environments

**Automatic Fix**: The installer now automatically applies the patch during setup:
- `install.py` runs `fix_speedtest_py313.py` after installing dependencies
- `make setup` includes the patch step
- `make update` reapplies the patch after updating dependencies

**Manual Fix** (if needed): Run `python fix_speedtest_py313.py` in the venv

**GUI Workaround**: Sets `KIVY_NO_CONSOLELOG=1` to disable console logging

## KDE Plasma Widget Development

### Widget Architecture
The Plasma widget consists of three main components:
1. **QML Frontend** (`main.qml`): User interface with two representations
   - Full representation: Detailed view with results, buttons, status indicators
   - Compact representation: Panel/tray icon with tooltip
2. **Python Backend** (`speedtest_helper.py`): Handles all business logic
   - `get_last`: Retrieves most recent result from database
   - `run_test`: Launches background speed test via `sp.py`
   - `check_network`: Verifies network connectivity
3. **Shell Wrapper** (`run_helper.sh`): Bridges QML DataSource to Python

### Widget Update Flow
```
User clicks "Run Test" → helperDS.run("run_test")
                      ↓
         speedtest_helper.py executes
                      ↓
         Spawns sp.py in background (detached process)
                      ↓
         Returns JSON: {"status": "success", "message": "..."}
                      ↓
         QML shows notification + spinner
                      ↓
         Timer polls every 5s for new results
                      ↓
         When timestamp changes → test complete!
                      ↓
         Show completion notification + update UI
```

### Testing Widget Changes
After modifying QML or Python code:
```bash
make install-plasmoid    # Reinstall widget
make restart-plasma      # Restart Plasma Shell
```

Or manually:
```bash
cd plasma-widget
./install_plasmoid.sh
kquitapp6 plasmashell && plasmashell --replace &
```

### Widget State Management
- `isRunning`: Boolean flag indicating test in progress
- `hasData`: True when valid results are loaded
- `networkConnected`: True when connectivity check passes
- `lastUpdate`: Timestamp string used for change detection
- Buttons enabled/disabled based on state combinations

### Debugging Widget
- Widget logs: `~/.local/share/plasma_speedtest.log`
- Plasma logs: `journalctl -f | grep plasma`
- QML console: Check `journalctl` for `[SpeedTest Widget]` messages

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
- Atexit handlers for guaranteed cleanup (use class-level flags to prevent duplicates)

## Recent Code Quality Improvements (Jan 2025)

The codebase recently underwent comprehensive code review addressing critical issues:

### Config Validator Architecture
- **Dynamic schema building**: Schema is built at runtime from `SpeedTestConfig.VALIDATION_RULES`
- **Lazy initialization**: Schema cached on first access, not at import time
- **Type inference**: Field types auto-detected from `DEFAULT_CONFIG` values
- **Zero drift**: Schema and validation rules cannot drift - single source of truth

### Resource Cleanup Patterns
- **GUI atexit handlers**: Class-level `_atexit_registered` flag prevents duplicate registrations
- **Cleanup state tracking**: `_cleanup_done` flag for safe multiple calls
- **SQLite atomicity**: Connection init uses `temp_conn` + `isolation_level=None` pattern
- **Thread join timeouts**: Capped at 30s to prevent UI freezing (not complex worst-case calculations)

### Widget Cache Security
- **Result validation**: `update_widget_cache()` checks `result.is_valid` before caching
- **Invalid result filtering**: Prevents misleading displays in Plasma widget
- **Status differentiation**: Cache sets `"status": "success" if is_valid else "failed"`

### Scheduler Timing Precision
- **Named constants**: `OVERDUE_YIELD_SECONDS`, `MAX_SLEEP_SECONDS` instead of magic numbers
- **Monotonic time reuse**: Calculates sleep duration from already-obtained timestamp
- **Event-based waiting**: `threading.Event.wait(timeout)` instead of `time.sleep()`

### Error Handling Specificity
- **Categorized exceptions**: Config errors separated into `IOError/OSError` vs `TypeError/KeyError/ValueError`
- **Validation vs IO errors**: Different messages for file access vs data validation failures
- **Lock release comments**: Clarified which `finally` block releases which lock

When making changes, maintain these patterns and quality standards.
