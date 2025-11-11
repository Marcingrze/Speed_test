# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Internet speed testing tool with both CLI and GUI interfaces. Uses speedtest.net to measure download/upload speeds and ping latency, with advanced features including scheduled testing, result storage, and data export.

## Environment Setup

The project uses a Python virtual environment named `ebv/`:

```bash
# Activate the virtual environment
source ebv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Running the Application

```bash
# Always activate virtual environment first
source ebv/bin/activate

# CLI application (basic usage)
python sp.py

# CLI with config file creation
python sp.py --create-config

# GUI application (KivyMD interface)
python speedtest_gui.py

# Scheduled testing (background daemon)
python scheduled_testing.py --interval 60  # Test every 60 minutes
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

## Common Development Tasks

```bash
# Test CLI changes
python sp.py

# Test GUI changes
python speedtest_gui.py

# Run config validation tests
python test_config_validation.py

# Create/modify configuration
python sp.py --create-config
nano speedtest_config.json

# View stored results (requires manual SQLite query or export)
# Results stored in speedtest_history.db
```

## Important Implementation Details

- **Thread Safety**: GUI uses threading to prevent UI blocking during tests. AsyncSpeedTestRunner manages the worker thread and provides callbacks for progress updates.
- **Error Handling**: SpeedTestEngine implements retry logic with configurable attempts and delays. All errors are categorized (network, timeout, validation).
- **Result Validation**: Results are validated against configured thresholds (max_typical_speed_gbps, max_reasonable_speed_gbps, etc.) with warnings for suspicious values.
- **Progress Tracking**: Both CLI and GUI receive progress updates through callbacks with stage information (connecting, downloading, uploading).

## File Ownership Note

Some files are owned by root, others by marcin. When editing, be aware of potential permission issues.
