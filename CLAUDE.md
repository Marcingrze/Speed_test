# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Internet speed testing tool with both CLI and GUI interfaces. Uses speedtest.net to measure download/upload speeds and ping latency, with advanced features including scheduled testing, result storage, and data export.

## Environment Setup

The project uses a Python virtual environment. Use either the existing `ebv/` or the installer's `speedtest_env/`:

```bash
# For development with existing environment
source ebv/bin/activate
pip install -r requirements.txt

# OR use Makefile for complete setup
make setup          # Creates speedtest_env/ and installs dependencies
make dev-setup      # Adds development tools (pytest, black, flake8, mypy)

# Install as executable commands (creates scripts in /usr/local/bin or ~/.local/bin)
make install        # System-wide (requires sudo)
make install-user   # Current user only
```

## Running the Application

```bash
# Development mode (activate venv first: source ebv/bin/activate)
python sp.py                              # CLI
python sp.py --create-config             # Create config file
python speedtest_gui.py                  # GUI
python scheduled_testing.py --interval 60 # Scheduler

# OR use Makefile shortcuts (handles venv automatically)
make run-cli
make run-gui
make run-scheduler
make config                               # Create speedtest_config.json

# OR use installed commands (after make install)
speedtest-cli                             # CLI test
speedtest-gui                             # GUI interface
speedtest-scheduler --immediate           # Single scheduled test
speedtest-scheduler --interval 30         # Test every 30 minutes
speedtest-scheduler --stats --days 7      # Show statistics
speedtest-storage export csv results.csv  # Export to CSV
```

## Architecture

### Core Components

**Multi-Interface Architecture**: The project separates business logic from UI, allowing different frontends (CLI, GUI) to share the same testing engine.

- **speedtest_core.py**: Core business logic module
  - `SpeedTestConfig`: Configuration management with validation
  - `SpeedTestEngine`: Main testing engine with retry logic and error handling
  - `SpeedTestResult`: Data class for test results
  - `AsyncSpeedTestRunner`: Threaded runner for GUI integration

- **sp.py**: CLI frontend
  - Command-line interface with progress indicators
  - Uses SpeedTestEngine from speedtest_core
  - Supports `--create-config` flag to generate speedtest_config.json

- **speedtest_gui.py**: KivyMD GUI frontend
  - Material Design interface with real-time progress updates
  - Asynchronous testing via AsyncSpeedTestRunner
  - Progress callbacks for UI updates
  - Thread-safe operations

### Storage & Scheduling

- **test_results_storage.py**: SQLite-based persistence
  - Stores historical test results
  - Export to CSV/JSON
  - Statistical analysis (averages, trends)

- **scheduled_testing.py**: Background test scheduler
  - Runs tests at configurable intervals
  - Integrates with TestResultStorage
  - Can run as daemon

### Utilities

- **config_validator.py**: Configuration validation logic
- **test_config_validation.py**: Test suite for config validation
- **fix_speedtest_py313.py**: Python 3.13 compatibility patch for speedtest-cli

## Configuration

Configuration is managed via `speedtest_config.json`:

```json
{
  "bits_to_mbps": 1000000,
  "connectivity_check_timeout": 10,
  "speedtest_timeout": 60,
  "max_retries": 3,
  "retry_delay": 2,
  "max_typical_speed_gbps": 1,
  "max_reasonable_speed_gbps": 10,
  "max_typical_ping_ms": 1000,
  "max_reasonable_ping_ms": 10000,
  "show_detailed_progress": true
}
```

- All configuration keys have validation rules defined in `SpeedTestConfig.VALIDATION_RULES`
- If config file is missing, defaults from `DEFAULT_CONFIG` are used
- CLI can create example config with `python sp.py --create-config`

## Key Dependencies

- **speedtest-cli==2.1.3**: Core testing library (requires Python 3.13 patch - see below)
- **Kivy==2.3.1**: Multi-platform GUI framework
- **KivyMD==1.2.0**: Material Design components for Kivy
- **Pillow==12.0.0**: Image processing for Kivy

## Python 3.13 Compatibility

The speedtest-cli library has a compatibility issue with Python 3.13 in Kivy environments (AttributeError on sys.stderr.fileno()).

**Fix**: Run the patch script once after installing dependencies:
```bash
python fix_speedtest_py313.py
```

This patches the speedtest module to catch AttributeError in addition to OSError.

## Data Flow

1. **CLI Testing**: sp.py → SpeedTestEngine → speedtest-cli → Results displayed
2. **GUI Testing**: speedtest_gui.py → AsyncSpeedTestRunner (thread) → SpeedTestEngine → Progress callbacks → UI updates
3. **Scheduled Testing**: scheduled_testing.py → SpeedTestEngine → TestResultStorage (SQLite)

## Testing & Development

```bash
# Run functionality tests
make test              # Basic tests (quick)
make test-full         # Complete test suite
make test-offline      # Tests without network
python test_config_validation.py  # Config validation tests
python test_installation.py       # Installation verification

# Code quality
make lint              # Run flake8 linter
make format            # Format with black

# Database operations
sqlite3 speedtest_history.db "SELECT * FROM test_results ORDER BY timestamp DESC LIMIT 10;"
speedtest-storage stats --days 30  # Statistics
speedtest-storage export csv data.csv  # Export data

# Maintenance
make clean             # Remove __pycache__ and temp files
make backup            # Backup config and database
make restore           # Restore from latest backup
make update            # Update dependencies
```

## Important Implementation Details

- **Thread Safety**: GUI uses threading to prevent UI blocking during tests. AsyncSpeedTestRunner manages the worker thread and provides callbacks for progress updates.
- **Error Handling**: SpeedTestEngine implements retry logic with configurable attempts and delays. All errors are categorized (network, timeout, validation).
- **Result Validation**: Results are validated against configured thresholds (max_typical_speed_gbps, max_reasonable_speed_gbps, etc.) with warnings for suspicious values.
- **Progress Tracking**: Both CLI and GUI receive progress updates through callbacks with stage information (connecting, downloading, uploading).
- **Installation System**: The `install.py` script creates bash wrapper scripts that activate the virtual environment and run the Python applications. These wrappers are placed in `/usr/local/bin` (system) or `~/.local/bin` (user mode).
- **File Locking**: Uses fcntl (Unix) or msvcrt (Windows) for safe concurrent access to shared resources.

## Known Issues

- **Python 3.13 Compatibility**: speedtest-cli has an AttributeError with sys.stderr.fileno() in Kivy environments. Run `python fix_speedtest_py313.py` to patch the module after installation.
- **File Permissions**: Some files may be owned by root, others by marcin. Be aware of permission issues when editing or running commands.
- **Virtual Environment**: The codebase references both `ebv/` (existing) and `speedtest_env/` (created by installer). Both are valid - use whichever exists in your environment.
