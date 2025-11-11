---
invokable: true
---

Review this code for potential issues, including:

**Python & Speed Testing Specific Issues:**
- **Network Error Handling**: Check for proper exception handling of `speedtest.SpeedtestException`, `ConfigRetrievalError`, `NoMatchedServers`, and network timeouts
- **Thread Safety**: Verify proper use of threading locks, queue operations, and safe resource cleanup in GUI and async components
- **Resource Leaks**: Ensure speedtest client cleanup, SQLite connection management, and proper thread termination with timeouts
- **Progress Callback Safety**: Check for exception handling in progress callbacks to prevent callback errors from crashing tests
- **Configuration Validation**: Verify JSON configuration loading, type validation, and graceful fallback to defaults
- **Python 3.13 Compatibility**: Look for `fileno()` AttributeError issues and proper Kivy environment variable setup

**Architecture & Design Patterns:**
- **Separation of Concerns**: Ensure core logic (`speedtest_core.py`) is properly separated from UI implementations
- **Error Recovery**: Check for intelligent retry logic with exponential backoff for transient network failures
- **Cancellation Support**: Verify proper `threading.Event` usage for responsive test cancellation
- **Database Operations**: Review SQLite transactions, WAL mode usage, and concurrent access patterns
- **Memory Management**: Look for potential memory leaks in long-running scheduled operations

**GUI & User Experience:**
- **Clock Event Management**: Ensure proper `Clock.schedule_interval` and `Clock.unschedule` usage to prevent memory leaks
- **Animation Cleanup**: Check for proper KivyMD animation lifecycle management
- **User Feedback**: Verify comprehensive progress updates and error messaging
- **Responsive Design**: Ensure UI remains responsive during background operations

**Configuration & Validation:**
- **Schema Compliance**: Check configuration values against defined ranges and logical consistency
- **File I/O Safety**: Verify proper file locking and error handling for configuration files
- **Environment Support**: Look for proper environment variable handling and deployment scenarios

**Performance & Scalability:**
- **Database Indexing**: Ensure proper SQLite indexes for timestamp and date range queries
- **Export Performance**: Check for efficient handling of large datasets in CSV/JSON export
- **Concurrent Operations**: Verify thread-safe operations for scheduled background testing
- **Memory Usage**: Look for efficient queue management and proper cleanup in async operations

**Security & Data Integrity:**
- **Input Validation**: Check for proper sanitization of user inputs and configuration values
- **File Path Safety**: Verify safe handling of file paths and prevention of directory traversal
- **Data Export Security**: Ensure safe file creation and proper encoding for export operations

Provide specific, actionable feedback for improvements, focusing on reliability, performance, and maintainability of the speed testing application.