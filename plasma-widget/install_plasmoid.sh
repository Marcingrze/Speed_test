#!/bin/bash
#
# Speed Test Plasma Widget Installer
# Installs the plasmoid to user's local Plasma widgets directory
#

set -e

WIDGET_NAME="org.kde.plasma.speedtest"
WIDGET_DIR="$HOME/.local/share/plasma/plasmoids/$WIDGET_NAME"
SOURCE_DIR="$(dirname "$0")/$WIDGET_NAME"

echo "========================================"
echo "Speed Test Plasma Widget Installer"
echo "========================================"
echo ""

# Check if source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: Widget source directory not found: $SOURCE_DIR"
    exit 1
fi

# Check if KDE Plasma is available
if ! command -v kpackagetool5 &> /dev/null && ! command -v kpackagetool6 &> /dev/null; then
    echo "Warning: kpackagetool not found. Installing manually..."

    # Manual installation
    echo "Installing widget to: $WIDGET_DIR"

    # Remove old installation if exists
    if [ -d "$WIDGET_DIR" ]; then
        echo "Removing old installation..."
        rm -rf "$WIDGET_DIR"
    fi

    # Create directory and copy files
    mkdir -p "$WIDGET_DIR"
    cp -r "$SOURCE_DIR"/* "$WIDGET_DIR/"

    echo "✓ Widget installed successfully"
    echo ""
    echo "To use the widget:"
    echo "  1. Right-click on your desktop or panel"
    echo "  2. Select 'Add Widgets'"
    echo "  3. Search for 'Speed Test'"
    echo "  4. Add it to your desktop or panel"
    echo ""
    echo "Note: You may need to restart Plasma for changes to take effect:"
    echo "  kquitapp5 plasmashell && kstart5 plasmashell"

else
    # Use kpackagetool
    KPACKAGETOOL="kpackagetool5"
    PLASMA_VERSION=5
    if command -v kpackagetool6 &> /dev/null; then
        KPACKAGETOOL="kpackagetool6"
        PLASMA_VERSION=6
    fi

    echo "Using $KPACKAGETOOL for installation (Plasma $PLASMA_VERSION)..."

    # Remove old installation if exists
    if $KPACKAGETOOL --type=Plasma/Applet --show="$WIDGET_NAME" &> /dev/null; then
        echo "Removing old installation..."
        $KPACKAGETOOL --type=Plasma/Applet --remove="$WIDGET_NAME" || true
    fi

    # Install widget
    echo "Installing widget..."
    if $KPACKAGETOOL --type=Plasma/Applet --install="$SOURCE_DIR"; then
        echo "✓ Widget installed successfully"
    else
        echo "Installation via kpackagetool failed, trying manual installation..."
        # Fallback to manual installation
        mkdir -p "$WIDGET_DIR"
        cp -r "$SOURCE_DIR"/* "$WIDGET_DIR/"
        echo "✓ Widget installed manually"
    fi

    echo ""
    echo "To use the widget:"
    echo "  1. Right-click on your desktop or panel"
    echo "  2. Select 'Add Widgets'"
    echo "  3. Search for 'Speed Test'"
    echo "  4. Add it to your desktop or panel"
    echo ""
    echo "Note: You may need to restart Plasma for changes to take effect:"
    if [ "$PLASMA_VERSION" = "6" ]; then
        echo "  kquitapp6 plasmashell && kstart6 plasmashell"
    else
        echo "  kquitapp5 plasmashell && kstart5 plasmashell"
    fi
fi

echo ""
echo "Installation complete!"
