# KDE Plasma Speed Test Widget - Technical Documentation

> **Polish version (complete)**: [pl/PLASMA_WIDGET.md](pl/PLASMA_WIDGET.md)

Complete technical documentation for the KDE Plasma widget, covering development, testing, and production deployment.

## 📋 Table of Contents

- [Architecture](#architecture)
- [Development Environment](#development-environment)
- [Installation](#installation)
- [Testing](#testing)
- [Debugging](#debugging)
- [Troubleshooting](#troubleshooting)
- [Backend API](#backend-api)

## Architecture

### Widget Structure

```
org.kde.plasma.speedtest/
├── metadata.json                      # KDE Plasma metadata
│   ├── KPlugin                        # Author, license, version info
│   ├── X-Plasma-API                   # declarativeappletscript
│   └── X-Plasma-MainScript            # ui/main.qml
│
└── contents/
    ├── ui/
    │   └── main.qml                   # Frontend (Qt Quick/QML)
    │       ├── PlasmoidItem           # Main widget container
    │       ├── fullRepresentation     # Full view (desktop)
    │       └── compactRepresentation  # Compact view (panel)
    │
    └── code/
        ├── speedtest_helper.py        # Python backend
        │   ├── get_last_result()      # Fetch last result from DB
        │   ├── run_test_background()  # Run test
        │   └── check_connectivity()   # Check network
        └── run_helper.sh              # Shell wrapper script
```

### Frontend ↔ Backend Communication

```
┌─────────────────────────────────────────────────────────────┐
│                      QML Frontend                            │
│  ┌────────────────────────────────────────────────────┐    │
│  │ Plasma5Support.DataSource (engine: "executable")   │    │
│  │   • Executes system processes                       │    │
│  │   • Receives stdout as string                       │    │
│  │   • Asynchronous execution                          │    │
│  └────────────────────────────────────────────────────┘    │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ Call: /bin/sh -c 'run_helper.sh <command>'
                        ↓
┌─────────────────────────────────────────────────────────────┐
│                   Python Backend                             │
│  ┌────────────────────────────────────────────────────┐    │
│  │ speedtest_helper.py                                │    │
│  │   • Parses arguments (get_last/run_test/check)     │    │
│  │   • Imports speedtest_core, test_results_storage  │    │
│  │   • Executes operation                             │    │
│  │   • Returns JSON on stdout                         │    │
│  │   • Logs to ~/.local/share/plasma_speedtest.log   │    │
│  └────────────────────────────────────────────────────┘    │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ JSON Response (via run_helper.sh)
                        ↓
┌─────────────────────────────────────────────────────────────┐
│                  SQLite Database                             │
│                 speedtest_history.db                         │
│  • Shared with CLI, GUI, Scheduler                          │
│  • WAL mode + busy timeout                                  │
│  • Widget cache: ~/.cache/plasma-speedtest/widget_cache.json│
└─────────────────────────────────────────────────────────────┘
```

### Data Format (JSON)

**get_last (success)**:
```json
{
  "status": "success",
  "download": 85.4,
  "upload": 45.2,
  "ping": 12.0,
  "server": "Orange Polska (Warsaw)",
  "timestamp": "2025-11-13 18:42:35",
  "is_valid": 1,
  "warnings": []
}
```

**get_last (no_data)**:
```json
{
  "status": "no_data",
  "message": "No test results available. Run a test first."
}
```

**error**:
```json
{
  "status": "error",
  "message": "Error description"
}
```

## Development Environment

### Prerequisites

```bash
# KDE Plasma 5 or 6
# Qt 5.15+ or Qt 6.x
# Python 3.8+
# kpackagetool5 or kpackagetool6
# plasmoidviewer (for testing)
```

### Setup

```bash
# Clone repository
git clone <repository-url>
cd Speed_test

# Setup main application
make setup

# Test backend helper
python3 plasma-widget/org.kde.plasma.speedtest/contents/code/speedtest_helper.py get_last
```

## Installation

### Using Makefile

```bash
# Install widget
make install-plasmoid

# Uninstall widget
make uninstall-plasmoid

# Restart Plasma Shell
make restart-plasma
```

### Manual Installation

```bash
# Navigate to widget directory
cd plasma-widget

# Install
./install_plasmoid.sh

# Uninstall
./uninstall_plasmoid.sh
```

### Installation Paths

- **Plasma 6**: `~/.local/share/plasma/plasmoids/org.kde.plasma.speedtest/`
- **Plasma 5**: `~/.local/share/plasma/plasmoids/org.kde.plasma.speedtest/`

## Testing

### Testing Backend Helper

```bash
# Test get_last command
cd plasma-widget/org.kde.plasma.speedtest/contents/code
bash run_helper.sh get_last

# Test with Python directly
python3 speedtest_helper.py get_last

# Test check_network
bash run_helper.sh check_network
```

### Testing Widget UI

```bash
# Test with plasmoidviewer (Plasma 6)
plasmoidviewer -a org.kde.plasma.speedtest

# Or with full path
plasmoidviewer -a plasma-widget/org.kde.plasma.speedtest

# Monitor logs
tail -f ~/.local/share/plasma_speedtest.log
```

### Integration Testing

```bash
# 1. Run a speed test via CLI to populate database
./speedtest_env/bin/python3 sp.py

# 2. Check that helper returns data
bash plasma-widget/org.kde.plasma.speedtest/contents/code/run_helper.sh get_last

# 3. Verify widget cache
cat ~/.cache/plasma-speedtest/widget_cache.json

# 4. Test widget refresh in plasmoidviewer
```

## Debugging

### Common Issues

#### Issue: Widget doesn't load results

**Symptoms:**
- Widget shows "No data available"
- Console shows JSON parse errors

**Solutions:**
```bash
# 1. Check backend helper output
cd /home/marcin/.local/share/plasma/plasmoids/org.kde.plasma.speedtest/contents/code
bash run_helper.sh get_last

# 2. Verify database exists and has data
ls -lh ~/Projekty/Speed_test/speedtest_history.db
./speedtest_env/bin/python3 test_results_storage.py info

# 3. Check helper script is executable
chmod +x ~/.local/share/plasma/plasmoids/org.kde.plasma.speedtest/contents/code/*.sh
chmod +x ~/.local/share/plasma/plasmoids/org.kde.plasma.speedtest/contents/code/*.py

# 4. Test helper with full path
/bin/sh -c '/home/marcin/.local/share/plasma/plasmoids/org.kde.plasma.speedtest/contents/code/run_helper.sh get_last'
```

#### Issue: JSON parse errors

**Symptoms:**
- Console: "SyntaxError: JSON.parse: Parse error"
- Widget shows error state

**Solutions:**
```bash
# 1. Check helper output for non-JSON content (logs, errors)
bash run_helper.sh get_last 2>&1 | head -20

# 2. Verify stderr is redirected (should be in run_helper.sh)
grep "2>/dev/null" run_helper.sh

# 3. Test JSON validity
bash run_helper.sh get_last | python3 -m json.tool
```

#### Issue: XMLHttpRequest errors (Fixed)

**Symptoms:**
- Console: "XMLHttpRequest: Using GET on a local file is disabled"

**Solution:**
This was fixed by removing XMLHttpRequest usage from main.qml. Widget now uses only DataSource for all operations.

### Debug Logging

```bash
# Enable QML debugging in plasmoidviewer
QML_CONSOLE_LOG_LEVEL=debug plasmoidviewer -a org.kde.plasma.speedtest

# Monitor Python backend logs
tail -f ~/.local/share/plasma_speedtest.log

# Monitor Plasma Shell logs
journalctl --user -u plasma-plasmashell.service -f
```

## Backend API

### Commands

```bash
# Get last test result from database
speedtest_helper.py get_last

# Run speed test in background
speedtest_helper.py run_test

# Check network connectivity
speedtest_helper.py check_network
```

### Response Format

All responses are JSON objects with a `status` field:
- `"success"`: Operation completed successfully
- `"no_data"`: No data available (for get_last)
- `"error"`: Operation failed

### Helper Script Functions

**get_last_result()**
- Queries SQLite database for latest result
- Formats timestamp to human-readable format
- Writes result to widget cache file
- Returns JSON with test data or error

**run_test_background()**
- Starts speed test in detached process
- Uses Popen with DEVNULL for stdout/stderr
- Returns immediately with success status
- Test results will be saved to database

**check_connectivity()**
- Uses SpeedTestEngine.check_network_connectivity()
- Returns boolean connected status
- Does not write to cache (read-only check)

## Troubleshooting

### Widget doesn't appear after installation

```bash
# Restart Plasma Shell
kquitapp6 plasmashell && kstart6 plasmashell
# or manually:
killall plasmashell && plasmashell &

# Verify installation
ls ~/.local/share/plasma/plasmoids/ | grep speedtest
```

### Widget shows outdated data

```bash
# Widget auto-refreshes every 30 seconds
# To force refresh, click the refresh button or:

# Clear cache and refresh
rm ~/.cache/plasma-speedtest/widget_cache.json
# Widget will fetch from database on next refresh
```

### Python import errors in helper

```bash
# Helper uses project root detection
# If imports fail, verify project structure:
ls ~/Projekty/Speed_test/speedtest_core.py
ls ~/Projekty/Speed_test/test_results_storage.py

# Check Python path in logs
grep "Found project root" ~/.local/share/plasma_speedtest.log
```

## Widget Features

- **Auto-refresh**: Updates every 30 seconds
- **Manual refresh**: Click refresh button to update immediately
- **Compact mode**: Shows in panel with tooltip
- **Full mode**: Desktop widget with detailed display
- **Database integration**: Reads from shared SQLite database
- **Network status**: Displays connection indicator
- **Error handling**: Graceful error messages for users

## Files Modified for Widget Support

### CLI Integration (sp.py)
- Writes widget cache after successful tests
- Cache location: `~/.cache/plasma-speedtest/widget_cache.json`
- Provides quick widget access without database query

### GUI Integration (speedtest_gui.py)
- Also updates widget cache on completion
- Ensures widget shows latest results immediately

### Helper Security
- Validates command arguments (whitelist)
- Uses absolute paths for project root
- Validates database path within project
- No arbitrary code execution

## Future Enhancements

- Configuration UI in widget settings
- Manual test triggering from widget (currently via CLI)
- Historical graph display
- Custom refresh intervals
- Multiple server selection
- Export functionality from widget context menu

---

For complete technical details, see [pl/PLASMA_WIDGET.md](pl/PLASMA_WIDGET.md)
