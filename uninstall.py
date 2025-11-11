#!/usr/bin/env python3
"""
Speed Test Tool - Uninstaller
==============================

Usuwa wszystkie pliki i konfiguracje zainstalowane przez Speed Test Tool.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import List


class SpeedTestUninstaller:
    """Uninstaller dla Speed Test Tool."""
    
    def __init__(self):
        self.app_dir = Path(__file__).parent.absolute()
        self.user_mode = os.geteuid() != 0
        
        # Determine installation directories
        if self.user_mode:
            self.install_dir = Path.home() / ".local" / "bin"
            self.desktop_dir = Path.home() / ".local" / "share" / "applications"
        else:
            self.install_dir = Path("/usr/local/bin")
            self.desktop_dir = None  # System-wide desktop entries handled differently
        
        self.script_names = [
            "speedtest-cli",
            "speedtest-gui", 
            "speedtest-gui-fallback",
            "speedtest-scheduler",
            "speedtest-storage"
        ]
        
        print(f"Running in {'user' if self.user_mode else 'system'} mode")
    
    def remove_executable_scripts(self) -> bool:
        """Usuń pliki uruchamialne."""
        print("Removing executable scripts...")
        removed_count = 0
        
        for script_name in self.script_names:
            script_path = self.install_dir / script_name
            
            if script_path.exists():
                try:
                    script_path.unlink()
                    print(f"✓ Removed {script_name}")
                    removed_count += 1
                except (OSError, IOError) as e:
                    print(f"✗ Failed to remove {script_name}: {e}")
                    return False
            else:
                print(f"- {script_name} not found (already removed)")
        
        if removed_count > 0:
            print(f"✓ Removed {removed_count} scripts")
        else:
            print("- No scripts found to remove")
        
        return True
    
    def remove_symbolic_links(self) -> bool:
        """Usuń linki symboliczne z /usr/bin (tylko w trybie root)."""
        if self.user_mode:
            return True
        
        print("Removing symbolic links from /usr/bin...")
        removed_count = 0
        usr_bin = Path("/usr/bin")
        
        for script_name in self.script_names:
            link_path = usr_bin / script_name
            
            if link_path.is_symlink():
                try:
                    link_path.unlink()
                    print(f"✓ Removed symlink {script_name}")
                    removed_count += 1
                except (OSError, IOError) as e:
                    print(f"✗ Failed to remove symlink {script_name}: {e}")
                    return False
            elif link_path.exists():
                print(f"- {script_name} exists but is not a symlink (skipping)")
            else:
                print(f"- {script_name} symlink not found")
        
        if removed_count > 0:
            print(f"✓ Removed {removed_count} symlinks")
        
        return True
    
    def remove_desktop_entry(self) -> bool:
        """Usuń .desktop file."""
        if not self.user_mode or not self.desktop_dir:
            return True
        
        desktop_file = self.desktop_dir / "speedtest.desktop"
        
        if desktop_file.exists():
            try:
                desktop_file.unlink()
                print("✓ Removed desktop entry")
                
                # Update desktop database
                try:
                    subprocess.run([
                        "update-desktop-database", str(self.desktop_dir)
                    ], check=True, capture_output=True)
                except (subprocess.CalledProcessError, FileNotFoundError):
                    # update-desktop-database might not be available
                    pass
                
                return True
            except (OSError, IOError) as e:
                print(f"✗ Failed to remove desktop entry: {e}")
                return False
        else:
            print("- Desktop entry not found")
            return True
    
    def remove_systemd_service(self) -> bool:
        """Usuń usługę systemd (tylko w trybie root)."""
        if self.user_mode:
            return True
        
        service_file = Path("/etc/systemd/system/speedtest.service")
        
        if service_file.exists():
            print("Removing systemd service...")
            try:
                # Stop and disable service
                subprocess.run([
                    "systemctl", "stop", "speedtest.service"
                ], check=True, capture_output=True)
                
                subprocess.run([
                    "systemctl", "disable", "speedtest.service"
                ], check=True, capture_output=True)
                
                # Remove service file
                service_file.unlink()
                
                # Reload systemd
                subprocess.run([
                    "systemctl", "daemon-reload"
                ], check=True, capture_output=True)
                
                print("✓ Removed systemd service")
                return True
                
            except (subprocess.CalledProcessError, OSError, IOError) as e:
                print(f"✗ Failed to remove systemd service: {e}")
                return False
        else:
            print("- Systemd service not found")
            return True
    
    def remove_virtual_environment(self) -> bool:
        """Usuń środowisko wirtualne."""
        venv_dir = self.app_dir / "speedtest_env"
        
        if venv_dir.exists():
            print("Removing virtual environment...")
            try:
                shutil.rmtree(venv_dir)
                print("✓ Removed virtual environment")
                return True
            except (OSError, IOError) as e:
                print(f"✗ Failed to remove virtual environment: {e}")
                return False
        else:
            print("- Virtual environment not found")
            return True
    
    def remove_config_files(self, remove_user_config: bool = False) -> bool:
        """Usuń pliki konfiguracyjne."""
        if remove_user_config:
            config_file = self.app_dir / "speedtest_config.json"
            if config_file.exists():
                try:
                    config_file.unlink()
                    print("✓ Removed user configuration")
                except (OSError, IOError) as e:
                    print(f"✗ Failed to remove user configuration: {e}")
                    return False
            else:
                print("- User configuration not found")
        else:
            print("- Keeping user configuration (use --remove-config to delete)")
        
        return True
    
    def remove_database(self, remove_data: bool = False) -> bool:
        """Usuń bazę danych z wynikami testów."""
        if remove_data:
            db_file = self.app_dir / "speedtest_history.db"
            if db_file.exists():
                try:
                    db_file.unlink()
                    print("✓ Removed test results database")
                except (OSError, IOError) as e:
                    print(f"✗ Failed to remove database: {e}")
                    return False
            else:
                print("- Test results database not found")
        else:
            print("- Keeping test results database (use --remove-data to delete)")
        
        return True
    
    def clean_pycache(self) -> bool:
        """Usuń pliki __pycache__."""
        print("Cleaning __pycache__ files...")
        removed_count = 0
        
        for pycache_dir in self.app_dir.rglob("__pycache__"):
            try:
                shutil.rmtree(pycache_dir)
                removed_count += 1
            except (OSError, IOError):
                pass  # Ignore errors
        
        # Remove .pyc files
        for pyc_file in self.app_dir.rglob("*.pyc"):
            try:
                pyc_file.unlink()
                removed_count += 1
            except (OSError, IOError):
                pass  # Ignore errors
        
        if removed_count > 0:
            print(f"✓ Cleaned {removed_count} cache files")
        else:
            print("- No cache files found")
        
        return True
    
    def show_summary(self, remove_config: bool, remove_data: bool) -> None:
        """Pokaż podsumowanie deinstalacji."""
        print("\n" + "=" * 40)
        print("Uninstallation Summary")
        print("=" * 40)
        
        if not remove_config:
            config_file = self.app_dir / "speedtest_config.json"
            if config_file.exists():
                print(f"Configuration preserved: {config_file}")
        
        if not remove_data:
            db_file = self.app_dir / "speedtest_history.db"
            if db_file.exists():
                print(f"Test data preserved: {db_file}")
        
        print(f"Application directory: {self.app_dir}")
        print("\nTo completely remove the application:")
        print(f"  rm -rf {self.app_dir}")
        
        if not remove_config or not remove_data:
            print("\nTo remove preserved files later:")
            if not remove_config:
                print(f"  rm {self.app_dir}/speedtest_config.json")
            if not remove_data:
                print(f"  rm {self.app_dir}/speedtest_history.db")
    
    def run_uninstallation(self, remove_config: bool = False, remove_data: bool = False) -> bool:
        """Uruchom pełny proces deinstalacji."""
        print("Speed Test Tool Uninstaller")
        print("=" * 30)
        
        success = True
        
        # Remove components
        success &= self.remove_executable_scripts()
        success &= self.remove_symbolic_links()
        success &= self.remove_desktop_entry()
        success &= self.remove_systemd_service()
        success &= self.remove_virtual_environment()
        success &= self.remove_config_files(remove_config)
        success &= self.remove_database(remove_data)
        success &= self.clean_pycache()
        
        if success:
            print("\n✓ Uninstallation completed successfully!")
        else:
            print("\n✗ Some components could not be removed")
        
        self.show_summary(remove_config, remove_data)
        
        return success


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Speed Test Tool Uninstaller"
    )
    parser.add_argument(
        "--remove-config", 
        action="store_true",
        help="Also remove user configuration file"
    )
    parser.add_argument(
        "--remove-data", 
        action="store_true",
        help="Also remove test results database"
    )
    parser.add_argument(
        "--remove-all",
        action="store_true", 
        help="Remove everything (config + data)"
    )
    
    args = parser.parse_args()
    
    remove_config = args.remove_config or args.remove_all
    remove_data = args.remove_data or args.remove_all
    
    # Confirm destructive actions
    if remove_config or remove_data:
        print("WARNING: This will permanently delete:")
        if remove_config:
            print("  - User configuration")
        if remove_data:
            print("  - All test results and history")
        
        response = input("Continue? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("Uninstallation cancelled")
            return 0
    
    uninstaller = SpeedTestUninstaller()
    
    try:
        success = uninstaller.run_uninstallation(remove_config, remove_data)
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\nUninstallation interrupted by user")
        return 1
    except Exception as e:
        print(f"Uninstallation failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())