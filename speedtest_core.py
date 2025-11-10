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
from typing import Optional, Dict, Any, Tuple, Callable
import threading
import queue


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
        'show_detailed_progress': True
    }
    
    def __init__(self, config_file: str = 'speedtest_config.json'):
        self.config_file = Path(config_file)
        self.config = self.DEFAULT_CONFIG.copy()
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from file or use defaults."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                self.config.update(file_config)
            except (json.JSONDecodeError, IOError):
                # Keep defaults if config file is invalid
                pass
    
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
                 is_valid: bool = False, warnings: list = None):
        self.download_mbps = download_mbps
        self.upload_mbps = upload_mbps
        self.ping_ms = ping_ms
        self.server_info = server_info
        self.is_valid = is_valid
        self.warnings = warnings or []
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
            'timestamp': self.timestamp
        }


class SpeedTestEngine:
    """Core engine for internet speed testing."""
    
    def __init__(self, config: SpeedTestConfig = None):
        self.config = config or SpeedTestConfig()
        self._progress_callback: Optional[Callable[[str, float], None]] = None
        self._cancel_event = threading.Event()
    
    def set_progress_callback(self, callback: Callable[[str, float], None]) -> None:
        """Set callback function for progress updates.
        
        Args:
            callback: Function that takes (message: str, progress: float [0-1])
        """
        self._progress_callback = callback
    
    def _update_progress(self, message: str, progress: float = -1) -> None:
        """Update progress if callback is set."""
        if self._progress_callback:
            self._progress_callback(message, progress)
    
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
                OSError, TimeoutError, ConnectionError):
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
        
        try:
            self._update_progress("Initializing speed test...", 0.1)
            if self._cancel_event.is_set():
                return SpeedTestResult()
            
            speedtest_client = speedtest.Speedtest(
                timeout=self.config['speedtest_timeout']
            )
            
            self._update_progress("Fetching server list...", 0.2)
            if self._cancel_event.is_set():
                return SpeedTestResult()
            speedtest_client.get_servers()
            
            self._update_progress("Selecting best server...", 0.3)
            if self._cancel_event.is_set():
                return SpeedTestResult()
            best_server = speedtest_client.get_best_server()
            server_info = f"{best_server['sponsor']} ({best_server['name']})"
            
            self._update_progress(f"Testing download speed...", 0.4)
            if self._cancel_event.is_set():
                return SpeedTestResult()
            speedtest_client.download()
            
            self._update_progress(f"Testing upload speed...", 0.7)
            if self._cancel_event.is_set():
                return SpeedTestResult()
            speedtest_client.upload()
            
            self._update_progress("Processing results...", 0.9)
            if self._cancel_event.is_set():
                return SpeedTestResult()
            
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
        except Exception as e:
            return SpeedTestResult(warnings=[f"Unexpected error: {e}"])
    
    def run_speed_test_with_retry(self) -> SpeedTestResult:
        """Run speed test with retry logic for transient failures."""
        max_retries = self.config['max_retries']
        
        for attempt in range(max_retries):
            if self._cancel_event.is_set():
                return SpeedTestResult()
                
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
                
                self._update_progress(f"Retrying in {self.config['retry_delay']} seconds...", 0.0)
                time.sleep(self.config['retry_delay'])
        
        return SpeedTestResult(warnings=["All retry attempts failed"])


class AsyncSpeedTestRunner:
    """Asynchronous speed test runner for GUI applications."""
    
    def __init__(self, engine: SpeedTestEngine):
        self.engine = engine
        self._thread: Optional[threading.Thread] = None
        self._result_queue = queue.Queue()
        self._progress_queue = queue.Queue()
        
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
        """Internal progress callback."""
        self._progress_queue.put((message, progress))
    
    def _run_test_thread(self) -> None:
        """Run test in background thread."""
        result = self.engine.run_speed_test_with_retry()
        self._result_queue.put(result)
    
    def get_progress(self) -> Optional[Tuple[str, float]]:
        """Get latest progress update if available."""
        try:
            return self._progress_queue.get_nowait()
        except queue.Empty:
            return None
    
    def get_result(self) -> Optional[SpeedTestResult]:
        """Get test result if available."""
        try:
            return self._result_queue.get_nowait()
        except queue.Empty:
            return None
    
    def cancel_test(self) -> None:
        """Cancel running test."""
        self.engine.cancel_test()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5.0)
    
    def is_running(self) -> bool:
        """Check if test is currently running."""
        return self._thread is not None and self._thread.is_alive()