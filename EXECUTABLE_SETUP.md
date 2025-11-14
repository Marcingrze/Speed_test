# Speed Test Tool - Executable Setup Guide

> **Polish version (complete)**: [pl/EXECUTABLE_SETUP.md](pl/EXECUTABLE_SETUP.md)

This document describes how to configure Speed Test Tool as a runnable application without directly calling Python.

## 🚀 Automatic Installation (Recommended)

### For all users (requires sudo):
```bash
sudo python3 install.py
```

### For current user only:
```bash
python3 install.py --user
```

### Using Makefile:
```bash
make install          # System-wide
make install-user     # User-only
```

## 📁 Post-Installation Structure

```
/usr/local/bin/              # System-wide installation
├── speedtest-cli*           # CLI interface executable
├── speedtest-gui*           # GUI interface executable
├── speedtest-gui-fallback*  # Alternative GUI executable
├── speedtest-scheduler*     # Background scheduler executable
└── speedtest-storage*       # Data management executable

~/.local/bin/                # User installation
├── speedtest-cli*           # Same executables for user
├── speedtest-gui*
└── ...
```

## 🎯 Created Executables

### 1. `speedtest-cli` - CLI Interface
```bash
# Basic usage
speedtest-cli

# Create configuration
speedtest-cli --create-config

# JSON output
speedtest-cli --json

# Help
speedtest-cli --help
```

**Functionality:**
- Download/upload/ping speed test
- Automatic retry on network errors
- Result validation and warnings
- JSON configuration support
- Database storage

### 2. `speedtest-gui` - Graphical Interface
```bash
# Launch GUI
speedtest-gui

# Material Design interface with:
# - Real-time progress
# - Cancellation support
# - Graphical results
# - Animations and feedback
```

**Functionality:**
- Modern Material Design
- Real-time progress tracking
- Test cancellation capability
- Visual result display

### 3. `speedtest-gui-fallback` - Alternative GUI
```bash
# If main GUI doesn't work
speedtest-gui-fallback

# Simpler interface as fallback
```

### 4. `speedtest-scheduler` - Automation
```bash
# One-time test with database save
speedtest-scheduler --immediate

# Automatic tests every 30 minutes
speedtest-scheduler --interval 30

# Display statistics
speedtest-scheduler --stats --days 7

# Run in background
nohup speedtest-scheduler --interval 60 > speedtest.log 2>&1 &
```

**Functionality:**
- Automated background testing
- SQLite database storage
- Historical statistics
- Data export

### 5. `speedtest-storage` - Data Management
```bash
# Statistics from last 30 days
speedtest-storage stats --days 30

# Export to CSV
speedtest-storage export csv results.csv

# Export to JSON
speedtest-storage export json data.json --days 7

# Database information
speedtest-storage info

# Clean old data
speedtest-storage cleanup --keep-days 365
```

## ⚙️ PATH Configuration

### Automatic (during installation):
The installer automatically checks if scripts are in PATH and displays instructions if needed.

### Manual configuration:
```bash
# For user installation - add to ~/.bashrc
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Verify it works
which speedtest-cli
```

## 🖥️ Desktop Integration (Linux)

### .desktop File
Installer automatically creates:
```
~/.local/share/applications/speedtest.desktop
```

**Functionality:**
- Icon in applications menu
- Launch by clicking
- Categories: Network, Utility

### Applications Menu
After installation, the application appears in:
- Menu → Network → Speed Test Tool
- or Applications → Internet → Speed Test Tool

## 🔧 Systemd Service (Optional)

### Service installation:
```bash
sudo make service-install
sudo systemctl enable speedtest.service
sudo systemctl start speedtest.service
```

### Management:
```bash
make service-status    # Service status
make service-start     # Start
make service-stop      # Stop
journalctl -u speedtest.service  # Logs
```

## 🎛️ Configuration

### Create configuration:
```bash
speedtest-cli --create-config
```

### File locations:
```
Speed_test/
├── speedtest_config.json     # User configuration
├── speedtest_history.db      # Results database
└── speedtest_env/            # Virtual environment
```

### Example configuration:
```json
{
  "bits_to_mbps": 1000000,
  "speedtest_timeout": 60,
  "max_retries": 3,
  "show_detailed_progress": true,
  "save_results_to_database": true
}
```

## 🧪 Installation Testing

### Quick test:
```bash
make test
# or
python3 test_installation.py --quick
```

### Full test:
```bash
make test-full
# or
python3 test_installation.py
```

### Offline test:
```bash
make test-offline
# or
python3 test_installation.py --no-network
```

### Command testing:
```bash
# Test each command
speedtest-cli --create-config
speedtest-storage info
speedtest-scheduler --immediate
speedtest-gui  # Test GUI (opens window)
```

## 🔍 Troubleshooting

### Scripts not found:
```bash
# Check PATH
echo $PATH

# Check installation
ls -la ~/.local/bin/speedtest-*
# or
ls -la /usr/local/bin/speedtest-*

# Reinstall
python3 install.py --user
```

### Permission errors:
```bash
# Fix permissions
chmod +x ~/.local/bin/speedtest-*

# or system-wide
sudo chmod +x /usr/local/bin/speedtest-*
```

### GUI won't start:
```bash
# Check dependencies
python3 -c "from kivymd.app import MDApp; print('GUI OK')"

# Set backend
export KIVY_GL_BACKEND=gl

# Use fallback
speedtest-gui-fallback
```

### Virtual environment errors:
```bash
# Check if exists
ls -la speedtest_env/

# Reinstall
make setup
python3 install.py
```

## 📊 System Information

### Installation status:
```bash
make info
```

### File locations:
```bash
# Executable scripts
which speedtest-cli
which speedtest-gui
which speedtest-scheduler

# Application files
ls -la Speed_test/

# Desktop entry
ls -la ~/.local/share/applications/speedtest.desktop
```

## 🗑️ Uninstallation

### Basic uninstall:
```bash
python3 uninstall.py
```

### Full uninstall (with data):
```bash
python3 uninstall.py --remove-all
```

### Manual uninstall:
```bash
# Remove scripts
rm ~/.local/bin/speedtest-*
# or
sudo rm /usr/local/bin/speedtest-*

# Remove desktop entry
rm ~/.local/share/applications/speedtest.desktop

# Remove application directory
rm -rf Speed_test/
```

## 💡 Usage Tips

### Aliases (optional):
```bash
# Add to ~/.bashrc for convenience
alias st="speedtest-cli"
alias stgui="speedtest-gui"
alias stats="speedtest-storage stats"
```

### Crontab (alternative to systemd):
```bash
# Edit crontab
crontab -e

# Add line for hourly tests
0 * * * * /home/user/.local/bin/speedtest-scheduler --immediate
```

### Monitoring:
```bash
# Logs from automated tests
tail -f speedtest.log

# Recent results
speedtest-storage stats --days 1

# Export for monitoring
speedtest-storage export json /monitoring/speedtest-$(date +%Y%m).json --days 30
```

## 📈 Usage Examples

### 1. One-time test:
```bash
speedtest-cli
```

### 2. Continuous monitoring:
```bash
# Run in background
nohup speedtest-scheduler --interval 60 > speedtest.log 2>&1 &

# Check results
speedtest-storage stats --days 7
```

### 3. Performance analysis:
```bash
# Export for analysis
speedtest-storage export csv "network-performance-$(date +%Y%m).csv" --days 30

# Import to spreadsheet or analytical tools
```

### 4. GUI for presentation:
```bash
# Launch GUI for demonstration
speedtest-gui

# Real-time monitoring with visual feedback
```

**✅ After installation, the application is ready to use as a standard system application without needing Python knowledge!**
