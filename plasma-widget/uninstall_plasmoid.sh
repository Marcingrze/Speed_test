#!/bin/bash
#
# Speed Test Plasma Widget Uninstaller
# Removes the plasmoid from user's local Plasma widgets directory
#

set -e

WIDGET_NAME="org.kde.plasma.speedtest"
WIDGET_DIR="$HOME/.local/share/plasma/plasmoids/$WIDGET_NAME"

echo "========================================"
echo "Speed Test Plasma Widget Uninstaller"
echo "========================================"
echo ""

# Check if widget is installed
if [ ! -d "$WIDGET_DIR" ]; then
    echo "Widget is not installed at: $WIDGET_DIR"

    # Try using kpackagetool to check
    if command -v kpackagetool5 &> /dev/null || command -v kpackagetool6 &> /dev/null; then
        KPACKAGETOOL="kpackagetool5"
        if command -v kpackagetool6 &> /dev/null; then
            KPACKAGETOOL="kpackagetool6"
        fi

        if $KPACKAGETOOL --type=Plasma/Applet --show="$WIDGET_NAME" &> /dev/null; then
            echo "Found widget installed via kpackagetool. Removing..."
            $KPACKAGETOOL --type=Plasma/Applet --remove="$WIDGET_NAME"
            echo "✓ Widget removed successfully"
            exit 0
        fi
    fi

    echo "Widget not found. Nothing to uninstall."
    exit 0
fi

# Remove widget directory
echo "Removing widget from: $WIDGET_DIR"
rm -rf "$WIDGET_DIR"

echo "✓ Widget removed successfully"
echo ""
echo "Note: You may need to restart Plasma for changes to take effect:"
echo "  kquitapp5 plasmashell && kstart5 plasmashell"
echo ""
echo "Uninstallation complete!"
