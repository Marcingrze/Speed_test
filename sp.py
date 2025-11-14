#!/usr/bin/env python3
"""
Internet Speed Test Tool (CLI)

Lightweight CLI frontend that delegates all business logic to speedtest_core.
- Loads and validates configuration via SpeedTestConfig
- Uses SpeedTestEngine for connectivity check and testing with retry
- Prints human-friendly results
"""

import sys
import json
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
    # Simple args parsing (keep CLI lightweight)
    args = sys.argv[1:]
    json_output = False

    # Initialize config and engine
    config = SpeedTestConfig()

    # Handle flags
    if args:
        # very simple parsing: support either flag in any single position
        if "--create-config" in args:
            create_sample_config()
            return 0
        if "--json" in args:
            json_output = True
        if "-h" in args or "--help" in args:
            print("Usage: python sp.py [--create-config] [--json]")
            return 0

    if not json_output:
        print("Internet Speed Test Tool")
        print("-" * 25)

    engine = SpeedTestEngine(config)

    # Connectivity check
    if not json_output:
        print("Checking network connectivity...")
    if not engine.check_network_connectivity():
        if json_output:
            print(json.dumps({
                "status": "error",
                "message": "No internet connection detected.",
                "is_valid": False,
            }, ensure_ascii=False))
        else:
            print("Error: No internet connection detected.")
            print("Please check your network connection and try again.")
        return 1
    if not json_output:
        print("Network connection detected.")

    # Run test with retry
    result = engine.run_speed_test_with_retry()

    if not result.is_valid:
        msg = "; ".join(result.warnings) if result.warnings else "Unknown error"
        if json_output:
            print(json.dumps({
                "status": "error",
                "message": msg,
                "warnings": result.warnings,
                "is_valid": False,
            }, ensure_ascii=False))
        else:
            print(f"\nSpeed test failed: {msg}")
        return 1

    # Display results
    if json_output:
        print(json.dumps({
            **result.to_dict(),
            "status": "success",
        }, ensure_ascii=False))
    else:
        format_and_display_results(result, config['bits_to_mbps'])

    # Save results to database if enabled
    if config['save_results_to_database']:
        storage = None
        try:
            storage = TestResultStorage()
            record_id = storage.save_result(result)
            if not json_output:
                print(f"\nResult saved to database (ID: {record_id}).")
        except Exception as e:
            if not json_output:
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

    # Update Plasma widget cache
    try:
        from pathlib import Path
        import json as json_module
        from datetime import datetime as dt

        cache_dir = Path.home() / '.cache' / 'plasma-speedtest'
        cache_file = cache_dir / 'widget_cache.json'
        cache_dir.mkdir(parents=True, exist_ok=True)

        cache_data = {
            "status": "success",
            "download": round(result.download_mbps, 1),
            "upload": round(result.upload_mbps, 1),
            "ping": round(result.ping_ms, 0),
            "server": result.server_info,
            "timestamp": dt.fromtimestamp(result.timestamp).strftime("%Y-%m-%d %H:%M:%S"),
            "is_valid": result.is_valid,
            "warnings": result.warnings
        }

        with open(cache_file, 'w', encoding='utf-8') as f:
            json_module.dump(cache_data, f, ensure_ascii=False, indent=2)

        if not json_output:
            print(f"Widget cache updated: {cache_file}")
    except Exception as e:
        # Don't fail if widget cache update fails
        if not json_output:
            print(f"Note: Failed to update widget cache: {e}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
