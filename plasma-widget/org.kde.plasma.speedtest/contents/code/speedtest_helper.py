#!/usr/bin/env python3
"""
Speed Test Helper for KDE Plasma Widget

Provides backend functionality for the Plasma widget:
- Retrieves last test results from database
- Triggers new speed tests
- Returns data in JSON format for QML consumption
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import speedtest modules
parent_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(parent_dir))

try:
    from test_results_storage import TestResultStorage
    from speedtest_core import SpeedTestEngine, SpeedTestConfig
except ImportError as e:
    # Fallback: try to import from installed location
    print(json.dumps({
        "error": f"Failed to import speedtest modules: {e}",
        "hint": "Make sure speedtest is installed"
    }))
    sys.exit(1)


def get_last_result():
    """Get the most recent test result from database."""
    try:
        storage = TestResultStorage()
        results = storage.get_recent_results(limit=1)

        if not results:
            return {
                "status": "no_data",
                "message": "No test results available. Run a test first."
            }

        result = results[0]
        # Convert timestamp to readable format
        test_time = datetime.fromtimestamp(result['timestamp'])

        return {
            "status": "success",
            "download": round(result['download_mbps'], 1),
            "upload": round(result['upload_mbps'], 1),
            "ping": round(result['ping_ms'], 0),
            "server": result['server_info'],
            "timestamp": test_time.strftime("%Y-%m-%d %H:%M:%S"),
            "is_valid": result['is_valid'],
            "warnings": json.loads(result['warnings']) if result['warnings'] else []
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to retrieve results: {str(e)}"
        }


def run_test_background():
    """Start a speed test in the background."""
    try:
        # Get the path to the CLI script
        cli_script = parent_dir / "sp.py"
        python_exec = parent_dir / "speedtest_env" / "bin" / "python3"

        if not cli_script.exists():
            return {
                "status": "error",
                "message": f"CLI script not found at {cli_script}"
            }

        if not python_exec.exists():
            python_exec = "python3"  # Fallback to system python

        # Run test in background
        subprocess.Popen(
            [str(python_exec), str(cli_script)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )

        return {
            "status": "success",
            "message": "Speed test started in background"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to start test: {str(e)}"
        }


def check_connectivity():
    """Check if network connection is available."""
    try:
        config = SpeedTestConfig()
        engine = SpeedTestEngine(config)
        is_connected = engine.check_network_connectivity()

        return {
            "status": "success",
            "connected": is_connected
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to check connectivity: {str(e)}",
            "connected": False
        }


def main():
    """Main entry point for the helper script."""
    if len(sys.argv) < 2:
        print(json.dumps({
            "status": "error",
            "message": "Usage: speedtest_helper.py <command>",
            "commands": ["get_last", "run_test", "check_network"]
        }))
        sys.exit(1)

    command = sys.argv[1]

    if command == "get_last":
        result = get_last_result()
    elif command == "run_test":
        result = run_test_background()
    elif command == "check_network":
        result = check_connectivity()
    else:
        result = {
            "status": "error",
            "message": f"Unknown command: {command}",
            "commands": ["get_last", "run_test", "check_network"]
        }

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
