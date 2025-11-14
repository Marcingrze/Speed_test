#!/bin/bash
# Wrapper script to run speedtest helper from Plasma widget

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HELPER_SCRIPT="$SCRIPT_DIR/speedtest_helper.py"

# Run helper script with the provided command
# Redirect stderr to /dev/null to avoid mixing logs with JSON output
python3 "$HELPER_SCRIPT" "$@" 2>/dev/null
