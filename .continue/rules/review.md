---
invokable: true
---

Review this code for potential issues, including:

## Configuration and Environment Management
- Configuration loading: Verify JSON parsing and error handling for malformed config files
- Default fallbacks: Ensure sensible defaults when configuration keys are missing
- Environment variable support: Consider if config should support environment overrides
- Config validation: Check that loaded configuration values are within reasonable bounds
- File path handling: Verify proper use of Path objects and cross-platform compatibility

## Network Reliability and Retry Logic
- Retry mechanism effectiveness: Verify that retry logic actually triggers for appropriate errors
- Timeout configuration: Check if timeout values are appropriate for different network scenarios
- Exception handling specificity: Ensure network errors are caught at the right level for retries
- Graceful degradation: Verify behavior when all retry attempts are exhausted
- Connection state management: Check for proper cleanup of network resources

## Data Validation and Result Processing
- Configuration-driven validation: Verify validation bounds are properly loaded from config
- Edge case handling: Test behavior with extreme values (zero speeds, very high ping)
- Tiered warning system: Check that warning messages are appropriate and actionable
- Data type safety: Ensure robust handling of unexpected API response formats
- Result consistency: Verify that validation logic aligns with display formatting

## Error Handling and User Experience
- Error message clarity: Check that error messages provide clear guidance for resolution
- Progress indication: Verify that progress messages are helpful and accurate
- Timing information: Check accuracy and usefulness of performance timing displays
- Interrupt handling: Ensure clean shutdown on user interruption (Ctrl+C)
- Exit code consistency: Verify proper exit codes for different failure scenarios

## Code Organization and Maintainability
- Function separation: Ensure configuration, network, and display logic are properly separated
- Global state management: Review use of global config variable and potential alternatives
- Type hint accuracy: Verify that type annotations match actual function behavior
- Documentation completeness: Check that all configuration options are documented
- Command-line interface: Verify argument parsing and help text accuracy

## Performance and Resource Management
- Configuration caching: Check if config loading is efficient for repeated calls
- Memory usage: Review potential memory leaks in network operations or config loading
- File I/O efficiency: Verify that configuration files are read efficiently
- Timing accuracy: Check precision and reliability of performance measurements
- Resource cleanup: Ensure proper cleanup of network connections and file handles

## Security and Input Validation
- Configuration security: Verify that config files are parsed safely
- Path traversal: Check for proper validation of file paths
- Input sanitization: Review handling of data from external speedtest API
- Privilege requirements: Ensure application runs with minimal required permissions
- Error information disclosure: Check that error messages don't leak sensitive information

## Testing and Observability
- Configuration testing: Consider how different config combinations can be tested
- Mock-ability: Check if external dependencies can be easily mocked for testing
- Error scenario coverage: Verify that all error paths can be triggered for testing
- Debugging information: Check adequacy of information for troubleshooting
- Integration testing: Consider real-world network condition testing approaches

## Enterprise Features and Scalability
- Configuration management: Check if config system is suitable for enterprise deployment
- Logging integration: Consider if application should integrate with logging frameworks
- Monitoring hooks: Check for opportunities to add monitoring or metrics collection
- Automation compatibility: Verify suitability for CI/CD and automated testing
- Documentation coverage: Ensure all features are properly documented

Focus particularly on:
- Configuration system robustness and error handling
- Retry logic effectiveness and network resilience
- User experience during various failure scenarios
- Maintainability and extensibility for enterprise use
- Performance characteristics under different network conditions

Provide specific, actionable feedback with code examples where helpful.