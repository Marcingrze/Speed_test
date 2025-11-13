# Speed Test KDE Plasma Widget

A lightweight desktop widget for KDE Plasma that displays internet speed test results.

## Features

- **Real-time Display**: Shows download speed, upload speed, and ping latency
- **Auto-refresh**: Automatically updates results every 30 seconds
- **One-click Testing**: Run new speed tests directly from the widget
- **Network Status**: Indicates when network connection is unavailable
- **Compact Mode**: Can be added to panel with tooltip showing quick stats
- **Database Integration**: Uses shared SQLite database with CLI and GUI versions

## Requirements

- KDE Plasma 5.x or 6.x
- Python 3.8+
- Speed Test application installed (parent directory)
- `test_results_storage.py` and `speedtest_core.py` modules accessible

## Installation

### Automatic Installation

```bash
cd plasma-widget
./install_plasmoid.sh
```

The script will:
1. Install the widget to `~/.local/share/plasma/plasmoids/`
2. Make it available in the "Add Widgets" menu

### Manual Installation (Alternative)

Using `kpackagetool`:

```bash
# For Plasma 5
kpackagetool5 --type=Plasma/Applet --install org.kde.plasma.speedtest

# For Plasma 6
kpackagetool6 --type=Plasma/Applet --install org.kde.plasma.speedtest
```

## Usage

### Adding to Desktop

1. Right-click on your desktop
2. Select **"Add Widgets"**
3. Search for **"Speed Test"**
4. Drag the widget to your desktop

### Adding to Panel

1. Right-click on your panel
2. Select **"Add Widgets"**
3. Search for **"Speed Test"**
4. Click to add to panel

### Using the Widget

- **View Results**: The widget displays the most recent test results from the database
- **Run Test**: Click the "Run Speed Test" button to start a new test
- **Refresh**: Click the refresh icon to manually update displayed results
- **Auto-update**: Results automatically refresh every 30 seconds
- **Compact Mode**: When in panel, hover over the icon to see quick stats

## Widget Layout

### Full Representation (Desktop)

```
┌────────────────────────────┐
│ Speed Test          [↻]    │
├────────────────────────────┤
│  Download      Upload      │
│  85.4 Mbps     45.2 Mbps   │
│     ↓             ↑        │
│                            │
│        Ping: 12 ms         │
├────────────────────────────┤
│  Orange Polska (Warsaw)    │
│  Last update: 18:42:35     │
├────────────────────────────┤
│    [Run Speed Test]        │
└────────────────────────────┘
```

### Compact Representation (Panel)

```
[Network Icon] ↓85.4 Mbps ↑45.2 Mbps
```

## Technical Details

### Backend Integration

The widget uses a Python helper script (`speedtest_helper.py`) that:

- **get_last**: Retrieves the most recent test result from SQLite database
- **run_test**: Starts a new speed test in the background (non-blocking)
- **check_network**: Verifies network connectivity status

### Communication

- QML frontend → Python backend via `PlasmaCore.DataSource` (executable engine)
- Data format: JSON
- All operations are asynchronous to prevent UI freezing

### File Structure

```
org.kde.plasma.speedtest/
├── metadata.json              # Widget metadata
└── contents/
    ├── ui/
    │   └── main.qml          # QML interface
    ├── code/
    │   └── speedtest_helper.py   # Python backend
    └── config/               # Configuration (future use)
```

## Uninstallation

```bash
cd plasma-widget
./uninstall_plasmoid.sh
```

Or manually:

```bash
# For Plasma 5
kpackagetool5 --type=Plasma/Applet --remove org.kde.plasma.speedtest

# For Plasma 6
kpackagetool6 --type=Plasma/Applet --remove org.kde.plasma.speedtest
```

## Troubleshooting

### Widget Not Showing Results

1. **Check database**: Ensure `speedtest_history.db` exists in the parent directory
2. **Run a test**: Use CLI or GUI to run at least one test first
3. **Check permissions**: Ensure helper script is executable (`chmod +x speedtest_helper.py`)

### "No network connection" Warning

- The widget checks connectivity on startup
- Click refresh icon to recheck
- Ensure speedtest_core.py is accessible

### Widget Not Appearing in Menu

1. Restart Plasma Shell:
   ```bash
   kquitapp5 plasmashell && kstart5 plasmashell
   ```
2. Or for Plasma 6:
   ```bash
   kquitapp6 plasmashell && kstart6 plasmashell
   ```

### Python Module Import Errors

- Ensure the Speed Test application is installed in the parent directory
- Check that `speedtest_env` virtual environment exists
- Verify `test_results_storage.py` and `speedtest_core.py` are accessible

## Configuration

Currently, the widget uses default settings:

- **Auto-refresh interval**: 30 seconds
- **Test completion wait**: 60 seconds
- **Database path**: `../speedtest_history.db` (relative to widget)

Future versions may include configurable settings through the widget configuration dialog.

## Development

### Testing Changes

After modifying QML or Python files:

```bash
# Reinstall widget
./install_plasmoid.sh

# Restart Plasma
kquitapp5 plasmashell && kstart5 plasmashell
```

### Debugging

Check Plasma logs for errors:

```bash
journalctl --user -f | grep plasma
```

## License

MIT License - Same as the main Speed Test application

## Credits

- Built for KDE Plasma Desktop Environment
- Integrates with Speed Test CLI/GUI application
- Uses Qt Quick/QML and Python
