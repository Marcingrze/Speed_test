#!/usr/bin/env python3
"""
Internet Speed Test Tool (CLI)

Lightweight CLI frontend that delegates all business logic to speedtest_core.
- Loads and validates configuration via SpeedTestConfig
- Uses SpeedTestEngine for connectivity check and testing with retry
- Prints human-friendly results
"""

import sys
from typing import Optional

from speedtest_core import SpeedTestEngine, SpeedTestConfig, SpeedTestResult
from test_results_storage import TestResultStorage


def create_sample_config() -> None:
    """Create a sample configuration file if it doesn't exist (validated)."""
    cfg = SpeedTestConfig()
    if cfg.create_sample_config():
        print("Sample configuration file created: speedtest_config.json")
        print("Edit this file to customize speed test settings.")
    else:
        print("Configuration file already exists.")


def format_and_display_results(result: SpeedTestResult, bits_to_mbps: int) -> None:
    """Format and display speed test results from SpeedTestResult."""
    print("\n" + "=" * 40)
    print("SPEED TEST RESULTS")
    print("=" * 40)
    print(f"Download: {result.download_mbps:.2f} Mbps")
    print(f"Upload:   {result.upload_mbps:.2f} Mbps")
    print(f"Ping:     {result.ping_ms:.1f} ms")
    if result.server_info:
        print(f"Server:   {result.server_info}")
    print("=" * 40)
    if result.warnings:
        print("Warnings:")
        for w in result.warnings:
            print(f" - {w}")


def main() -> int:
    """Run CLI speed test using core engine."""
    print("Internet Speed Test Tool")
    print("-" * 25)

    # Initialize config and engine
    config = SpeedTestConfig()

    # Handle --create-config
    if len(sys.argv) > 1 and sys.argv[1] == "--create-config":
        create_sample_config()
        return 0

    engine = SpeedTestEngine(config)

    # Connectivity check
    print("Checking network connectivity...")
    if not engine.check_network_connectivity():
        print("Error: No internet connection detected.")
        print("Please check your network connection and try again.")
        return 1
    print("Network connection detected.")

    # Run test with retry
    result = engine.run_speed_test_with_retry()

    if not result.is_valid:
        msg = "; ".join(result.warnings) if result.warnings else "Unknown error"
        print(f"\nSpeed test failed: {msg}")
        return 1

    # Display formatted results
    format_and_display_results(result, config['bits_to_mbps'])

    # Save results to database if enabled
    if config['save_results_to_database']:
        storage = None
        try:
            storage = TestResultStorage()
            record_id = storage.save_result(result)
            print(f"\nResult saved to database (ID: {record_id}).")
        except Exception as e:
            print(f"\nWarning: Failed to save result to database: {e}")
            # Log full exception for debugging
            import traceback
            traceback.print_exc()
        finally:
            # Ensure cleanup even if storage creation failed
            if storage and hasattr(storage, 'close'):
                try:
                    storage.close()
                except Exception:
                    pass  # Ignore cleanup errors

    return 0


if __name__ == "__main__":
    sys.exit(main())
