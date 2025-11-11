#!/usr/bin/env python3
"""
Speed Test Tool - Installation Tester
=====================================

Skrypt testujący poprawność instalacji i funkcjonalności Speed Test Tool.
"""

import os
import sys
import subprocess
import shutil
import time
from pathlib import Path
from typing import List, Tuple, Optional


class InstallationTester:
    """Tester instalacji Speed Test Tool."""
    
    def __init__(self):
        self.app_dir = Path(__file__).parent.absolute()
        self.venv_dir = self.app_dir / "speedtest_env"
        self.venv_python = self.venv_dir / "bin" / "python3"
        
        # Determine installation directory
        if os.geteuid() == 0:
            self.install_dir = Path("/usr/local/bin")
        else:
            self.install_dir = Path.home() / ".local" / "bin"
        
        self.test_results: List[Tuple[str, bool, str]] = []
    
    def log_test(self, test_name: str, success: bool, details: str = "") -> None:
        """Zapisz wynik testu."""
        self.test_results.append((test_name, success, details))
        status = "✓" if success else "✗"
        print(f"  {status} {test_name}")
        if details and not success:
            print(f"    {details}")
    
    def test_python_version(self) -> bool:
        """Test wersji Pythona."""
        version = sys.version_info
        if version.major >= 3 and version.minor >= 6:
            self.log_test(f"Python {version.major}.{version.minor}.{version.micro}", True)
            return True
        else:
            self.log_test(f"Python {version.major}.{version.minor}.{version.micro}", False, 
                         "Requires Python 3.6+")
            return False
    
    def test_virtual_environment(self) -> bool:
        """Test środowiska wirtualnego."""
        if self.venv_dir.exists() and self.venv_python.exists():
            self.log_test("Virtual Environment", True)
            return True
        else:
            self.log_test("Virtual Environment", False, "Not found or incomplete")
            return False
    
    def test_core_dependencies(self) -> bool:
        """Test podstawowych zależności."""
        dependencies = [
            ("speedtest", "speedtest module"),
            ("sqlite3", "SQLite database"),
            ("json", "JSON handling"),
            ("pathlib", "Path handling")
        ]
        
        all_ok = True
        for module, description in dependencies:
            try:
                result = subprocess.run([
                    str(self.venv_python), "-c", f"import {module}"
                ], capture_output=True, check=True)
                self.log_test(f"Core: {description}", True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.log_test(f"Core: {description}", False, f"Module {module} not available")
                all_ok = False
        
        return all_ok
    
    def test_gui_dependencies(self) -> bool:
        """Test zależności GUI."""
        gui_modules = [
            ("kivy", "Kivy framework"),
            ("kivymd", "Material Design components")
        ]
        
        all_ok = True
        for module, description in gui_modules:
            try:
                result = subprocess.run([
                    str(self.venv_python), "-c", f"import {module}"
                ], capture_output=True, check=True)
                self.log_test(f"GUI: {description}", True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.log_test(f"GUI: {description}", False, f"Module {module} not available")
                all_ok = False
        
        return all_ok
    
    def test_application_modules(self) -> bool:
        """Test modułów aplikacji."""
        app_modules = [
            ("speedtest_core", "Core engine"),
            ("test_results_storage", "Data storage"),
            ("config_validator", "Configuration"),
            ("scheduled_testing", "Scheduler")
        ]
        
        all_ok = True
        for module, description in app_modules:
            try:
                result = subprocess.run([
                    str(self.venv_python), "-c", f"from {module} import *"
                ], cwd=str(self.app_dir), capture_output=True, check=True)
                self.log_test(f"App: {description}", True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.log_test(f"App: {description}", False, f"Module {module} import failed")
                all_ok = False
        
        return all_ok
    
    def test_executable_scripts(self) -> bool:
        """Test plików wykonywalnych."""
        scripts = [
            ("speedtest-cli", "CLI interface"),
            ("speedtest-gui", "GUI interface"),
            ("speedtest-scheduler", "Background scheduler"),
            ("speedtest-storage", "Data management")
        ]
        
        all_ok = True
        for script_name, description in scripts:
            script_path = self.install_dir / script_name
            
            if script_path.exists():
                if os.access(script_path, os.X_OK):
                    self.log_test(f"Script: {description}", True)
                else:
                    self.log_test(f"Script: {description}", False, "Not executable")
                    all_ok = False
            else:
                self.log_test(f"Script: {description}", False, "Not found")
                all_ok = False
        
        return all_ok
    
    def test_configuration(self) -> bool:
        """Test systemu konfiguracji."""
        config_file = self.app_dir / "speedtest_config.json"
        example_file = self.app_dir / "speedtest_config.json.example"
        
        # Test example file
        if example_file.exists():
            self.log_test("Configuration: Example file", True)
        else:
            self.log_test("Configuration: Example file", False, "Template not found")
            return False
        
        # Test config creation
        try:
            result = subprocess.run([
                str(self.venv_python), "sp.py", "--create-config"
            ], cwd=str(self.app_dir), capture_output=True, check=True)
            
            if config_file.exists():
                self.log_test("Configuration: Creation", True)
                return True
            else:
                self.log_test("Configuration: Creation", False, "Config file not created")
                return False
                
        except subprocess.CalledProcessError as e:
            self.log_test("Configuration: Creation", False, f"Command failed: {e}")
            return False
    
    def test_database_functionality(self) -> bool:
        """Test funkcjonalności bazy danych."""
        try:
            result = subprocess.run([
                str(self.venv_python), "-c", 
                "from test_results_storage import TestResultStorage; "
                "storage = TestResultStorage(); "
                "print('Database OK')"
            ], cwd=str(self.app_dir), capture_output=True, check=True, text=True)
            
            self.log_test("Database: Initialization", True)
            return True
            
        except subprocess.CalledProcessError as e:
            self.log_test("Database: Initialization", False, f"Failed: {e}")
            return False
    
    def test_network_connectivity(self) -> bool:
        """Test łączności sieciowej (opcjonalny)."""
        try:
            result = subprocess.run([
                str(self.venv_python), "-c",
                "from speedtest_core import SpeedTestEngine, SpeedTestConfig; "
                "engine = SpeedTestEngine(SpeedTestConfig()); "
                "print('Network check:', engine.check_network_connectivity())"
            ], cwd=str(self.app_dir), capture_output=True, check=True, text=True, timeout=15)
            
            if "True" in result.stdout:
                self.log_test("Network: Connectivity", True)
                return True
            else:
                self.log_test("Network: Connectivity", False, "No internet connection")
                return False
                
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            self.log_test("Network: Connectivity", False, "Connection test failed")
            return False
    
    def test_command_line_interface(self) -> bool:
        """Test interfejsu linii komend (szybki test)."""
        script_path = self.install_dir / "speedtest-cli"
        
        if not script_path.exists():
            self.log_test("CLI: Command execution", False, "speedtest-cli not found")
            return False
        
        try:
            # Test help option (should be fast)
            result = subprocess.run([
                str(script_path), "--create-config"
            ], capture_output=True, check=True, timeout=10)
            
            self.log_test("CLI: Command execution", True)
            return True
            
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as e:
            self.log_test("CLI: Command execution", False, f"Execution failed: {e}")
            return False
    
    def run_full_test_suite(self, test_network: bool = True) -> bool:
        """Uruchom pełny zestaw testów."""
        print("Speed Test Tool - Installation Test Suite")
        print("=" * 45)
        
        tests = [
            ("Python Version", self.test_python_version),
            ("Virtual Environment", self.test_virtual_environment),
            ("Core Dependencies", self.test_core_dependencies),
            ("GUI Dependencies", self.test_gui_dependencies),
            ("Application Modules", self.test_application_modules),
            ("Executable Scripts", self.test_executable_scripts),
            ("Configuration System", self.test_configuration),
            ("Database Functionality", self.test_database_functionality),
            ("CLI Interface", self.test_command_line_interface)
        ]
        
        if test_network:
            tests.append(("Network Connectivity", self.test_network_connectivity))
        
        all_passed = True
        
        for test_name, test_func in tests:
            print(f"\n{test_name}:")
            try:
                success = test_func()
                if not success:
                    all_passed = False
            except Exception as e:
                self.log_test(f"{test_name}", False, f"Exception: {e}")
                all_passed = False
        
        return all_passed
    
    def print_summary(self) -> None:
        """Wyświetl podsumowanie testów."""
        print("\n" + "=" * 45)
        print("TEST SUMMARY")
        print("=" * 45)
        
        passed = sum(1 for _, success, _ in self.test_results if success)
        total = len(self.test_results)
        
        print(f"Tests passed: {passed}/{total}")
        
        if passed == total:
            print("✅ All tests PASSED - Installation is working correctly!")
        else:
            print("❌ Some tests FAILED - Check issues above")
            print("\nFailed tests:")
            for test_name, success, details in self.test_results:
                if not success:
                    print(f"  - {test_name}: {details}")
        
        print(f"\nInstallation directory: {self.install_dir}")
        print(f"Application directory: {self.app_dir}")
        print(f"Virtual environment: {self.venv_dir}")
        
        if passed != total:
            print("\nTroubleshooting:")
            print("1. Run: python3 install.py")
            print("2. Check: make test")
            print("3. Verify: make info")


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Speed Test Tool installation")
    parser.add_argument("--no-network", action="store_true", help="Skip network connectivity test")
    parser.add_argument("--quick", action="store_true", help="Run quick tests only")
    
    args = parser.parse_args()
    
    tester = InstallationTester()
    
    try:
        test_network = not args.no_network
        
        if args.quick:
            print("Running quick installation test...")
            success = (tester.test_python_version() and 
                      tester.test_virtual_environment() and
                      tester.test_core_dependencies())
        else:
            success = tester.run_full_test_suite(test_network)
        
        tester.print_summary()
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        return 1
    except Exception as e:
        print(f"Test suite failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())