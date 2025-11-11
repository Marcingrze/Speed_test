# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Internet speed testing tool with CLI and GUI interfaces. Uses speedtest.net to measure download/upload speeds and ping latency. Includes scheduled testing, SQLite result storage, and data export capabilities.

## Quick Start

```bash
# Setup
make setup          # Create venv and install dependencies
make dev-setup      # Add pytest, black, flake8, mypy

# Run
make run-cli        # CLI interface
make run-gui        # GUI interface
make run-scheduler  # Background scheduler

# Test & Quality
make test           # Quick functionality tests
make test-full      # Complete test suite
make lint           # Run flake8
make format         # Format with black
```

## Architecture

**Multi-Interface Architecture**: Business logic is separated from UI, allowing CLI, GUI, and scheduler to share the same testing engine.

### Core Flow
```
SpeedTestConfig → SpeedTestEngine → SpeedTestResult
                       ↓
      ┌────────────────┼────────────────┐
      ↓                ↓                ↓
    CLI (sp.py)    GUI (async)    Scheduler
                       ↓                ↓
                 Progress        TestResultStorage
                 Callbacks           (SQLite)
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

## Configuration System

Config loaded from `speedtest_config.json` (falls back to defaults if missing):
- Validation rules defined in `SpeedTestConfig.VALIDATION_RULES`
- Config must stay in sync with `config_validator.py` schema (uses import to avoid drift)
- File locking via `fcntl` on Unix (shared locks during reads)
- Create config: `python sp.py --create-config`

Key settings: timeouts, retry logic, validation thresholds (typical vs reasonable speeds/pings)

## Dependencies

- **speedtest-cli 2.1.3**: Requires Python 3.13 patch via `fix_speedtest_py313.py`
- **Kivy 2.3.1 + KivyMD 1.2.0**: GUI framework (Material Design)
- **Python**: Pillow 12 and Kivy require 3.8+, not 3.6 (docs may be outdated)

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

This project includes custom slash commands for Continue CLI and Claude Code:
- **Continue**: `/review` command defined in `.continue/rules/review.md`
- **Claude Code**: `python-code-reviewer` agent in `.claude/agents/`

When reviewing code, focus on:
- Thread safety (GUI callbacks, queue handling, Clock scheduling)
- Config validation consistency between `SpeedTestConfig.VALIDATION_RULES` and `config_validator.py`
- SQLite connection management and index usage
- Python 3.13 compatibility (AttributeError handling)
- Network retry strategy and cancellation UX
- Resource cleanup (connections, file handles, threads)
