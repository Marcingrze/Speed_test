---
invokable: true
---

Review this Python speed testing application code for potential issues, focusing on:

## Core Architecture & Threading Safety
- **Module separation**: Verify clean separation between speedtest_core.py, GUI, storage, and scheduling
- **Progress callbacks**: Check that progress updates work correctly without race conditions
- **Thread safety**: Verify GUI operations (speedtest_gui.py) don't block UI thread
- **Cancellation handling**: Ensure speed test cancellation propagates through all layers
- **Resource cleanup**: Check proper cleanup of speedtest-cli connections and threads

## SpeedTest Core Engine (speedtest_core.py)
- **Config validation**: Verify SpeedTestConfig handles invalid JSON and out-of-range values
- **Network error handling**: Check retry logic for speedtest-cli exceptions
- **Result validation**: Ensure speed/ping validation catches unrealistic values
- **Progress tracking**: Verify progress callbacks work with different speedtest phases
- **Memory management**: Check for leaks in long-running SpeedTestEngine instances

## SQLite Storage & Data Management (test_results_storage.py)
- **Database schema**: Check speedtest_history.db table creation and indexing
- **Transaction safety**: Verify SQLite operations handle concurrent access properly
- **Export functions**: Test CSV/JSON export with large datasets (10k+ results)
- **Statistics accuracy**: Verify mean/median calculations for speed/ping metrics
- **Cleanup operations**: Ensure old data deletion doesn't corrupt active sessions

## Kivy/KivyMD GUI Application (speedtest_gui.py)
- **Threading model**: Check AsyncSpeedTestRunner integration with Kivy Clock
- **Progress updates**: Verify queue-based progress updates don't cause memory leaks
- **UI responsiveness**: Ensure speed tests don't freeze Material Design interface
- **Error dialogs**: Check user-friendly error messages and Snackbar notifications
- **Resource cleanup**: Verify proper thread cleanup on app close or test cancellation

## Network Testing & Retry Logic (CLI & Core)
- **speedtest-cli integration**: Check proper handling of speedtest.SpeedtestException
- **Retry strategies**: Verify network errors trigger retries but not measurement errors
- **Timeout handling**: Check connectivity_check_timeout vs speedtest_timeout values
- **Server selection**: Ensure best server selection doesn't fail on limited networks
- **Python 3.13 compatibility**: Verify fileno() patch for speedtest-cli is applied

## Background Scheduling (scheduled_testing.py)
- **Signal handling**: Check SIGINT/SIGTERM graceful shutdown with proper thread cleanup
- **Monotonic timing**: Verify scheduler uses monotonic time to avoid clock drift issues
- **Error recovery**: Ensure individual test failures don't crash scheduler loop
- **Database contention**: Check concurrent access between scheduler and CLI/GUI
- **Memory usage**: Verify long-running scheduler doesn't accumulate memory leaks

## Data Export and Analytics
- Export format consistency: Verify CSV and JSON exports maintain data integrity
- Large dataset handling: Check performance with large historical datasets
- Date range filtering: Verify correct handling of date range queries and edge cases
- Statistical accuracy: Check calculations for mean, median, and other statistics
- Export file safety: Ensure exported files are created safely without data corruption

## Error Handling and User Experience
- Error message clarity: Check that error messages provide actionable guidance
- Graceful degradation: Verify application behavior when components fail partially
- Progress indication: Ensure progress updates are accurate and informative
- Interrupt handling: Check clean shutdown on user interruption (Ctrl+C)
- Exit code consistency: Verify proper exit codes for automation and scripting

## Performance and Scalability
- Memory usage patterns: Check for memory leaks in long-running operations
- Database performance: Verify query performance with large datasets
- Thread pool management: Check efficient use of threads without over-creation
- Configuration loading efficiency: Verify config files aren't loaded repeatedly
- Resource cleanup timing: Ensure resources are released promptly

## Security and Input Validation
- Configuration file parsing: Verify safe parsing of JSON configuration files
- Path validation: Check for proper validation of file paths and directory access
- Data sanitization: Review handling of external data from speedtest API
- File permissions: Ensure application creates files with appropriate permissions
- SQL injection prevention: Verify proper parameterization of SQL queries

## Testing and Maintainability
- Module testability: Check if components can be easily unit tested in isolation
- Mock points: Verify external dependencies can be mocked for testing
- Error scenario coverage: Ensure all error paths can be triggered for testing
- Documentation accuracy: Check that code comments match actual implementation
- Type hint accuracy: Verify type annotations align with runtime behavior

## Cross-Platform Compatibility
- Path handling: Verify proper use of pathlib for cross-platform file paths
- GUI framework compatibility: Check Kivy/KivyMD behavior across different platforms
- Virtual environment setup: Ensure virtual environment works on different systems
- Signal handling: Verify signal handling works correctly on different operating systems
- File encoding: Check proper handling of unicode in configuration and data files

## Production Deployment Considerations
- Service mode operation: Check suitability for running as a system service
- Logging integration: Consider integration with standard logging frameworks
- Configuration management: Verify enterprise-suitable configuration deployment
- Monitoring hooks: Check for opportunities to add monitoring and metrics
- Resource limits: Ensure application respects system resource constraints

## Code Quality and Maintenance
- Type safety: Verify comprehensive type hints throughout codebase
- Error propagation: Check that errors bubble up appropriately through layers
- Code duplication: Look for opportunities to reduce duplicate logic
- Documentation completeness: Ensure all public interfaces are documented
- Version compatibility: Check compatibility with specified Python and library versions

Focus specifically on:
- **speedtest-cli integration**: Check for proper exception handling of network timeouts
- **Kivy threading**: Verify Clock.schedule_interval usage doesn't create race conditions
- **SQLite concurrent access**: Check database operations during scheduled tests
- **Configuration validation**: Ensure JSON schema prevents invalid speed/ping thresholds
- **Resource cleanup**: Verify threads/connections are properly closed on cancellation
- **Error user experience**: Check that speedtest failures show actionable error messages
- **Performance with large datasets**: Test export/stats functions with 10k+ historical results

Provide actionable feedback with code examples for:
- Threading issues in AsyncSpeedTestRunner or ScheduledTestRunner
- SQLite transaction safety in TestResultStorage operations
- speedtest-cli error handling in SpeedTestEngine
- Kivy/KivyMD UI responsiveness during long operations
- Configuration validation edge cases in SpeedTestConfig
- Memory leaks in long-running scheduled testing scenarios