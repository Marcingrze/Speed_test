# Repository Overview

## Project Description
- What this project does
  - Professional Python tool to measure internet performance using speedtest.net: download, upload, and latency (ping)
  - Provides both a CLI and a modern Material Design GUI with real-time progress
  - Persists results to SQLite with statistics and export (CSV/JSON)
  - Supports automated scheduled background testing with graceful shutdown
  - Robust configuration and validation system with sensible defaults and fallbacks
- Main purpose and goals
  - Reliable, repeatable speed testing for personal and enterprise use
  - Clear separation of core testing logic from interfaces (CLI/GUI/Scheduler)
  - Error-tolerant operation with retries, validation, and actionable feedback
  - Historical analysis, reporting, and automation
- Key technologies used
  - Python 3.6+ (GUI stack generally runs best on Python 3.8+)
  - speedtest-cli 2.1.3
  - Kivy 2.3.1 and KivyMD 1.2.0 (GUI)
  - SQLite (built-in) for persistent storage
  - requests for ancillary HTTP operations (via speedtest-cli)
  - JSON configuration with validation and Unix file locking
  - Threading for async execution and responsive GUI

## Architecture Overview
- High-level architecture
  - Core engine (speedtest_core.py) implements business logic, progress callbacks, cancellation, and result validation. This module is UI-agnostic and reused by CLI, GUI, and scheduler.
  - CLI (sp.py) is a thin wrapper around the core, handling minimal arguments and displaying results.
  - GUI (speedtest_gui.py) provides a Material Design interface using Kivy/KivyMD, running tests in background threads and reflecting progress via callbacks.
  - Scheduler (scheduled_testing.py) runs tests periodically in a background thread, saving results to SQLite and reporting status.
  - Storage (test_results_storage.py) encapsulates SQLite persistence, statistics, and export features.
  - Configuration (speedtest_core.SpeedTestConfig and config_validator.py) loads, validates, and documents configuration, including shared file locking on Unix.
- Main components and their relationships
  - SpeedTestConfig -> SpeedTestEngine -> SpeedTestResult
  - AsyncSpeedTestRunner wraps SpeedTestEngine for GUI background operation
  - ScheduledTestRunner composes SpeedTestEngine and TestResultStorage for automation
  - TestResultStorage persists SpeedTestResult and provides analytics/exports
- Data flow and system interactions
  1. Load configuration (defaults + optional JSON file; validation and warnings)
  2. Connectivity pre-check with timeout
  3. Server discovery and best server selection via speedtest-cli
  4. Download and upload tests with progress callbacks
  5. Result validation (sanity checks, typical vs reasonable thresholds)
  6. Persist valid results in SQLite with indexed timestamp/date
  7. Optional export to CSV/JSON and statistics queries
  8. GUI updates progress/results via callback queues; scheduler runs periodically using monotonic time

## Directory Structure
- Important directories and their purposes
  - .continue/      Custom Continue CLI rules (slash commands like /review)
  - backups/        Optional backups created via Makefile targets
  - speedtest_env/  Project-local virtualenv created by Makefile/installer
  - ebv/            Alternate virtualenv mentioned in docs (optional)
- Key files and configuration
  - speedtest_core.py               Core engine, config, async runner, validation
  - sp.py                           CLI entry point delegating to core
  - speedtest_gui.py                Kivy/KivyMD GUI application
  - speedtest_gui_fallback.py       Alternative GUI implementation (legacy/fallback)
  - scheduled_testing.py            Periodic background testing (scheduler)
  - test_results_storage.py         SQLite storage, stats, export
  - config_validator.py             Config schema validation and tooling
  - requirements.txt                Pinned dependencies (CLI+GUI)
  - speedtest_config.json.example   Example configuration
  - speedtest_config.json           User configuration (gitignored)
  - fix_speedtest_py313.py          Patch helper for Python 3.13 compatibility
  - Makefile                        Common tasks (setup, run, test, lint, format)
  - INSTALLER.md / install.py       Installer logic and docs
  - uninstall.py                    Uninstaller with optional full cleanup
  - QUICKSTART.md / README.md       User-facing documentation
  - IMPLEMENTATION_FIXES.md         Notes on specific fixes and improvements
  - EXECUTABLE_SETUP.md             Executable setup instructions
- Entry points and main modules
  - CLI: python sp.py
  - GUI: python speedtest_gui.py
  - Scheduler: python scheduled_testing.py
  - Storage management: python test_results_storage.py [stats|export|info|cleanup]
  - Config validation: python config_validator.py [--schema|<config.json>]

## Development Workflow
- How to build/run the project
  - Using Makefile
    - make setup (create venv and install deps into speedtest_env)
    - make run-cli / make run-gui / make run-scheduler
    - make install or python install.py [--user] to generate executables
  - Manually
    - python3 -m venv speedtest_env; source speedtest_env/bin/activate
    - pip install -r requirements.txt
    - python sp.py (CLI), python speedtest_gui.py (GUI), python scheduled_testing.py (scheduler)
- Testing approach
  - Configuration validation and installer tests are provided
    - python test_config_validation.py
    - python test_installation.py [--quick|--no-network]
    - python test_results_storage.py
  - Manual CLI/GUI testing under varying network conditions
  - Scheduler smoke tests with short intervals in a controlled environment
- Development environment setup
  - make dev-setup installs pytest, black, flake8, mypy into the local venv
  - requirements.txt pins runtime deps: speedtest-cli, Kivy/KivyMD, Pillow, requests
  - Note: On Python 3.13, apply fix_speedtest_py313.py or rely on built-in AttributeError handling in core and disabled Kivy console logging
- Lint and format commands
  - make lint (flake8 with configured max line length and ignores)
  - make format (black with configured line length)

Notes and gotchas
- speedtest-cli 2.1.3 has a known fileno() issue under Python 3.13 in some environments. The GUI sets KIVY_NO_CONSOLELOG=1 to mitigate, and the core handles AttributeError; fix_speedtest_py313.py provides a patch helper as well.
- On Unix, configuration file reads are protected by a shared flock; on Windows, the code avoids fcntl. SQLite uses WAL mode and a busy timeout to improve concurrent access.
- The Makefile virtual environment directory (speedtest_env) differs from the repo’s ebv/ directory used in docs; you may use either approach consistently in your setup.
