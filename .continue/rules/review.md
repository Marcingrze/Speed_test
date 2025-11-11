---
invokable: true
---

Review this code for potential issues, including:

Python, dependencies, and environment
- Python/version compatibility: verify requirements vs supported Python. Pillow 12 and Kivy 2.3.1 may require newer Python than 3.6; ensure docs and Makefile reflect actual minimum version
- speedtest-cli 2.1.3 on Python 3.13: confirm AttributeError fileno() handling and Kivy env vars (KIVY_NO_CONSOLELOG) are sufficient; ensure fix_speedtest_py313.py guidance is current
- Optional dependency handling: graceful failure if Kivy/KivyMD are missing when running CLI-only; avoid import-time crashes
- Pinning policy: check if pinned versions are still maintained and compatible across platforms

Error handling, retries, and cancellation
- Network error handling: coverage for speedtest.SpeedtestException, ConfigRetrievalError, NoMatchedServers, timeouts, and OS/network errors
- Retry strategy: consider exponential backoff or jitter instead of fixed retry_delay for transient failures; ensure max_retries bounds are respected
- Cancellation path: when cancelled, run_speed_test_with_retry returns a default, invalid result. Ensure callers can distinguish cancellation vs failure and surface appropriate UX
- Broad AttributeError excepts: confirm they won’t mask unrelated bugs beyond Python 3.13 fileno cases

Concurrency, threading, and GUI responsiveness
- Thread safety: verify access to progress callback under lock; ensure no deadlocks
- Queue capacity: AsyncSpeedTestRunner uses bounded queues (progress maxsize=20). Ensure producers won’t block indefinitely; consider non-blocking put with drop-old strategy if needed
- Kivy Clock events: confirm Clock.schedule_interval is always unscheduled on completion/cancel to avoid leaks
- Animation/dialog lifecycle: verify dialogs are dismissed and references cleared to prevent memory leaks

Core logic and result validation
- Validation thresholds: sanity, typical vs reasonable ranges; confirm units consistency (bits vs Mbps) and division by config['bits_to_mbps]
- Handling extreme or negative values: ensure invalid structures return actionable warnings
- Connectivity pre-check: balance timeout and user experience; confirm it avoids blocking the GUI thread

Data persistence and performance
- SQLite setup: WAL mode and busy timeout are set; validate correct use and close semantics; consider connection reuse or context managers everywhere
- Indexes: idx_timestamp and idx_test_date exist; confirm queries use them (especially date range)
- Data types: is_valid stored as BOOLEAN; verify cross-platform truthiness and query filters
- Export scalability: streaming large exports (CSV/JSON) and proper encoding; consider newline handling on Windows
- Migration/compatibility: no schema versioning; suggest lightweight migrations for future changes

Configuration and validation
- Consistency between SpeedTestConfig.VALIDATION_RULES and ConfigValidator.SCHEMA; ensure no drift (there is syncing code—verify it’s effective)
- File locking: fcntl shared locks on Unix; confirm safe behavior on Windows where msvcrt is imported but not used; consider advisory locking alternative on Windows
- Error messaging: when falling back to defaults, ensure warnings are user-actionable and not too verbose

Scheduler and long-running reliability
- Monotonic time: confirm consistent use for interval scheduling; check for clock drift edge cases
- Graceful shutdown: signal handlers and thread joins; ensure no orphaned threads and predictable exit
- Backoff when offline: consider using network_retry_delay between failed connectivity checks

CLI/UX and logging
- CLI sp.py minimal flags: verify outputs and exit codes; consider adding verbosity and JSON output for automation
- Logging vs print: recommend a logging framework with levels for production use and headless environments
- Internationalization: README is in Polish; ensure CLI/UX messages are consistent with target audience

Security and data integrity
- File path and permissions: ensure speedtest_history.db and config locations are writable in service mode; Makefile’s systemd service uses user “speedtest” (ensure user/group and dirs exist)
- Input validation: sanitize user-provided paths/args for export commands
- Data integrity: ensure atomic writes for config and exports; consider fsync where necessary

Testing and maintainability
- Tests should be network-optional; verify test_installation.py supports --no-network paths without real HTTP calls
- Add unit tests for validation, retry logic, cancellation, and storage
- Consider CI to run lint/format/tests across Linux/macOS/Windows

Provide specific, actionable feedback for improvements.