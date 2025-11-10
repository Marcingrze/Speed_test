---
invokable: true
---

Review this code for potential issues, including:

## Architecture and Modular Design
- Module separation: Verify clean separation between core logic, UI, storage, and scheduling
- Interface consistency: Check that progress callbacks and result objects follow consistent patterns
- Dependency injection: Ensure components can be easily tested and mocked
- Async/threading safety: Verify thread-safe operations in GUI and scheduling modules
- Progress cancellation: Check that cancellation signals propagate properly through all layers

## Configuration and Validation System
- JSON schema validation: Verify configuration loading handles malformed JSON gracefully
- Value range validation: Check that configuration values are within reasonable bounds
- Environment overrides: Consider if configuration should support environment variable overrides
- Configuration migration: Verify backward compatibility when configuration format changes
- Default fallbacks: Ensure sensible defaults for all configuration options

## Data Persistence and Storage
- SQLite schema management: Check database schema creation, migration, and indexing
- Transaction safety: Verify proper transaction handling for data consistency
- Export functionality: Test CSV and JSON export with various data sizes
- Data cleanup: Check that old data cleanup doesn't affect current operations
- Statistics calculations: Verify accuracy of statistical computations and aggregations

## GUI Application Architecture
- Threading model: Verify GUI operations are thread-safe and don't block the UI
- Progress updates: Check that real-time progress updates work correctly without memory leaks
- Resource management: Ensure proper cleanup of GUI resources and background threads
- Error handling in UI: Verify error messages are user-friendly and actionable
- Material Design compliance: Check adherence to Material Design patterns and accessibility

## Network Resilience and Retry Logic
- Retry effectiveness: Verify retry logic triggers for appropriate network errors
- Timeout configurations: Check that timeout values are suitable for different network conditions
- Connection state management: Ensure proper cleanup of network resources
- Error classification: Verify that transient vs permanent errors are handled differently
- Progress tracking accuracy: Check that progress estimates are realistic and helpful

## Background Scheduling and Automation
- Signal handling: Verify graceful shutdown on system signals (SIGTERM, SIGINT)
- Scheduler reliability: Check that scheduled tests run consistently and handle clock changes
- Resource management: Ensure long-running processes don't leak memory or resources
- Error recovery: Verify scheduler continues operating after individual test failures
- Configuration reloading: Check if scheduler can adapt to configuration changes

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

Focus particularly on:
- Thread safety in GUI and scheduled operations
- Data integrity in SQLite operations and exports
- Network error resilience and retry logic effectiveness
- Resource cleanup in long-running processes
- User experience during various failure scenarios
- Performance with large historical datasets
- Configuration system robustness and validation
- Cross-module interface consistency and testability

Provide specific, actionable feedback with code examples where helpful, especially for:
- Threading issues or race conditions
- Database transaction safety
- Error handling improvements
- Performance optimization opportunities
- Security vulnerabilities or input validation gaps