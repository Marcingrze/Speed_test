#!/usr/bin/env python3
"""
Scheduled Testing Module

Provides automated background speed testing with configurable schedules.
"""

import time
import threading
import signal
import sys
from datetime import datetime, timedelta
from typing import Optional, Callable
import json
from pathlib import Path

from speedtest_core import SpeedTestEngine, SpeedTestConfig
from test_results_storage import TestResultStorage


class ScheduledTestRunner:
    """Runs speed tests on a scheduled interval."""
    
    def __init__(self, 
                 interval_minutes: int = 60,
                 config: Optional[SpeedTestConfig] = None,
                 storage: Optional[TestResultStorage] = None,
                 result_callback: Optional[Callable] = None):
        """Initialize scheduled test runner.
        
        Args:
            interval_minutes: Minutes between tests
            config: SpeedTestConfig instance
            storage: TestResultStorage instance
            result_callback: Optional callback for test results
        """
        self.interval_minutes = interval_minutes
        self.config = config or SpeedTestConfig()
        self.storage = storage or TestResultStorage()
        self.result_callback = result_callback
        
        self.engine = SpeedTestEngine(self.config)
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._next_test_time: Optional[datetime] = None
        self._next_test_monotonic: Optional[float] = None
        
        # Statistics
        self.tests_completed = 0
        self.tests_failed = 0
        self.start_time: Optional[datetime] = None
        self.start_monotonic: Optional[float] = None
    
    def start_scheduler(self) -> None:
        """Start the scheduled testing with monotonic time tracking."""
        if self._running:
            return
        
        self._running = True
        self._stop_event.clear()
        
        # Use both wall clock time for display and monotonic time for scheduling
        now = datetime.now()
        now_monotonic = time.monotonic()
        
        self.start_time = now
        self.start_monotonic = now_monotonic
        self._next_test_time = now
        self._next_test_monotonic = now_monotonic
        
        self._thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self._thread.start()
        
        print(f"📅 Scheduler started - testing every {self.interval_minutes} minutes")
        print(f"⏰ Next test: {self._next_test_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def stop_scheduler(self) -> None:
        """Stop the scheduled testing."""
        if not self._running:
            return
        
        self._running = False
        self._stop_event.set()
        
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5.0)
        
        print("⏹️  Scheduler stopped")
    
    def _scheduler_loop(self) -> None:
        """Main scheduler loop using monotonic time for reliability."""
        while self._running and not self._stop_event.is_set():
            current_monotonic = time.monotonic()
            current_time = datetime.now()
            
            # Check if it's time for a test using monotonic time
            if current_monotonic >= self._next_test_monotonic:
                self._run_scheduled_test()
                
                # Schedule next test using monotonic time
                self._next_test_monotonic = current_monotonic + (self.interval_minutes * 60)
                # Update display time for user feedback
                self._next_test_time = current_time + timedelta(minutes=self.interval_minutes)
                print(f"⏰ Next test: {self._next_test_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Calculate sleep time based on monotonic time
            # Ensure at least 1 second sleep to prevent busy loop
            time_until_next = self._next_test_monotonic - current_monotonic
            sleep_seconds = max(1, min(60, time_until_next))

            # Always sleep to prevent busy loop
            self._stop_event.wait(timeout=sleep_seconds)
    
    def _run_scheduled_test(self) -> None:
        """Run a single scheduled test."""
        test_start = datetime.now()
        print(f"🚀 Starting scheduled test at {test_start.strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Check connectivity first
            if not self.engine.check_network_connectivity():
                print("❌ No network connection - skipping test")
                self.tests_failed += 1
                return
            
            # Run the test
            result = self.engine.run_speed_test_with_retry()
            
            if result.is_valid:
                # Save to storage
                self.storage.save_result(result)
                self.tests_completed += 1
                
                test_duration = (datetime.now() - test_start).total_seconds()
                print(f"✅ Test completed in {test_duration:.1f}s")
                print(f"   Download: {result.download_mbps:.1f} Mbps")
                print(f"   Upload: {result.upload_mbps:.1f} Mbps")
                print(f"   Ping: {result.ping_ms:.0f} ms")
                
                if result.warnings:
                    print(f"⚠️  Warnings: {'; '.join(result.warnings)}")
                
                # Call result callback if provided
                if self.result_callback:
                    self.result_callback(result)
            else:
                self.tests_failed += 1
                error_msg = '; '.join(result.warnings) if result.warnings else "Unknown error"
                print(f"❌ Test failed: {error_msg}")
        
        except Exception as e:
            self.tests_failed += 1
            print(f"❌ Unexpected error during test: {e}")
    
    def get_status(self) -> dict:
        """Get current scheduler status with accurate runtime using monotonic time."""
        runtime = None
        if self.start_monotonic:
            runtime = time.monotonic() - self.start_monotonic
        
        return {
            'running': self._running,
            'interval_minutes': self.interval_minutes,
            'tests_completed': self.tests_completed,
            'tests_failed': self.tests_failed,
            'runtime_seconds': runtime,
            'next_test_time': self._next_test_time.isoformat() if self._next_test_time else None,
            'start_time': self.start_time.isoformat() if self.start_time else None
        }
    
    def run_immediate_test(self) -> None:
        """Run an immediate test outside the schedule."""
        print("🔄 Running immediate test...")
        self._run_scheduled_test()


class SchedulerConfig:
    """Configuration management for scheduler."""
    
    def __init__(self, config_file: str = "scheduler_config.json"):
        self.config_file = Path(config_file)
        self.default_config = {
            'interval_minutes': 60,
            'auto_start': False,
            'max_runtime_hours': 24,
            'network_retry_delay': 300,  # 5 minutes
            'log_file': 'scheduler.log'
        }
        self.config = self.default_config.copy()
        self.load_config()
    
    def load_config(self) -> None:
        """Load scheduler configuration."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                self.config.update(file_config)
            except (json.JSONDecodeError, IOError):
                pass  # Keep defaults
    
    def save_config(self) -> None:
        """Save current configuration."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except IOError:
            pass
    
    def create_sample_config(self) -> bool:
        """Create sample configuration file."""
        if not self.config_file.exists():
            self.save_config()
            return True
        return False


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    print("\n🛑 Shutdown signal received...")
    global scheduler
    if 'scheduler' in globals() and scheduler:
        scheduler.stop_scheduler()
    sys.exit(0)


def main():
    """CLI interface for scheduled testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Scheduled Speed Test Runner')
    parser.add_argument('--interval', type=int, default=60, 
                        help='Test interval in minutes (default: 60)')
    parser.add_argument('--max-runtime', type=int, default=24*60,
                        help='Maximum runtime in minutes (default: 1440 = 24 hours)')
    parser.add_argument('--config', default='scheduler_config.json',
                        help='Configuration file path')
    parser.add_argument('--create-config', action='store_true',
                        help='Create sample configuration file')
    parser.add_argument('--immediate', action='store_true',
                        help='Run immediate test and exit')
    parser.add_argument('--stats', action='store_true',
                        help='Show recent test statistics and exit')
    
    args = parser.parse_args()
    
    # Handle configuration file creation
    if args.create_config:
        config_obj = SchedulerConfig(args.config)
        if config_obj.create_sample_config():
            print(f"✅ Created sample configuration: {args.config}")
        else:
            print(f"❌ Configuration file already exists: {args.config}")
        return 0
    
    # Handle statistics display
    if args.stats:
        storage = TestResultStorage()
        stats = storage.get_statistics(days=7)  # Last 7 days
        
        if stats['count'] == 0:
            print("📊 No test results found in the last 7 days")
            return 0
        
        print("📊 Recent Test Statistics (last 7 days)")
        print("=" * 45)
        print(f"Total tests: {stats['count']}")
        print(f"Average download: {stats['download']['mean']:.1f} Mbps")
        print(f"Average upload: {stats['upload']['mean']:.1f} Mbps")
        print(f"Average ping: {stats['ping']['mean']:.1f} ms")
        return 0
    
    # Handle immediate test
    if args.immediate:
        print("🚀 Running immediate speed test...")
        config = SpeedTestConfig()
        storage = TestResultStorage()
        engine = SpeedTestEngine(config)
        
        if not engine.check_network_connectivity():
            print("❌ No network connection detected")
            return 1
        
        result = engine.run_speed_test_with_retry()
        if result.is_valid:
            storage.save_result(result)
            print("✅ Test completed and saved:")
            print(f"   Download: {result.download_mbps:.1f} Mbps")
            print(f"   Upload: {result.upload_mbps:.1f} Mbps")
            print(f"   Ping: {result.ping_ms:.0f} ms")
            return 0
        else:
            error_msg = '; '.join(result.warnings) if result.warnings else "Unknown error"
            print(f"❌ Test failed: {error_msg}")
            return 1
    
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Load configuration
    config_obj = SchedulerConfig(args.config)
    
    # Initialize scheduler
    global scheduler
    scheduler = ScheduledTestRunner(
        interval_minutes=args.interval,
        config=SpeedTestConfig(),
        storage=TestResultStorage()
    )
    
    print("📋 Speed Test Scheduler")
    print("=" * 30)
    print(f"Test interval: {args.interval} minutes")
    print(f"Max runtime: {args.max_runtime} minutes")
    print("Press Ctrl+C to stop")
    print()
    
    # Start scheduler
    scheduler.start_scheduler()
    
    try:
        # Run for specified duration
        start_time = datetime.now()
        max_runtime = timedelta(minutes=args.max_runtime)
        
        while datetime.now() - start_time < max_runtime:
            time.sleep(10)  # Check every 10 seconds
            
            # Print status update every 10 minutes
            if (datetime.now() - start_time).total_seconds() % 600 < 10:
                status = scheduler.get_status()
                print(f"📈 Status: {status['tests_completed']} completed, "
                      f"{status['tests_failed']} failed, "
                      f"runtime: {status['runtime_seconds']:.0f}s")
    
    except KeyboardInterrupt:
        pass
    finally:
        scheduler.stop_scheduler()
        print("👋 Scheduler shut down gracefully")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())