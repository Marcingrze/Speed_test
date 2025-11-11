---
invokable: true
---

Review this code for potential issues, including:

Python, dependencies, and environment
- Version compatibility: requirements pin recent libs (e.g., Pillow 12.0.0, Kivy 2.3.1) while docs/installer mention Python 3.6+. Verify real minimum Python version and align README/INSTALLER/installer checks.
- speedtest-cli 2.1.3 on Python 3.13: confirm AttributeError fileno() mitigation (KIVY_NO_CONSOLELOG, try/except in core) and the fix_speedtest_py313.py guidance is accurate and referenced where needed.
- Optional GUI deps: ensure CLI paths don’t import Kivy/KivyMD inadvertently; graceful messages if GUI deps missing.
- Pinning policy: evaluate if pins are necessary and cross-platform installable; consider constraints files.

Error handling, retries, and cancellation
- Retry strategy in SpeedTestEngine.run_speed_test_with_retry: consider exponential backoff/jitter and clearer classification of retryable errors.
- Distinguish cancellation vs failure: currently cancellation yields an invalid result; propose a cancelled flag or exception to let UI/CLI show correct UX.
- Exception breadth: broad AttributeError except may mask unrelated bugs; tighten or log extra context.

Concurrency, threading, and GUI responsiveness
- Async progress queue backpressure: AsyncSpeedTestRunner uses Queue(maxsize=20) and blocking put. If full, producer blocks test thread. Consider put_nowait with queue.Full handling (drop oldest/newest) or unbounded SimpleQueue.
- Progress callback locking: verify no deadlocks and minimal work in callback.
- Kivy Clock events and dialogs: ensure events are always unscheduled on complete/cancel; confirm dialogs are dismissed and references cleared.

Core logic and validation
- Units consistency: bits vs Mbps conversion via config['bits_to_mbps']; verify correctness across all uses.
- Validation thresholds: sanity/typical/reasonable ranges—confirm defaults are sensible and warnings actionable.
- Connectivity check: timeout balance for UX; avoid blocking GUI thread.

Data persistence and performance
- SQLite usage: WAL and busy_timeout are set—good. Consider connection reuse if performance becomes an issue; ensure proper closing on exceptions.
- Indexes: you have idx_timestamp and idx_test_date, but date-range queries use timestamp; verify idx_test_date is needed or add test_date queries that benefit.
- Export scalability: CSV/JSON export reads all records when days is None; consider streaming/iterating for very large datasets.

Configuration and validation
- Keep ConfigValidator.SCHEMA and SpeedTestConfig.VALIDATION_RULES in sync (there is syncing code—validate coverage of all keys and ranges).
- File locking: fcntl shared locks on Unix only; on Windows msvcrt is imported but unused—consider a Windows-safe approach or document behavior.
- Error messaging: on invalid config, ensure warnings are concise and actionable.

Scheduler and long-running reliability
- Monotonic scheduling is used—good. When offline, consider using network_retry_delay between checks to avoid tight loops.
- Graceful shutdown: signals, thread joins, and resource cleanup—verify no orphaned threads and predictable shutdown.
- Logging: replace prints/emojis with logging module levels for services.

CLI/UX and documentation
- CLI flags are minimal; consider adding JSON output and verbosity levels for automation.
- Internationalization: README is Polish while code messages are English+emojis; align language and tone for target users or provide i18n.
- Consistency: Makefile lint ignores E501 while also setting max-line-length—clarify lint rules.

Security and operations
- Installer uses os.geteuid (Linux/Unix only); clarify Windows support or guard accordingly.
- Service setup: systemd unit assumes user/group "speedtest" and writable working dir; document/user creation and file permissions for DB/config paths.
- PATH instructions typo in install.py help ("~/. local/bin"): fix spacing.

Testing and CI
- Ensure tests can run offline (test_installation.py has --no-network) and add unit tests for validation, retry/backoff, cancellation, and storage.
- Consider adding CI to run lint/format/tests on Linux/macOS/Windows with different Python versions.

Provide specific, actionable feedback for improvements.