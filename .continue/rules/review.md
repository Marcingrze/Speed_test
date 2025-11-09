---
invokable: true
---

Review this code for potential issues, including:

## Network Reliability and Timeout Management
- Timeout configuration: Verify appropriate timeout values for different network scenarios
- Connection handling: Check for proper handling of intermittent network failures
- Retry mechanisms: Consider if operations should retry on transient failures
- Resource cleanup: Ensure network resources are properly released
- Error recovery: Verify graceful recovery from network interruptions

## Data Validation and Result Processing
- Result bounds checking: Verify validation constants are appropriate (10 Gbps max, 10s ping max)
- Edge case handling: Check behavior with zero speeds, missing data fields
- Data type safety: Ensure robust handling of unexpected data types from API
- Unit conversion accuracy: Verify bit-to-Mbps calculations are mathematically correct
- Warning thresholds: Consider if validation warnings provide sufficient user guidance

## Error Handling Specificity
- Exception granularity: Ensure specific exceptions are caught rather than broad catches
- Error message clarity: Verify error messages provide actionable guidance to users
- Fallback behavior: Check that failures degrade gracefully with helpful feedback
- Logging vs output: Consider if error information should be logged vs printed
- Exit code consistency: Verify proper exit codes for different failure scenarios

## Code Organization and Maintainability
- Function cohesion: Ensure each function has a single, clear responsibility
- Configuration management: Check if hardcoded values should be configurable
- Type hint accuracy: Verify type annotations match actual usage patterns
- Documentation completeness: Check that docstrings accurately describe behavior
- Constant organization: Ensure related constants are logically grouped

## Performance and User Experience
- Progress indication: Verify adequate feedback during long-running operations
- Memory efficiency: Check for potential memory leaks in network operations
- Interrupt handling: Ensure clean shutdown on user interruption (Ctrl+C)
- Output formatting: Verify consistent decimal precision and unit display
- Cross-platform compatibility: Check shebang and path handling across systems

## Testing and Observability
- Testability: Consider if functions are structured for easy unit testing
- Mock points: Identify where external dependencies could be mocked for testing
- Error scenario coverage: Check if all error paths can be tested
- Debugging information: Verify sufficient information for troubleshooting issues
- Integration testing: Consider real-world network condition testing approaches

## Security and Dependencies
- Dependency versioning: Verify pinned versions are current and secure
- Input validation: Check handling of data from external speedtest API
- Network security: Review connection parameters and timeout settings
- Privilege requirements: Ensure minimal system permissions needed
- Virtual environment isolation: Verify proper dependency isolation

Focus particularly on:
- Network resilience under poor connection conditions
- Data validation edge cases and boundary conditions
- User experience during failures and long operations
- Code maintainability and future extensibility

Provide specific, actionable feedback with code examples where helpful.