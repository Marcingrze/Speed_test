#!/usr/bin/env python3
"""
Internet Speed Test Tool

A simple utility to test internet connection speed using speedtest.net.
Measures download speed, upload speed, and ping latency.
"""

import sys
import time
import json
from pathlib import Path
import speedtest
from typing import Optional, Dict, Any, Tuple

# Import configuration management from core module
try:
    from speedtest_core import SpeedTestConfig
    USE_CORE_CONFIG = True
except ImportError:
    # Fallback to local config if speedtest_core is not available
    USE_CORE_CONFIG = False


# Default configuration (used if speedtest_core is not available)
DEFAULT_CONFIG = {
    'bits_to_mbps': 1_000_000,
    'connectivity_check_timeout': 10,
    'speedtest_timeout': 60,
    'max_retries': 3,
    'retry_delay': 2,
    'max_typical_speed_gbps': 1,
    'max_reasonable_speed_gbps': 10,
    'max_typical_ping_ms': 1000,
    'max_reasonable_ping_ms': 10000,
    'show_detailed_progress': True
}

# Global configuration (will be loaded from file or defaults)
config_obj = None
config = DEFAULT_CONFIG.copy()


def load_config() -> None:
    """Load configuration from file or use defaults with validation.

    Looks for speedtest_config.json in current directory.
    If not found, uses default configuration.
    """
    global config, config_obj

    if USE_CORE_CONFIG:
        # Use validated configuration from speedtest_core
        config_obj = SpeedTestConfig()
        config = config_obj.config
        print("Configuration loaded and validated")
    else:
        # Fallback to simple file loading without validation
        config_file = Path('speedtest_config.json')

        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    file_config = json.load(f)
                # Update config with values from file, keeping defaults for missing keys
                config.update(file_config)
                print(f"Configuration loaded from {config_file}")
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load config file {config_file}: {e}")
                print("Using default configuration.")
        else:
            print("Using default configuration (create speedtest_config.json to customize).")


def create_sample_config() -> None:
    """Create a sample configuration file if it doesn't exist."""
    if USE_CORE_CONFIG:
        # Use core module to create validated config
        temp_config = SpeedTestConfig()
        if temp_config.create_sample_config():
            print("Sample configuration file created: speedtest_config.json")
            print("Edit this file to customize speed test settings.")
        else:
            print("Configuration file already exists.")
    else:
        # Fallback to simple file creation
        config_file = Path('speedtest_config.json')
        if not config_file.exists():
            with open(config_file, 'w') as f:
                json.dump(DEFAULT_CONFIG, f, indent=2)
            print(f"Sample configuration file created: {config_file}")
            print("Edit this file to customize speed test settings.")


def check_network_connectivity() -> bool:
    """Check if internet connection is available.
    
    Returns:
        bool: True if connection is available, False otherwise
    """
    try:
        # Try to create a speedtest object with a short timeout
        test_client = speedtest.Speedtest(timeout=config['connectivity_check_timeout'])
        test_client.get_config()
        return True
    except (speedtest.SpeedtestException, speedtest.ConfigRetrievalError, 
            OSError, TimeoutError, ConnectionError):
        return False


def run_speed_test_with_retry(max_retries: int = None) -> Optional[Dict[str, Any]]:
    """Run speed test with retry logic for transient failures.
    
    Args:
        max_retries: Maximum number of retry attempts
        
    Returns:
        Dict containing test results or None if all attempts failed
    """
    if max_retries is None:
        max_retries = config['max_retries']
        
    for attempt in range(max_retries):
        try:
            return run_speed_test()
        except (speedtest.ConfigRetrievalError, OSError, ConnectionError) as e:
            if attempt < max_retries - 1:
                print(f"Attempt {attempt + 1} failed: {e}")
                print(f"Retrying in {config['retry_delay']} seconds...")
                time.sleep(config['retry_delay'])
                continue
            else:
                print(f"All {max_retries} attempts failed. Last error: {e}")
                return None
        except Exception as e:
            # Don't retry for non-network errors
            print(f"Non-recoverable error: {e}")
            return None
    
    return None


def run_speed_test() -> Optional[Dict[str, Any]]:
    """Run internet speed test and return results.
    
    Returns:
        Dict containing test results or None if test failed
    """
    speedtest_client = None
    
    try:
        print("Initializing speed test...")
        speedtest_client = speedtest.Speedtest(timeout=config['speedtest_timeout'])
        
        print("Fetching server list...")
        speedtest_client.get_servers()
        
        print("Selecting best server...")
        best_server = speedtest_client.get_best_server()
        print(f"Using server: {best_server['sponsor']} ({best_server['name']})")
        
        # Download test with detailed progress
        if config['show_detailed_progress']:
            print("Testing download speed... (typically takes 10-30 seconds)")
        else:
            print("Testing download speed...")
        start_time = time.time()
        speedtest_client.download()
        download_time = time.time() - start_time
        print(f"Download test completed in {download_time:.1f} seconds")
        
        # Upload test with detailed progress
        if config['show_detailed_progress']:
            print("Testing upload speed... (typically takes 15-45 seconds)")
        else:
            print("Testing upload speed...")
        start_time = time.time()
        speedtest_client.upload()
        upload_time = time.time() - start_time
        print(f"Upload test completed in {upload_time:.1f} seconds")
        
        # Safely extract results
        results = speedtest_client.results.dict()
        
        # Validate results with detailed warnings
        is_valid, warning_message = validate_results(results)
        if warning_message:
            print(f"Warning: {warning_message}")
        
        return results
        
    except speedtest.ConfigRetrievalError:
        print("Error: Unable to retrieve speedtest configuration.")
        print("Please check your internet connection and try again.")
        return None
    except speedtest.NoMatchedServers:
        print("Error: No speedtest servers found.")
        print("Please try again later.")
        return None
    except speedtest.SpeedtestException as e:
        print(f"Speedtest error: {e}")
        return None
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
        return None
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
        print("Please check your internet connection and try again.")
        return None
    finally:
        # speedtest-cli handles cleanup automatically
        pass


def validate_results(results: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate speedtest results with tiered warnings.
    
    Args:
        results: Dictionary containing test results
        
    Returns:
        Tuple of (is_valid, warning_message)
        - is_valid: True if results are not completely invalid
        - warning_message: Empty string if no issues, otherwise descriptive warning
    """
    try:
        download = results.get('download', 0)
        upload = results.get('upload', 0)
        ping = results.get('ping', 0)
        
        # Check for completely invalid values
        if download < 0 or upload < 0 or ping < 0:
            return False, "Invalid negative values detected - measurement failed"
            
        # Check for absolutely unreasonable values
        max_reasonable_bps = config['max_reasonable_speed_gbps'] * 1_000_000_000
        if download > max_reasonable_bps or upload > max_reasonable_bps:
            return False, "Extremely high speeds detected - likely measurement error"
            
        if ping > config['max_reasonable_ping_ms']:
            return False, "Extremely high ping detected - likely measurement error"
        
        # Check for unusually high but not impossible values
        max_typical_bps = config['max_typical_speed_gbps'] * 1_000_000_000
        if download > max_typical_bps or upload > max_typical_bps:
            speed_gbps = max(download, upload) / 1_000_000_000
            return True, f"Unusually high speed ({speed_gbps:.1f} Gbps) - please verify results"
            
        if ping > config['max_typical_ping_ms']:
            return True, f"High latency ({ping:.0f} ms) detected - connection may be slow"
        
        # Check for suspiciously low values that might indicate issues
        if download < 1_000_000 and upload < 1_000_000:  # Less than 1 Mbps
            return True, "Very low speeds detected - check network connection"
            
        return True, ""  # No issues detected
        
    except (KeyError, TypeError, ValueError):
        return False, "Invalid result data structure - measurement failed"


def format_and_display_results(results: Dict[str, Any]) -> None:
    """Format and display speed test results.
    
    Args:
        results: Dictionary containing test results
    """
    try:
        # Safely extract values with defaults
        download_speed = results.get('download', 0) / config['bits_to_mbps']
        upload_speed = results.get('upload', 0) / config['bits_to_mbps']
        ping_latency = results.get('ping', 0)
        
        print("\n" + "="*40)
        print("SPEED TEST RESULTS")
        print("="*40)
        print(f"Download: {download_speed:.2f} Mbps")
        print(f"Upload:   {upload_speed:.2f} Mbps")
        print(f"Ping:     {ping_latency:.1f} ms")
        print("="*40)
        
    except (KeyError, TypeError, ValueError) as e:
        print(f"Error formatting results: {e}")
        print("Raw results:", results)


def main() -> int:
    """Main function to orchestrate the speed test.
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    print("Internet Speed Test Tool")
    print("-" * 25)
    
    # Load configuration
    load_config()
    
    # Check if user wants to create sample config
    if len(sys.argv) > 1 and sys.argv[1] == '--create-config':
        create_sample_config()
        return 0
    
    # Check network connectivity first
    print("Checking network connectivity...")
    if not check_network_connectivity():
        print("Error: No internet connection detected.")
        print("Please check your network connection and try again.")
        return 1
    
    print("Network connection detected.")
    
    # Run the speed test with retry logic
    results = run_speed_test_with_retry()
    
    if results is None:
        print("\nSpeed test failed. Please try again.")
        return 1
    
    # Display results
    format_and_display_results(results)
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)