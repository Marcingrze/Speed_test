---
invokable: true
---

Review this code for potential issues, including:

Python, dependencies, and environment
- Minimum supported Python: docs mention 3.6+, but GUI deps (Kivy/KivyMD, Pillow 12) typically require 3.8+. Confirm and align README/INSTALLER/Makefile and installer checks.
- speedtest-cli 2.1.3 on Python 3.13: verify fileno() mitigation (KIVY_NO_CONSOLELOG=1 in GUI, AttributeError handling in core, fix_speedtest_py313.py usage in Makefile/install). Ensure CLI path never imports GUI modules.
- Dependency pinning: validate that pinned versions install cross-platform; consider constraints or relaxed pins where safe.

Core logic, validation, and error handling
- Config validation: ensure SpeedTestConfig.DEFAULT_CONFIG, VALIDATION_RULES, and ConfigValidator.SCHEMA stay in sync. Confirm logical consistency checks (typical < reasonable) and actionable warning messages.
- Result validation thresholds: assess defaults for typical/reasonable speeds/ping; ensure units correctness (bits_to_mbps) and consistent conversions.
- Connectivity pre-check: timeout tradeoffs for CLI vs GUI; avoid blocking the GUI thread.
- Retry/backoff: evaluate classification of retryable errors and exponential backoff with jitter; cap delays appropriately.
- Cancellation flow: distinguish cancelled vs failed runs; propagate is_cancelled to UI/CLI for correct UX.

Concurrency, threading, and responsiveness
- Progress callback: thread-safety and minimal work inside callback; verify no deadlocks around _callback_lock.
- Queues: AsyncSpeedTestRunner uses SimpleQueue for progress and bounded queue for result; confirm no backpressure stalls. In GUI, ensure Clock events are always unscheduled and threads joined with timeouts.
- Resource cleanup: verify speedtest client/opener closed in finally; ensure DB connections are closed on exceptions.

Storage, performance, and data integrity
- SQLite: WAL and busy_timeout are set—good. Confirm indices match query patterns (timestamp/date) and consider VACUUM/PRAGMA tuning if DB grows.
- Export scalability: CSV/JSON export should stream for large datasets (batched implemented)—verify memory usage and document limits.
- Schema: warnings stored as JSON text—ensure consistent encoding/decoding and null handling.

Scheduler and operations
- Monotonic scheduling is used—good. When offline, consider network_retry_delay behavior to avoid frequent checks. Verify graceful shutdown (signals, joins) and predictable state.
- Logging: prints/emojis are fine for CLI, but consider logging module for scheduler/service contexts.

CLI/UX and documentation
- CLI flags: consider JSON output and verbosity options for automation; ensure consistent language (README partly PL, messages EN). Align paths and names (speedtest_env vs ebv).
- Installer/systemd: validate user/group expectations, permissions on DB and working dir, and PATH instructions.

Security and portability
- File locking: shared flock on Unix, exclusive byte lock on Windows; document this behavior and ensure it won’t deadlock on network shares.
- Cross-platform support: clarify Windows/macOS support for GUI and installer steps.

Testing and CI
- Ensure tests run without network when flagged; add unit tests for retry/backoff, cancellation, storage exports, and scheduler timing. Consider CI across Python 3.8–3.13 on Linux/macOS/Windows.

Provide specific, actionable feedback for improvements.