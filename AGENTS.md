# Repository Overview

## Project Description
- What this project does
  - Measures internet performance via speedtest.net: download, upload, and latency (ping)
  - Offers three interfaces: CLI, a modern Kivy/KivyMD GUI, and a KDE Plasma widget
  - Stores results in SQLite with stats and export (CSV/JSON)
  - Supports automated scheduled testing with graceful shutdown
  - Validates configuration and results with sensible defaults and warnings
- Main purpose and goals  
  - Reliable, repeatable speed testing for personal and enterprise use
  - Clear separation of core logic from interfaces (CLI/GUI/Scheduler/Widget)
  - Error-tolerant operation with retries, validation, and actionable feedback
  - Historical analysis and automation (exports, stats)
- Key technologies used
  - Python (recommended 3.8+; some dependencies may not install on 3.6)
  - speedtest-cli 2.1.3
  - Kivy 2.3.1 and KivyMD 1.2.0 for GUI
  - SQLite (built-in) with WAL mode for persistence
  - requests (via speedtest-cli)
  - JSON configuration with file locking (fcntl/msvcrt)
  - Threading for async execution and responsive UI

## Architecture Overview
- High-level architecture
  - Core engine (speedtest_core.py) implements config loading/validation, connectivity checks, running tests with progress/cancellation, and result validation. It is UI-agnostic and reused by CLI, GUI, scheduler, and widget.
  - CLI (sp.py) is a thin wrapper: handles --create-config, runs a test, prints formatted results, saves to DB, and updates a widget cache.
  - GUI (speedtest_gui.py) uses Kivy/KivyMD, runs tests in a background thread via AsyncSpeedTestRunner, and animates real-time progress/results.
  - Scheduler (scheduled_testing.py) periodically runs tests using monotonic time, saves results, prints status, and can show stats or run an immediate test.
  - Storage (test_results_storage.py) encapsulates SQLite persistence, stats, export (CSV/JSON), cleanup, and info.
  - Config validation (config_validator.py) documents and validates the JSON config and syncs ranges with SpeedTestConfig.
  - Plasma widget (plasma-widget/) provides a QML UI that talks to a Python helper (speedtest_helper.py) to fetch latest results/run tests.
- Main components and their relationships
  - SpeedTestConfig -> SpeedTestEngine -> SpeedTestResult
  - AsyncSpeedTestRunner wraps SpeedTestEngine for GUI background operation
  - ScheduledTestRunner composes SpeedTestEngine and TestResultStorage for automation
  - TestResultStorage persists SpeedTestResult and provides analytics/exports
  - Plasma widget helper uses SpeedTestEngine/TestResultStorage for desktop display
- Data flow and system interactions
  1. Load configuration (defaults + optional speedtest_config.json; validation and warnings; file-lock guarded reads on Unix/Windows)
  2. Connectivity pre-check with timeout
  3. Server discovery and best server selection via speedtest-cli
  4. Download and upload tests with progress callbacks; supports cancellation
  5. Result validation (sanity checks; typical vs reasonable thresholds; warnings)
  6. Persist valid results in SQLite with indexes on timestamp/date
  7. Optional export to CSV/JSON and statistics queries
  8. Interfaces consume core via callbacks/queues; scheduler uses monotonic time; widget reads DB or triggers tests

## Directory Structure
- Important directories and their purposes
  - plasma-widget/                      KDE Plasma widget package (QML + helper)
  - .continue/rules/                    Custom Continue CLI slash commands
  - speedtest_env/ or ebv/              Local virtualenvs (created by Makefile/installer or manual)
  - backups/                            Optional backups created by Makefile
- Key files and configuration
  - speedtest_core.py                   Core engine, config, async runner, validation
  - sp.py                               CLI entry point delegating to core
  - speedtest_gui.py                    Kivy/KivyMD GUI application
  - speedtest_gui_fallback.py           Fallback GUI that can use Tkinter
  - scheduled_testing.py                Periodic background testing (scheduler)
  - test_results_storage.py             SQLite storage, stats, export, cleanup
  - config_validator.py                 Config schema validation and syncing
  - requirements.txt                    Pinned runtime dependencies
  - speedtest_config.json.example       Example configuration
  - speedtest_config.json               User configuration (gitignored)
  - fix_speedtest_py313.py              Helper patch for Python 3.13 compatibility
  - Makefile                            Common tasks (setup, run, test, lint, format, widget)
  - INSTALLER.md / install.py           Installer logic and docs
  - uninstall.py                        Uninstaller with optional full cleanup
  - QUICKSTART.md / README.md           User-facing documentation (PL/EN style)
  - IMPLEMENTATION_FIXES.md             Notes on specific fixes and improvements
  - EXECUTABLE_SETUP.md                 Executable setup instructions
  - plasma-widget/...                   QML UI and Python helper for KDE Plasma
- Entry points and main modules
  - CLI: python sp.py
  - GUI: python speedtest_gui.py
  - GUI fallback: python speedtest_gui_fallback.py
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
  - Provided tests and utilities:
    - python test_config_validation.py
    - python test_installation.py [--quick|--no-network]
    - python test_results_storage.py
  - Manual CLI/GUI testing under varying network conditions
  - Scheduler smoke tests with short intervals
- Development environment setup
  - make dev-setup installs pytest, black, flake8, mypy into the local venv
  - requirements.txt pins runtime deps: speedtest-cli, Kivy/KivyMD, Pillow, requests
  - On Python 3.13, apply fix_speedtest_py313.py or rely on core handling and KIVY_NO_CONSOLELOG=1
- Lint and format commands
  - make lint (flake8 with configured max line length and ignores)
  - make format (black with configured line length)

Notes and gotchas
- Dependency and Python versions: Kivy/KivyMD and Pillow versions typically require Python 3.8+; README mentions 3.6+. Prefer 3.8+ for GUI.
- speedtest-cli 2.1.3 has a known fileno() issue on Python 3.13 in some environments. GUI disables console logging; core handles AttributeError; fix_speedtest_py313.py can patch.
- On Unix, config reads use shared flock; on Windows, msvcrt-based locking results in an exclusive lock for a single byte. SQLite uses WAL and a busy timeout to improve concurrent access.
- Widget cache: CLI/GUI update ~/.cache/plasma-speedtest/widget_cache.json for quick widget display.
