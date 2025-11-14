#!/usr/bin/env python3
"""
Speed Test Core Module

This module contains the core business logic for internet speed testing,
separated from any UI implementation. It provides a clean API that can be
used by different frontends (CLI, GUI, web, etc.).
"""

import time
import json
from pathlib import Path
import speedtest
from typing import Optional, Dict, Any, Tuple, Callable, List
import threading
import queue
import sys
import platform
import random

# Import file locking based on platform
_IS_WINDOWS = platform.system() == 'Windows'
_HAS_FILE_LOCKING = False

if _IS_WINDOWS:
    try:
        import msvcrt
        _HAS_FILE_LOCKING = True
    except ImportError:
        pass
else:
    try:
        import fcntl
        _HAS_FILE_LOCKING = True
    except ImportError:
        pass


def _lock_file_shared(file_obj):
    """Acquire file lock (platform-agnostic).

    Note: On Unix, this acquires a shared (read) lock via fcntl.flock().
    On Windows, msvcrt.locking() only supports exclusive locks, so this
    function provides exclusive locking on Windows. This is acceptable for
    config file reads since they are fast operations.
    """
    if not _HAS_FILE_LOCKING:
        return  # No locking available

    if _IS_WINDOWS:
        import msvcrt
        # Windows: msvcrt.locking() only supports exclusive locks
        # Lock first byte to minimize lock scope
        try:
            # Try non-blocking exclusive lock first
            msvcrt.locking(file_obj.fileno(), msvcrt.LK_NBLCK, 1)
        except (IOError, OSError):
            # File already locked, wait with blocking exclusive lock
            msvcrt.locking(file_obj.fileno(), msvcrt.LK_LOCK, 1)
    else:
        import fcntl
        # Unix: use shared (read) lock
        fcntl.flock(file_obj.fileno(), fcntl.LOCK_SH)


def _unlock_file(file_obj):
    """Release file lock (platform-agnostic)."""
    if not _HAS_FILE_LOCKING:
        return  # No locking available

    if _IS_WINDOWS:
        import msvcrt
        try:
            msvcrt.locking(file_obj.fileno(), msvcrt.LK_UNLCK, 1)
        except (IOError, OSError):
            pass  # Ignore unlock errors
    else:
        import fcntl
        fcntl.flock(file_obj.fileno(), fcntl.LOCK_UN)


class SpeedTestConfig:
    """Configuration management for speed test application."""
    
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
        'show_detailed_progress': True,
        'save_results_to_database': True
    }
    
    # Configuration validation rules
    VALIDATION_RULES = {
        'bits_to_mbps': (100_000, 10_000_000),  # 100k to 10M
        'connectivity_check_timeout': (5, 60),   # 5 to 60 seconds
        'speedtest_timeout': (10, 300),          # 10 to 300 seconds
        'max_retries': (1, 10),                  # 1 to 10 attempts
        'retry_delay': (1, 30),                  # 1 to 30 seconds
        'max_typical_speed_gbps': (0.1, 100),   # 0.1 to 100 Gbps
        'max_reasonable_speed_gbps': (1, 1000), # 1 to 1000 Gbps
        'max_typical_ping_ms': (50, 5000),      # 50 to 5000 ms
        'max_reasonable_ping_ms': (100, 30000), # 100 to 30000 ms
    }
    
    def __init__(self, config_file: str = 'speedtest_config.json'):
        self.config_file = Path(config_file)
        self.config = self.DEFAULT_CONFIG.copy()
        self.load_config()
    
    def _validate_config_value(self, key: str, value: Any) -> Any:
        """Validate a single configuration value.
        
        Args:
            key: Configuration key
            value: Value to validate
            
        Returns:
            Validated value
            
        Raises:
            ValueError: If value is invalid
        """
        if key in ('show_detailed_progress', 'save_results_to_database'):
            if not isinstance(value, bool):
                raise ValueError(f"'{key}' must be a boolean, got {type(value).__name__}")
            return value
        
        if key in self.VALIDATION_RULES:
            min_val, max_val = self.VALIDATION_RULES[key]
            
            if not isinstance(value, (int, float)):
                raise ValueError(f"'{key}' must be a number, got {type(value).__name__}")
            
            if not (min_val <= value <= max_val):
                raise ValueError(f"'{key}' must be between {min_val} and {max_val}, got {value}")
            
            return value
        
        # Unknown key - keep as is but warn
        return value
    
    def _validate_and_update_config(self, file_config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate configuration values and return validated config.
        
        Args:
            file_config: Configuration loaded from file
            
        Returns:
            Dictionary of validated configuration values
        """
        validated_config = {}
        validation_errors = []
        
        for key, value in file_config.items():
            if key not in self.DEFAULT_CONFIG:
                validation_errors.append(f"Unknown configuration key: '{key}'")
                continue
                
            try:
                validated_value = self._validate_config_value(key, value)
                validated_config[key] = validated_value
            except ValueError as e:
                validation_errors.append(f"Invalid value for '{key}': {e}")
                # Use default value for invalid entries
                validated_config[key] = self.DEFAULT_CONFIG[key]
        
        # Check for zero/negative values before logical consistency
        speed_keys = ['max_typical_speed_gbps', 'max_reasonable_speed_gbps']
        for key in speed_keys:
            if key in validated_config and validated_config[key] <= 0:
                validation_errors.append(f"{key} must be positive")
                validated_config[key] = self.DEFAULT_CONFIG[key]
        
        ping_keys = ['max_typical_ping_ms', 'max_reasonable_ping_ms']
        for key in ping_keys:
            if key in validated_config and validated_config[key] <= 0:
                validation_errors.append(f"{key} must be positive")
                validated_config[key] = self.DEFAULT_CONFIG[key]
        
        # Check logical consistency
        if 'max_typical_speed_gbps' in validated_config and 'max_reasonable_speed_gbps' in validated_config:
            if validated_config['max_typical_speed_gbps'] >= validated_config['max_reasonable_speed_gbps']:
                validation_errors.append("max_typical_speed_gbps must be less than max_reasonable_speed_gbps")
                validated_config['max_typical_speed_gbps'] = self.DEFAULT_CONFIG['max_typical_speed_gbps']
        
        if 'max_typical_ping_ms' in validated_config and 'max_reasonable_ping_ms' in validated_config:
            if validated_config['max_typical_ping_ms'] >= validated_config['max_reasonable_ping_ms']:
                validation_errors.append("max_typical_ping_ms must be less than max_reasonable_ping_ms")
                validated_config['max_typical_ping_ms'] = self.DEFAULT_CONFIG['max_typical_ping_ms']
        
        if validation_errors:
            print("Configuration validation warnings:")
            for error in validation_errors:
                print(f"  - {error}")
        
        return validated_config
    
    def load_config(self) -> None:
        """Load and validate configuration from file or use defaults."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    # Platform-agnostic file locking to prevent concurrent access
                    try:
                        _lock_file_shared(f)
                        file_config = json.load(f)
                    finally:
                        _unlock_file(f)

                # Validate configuration
                validated_config = self._validate_and_update_config(file_config)
                self.config.update(validated_config)

            except (json.JSONDecodeError, IOError, OSError) as e:
                print(f"Error loading configuration file: {e}")
                print("Using default configuration.")
                # Keep defaults if config file is invalid
    
    def create_sample_config(self) -> bool:
        """Create a sample configuration file. Returns True if created."""
        if not self.config_file.exists():
            try:
                with open(self.config_file, 'w') as f:
                    json.dump(self.DEFAULT_CONFIG, f, indent=2)
                return True
            except IOError:
                return False
        return False
    
    def get(self, key: str, default=None):
        """Get configuration value."""
        return self.config.get(key, default)
    
    def __getitem__(self, key: str):
        """Allow dict-like access to config."""
        return self.config[key]


class SpeedTestResult:
    """Container for speed test results."""

    def __init__(self, download_mbps: float = 0, upload_mbps: float = 0,
                 ping_ms: float = 0, server_info: str = "",
                 is_valid: bool = False, warnings: list = None,
                 is_cancelled: bool = False):
        self.download_mbps = download_mbps
        self.upload_mbps = upload_mbps
        self.ping_ms = ping_ms
        self.server_info = server_info
        self.is_valid = is_valid
        self.warnings = warnings or []
        self.is_cancelled = is_cancelled
        self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            'download_mbps': self.download_mbps,
            'upload_mbps': self.upload_mbps,
            'ping_ms': self.ping_ms,
            'server_info': self.server_info,
            'is_valid': self.is_valid,
            'warnings': self.warnings,
            'is_cancelled': self.is_cancelled,
            'timestamp': self.timestamp
        }


class SpeedTestEngine:
    """Core engine for internet speed testing."""
    
    def __init__(self, config: SpeedTestConfig = None):
        self.config = config or SpeedTestConfig()
        self._progress_callback: Optional[Callable[[str, Optional[float]], None]] = None
        self._callback_lock = threading.Lock()
        self._cancel_event = threading.Event()

    def set_progress_callback(self, callback: Callable[[str, Optional[float]], None]) -> None:
        """Set callback function for progress updates (thread-safe).

        Args:
            callback: Function that takes (message: str, progress: Optional[float] [0-1])
        """
        with self._callback_lock:
            self._progress_callback = callback

    def _update_progress(self, message: str, progress: Optional[float] = None) -> None:
        """Update progress if callback is set (thread-safe).

        Args:
            message: Progress message
            progress: Progress value between 0 and 1, or None for indeterminate
        """
        with self._callback_lock:
            if self._progress_callback:
                try:
                    self._progress_callback(message, progress)
                except Exception as e:
                    # Don't let callback errors crash the test
                    print(f"Warning: Progress callback error: {e}", file=sys.stderr)
    
    def cancel_test(self) -> None:
        """Cancel currently running test."""
        self._cancel_event.set()
    
    def check_network_connectivity(self) -> bool:
        """Check if internet connection is available."""
        try:
            test_client = speedtest.Speedtest(
                timeout=self.config['connectivity_check_timeout']
            )
            test_client.get_config()
            return True
        except (speedtest.SpeedtestException, speedtest.ConfigRetrievalError, 
                OSError, TimeoutError, ConnectionError, AttributeError):
            # AttributeError specifically for Python 3.13 fileno() issues
            return False
    
    def validate_results(self, results: Dict[str, Any]) -> Tuple[bool, list]:
        """Validate speedtest results with tiered warnings.
        
        Args:
            results: Dictionary containing test results
            
        Returns:
            Tuple of (is_valid, warnings_list)
        """
        warnings = []
        
        try:
            download = results.get('download', 0)
            upload = results.get('upload', 0) 
            ping = results.get('ping', 0)
            
            # Check for completely invalid values
            if download < 0 or upload < 0 or ping < 0:
                return False, ["Invalid negative values detected - measurement failed"]
                
            # Check for absolutely unreasonable values
            max_reasonable_bps = self.config['max_reasonable_speed_gbps'] * 1_000_000_000
            if download > max_reasonable_bps or upload > max_reasonable_bps:
                return False, ["Extremely high speeds detected - likely measurement error"]
                
            if ping > self.config['max_reasonable_ping_ms']:
                return False, ["Extremely high ping detected - likely measurement error"]
            
            # Check for unusually high but not impossible values
            max_typical_bps = self.config['max_typical_speed_gbps'] * 1_000_000_000
            if download > max_typical_bps or upload > max_typical_bps:
                speed_gbps = max(download, upload) / 1_000_000_000
                warnings.append(f"Unusually high speed ({speed_gbps:.1f} Gbps) - please verify results")
                
            if ping > self.config['max_typical_ping_ms']:
                warnings.append(f"High latency ({ping:.0f} ms) detected - connection may be slow")
            
            # Check for suspiciously low values
            if download < 1_000_000 and upload < 1_000_000:
                warnings.append("Very low speeds detected - check network connection")
                
            return True, warnings
            
        except (KeyError, TypeError, ValueError):
            return False, ["Invalid result data structure - measurement failed"]
    
    def run_speed_test(self) -> SpeedTestResult:
        """Run internet speed test and return results.
        
        Returns:
            SpeedTestResult object with test results
        """
        self._cancel_event.clear()
        speedtest_client = None
        
        try:
            self._update_progress("Initializing speed test...", 0.1)
            if self._cancel_event.is_set():
                return SpeedTestResult(is_cancelled=True, warnings=["Test cancelled by user"])

            speedtest_client = speedtest.Speedtest(
                timeout=self.config['speedtest_timeout']
            )

            self._update_progress("Fetching server list...", 0.2)
            if self._cancel_event.is_set():
                return SpeedTestResult(is_cancelled=True, warnings=["Test cancelled by user"])
            speedtest_client.get_servers()

            self._update_progress("Selecting best server...", 0.3)
            if self._cancel_event.is_set():
                return SpeedTestResult(is_cancelled=True, warnings=["Test cancelled by user"])
            best_server = speedtest_client.get_best_server()
            server_info = f"{best_server['sponsor']} ({best_server['name']})"

            self._update_progress(f"Testing download speed...", 0.4)
            if self._cancel_event.is_set():
                return SpeedTestResult(is_cancelled=True, warnings=["Test cancelled by user"])
            speedtest_client.download()

            self._update_progress(f"Testing upload speed...", 0.7)
            if self._cancel_event.is_set():
                return SpeedTestResult(is_cancelled=True, warnings=["Test cancelled by user"])
            speedtest_client.upload()

            self._update_progress("Processing results...", 0.9)
            if self._cancel_event.is_set():
                return SpeedTestResult(is_cancelled=True, warnings=["Test cancelled by user"])
            
            # Extract and convert results
            results = speedtest_client.results.dict()
            download_mbps = results.get('download', 0) / self.config['bits_to_mbps']
            upload_mbps = results.get('upload', 0) / self.config['bits_to_mbps']
            ping_ms = results.get('ping', 0)
            
            # Validate results
            is_valid, warnings = self.validate_results(results)
            
            self._update_progress("Test completed!", 1.0)
            
            return SpeedTestResult(
                download_mbps=download_mbps,
                upload_mbps=upload_mbps,
                ping_ms=ping_ms,
                server_info=server_info,
                is_valid=is_valid,
                warnings=warnings
            )
            
        except speedtest.ConfigRetrievalError:
            return SpeedTestResult(warnings=["Unable to retrieve speedtest configuration"])
        except speedtest.NoMatchedServers:
            return SpeedTestResult(warnings=["No speedtest servers found"])
        except speedtest.SpeedtestException as e:
            return SpeedTestResult(warnings=[f"Speedtest error: {e}"])
        except AttributeError as e:
            # Handle Python 3.13 fileno() compatibility issues specifically
            error_msg = str(e).lower()
            if 'fileno' in error_msg or 'stderr' in error_msg or 'stdout' in error_msg:
                return SpeedTestResult(warnings=[f"Python 3.13 compatibility error: {e}"])
            # Unexpected AttributeError - log full traceback for debugging to avoid masking bugs
            import traceback
            traceback.print_exc()
            return SpeedTestResult(warnings=[f"Unexpected AttributeError: {e}. Check logs for details."])
        except Exception as e:
            return SpeedTestResult(warnings=[f"Unexpected error: {e}"])
        finally:
            # Ensure speedtest client resources are cleaned up
            if speedtest_client:
                if hasattr(speedtest_client, 'close'):
                    try:
                        speedtest_client.close()
                    except Exception as e:
                        # Log cleanup errors for debugging instead of silently ignoring
                        print(f"Warning: Error during speedtest client cleanup: {e}", file=sys.stderr)

                # Additional cleanup: close any open connections
                if hasattr(speedtest_client, '_opener'):
                    try:
                        speedtest_client._opener.close()
                    except Exception:
                        pass  # _opener cleanup is optional
    
    def run_speed_test_with_retry(self) -> SpeedTestResult:
        """Run speed test with exponential backoff retry logic for transient failures."""
        max_retries = self.config['max_retries']
        base_delay = self.config['retry_delay']

        for attempt in range(max_retries):
            if self._cancel_event.is_set():
                return SpeedTestResult(is_cancelled=True, warnings=["Test cancelled by user"])

            self._update_progress(f"Attempt {attempt + 1}/{max_retries}", 0.0)

            result = self.run_speed_test()

            # If test was successful or cancelled, return result
            if result.is_valid or self._cancel_event.is_set():
                return result

            # Check if error is retryable (network-related)
            if result.warnings:
                error_msg = result.warnings[0].lower()
                retryable_errors = ['unable to retrieve', 'no speedtest servers',
                                  'connection', 'timeout', 'network']
                is_retryable = any(err in error_msg for err in retryable_errors)

                if not is_retryable or attempt == max_retries - 1:
                    return result

                # Exponential backoff with jitter
                # delay = base * (2^attempt) + random jitter
                backoff = base_delay * (2 ** attempt)
                jitter = random.uniform(0, backoff * 0.1)  # 10% jitter
                delay = min(backoff + jitter, 30)  # Cap at 30 seconds

                self._update_progress(f"Retrying in {delay:.1f} seconds...", None)
                time.sleep(delay)

        return SpeedTestResult(warnings=["All retry attempts failed"])


class AsyncSpeedTestRunner:
    """Asynchronous speed test runner for GUI applications."""
    
    def __init__(self, engine: SpeedTestEngine):
        self.engine = engine
        self._thread: Optional[threading.Thread] = None
        self._result_queue = queue.Queue(maxsize=1)  # Only need latest result
        # Use SimpleQueue (unbounded) to prevent blocking - GUI consumption rate may vary
        self._progress_queue = queue.SimpleQueue()

    def start_test(self) -> None:
        """Start speed test in background thread."""
        if self._thread and self._thread.is_alive():
            return  # Test already running

        # Set up progress callback
        self.engine.set_progress_callback(self._progress_callback)

        # Start test in background
        self._thread = threading.Thread(target=self._run_test_thread)
        self._thread.daemon = True
        self._thread.start()

    def _progress_callback(self, message: str, progress: float) -> None:
        """Internal progress callback that never blocks."""
        self._progress_queue.put((message, progress))
    
    def _run_test_thread(self) -> None:
        """Run test in background thread."""
        result = self.engine.run_speed_test_with_retry()
        self._result_queue.put(result)
    
    def get_progress(self) -> Optional[Tuple[str, float]]:
        """Get latest progress update if available (non-blocking)."""
        try:
            return self._progress_queue.get(block=False)
        except queue.Empty:
            return None

    def get_all_progress(self) -> List[Tuple[str, float]]:
        """Get all available progress updates atomically (non-blocking)."""
        updates = []
        try:
            while True:
                updates.append(self._progress_queue.get(block=False))
        except queue.Empty:
            pass
        return updates
    
    def get_result(self) -> Optional[SpeedTestResult]:
        """Get test result if available."""
        try:
            return self._result_queue.get_nowait()
        except queue.Empty:
            return None
    
    def cancel_test(self) -> None:
        """Cancel running test with progressive timeout."""
        self.engine.cancel_test()
        if self._thread and self._thread.is_alive():
            # Give more time for network operations to complete gracefully
            self._thread.join(timeout=10.0)
            if self._thread.is_alive():
                # Log warning but don't force - daemon thread will clean up
                print("Warning: Background test thread did not terminate gracefully")
    
    def is_running(self) -> bool:
        """Check if test is currently running."""
        return self._thread is not None and self._thread.is_alive()