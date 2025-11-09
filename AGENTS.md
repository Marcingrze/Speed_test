# Repository Overview

## Project Description
This is a robust Python utility for testing internet connection speed. The project provides a reliable command-line tool that measures download speed, upload speed, and ping latency using the speedtest.net service with comprehensive error handling and user feedback.

**Main purpose and goals:**
- Quick and reliable internet speed testing from command line
- Accurate measurement of network performance metrics with error resilience
- Professional-grade tool with proper error handling and user experience
- Lightweight tool with minimal dependencies but robust functionality

**Key technologies used:**
- Python 3.x with type hints
- speedtest-cli library (v2.1.3)
- Virtual environment for dependency isolation
- Structured error handling and logging

## Architecture Overview
This is a well-structured single-script application with robust error handling and modular design:

**Main components:**
- `sp.py`: Main application with modular functions for different responsibilities
- `speedtest-cli`: External library handling the actual network measurements
- Virtual environment (`ebv/`): Isolated Python environment for dependencies

**Core functions:**
- `main()`: Entry point and orchestration
- `check_network_connectivity()`: Pre-flight network validation
- `run_speed_test()`: Core testing logic with comprehensive error handling
- `format_and_display_results()`: Safe result processing and display
- `validate_results()`: Data validation and sanity checking

**Data flow:**
1. Network connectivity pre-check with timeout
2. User feedback during initialization and server selection
3. Safe speedtest object creation with error handling
4. Server discovery and best server selection with user notification
5. Download and upload speed measurements with progress indication
6. Safe result extraction with fallback values
7. Formatted console output with proper error reporting

**Error handling strategy:**
- Specific exception handling for speedtest library errors
- Network connectivity validation before testing
- Graceful degradation with informative error messages
- Proper resource cleanup in finally blocks
- Exit codes for script automation

**System interactions:**
- Network communication with speedtest.net servers (with timeouts)
- Progressive console output for user feedback
- Proper exit code handling for automation
- No persistent data storage or external APIs

## Directory Structure

```
Speed_test/
├── sp.py                    # Main application script (improved with error handling)
├── requirements.txt         # Python dependencies
├── CLAUDE.md               # AI agent guidance file
├── AGENTS.md               # This file - repository documentation
├── .continue/              # Continue CLI configuration
│   └── rules/              # Custom slash commands
│       └── review.md       # Code review command
└── ebv/                    # Python virtual environment
    ├── bin/                # Virtual env executables
    ├── lib/                # Python packages
    ├── include/            # Header files
    └── pyvenv.cfg          # Virtual env configuration
```

**Key files:**
- `sp.py`: Entry point with modular functions and comprehensive error handling
- `requirements.txt`: Single dependency specification
- `ebv/`: Virtual environment containing speedtest-cli package
- `.continue/rules/review.md`: Custom code review slash command

## Development Workflow

### Environment Setup
```bash
# Activate virtual environment
source ebv/bin/activate

# Install dependencies (if setting up fresh)
pip install -r requirements.txt
```

### Running the Application
```bash
# Ensure virtual environment is active
source ebv/bin/activate

# Run speed test
python sp.py
```

### Development Environment
- **Python Version**: Compatible with Python 3.x
- **Virtual Environment**: Uses `ebv/` directory for isolation
- **Dependencies**: Single external dependency (speedtest-cli)

### Testing Approach
- No automated test suite currently implemented
- Manual testing by running speed tests and verifying output format
- Network connectivity required for functional testing
- Error scenarios can be tested by disconnecting network or interrupting tests
- Built-in connectivity check allows testing of error paths

### Development Commands
```bash
# Activate environment
source ebv/bin/activate

# Run the application
python sp.py

# Install new dependencies
pip install <package>
pip freeze > requirements.txt

# Deactivate environment
deactivate
```

### Code Style and Quality
- Well-structured Python code with type hints
- Comprehensive error handling for network operations
- Modular function design with single responsibilities
- Detailed docstrings for all functions
- Progressive user feedback and informative error messages
- Professional console output formatting
- Proper resource management and cleanup
- Exit codes for automation compatibility