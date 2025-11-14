# Speed Test Tool - Quick Start Guide

> **Polish version**: [pl/QUICKSTART.md](pl/QUICKSTART.md)

## 🚀 Installation in 3 Steps

### 1. Download and Prepare
```bash
# Clone the repository
git clone https://github.com/your-username/Speed_test.git
cd Speed_test

# Grant execution permissions
chmod +x install.py sp.py speedtest_gui.py
```

### 2. Install Automatically
```bash
# For all users (requires sudo)
sudo python3 install.py

# OR for current user only
python3 install.py --user
```

### 3. Run the Application
```bash
# CLI - Terminal speed test
speedtest-cli

# GUI - Graphical interface
speedtest-gui

# Scheduler - Automated tests
speedtest-scheduler --immediate
```

---

## 📋 Alternative Launch Methods

### A. Without Installation (Development Mode)
```bash
# Environment setup
make setup

# Direct execution
make run-cli          # CLI
make run-gui          # GUI
make run-scheduler    # Scheduler
```

### B. Using Makefile
```bash
# Full installation
make install

# Development environment only
make dev-setup

# Functionality tests
make test
```

### C. Manually (Without Automation)
```bash
# Create virtual environment
python3 -m venv speedtest_env
source speedtest_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run
python3 sp.py              # CLI
python3 speedtest_gui.py   # GUI
```

---

## ⚙️ Configuration

### Creating Configuration
```bash
# Create sample configuration
speedtest-cli --create-config

# Edit configuration
nano speedtest_config.json
```

### Example Configuration
```json
{
  "bits_to_mbps": 1000000,
  "speedtest_timeout": 60,
  "max_retries": 3,
  "show_detailed_progress": true,
  "save_results_to_database": true
}
```

---

## 🖥️ User Interfaces

### 1. CLI (Command Line)
```bash
speedtest-cli                    # Basic test
speedtest-cli --create-config    # Create configuration
speedtest-cli --json             # JSON output
```

**Features:**
- ✅ Download/upload/ping test
- ✅ Automatic retry on errors
- ✅ Result validation
- ✅ Colored output
- ✅ Database storage

### 2. GUI (Graphical Interface)
```bash
speedtest-gui                    # Material Design GUI
speedtest-gui-fallback          # Alternative GUI
```

**Features:**
- ✅ Material Design
- ✅ Real-time progress
- ✅ Test cancellation
- ✅ Graphical results
- ✅ History display

### 3. Scheduler (Automation)
```bash
speedtest-scheduler --immediate              # One-time test
speedtest-scheduler --interval 30           # Every 30 minutes
speedtest-scheduler --stats --days 7        # Statistics
```

**Features:**
- ✅ Automated tests
- ✅ Database storage
- ✅ Historical statistics
- ✅ Data export

---

## 🖥️ KDE Plasma Widget

### Widget Installation
```bash
# Install widget
make install-plasmoid

# Or manually
cd plasma-widget
./install_plasmoid.sh
```

### Using the Widget
- Right-click on desktop → Add Widgets → Search "Speed Test"
- Widget displays latest results from database
- Auto-refreshes every 30 seconds
- Can be added to panel or desktop

---

## 📊 Data Management

### Displaying Statistics
```bash
speedtest-storage stats --days 30           # Last 30 days
speedtest-storage info                      # Database info
```

### Data Export
```bash
speedtest-storage export csv results.csv     # Export to CSV
speedtest-storage export json data.json    # Export to JSON
```

### Cleaning Old Data
```bash
speedtest-storage cleanup --keep-days 365   # Delete older than 1 year
```

---

## 🔧 Troubleshooting

### GUI Won't Start (Python 3.13+)
```bash
# Automatic patch is applied during installation
# If GUI doesn't work, apply patch manually:
source speedtest_env/bin/activate
python3 fix_speedtest_py313.py

# Check GUI dependencies
python3 -c "from kivymd.app import MDApp; print('GUI OK')"

# Set OpenGL backend
export KIVY_GL_BACKEND=gl

# Use alternative GUI
speedtest-gui-fallback
```

### Network Issues
```bash
# Test basic connectivity
ping -c 4 8.8.8.8

# Debug speedtest-cli
speedtest-cli --simple
```

### Permission Issues
```bash
# Fix permissions
chmod +x speedtest-*

# User installation
python3 install.py --user
```

---

## 🎯 Common Use Cases

### One-Time Test
```bash
speedtest-cli
```

### Background Monitoring
```bash
# Run in background
nohup speedtest-scheduler --interval 60 > speedtest.log 2>&1 &

# Check status
tail -f speedtest.log
```

### Performance Analysis
```bash
# Weekly statistics
speedtest-scheduler --stats --days 7

# Export for further analysis
speedtest-storage export csv "analysis-$(date +%Y%m).csv" --days 30
```

### Testing After Network Changes
```bash
# Test before change
speedtest-cli > before.txt

# Test after change
speedtest-cli > after.txt

# Compare results
diff before.txt after.txt
```

---

## 📁 File Structure

```
Speed_test/
├── speedtest-cli*           # CLI executable
├── speedtest-gui*           # GUI executable
├── speedtest-scheduler*     # Scheduler executable
├── speedtest-storage*       # Storage management
├── speedtest_config.json    # User configuration
├── speedtest_history.db     # Results database
├── plasma-widget/           # KDE Plasma widget
├── install.py*              # Installer
├── uninstall.py*            # Uninstaller
└── Makefile                 # Build automation
```

---

## 🔄 Updates

### Code Updates
```bash
git pull origin main
make update                  # Update dependencies
sudo python3 install.py     # Reinstall scripts
```

### Data Backup
```bash
make backup                  # Backup config and data
make restore                 # Restore from backup
```

---

## 🗑️ Uninstallation

### Partial (Keep Data)
```bash
python3 uninstall.py
```

### Complete (Remove Everything)
```bash
python3 uninstall.py --remove-all
```

### Manual Removal
```bash
# Remove executables
sudo rm /usr/local/bin/speedtest-*
# Or for user installation:
rm ~/.local/bin/speedtest-*

# Remove application directory
rm -rf Speed_test/
```

---

## 📞 Support

- **Bugs**: Create an issue on GitHub
- **Documentation**: README.md, AGENTS.md, INSTALLER.md
- **Configuration**: speedtest_config.json.example

---

## ⚡ Command Reference

| Command | Description |
|---------|-------------|
| `speedtest-cli` | CLI test |
| `speedtest-cli --json` | JSON output |
| `speedtest-gui` | Graphical interface |
| `speedtest-scheduler --immediate` | One-time test |
| `speedtest-scheduler --interval 30` | Every 30 min |
| `speedtest-storage stats` | Statistics |
| `speedtest-storage export csv` | CSV export |
| `make install` | Installation |
| `make install-plasmoid` | Install KDE widget |
| `make test` | Functionality test |
| `make clean` | Cleanup |

**Get Started in 30 Seconds:**
```bash
git clone repo && cd Speed_test
make setup
python3 sp.py --create-config
python3 speedtest_gui.py
```
