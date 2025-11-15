#!/usr/bin/env python3
"""
Speed Test Helper for KDE Plasma Widget

Provides backend functionality for the Plasma widget:
- Retrieves last test results from database
- Triggers new speed tests
- Returns data in JSON format for QML consumption
- Maintains cache file for widget to read
"""

import sys
import json
import subprocess
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Setup logging
log_dir = Path.home() / '.local' / 'share'
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'plasma_speedtest.log'),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)

# Cache file for widget to read
CACHE_DIR = Path.home() / '.cache' / 'plasma-speedtest'
CACHE_FILE = CACHE_DIR / 'widget_cache.json'

def ensure_cache_dir():
    """Ensure cache directory exists."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def find_project_root() -> Path:
    """Find project root by looking for marker file.

    Returns:
        Path to project root directory

    Raises:
        RuntimeError: If project root cannot be located
    """
    current = Path(__file__).resolve().parent

    # Search upward for speedtest_core.py (marker file)
    for _ in range(10):  # Limit depth to prevent infinite loop
        if (current / "speedtest_core.py").exists():
            logger.info(f"Found project root at: {current}")
            return current
        if current.parent == current:  # Reached filesystem root
            break
        current = current.parent

    # Fallback: check common installation locations
    possible_roots = [
        Path.home() / "Projekty" / "Speed_test",
        Path("/opt/Speed_test"),
        Path("/usr/local/share/Speed_test")
    ]

    for root in possible_roots:
        if root.exists() and (root / "speedtest_core.py").exists():
            logger.info(f"Found project root at fallback location: {root}")
            return root

    error_msg = "Could not locate project root. Searched paths: " + ", ".join(str(p) for p in possible_roots)
    logger.error(error_msg)
    raise RuntimeError(error_msg)


# Find and validate project root
try:
    parent_dir = find_project_root()
    sys.path.insert(0, str(parent_dir))
except RuntimeError as e:
    print(json.dumps({
        "status": "error",
        "message": f"Failed to locate Speed Test installation: {e}",
        "hint": "Make sure Speed Test is installed. Try running 'make setup' in the project directory."
    }))
    sys.exit(1)

# Import speedtest modules
try:
    from test_results_storage import TestResultStorage
    from speedtest_core import SpeedTestEngine, SpeedTestConfig
except ImportError as e:
    logger.error(f"Import error: {e}", exc_info=True)
    print(json.dumps({
        "status": "error",
        "message": f"Failed to import speedtest modules: {e}",
        "hint": "Make sure speedtest is installed. Try running 'make setup' in the project directory.",
        "path_searched": str(parent_dir)
    }))
    sys.exit(1)


def find_python_executable() -> Path:
    """Find the appropriate Python executable.

    Returns:
        Path to Python executable
    """
    # Check common venv locations in project root
    for venv_name in ['speedtest_env', 'venv', '.venv', 'env', 'ebv']:
        venv_python = parent_dir / venv_name / "bin" / "python3"
        if venv_python.exists():
            logger.info(f"Found Python in venv: {venv_python}")
            return venv_python

    # Check if installed system-wide
    system_python = shutil.which("python3")
    if system_python:
        logger.info(f"Using system Python: {system_python}")
        return Path(system_python)

    # Last resort
    logger.warning("Using fallback Python: /usr/bin/python3")
    return Path("/usr/bin/python3")


def write_cache(data: Dict[str, Any]) -> None:
    """Write data to cache file for widget to read.

    Args:
        data: Dictionary to write to cache
    """
    try:
        ensure_cache_dir()
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Cache updated: {CACHE_FILE}")
    except Exception as e:
        logger.error(f"Failed to write cache: {e}", exc_info=True)


def get_last_result() -> Dict[str, Any]:
    """Get the most recent test result from database.

    Returns:
        Dictionary with test result or error information
    """
    try:
        # Use default database path (shared by all components)
        storage = TestResultStorage()
        results = storage.get_recent_results(limit=1)

        if not results:
            result_data = {
                "status": "no_data",
                "message": "No test results available. Run a test first."
            }
            write_cache(result_data)
            return result_data

        result = results[0]
        # Convert timestamp to readable format
        test_time = datetime.fromtimestamp(result['timestamp'])

        # Safely parse warnings JSON
        warnings = []
        if result['warnings']:
            try:
                warnings = json.loads(result['warnings'])
            except (json.JSONDecodeError, TypeError) as e:
                logger.warning(f"Failed to parse warnings JSON: {e}")
                warnings = [f"Error parsing warnings: {str(e)}"]

        result_data = {
            "status": "success",
            "download": round(result['download_mbps'], 1),
            "upload": round(result['upload_mbps'], 1),
            "ping": round(result['ping_ms'], 0),
            "server": result['server_info'],
            "timestamp": test_time.strftime("%Y-%m-%d %H:%M:%S"),
            "is_valid": result['is_valid'],
            "warnings": warnings
        }
        write_cache(result_data)
        return result_data
    except Exception as e:
        logger.error(f"Failed to retrieve results: {e}", exc_info=True)
        error_data = {
            "status": "error",
            "message": f"Failed to retrieve results: {str(e)}"
        }
        write_cache(error_data)
        return error_data


def run_test_background() -> Dict[str, Any]:
    """Start a speed test in the background.

    Returns:
        Dictionary with success/error information
    """
    try:
        # Get and validate paths
        cli_script = parent_dir / "sp.py"
        python_exec = find_python_executable()

        # Security: Resolve to absolute paths
        cli_script = cli_script.resolve()
        python_exec = python_exec.resolve()

        # Security: Verify cli_script is within expected directory
        if not str(cli_script).startswith(str(parent_dir.resolve())):
            error_msg = "Security error: CLI script path validation failed"
            logger.error(f"{error_msg}: {cli_script} not under {parent_dir}")
            return {
                "status": "error",
                "message": error_msg
            }

        if not cli_script.exists():
            error_msg = f"CLI script not found at {cli_script}"
            logger.error(error_msg)
            return {
                "status": "error",
                "message": error_msg
            }

        if not python_exec.exists():
            error_msg = f"Python executable not found at {python_exec}"
            logger.error(error_msg)
            return {
                "status": "error",
                "message": error_msg
            }

        # Run test in background with explicit working directory
        logger.info(f"Starting background test: {python_exec} {cli_script}")
        subprocess.Popen(
            [str(python_exec), str(cli_script)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
            cwd=str(parent_dir)  # Explicit working directory
        )
        logger.info("Background test started successfully")

        return {
            "status": "success",
            "message": "Speed test started in background"
        }
    except Exception as e:
        logger.error(f"Failed to start background test: {e}", exc_info=True)
        return {
            "status": "error",
            "message": f"Failed to start test: {str(e)}"
        }


def check_connectivity() -> Dict[str, Any]:
    """Check if network connection is available.

    Returns:
        Dictionary with connectivity status
    """
    try:
        config = SpeedTestConfig()
        engine = SpeedTestEngine(config)
        is_connected = engine.check_network_connectivity()

        # Don't overwrite existing test results, just log connectivity
        logger.info(f"Network connectivity check: {is_connected}")

        return {
            "status": "success",
            "connected": is_connected
        }
    except Exception as e:
        logger.error(f"Failed to check connectivity: {e}", exc_info=True)
        return {
            "status": "error",
            "message": f"Failed to check connectivity: {str(e)}",
            "connected": False
        }


def main() -> None:
    """Main entry point for the helper script."""
    valid_commands = ["get_last", "run_test", "check_network"]

    if len(sys.argv) < 2:
        print(json.dumps({
            "status": "error",
            "message": "Usage: speedtest_helper.py <command>",
            "commands": valid_commands
        }))
        sys.exit(1)

    command = sys.argv[1]

    # Validate command
    if not isinstance(command, str) or command not in valid_commands:
        logger.warning(f"Invalid command received: {command}")
        print(json.dumps({
            "status": "error",
            "message": f"Invalid command: {command}",
            "commands": valid_commands
        }))
        sys.exit(1)

    # Execute command
    if command == "get_last":
        result = get_last_result()
    elif command == "run_test":
        result = run_test_background()
    elif command == "check_network":
        result = check_connectivity()
    else:
        # Should never reach here due to validation above
        result = {
            "status": "error",
            "message": f"Unknown command: {command}",
            "commands": valid_commands
        }

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
