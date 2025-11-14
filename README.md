# Internet Speed Test Tool

Professional internet speed testing tool with advanced error handling, configuration, and result validation. Available as a command-line application (CLI), graphical user interface (GUI), and KDE Plasma widget.

> **Polish documentation**: [pl/README.md](pl/README.md)

## 📋 Description

A professional Python-based internet speed testing tool that uses speedtest.net to measure:
- Download speed
- Upload speed
- Latency (ping)

### ✨ Key Features

- **Three interfaces** - CLI, GUI (KivyMD), and KDE Plasma widget
- **Advanced error handling** - automatic retries for transient network issues
- **Flexible configuration** - all parameters customizable via JSON file
- **Result validation** - intelligent warnings for improbable results
- **Progress reporting** - detailed information about test stages
- **Connectivity check** - preliminary internet connection verification
- **User-friendly interface** - clear results display with formatting
- **Modern Material Design** - contemporary GUI with animations and responsive design
- **KDE Desktop widget** - lightweight Plasma widget with automatic refresh
- **Test history** - SQLite database storage with CSV/JSON export

## 🚀 Quick Start

### System Requirements

- Python 3.8+ (3.6+ for CLI only, but GUI dependencies require 3.8+)
- Internet connection
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd Speed_test
```

2. **Set up with Makefile (recommended)**
```bash
make setup          # Create venv and install dependencies
make run-cli        # Run CLI test
make run-gui        # Run GUI test
```

3. **Or manually**
```bash
python3 -m venv speedtest_env
source speedtest_env/bin/activate  # On Windows: speedtest_env\Scripts\activate
pip install -r requirements.txt
```

### Basic Usage

**CLI Application:**
```bash
# Run test with default configuration
python sp.py

# Run test with JSON output
python sp.py --json

# Create configuration file for customization
python sp.py --create-config
```

### How CLI Works
- sp.py is a lightweight wrapper that delegates all logic to speedtest_core
- Configuration is loaded and validated by SpeedTestConfig
- Testing (with retry and validation) is performed by SpeedTestEngine
- sp.py only handles the --create-config flag and displays results

**GUI Application:**
```bash
# Launch graphical interface
python speedtest_gui.py
```

## 🎨 Graphical User Interface (GUI)

### GUI Features

- **Modern Material Design** - contemporary look following Material Design guidelines
- **Real-time progress** - animated progress bar with test stage information
- **Responsive design** - automatic window size adaptation
- **Intuitive controls** - simple interface with Start/Stop buttons
- **Visual results** - clear result display in cards
- **Error handling** - friendly error and warning messages
- **Settings dialog** - configuration options (planned for future versions)

### Running the GUI

```bash
# Launch graphical application
python speedtest_gui.py
```

### GUI Architecture

- **speedtest_gui.py** - main GUI application with KivyMD interface
- **speedtest_core.py** - business logic shared by CLI and GUI
- **Asynchronous testing** - tests run in background without blocking interface
- **Progress callbacks** - real-time progress updates
- **Thread safety** - safe multithreaded operations

## 🖥️ KDE Plasma Widget

Desktop widget for KDE Plasma displaying speed test results.

### Widget Features

- **Result display** - shows download, upload speeds and ping
- **Automatic refresh** - updates every 30 seconds
- **Test triggering** - button for quick new test launch
- **Network status** - internet connection indicator
- **Compact mode** - can be added to panel with tooltip
- **Database integration** - uses shared SQLite database

### Widget Installation

```bash
# Install widget
make install-plasmoid

# Or manually
cd plasma-widget
./install_plasmoid.sh
```

### Adding to Desktop

1. Right-click on desktop
2. Select **"Add Widgets"**
3. Search for **"Speed Test"**
4. Drag widget to desktop or panel

### Using the Widget

- **View results**: Widget displays latest results from database
- **Run test**: Click "Run Speed Test" button
- **Refresh**: Refresh icon manually updates results
- **Panel mode**: Add to panel for quick overview

More information in [plasma-widget/README.md](plasma-widget/README.md)

## ⚙️ Configuration

### Creating Configuration File

```bash
python sp.py --create-config
```

This creates a `speedtest_config.json` file with default settings.

### Available Configuration Options

```json
{
  "bits_to_mbps": 1000000,                    // Bits to Mbps conversion
  "connectivity_check_timeout": 10,           // Connectivity check timeout (s)
  "speedtest_timeout": 60,                    // Main test timeout (s)
  "max_retries": 3,                          // Maximum retry attempts
  "retry_delay": 2,                          // Delay between retries (s)
  "max_typical_speed_gbps": 1,               // Typical speed threshold (Gbps)
  "max_reasonable_speed_gbps": 10,           // Maximum reasonable speed (Gbps)
  "max_typical_ping_ms": 1000,               // Typical ping threshold (ms)
  "max_reasonable_ping_ms": 10000,           // Maximum reasonable ping (ms)
  "show_detailed_progress": true,            // Detailed progress information
  "save_results_to_database": true           // Save results to SQLite database
}
```

## 📊 Usage Examples

### Standard Run

```bash
$ python sp.py

Internet Speed Test Tool
-------------------------
Checking network connectivity...
Network connection detected.

========================================
SPEED TEST RESULTS
========================================
Download: 85.42 Mbps
Upload:   45.67 Mbps
Ping:     12.4 ms
Server:   Orange Polska (Warsaw)
========================================

Result saved to database (ID: 1).
```

Note: Any warnings (e.g., unusually high speeds) will be displayed below results in the "Warnings:" section.

### Run with Custom Configuration

```bash
# 1. Create configuration file
python sp.py --create-config

# 2. Edit speedtest_config.json as needed
nano speedtest_config.json

# 3. Run with custom configuration
python sp.py
```

### JSON Output Mode

```bash
# Machine-readable JSON output
python sp.py --json
```

## 🔧 Project Structure

```
Speed_test/
├── sp.py                           # Lightweight CLI frontend delegating to speedtest_core
├── speedtest_gui.py                # GUI application (Kivy/KivyMD)
├── speedtest_core.py               # Business logic (shared by CLI/GUI)
├── scheduled_testing.py            # Background scheduler for automated testing
├── test_results_storage.py         # SQLite storage with export capabilities
├── config_validator.py             # Configuration validation
├── requirements.txt                # Python dependencies
├── speedtest_config.json.example   # Example configuration
├── speedtest_config.json          # User configuration (ignored by git)
├── Makefile                        # Build automation
├── plasma-widget/                  # KDE Plasma widget
├── README.md                      # This documentation
├── pl/                            # Polish documentation
├── speedtest_env/                 # Python virtual environment
└── .gitignore                     # Git ignore patterns
```

## 🛠️ Advanced Features

### Error Handling

- **Automatic retry**: For transient network problems
- **Connectivity check**: Connection verification before test
- **Graceful degradation**: Clear error messages
- **Result validation**: Warnings about unusual results

### Intelligent Validation

The tool automatically detects and warns about:
- Improbably high speeds (>1 Gbps)
- Extremely high latencies (>1000 ms)
- Very low speeds (<1 Mbps)
- Invalid measurement data

### Exit Codes

- `0`: Test completed successfully
- `1`: Test failed (no internet, measurement error)

## 🐛 Troubleshooting

### No Internet Connection

```
Error: No internet connection detected.
Please check your network connection and try again.
```
**Solution**: Check your internet connection and try again.

### Configuration Errors

```
Warning: Could not load config file speedtest_config.json: ...
Using default configuration.
```
**Solution**: Check JSON syntax in configuration file or delete file to use default configuration.

### High Latency/Low Speeds

```
Warning: High latency (1500 ms) detected - connection may be slow
```
**Solution**: This is informational - indicates issues with internet connection.

### GUI Issues

```
Error: Unable to start GUI application
```
**Solution**: Ensure all GUI dependencies are installed:
```bash
pip install -r requirements.txt
```

### Python 3.13 Compatibility

```
AttributeError: 'ProcessingStream' object has no attribute 'fileno'
```

**Automatic solution**: The patch is automatically applied during installation.

**Manual solution** (if needed):
```bash
source speedtest_env/bin/activate
python3 fix_speedtest_py313.py
```

**Alternative** - apply patch manually by adding `AttributeError` to exception handling in `speedtest.py` around line 181:
```python
# Before:
except OSError:
# After:
except (OSError, AttributeError):
```

## 📦 Dependencies

### CLI Application
- **speedtest-cli** (v2.1.3): Internet speed testing library
- **Python 3.8+**: With type hints support

### GUI Application (additional)
- **Kivy** (v2.3.1): Multiplatform application framework
- **KivyMD** (v1.2.0): Material Design components for Kivy
- **Pillow**: Image handling in Kivy

### Database & Storage
- **SQLite3**: Built into Python, used for test result storage

## 🧪 Testing & Development

### Development Environment

```bash
# Setup development environment
make dev-setup      # Installs pytest, black, flake8, mypy

# Run tests
make test           # Quick functionality tests
make test-full      # Complete test suite
make test-offline   # Tests without network

# Code quality
make lint           # Run flake8
make format         # Format with black
```

### Running Tests

```bash
# Quick tests
./speedtest_env/bin/python3 test_installation.py --quick

# Full test suite
./speedtest_env/bin/python3 test_installation.py

# Offline tests
./speedtest_env/bin/python3 test_installation.py --no-network

# Config validation tests
./speedtest_env/bin/python3 test_config_validation.py
```

### Adding New Features

1. Edit the appropriate file (`sp.py` for CLI, `speedtest_gui.py` for GUI, `speedtest_core.py` for shared logic)
2. Test changes under various network scenarios
3. Update documentation as needed
4. Commit changes with descriptive messages

## 📄 License

This project is available under the MIT License. See LICENSE file for details.

### Third-Party Licenses

This project uses the following libraries:
- **speedtest-cli** - Apache License 2.0 (full text in LICENSE-APACHE-2.0)
- **Kivy** - MIT License
- **KivyMD** - MIT License
- **Pillow** - HPND License

See NOTICE file for detailed attribution and license information.

## 🔗 Useful Links

- [speedtest-cli documentation](https://pypi.org/project/speedtest-cli/)
- [Kivy documentation](https://kivy.org/doc/stable/)
- [KivyMD documentation](https://kivymd.readthedocs.io/)
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)
- [JSON Configuration Format](https://www.json.org/)

---

**Note**: This tool requires an active internet connection to function properly. All tests are conducted using speedtest.net services.
