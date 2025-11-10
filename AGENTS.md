# Repository Overview

## Project Description

This is an enterprise-grade Python utility for testing internet connection speed. The project provides a highly configurable, robust command-line tool that measures download speed, upload speed, and ping latency using the speedtest.net service with comprehensive error handling, retry logic, and intelligent result validation.

**Main purpose and goals:**
- Professional internet speed testing with enterprise-level reliability
- Comprehensive error handling and network resilience for production environments
- Flexible configuration system for different network environments and use cases
- Intelligent result validation with tiered warning system
- Automation-friendly with proper exit codes and configurable behavior

**Key technologies used:**
- Python 3.x with comprehensive type hints
- speedtest-cli library (v2.1.3) for network measurements
- JSON-based configuration system with validation
- Virtual environment for dependency isolation
- Git version control with proper ignore patterns

## Architecture Overview

This is a sophisticated single-script application with enterprise-grade architecture and extensive configuration capabilities:

**Main components:**
- `sp.py`: Core application with modular functions and enterprise-grade error handling
- `speedtest_config.json`: User configuration file with customizable parameters
- `speedtest_config.json.example`: Example configuration template
- `speedtest-cli`: External library handling network measurements
- Virtual environment (`ebv/`): Isolated Python environment

**Core functions:**
- `main()`: Entry point with configuration loading and command-line argument handling
- `load_config()` / `create_sample_config()`: Configuration management system
- `check_network_connectivity()`: Pre-flight network validation with configurable timeouts
- `run_speed_test_with_retry()`: Retry wrapper with intelligent network error handling
- `run_speed_test()`: Core testing logic with progress feedback and timing
- `validate_results()`: Tiered result validation with intelligent warnings
- `format_and_display_results()`: Professional output formatting

**Configuration system:**
- JSON-based configuration with automatic loading
- Fallback to sensible defaults if configuration file missing
- All timeouts, retry parameters, and validation bounds configurable
- Environment-specific customization support
- Backward compatibility with existing usage patterns

**Data flow:**
1. Application startup with configuration loading
2. Command-line argument processing (--create-config support)
3. Network connectivity pre-check with configurable timeout
4. Progressive user feedback during server selection
5. Retry-wrapped speedtest execution with intelligent error handling
6. Download and upload measurements with timing and progress estimates
7. Intelligent result validation with tiered warnings
8. Professional formatted output with proper error reporting

**Error handling strategy:**
- Specific exception handling for different speedtest library errors
- Intelligent retry logic for transient network failures (configurable attempts)
- Network connectivity validation before expensive operations
- Graceful degradation with actionable error messages
- Proper resource cleanup and exit codes for automation
- Configuration file error handling with fallbacks

**System interactions:**
- Network communication with speedtest.net servers (configurable timeouts)
- JSON configuration file loading with error handling
- Progressive console output with configurable verbosity
- Command-line argument processing for configuration management
- Proper exit code handling for automation and scripting
- No persistent data storage beyond configuration files

## Directory Structure

```
Speed_test/
├── sp.py                           # Main application (10KB+ enterprise-grade code)
├── requirements.txt                # Python dependencies
├── speedtest_config.json.example   # Example configuration template
├── speedtest_config.json          # User configuration (gitignored)
├── CLAUDE.md                      # AI agent guidance file
├── AGENTS.md                      # This file - comprehensive repository documentation
├── .gitignore                     # Git ignore patterns (Python + config files)
├── .continue/                     # Continue CLI configuration
│   └── rules/                     # Custom slash commands
│       └── review.md              # Code review command
├── .git/                          # Git repository
└── ebv/                          # Python virtual environment
    ├── bin/                       # Virtual env executables
    ├── lib/                       # Python packages (speedtest-cli)
    ├── include/                   # Header files
    └── pyvenv.cfg                 # Virtual env configuration
```

**Key files:**
- `sp.py`: Main application with 300+ lines of enterprise-grade code
- `requirements.txt`: Pinned dependency versions for reproducibility
- `speedtest_config.json.example`: Configuration template with all options documented
- `speedtest_config.json`: User configuration file (excluded from version control)
- `ebv/`: Virtual environment with isolated dependencies
- `.continue/rules/review.md`: Custom code review slash command
- `.gitignore`: Comprehensive exclusions for Python projects and user configs

## Development Workflow

### Environment Setup
```bash
# Clone repository and navigate to directory
cd Speed_test

# Activate virtual environment
source ebv/bin/activate

# Install dependencies (if setting up fresh environment)
pip install -r requirements.txt

# Create user configuration (optional)
python sp.py --create-config
```

### Running the Application
```bash
# Ensure virtual environment is active
source ebv/bin/activate

# Run with default configuration
python sp.py

# Create sample configuration file
python sp.py --create-config

# Run with custom configuration (edit speedtest_config.json first)
python sp.py
```

### Configuration Management
```bash
# Create sample configuration
python sp.py --create-config

# Edit configuration file
nano speedtest_config.json

# Available configuration options:
# - connectivity_check_timeout: Network pre-check timeout (default: 10s)
# - speedtest_timeout: Main test timeout (default: 60s) 
# - max_retries: Number of retry attempts (default: 3)
# - retry_delay: Delay between retries (default: 2s)
# - max_typical_speed_gbps: Typical speed threshold (default: 1 Gbps)
# - max_reasonable_speed_gbps: Maximum reasonable speed (default: 10 Gbps)
# - max_typical_ping_ms: Typical ping threshold (default: 1000ms)
# - max_reasonable_ping_ms: Maximum reasonable ping (default: 10000ms)
# - show_detailed_progress: Enable progress estimates (default: true)
```

### Development Environment
- **Python Version**: Compatible with Python 3.x (type hints require 3.6+)
- **Virtual Environment**: Uses `ebv/` directory for complete isolation
- **Dependencies**: Single external dependency (speedtest-cli==2.1.3)
- **Configuration**: JSON-based with validation and error handling
- **Version Control**: Git with comprehensive .gitignore patterns

### Testing Approach
- **Manual Integration Testing**: Run speed tests and verify output formatting
- **Network Connectivity Testing**: Test with and without internet connection
- **Error Scenario Testing**: Interrupt tests, disconnect network, invalid configs
- **Retry Logic Testing**: Test transient network failures and recovery
- **Configuration Testing**: Test with various configuration combinations
- **Edge Case Testing**: Test extremely fast/slow connections, high latency scenarios
- **Built-in Validation**: Comprehensive result validation with tiered warnings

### Development Commands
```bash
# Environment management
source ebv/bin/activate                    # Activate environment
deactivate                                # Deactivate environment

# Application execution
python sp.py                              # Run speed test
python sp.py --create-config              # Generate configuration template

# Configuration management
cat speedtest_config.json.example         # View example configuration
cp speedtest_config.json.example speedtest_config.json  # Copy template

# Development workflow
pip install <package>                     # Install new dependencies
pip freeze > requirements.txt             # Update requirements file

# Git workflow
git add .                                 # Stage changes
git commit -m "Description"               # Commit changes
git log --oneline                         # View commit history
```

### Code Style and Quality
- **Enterprise-grade Python code** with comprehensive type hints
- **Modular architecture** with single-responsibility functions
- **Comprehensive error handling** for all network and configuration scenarios
- **Extensive documentation** with detailed docstrings and inline comments
- **Professional user experience** with progress feedback and intelligent warnings
- **Configuration-driven design** with sensible defaults and validation
- **Automation-friendly** with proper exit codes and configurable behavior
- **Resource management** with proper cleanup and timeout handling
- **Version control best practices** with meaningful commits and proper .gitignore
- **Security considerations** with input validation and safe file operations