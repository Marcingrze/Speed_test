# Repository Overview

## Project Description

This is a comprehensive Python-based internet speed testing suite with both CLI and GUI interfaces. The project provides professional-grade network testing capabilities with enterprise-level reliability, extensive configuration options, persistent storage, and automated scheduling features.

**Main purpose and goals:**
- Professional internet speed testing with multiple interface options (CLI, GUI)
- Enterprise-grade reliability with comprehensive error handling and retry logic
- Persistent storage and historical analysis of test results
- Automated scheduled testing with background operation capabilities
- Flexible configuration system for different network environments and use cases
- Modern Material Design GUI with real-time progress updates
- Data export and analysis capabilities for network performance monitoring

**Key technologies used:**
- **Python 3.6+** with comprehensive type hints and modern async patterns
- **speedtest-cli 2.1.3** for network measurements via speedtest.net
- **Kivy 2.3.1 & KivyMD 1.2.0** for cross-platform Material Design GUI
- **SQLite** for persistent test result storage and historical data
- **JSON configuration** system with validation and fallbacks
- **Threading** for asynchronous operations and GUI responsiveness
- **Virtual environment** (`ebv/`) for dependency isolation

## Architecture Overview

This is a sophisticated modular application with clean separation of concerns:

**Core Modules:**
- **`speedtest_core.py`**: Business logic engine with async support and progress callbacks
- **`sp.py`**: CLI interface with enterprise-grade error handling
- **`speedtest_gui.py`**: Modern Material Design GUI with real-time updates
- **`test_results_storage.py`**: SQLite-based persistence with export capabilities
- **`scheduled_testing.py`**: Background automation and scheduling system
- **`config_validator.py`**: Configuration validation and management utilities

**Architectural Patterns:**
- **Separation of Concerns**: Core logic separated from UI implementations
- **Observer Pattern**: Progress callbacks for real-time UI updates
- **Command Pattern**: Modular CLI and scheduled operations
- **Strategy Pattern**: Configurable validation and retry strategies
- **Factory Pattern**: Configuration and storage object creation

**Key Components:**
- **SpeedTestEngine**: Core testing logic with cancellation and progress tracking
- **SpeedTestConfig**: JSON-based configuration management with validation
- **TestResultStorage**: SQLite persistence with statistics and export functions
- **AsyncSpeedTestRunner**: Thread-safe async wrapper for GUI applications
- **ScheduledTestRunner**: Background automation with configurable intervals

**Data Flow:**
1. Configuration loading with validation and fallbacks
2. Network connectivity pre-validation with timeout handling
3. Server selection and optimization with progress feedback
4. Parallel download/upload testing with real-time progress
5. Result validation with tiered warning system
6. Persistent storage with historical analysis
7. Export capabilities (CSV, JSON) for external analysis
8. Optional scheduling for automated background testing

**Error Handling Strategy:**
- **Layered exception handling** with specific network error recovery
- **Intelligent retry logic** for transient network failures
- **Graceful degradation** with actionable error messages
- **Progress cancellation** support for responsive user control
- **Resource cleanup** with proper thread and connection management
- **Comprehensive logging** with configurable verbosity levels

## Directory Structure

```
Speed_test/
├── speedtest_core.py               # Core business logic (13KB+ modular engine)
├── sp.py                          # CLI interface (10KB+ enterprise-grade)
├── speedtest_gui.py               # GUI application (15KB+ Material Design)
├── test_results_storage.py        # Data persistence (14KB+ with analytics)
├── scheduled_testing.py           # Background automation (12KB+ scheduler)
├── config_validator.py            # Configuration management (8KB+ validation)
├── speedtest_gui_fallback.py      # Alternative GUI implementation (10KB+)
├── requirements.txt               # Pinned dependencies with GUI support
├── speedtest_config.json.example  # Configuration template with documentation
├── speedtest_config.json          # User configuration (gitignored)
├── kivy_frontend_python.md        # GUI development documentation
├── README.md                      # Comprehensive user documentation (Polish/English)
├── AGENTS.md                      # This repository documentation
├── CLAUDE.md                      # AI agent interaction guidelines
├── .gitignore                     # Comprehensive Python + config exclusions
├── .continue/                     # Continue CLI configuration
│   └── rules/
│       └── review.md              # Custom code review slash command
└── ebv/                          # Python virtual environment
    ├── bin/                       # Virtual environment executables
    └── lib/                       # Python packages and dependencies
```

**Key Features by Component:**
- **Core Engine**: Async operations, progress tracking, cancellation, validation
- **CLI Interface**: Enterprise error handling, retry logic, configuration management
- **GUI Application**: Material Design, real-time progress, responsive controls
- **Data Storage**: SQLite persistence, historical analysis, export capabilities
- **Scheduling**: Background automation, configurable intervals, graceful shutdown
- **Configuration**: JSON validation, environment support, sensible defaults

## Development Workflow

### Environment Setup
```bash
# Clone and setup environment
cd Speed_test
source ebv/bin/activate

# Install all dependencies (including GUI)
pip install -r requirements.txt

# Verify installation with core modules
python -c "from speedtest_core import SpeedTestEngine; print('Core engine ready')"
python -c "from kivymd.app import MDApp; print('GUI dependencies ready')"
```

### Running Applications

**CLI Interface:**
```bash
# Basic speed test
python sp.py

# Create and customize configuration
python sp.py --create-config
nano speedtest_config.json

# Run with custom settings
python sp.py
```

**GUI Application:**
```bash
# Launch Material Design interface
python speedtest_gui.py

# Alternative GUI implementation
python speedtest_gui_fallback.py
```

**Background Automation:**
```bash
# Run immediate test with storage
python scheduled_testing.py --immediate

# Start scheduler (60-minute intervals)
python scheduled_testing.py --interval 60

# View recent statistics
python scheduled_testing.py --stats
```

**Data Management:**
```bash
# View test statistics
python test_results_storage.py stats --days 30

# Export data
python test_results_storage.py export csv results.csv --days 7
python test_results_storage.py export json results.json

# Database information
python test_results_storage.py info

# Cleanup old records
python test_results_storage.py cleanup --keep-days 365
```

### Configuration System

**Core Configuration Options:**
```json
{
  "bits_to_mbps": 1000000,                    // Speed conversion factor
  "connectivity_check_timeout": 10,           // Pre-test connectivity check (s)
  "speedtest_timeout": 60,                    // Main test timeout (s)
  "max_retries": 3,                          // Retry attempts for failed tests
  "retry_delay": 2,                          // Delay between retry attempts (s)
  "max_typical_speed_gbps": 1,               // Threshold for "typical" speeds
  "max_reasonable_speed_gbps": 10,           // Maximum credible speed limit
  "max_typical_ping_ms": 1000,               // Threshold for "typical" latency
  "max_reasonable_ping_ms": 10000,           // Maximum credible latency
  "show_detailed_progress": true             // Enable verbose progress updates
}
```

**Advanced Features:**
- **Environment variable overrides** for deployment scenarios
- **Validation ranges** to prevent invalid configuration values
- **Backward compatibility** with older configuration formats
- **Runtime reconfiguration** support for long-running processes

### Testing Approach

**Manual Testing:**
- **CLI Testing**: Various network conditions, configuration combinations
- **GUI Testing**: User interaction flows, progress updates, error handling
- **Integration Testing**: Storage, export, scheduling components
- **Edge Case Testing**: Network interruptions, extreme values, cancellation

**Automated Testing Scenarios:**
```bash
# Test configuration validation
python config_validator.py --test-all

# Test storage and export functionality
python test_results_storage.py info
python test_results_storage.py stats

# Test scheduling system
python scheduled_testing.py --immediate
```

**Performance Testing:**
- **Memory usage** during long-running scheduled tests
- **Thread safety** in GUI applications with background operations
- **Database performance** with large historical datasets
- **Network resilience** under various failure conditions

### Development Environment

**Core Dependencies:**
- **Python 3.6+**: Type hints, async/await syntax, pathlib
- **speedtest-cli 2.1.3**: Network testing library
- **Kivy 2.3.1**: Cross-platform GUI framework
- **KivyMD 1.2.0**: Material Design components
- **Pillow**: Image processing for GUI
- **SQLite**: Embedded database (Python standard library)

**Development Tools:**
- **Virtual Environment**: Complete isolation in `ebv/` directory
- **Type Checking**: Comprehensive type hints throughout codebase
- **Error Handling**: Specific exception classes and graceful degradation
- **Documentation**: Extensive docstrings and inline comments

### Code Quality Standards

**Architecture Principles:**
- **Modular Design**: Clear separation between core, UI, storage, and scheduling
- **Async-Ready**: Thread-safe operations with proper cancellation support
- **Configuration-Driven**: All behavior customizable through JSON configuration
- **Error Resilient**: Comprehensive error handling with user-friendly messages
- **Performance Conscious**: Efficient resource usage and cleanup

**Code Style:**
- **Enterprise-grade Python** with comprehensive type annotations
- **Clean Architecture** with dependency injection and interface abstraction
- **Comprehensive Error Handling** for all external dependencies
- **Resource Management** with proper cleanup and timeout handling
- **Professional UX** with progress feedback and intelligent validation
- **Security Practices** with input validation and safe file operations

### Deployment and Production Use

**Configuration Management:**
```bash
# Production configuration template
cp speedtest_config.json.example speedtest_config.json

# Environment-specific settings
export SPEEDTEST_CONFIG_PATH=/etc/speedtest/config.json
export SPEEDTEST_DATA_PATH=/var/lib/speedtest/

# Service deployment
python scheduled_testing.py --config production.json --interval 30
```

**Monitoring and Analytics:**
```bash
# Historical analysis
python test_results_storage.py stats --days 90

# Export for external monitoring
python test_results_storage.py export json /monitoring/speedtest-$(date +%Y%m).json --days 30

# Database maintenance
python test_results_storage.py cleanup --keep-days 365
```

**Enterprise Features:**
- **Persistent Storage**: SQLite database with automatic schema management
- **Data Export**: CSV and JSON formats for external analysis tools
- **Background Operation**: Daemon-compatible scheduling with signal handling
- **Configuration Validation**: Prevents invalid settings that could cause failures
- **Historical Analysis**: Statistical analysis of network performance trends
- **Resource Cleanup**: Automatic cleanup of old data to manage storage usage