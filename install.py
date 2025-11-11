#!/usr/bin/env python3
"""
Speed Test Tool - Automatic Installer
=====================================

Automatyczny installer tworzy pliki uruchamialne i konfiguruje system
dla łatwego użytkowania Speed Test Tool bez wywoływania Python bezpośrednio.
"""

import os
import sys
import stat
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional


class SpeedTestInstaller:
    """Installer dla Speed Test Tool."""
    
    def __init__(self):
        self.app_dir = Path(__file__).parent.absolute()
        self.venv_dir = self.app_dir / "speedtest_env"
        self.venv_python = self.venv_dir / "bin" / "python3"
        self.install_dir = Path("/usr/local/bin")
        self.user_mode = False
        
        # Check if running as root
        if os.geteuid() != 0:
            self.user_mode = True
            self.install_dir = Path.home() / ".local" / "bin"
            print("Running in user mode - installing to ~/.local/bin")
        else:
            print("Running as root - installing to /usr/local/bin")
    
    def check_python_version(self) -> bool:
        """Sprawdź czy Python ma odpowiednią wersję."""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 6):
            print(f"Error: Python 3.6+ required, found {version.major}.{version.minor}")
            return False
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} OK")
        return True
    
    def create_virtual_environment(self) -> bool:
        """Utwórz środowisko wirtualne jeśli nie istnieje."""
        if self.venv_dir.exists():
            print("✓ Virtual environment already exists")
            return True
        
        print("Creating virtual environment...")
        try:
            subprocess.run([
                sys.executable, "-m", "venv", str(self.venv_dir)
            ], check=True, capture_output=True)
            print("✓ Virtual environment created")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error creating virtual environment: {e}")
            return False
    
    def install_dependencies(self) -> bool:
        """Zainstaluj zależności w środowisku wirtualnym."""
        requirements_file = self.app_dir / "requirements.txt"
        if not requirements_file.exists():
            print("Error: requirements.txt not found")
            return False

        print("Installing dependencies...")

        # Try to upgrade pip, but don't fail if it errors
        try:
            subprocess.run([
                str(self.venv_python), "-m", "pip", "install",
                "--upgrade", "pip"
            ], check=True, capture_output=True, timeout=120)
            print("✓ pip upgraded")
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            print("Warning: Could not upgrade pip, continuing with existing version")
            # Don't return False - continue with installation

        # Install requirements - this is critical
        try:
            subprocess.run([
                str(self.venv_python), "-m", "pip", "install",
                "-r", str(requirements_file)
            ], check=True, timeout=600)
            print("✓ Dependencies installed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error installing dependencies: {e}")
            return False
        except subprocess.TimeoutExpired:
            print("Error: Installation timed out (took longer than 10 minutes)")
            return False
    
    def create_executable_scripts(self) -> bool:
        """Utwórz pliki uruchamialne."""
        scripts = [
            ("speedtest-cli", "sp.py", "CLI Speed Test"),
            ("speedtest-gui", "speedtest_gui.py", "GUI Speed Test"),
            ("speedtest-gui-fallback", "speedtest_gui_fallback.py", "Fallback GUI"),
            ("speedtest-scheduler", "scheduled_testing.py", "Speed Test Scheduler"),
            ("speedtest-storage", "test_results_storage.py", "Results Management")
        ]
        
        # Create install directory if it doesn't exist
        self.install_dir.mkdir(parents=True, exist_ok=True)
        
        for script_name, python_file, description in scripts:
            script_path = self.install_dir / script_name
            
            # Create script content
            script_content = self._create_script_content(python_file, description)
            
            try:
                with open(script_path, 'w') as f:
                    f.write(script_content)
                
                # Make executable
                script_path.chmod(script_path.stat().st_mode | stat.S_IEXEC)
                print(f"✓ Created {script_name}")
                
            except (IOError, OSError) as e:
                print(f"Error creating {script_name}: {e}")
                return False
        
        return True
    
    def _create_script_content(self, python_file: str, description: str) -> str:
        """Utwórz zawartość skryptu uruchamialnego."""
        return f"""#!/bin/bash
# {description}
# Auto-generated by Speed Test Tool Installer

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" &> /dev/null && pwd)"

# Try to find the app directory
APP_DIR="{self.app_dir}"

# If running from installed location, try to find app directory
if [ ! -d "$APP_DIR" ]; then
    # Look in common locations
    for dir in "/opt/speedtest" "$HOME/Speed_test" "$HOME/speedtest" "./Speed_test"; do
        if [ -d "$dir" ] && [ -f "$dir/{python_file}" ]; then
            APP_DIR="$dir"
            break
        fi
    done
fi

# Check if app directory exists
if [ ! -d "$APP_DIR" ]; then
    echo "Error: Speed Test application directory not found"
    echo "Please ensure the application is properly installed"
    exit 1
fi

# Change to app directory
cd "$APP_DIR" || {{
    echo "Error: Cannot access application directory: $APP_DIR"
    exit 1
}}

# Check if virtual environment exists
VENV_DIR="$APP_DIR/speedtest_env"
if [ ! -d "$VENV_DIR" ]; then
    echo "Error: Virtual environment not found at $VENV_DIR"
    echo "Please run the installer again: python3 install.py"
    exit 1
fi

# Activate virtual environment and run the application
source "$VENV_DIR/bin/activate" || {{
    echo "Error: Cannot activate virtual environment"
    exit 1
}}

# Run the Python application with all passed arguments
python3 "{python_file}" "$@"
EXIT_CODE=$?

# Deactivate virtual environment
deactivate

# Exit with the same code as the Python application
exit $EXIT_CODE
"""
    
    def create_desktop_entry(self) -> bool:
        """Utwórz .desktop file dla GUI application."""
        desktop_dir = Path.home() / ".local" / "share" / "applications"
        desktop_dir.mkdir(parents=True, exist_ok=True)
        
        desktop_file = desktop_dir / "speedtest.desktop"
        
        # Find icon file
        icon_path = self.app_dir / "icon.png"
        if not icon_path.exists():
            # Create simple icon placeholder
            icon_path = "applications-internet"
        
        desktop_content = f"""[Desktop Entry]
Name=Speed Test Tool
GenericName=Internet Speed Test
Comment=Test your internet connection speed
Exec={self.install_dir / 'speedtest-gui'}
Icon={icon_path}
Terminal=false
Type=Application
Categories=Network;Utility;System;
Keywords=speed;test;internet;network;bandwidth;
StartupNotify=true
"""
        
        try:
            with open(desktop_file, 'w') as f:
                f.write(desktop_content)
            print("✓ Desktop entry created")
            
            # Update desktop database
            try:
                subprocess.run([
                    "update-desktop-database", str(desktop_dir)
                ], check=True, capture_output=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                # update-desktop-database might not be available
                pass
            
            return True
            
        except (IOError, OSError) as e:
            print(f"Warning: Could not create desktop entry: {e}")
            return False
    
    def update_path_instructions(self) -> None:
        """Wyświetl instrukcje dotyczące PATH."""
        if self.user_mode:
            path_dir = self.install_dir
            shell_rc = Path.home() / ".bashrc"
            
            # Check if already in PATH
            try:
                result = subprocess.run([
                    "bash", "-c", f"command -v speedtest-cli"
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print("✓ Scripts already in PATH")
                    return
                    
            except subprocess.CalledProcessError:
                pass
            
            print(f"\nTo use commands from anywhere, add to your PATH:")
            print(f"echo 'export PATH=\"{path_dir}:$PATH\"' >> {shell_rc}")
            print(f"source {shell_rc}")
            print("\nOr run commands with full path:")
            print(f"{path_dir}/speedtest-cli")
    
    def verify_installation(self) -> bool:
        """Sprawdź czy instalacja przebiegła pomyślnie."""
        print("\nVerifying installation...")
        
        scripts_to_check = ["speedtest-cli", "speedtest-gui", "speedtest-scheduler"]
        
        for script_name in scripts_to_check:
            script_path = self.install_dir / script_name
            if not script_path.exists():
                print(f"✗ {script_name} not found")
                return False
            
            if not os.access(script_path, os.X_OK):
                print(f"✗ {script_name} not executable")
                return False
            
            print(f"✓ {script_name} OK")
        
        # Test basic import
        try:
            subprocess.run([
                str(self.venv_python), "-c", 
                "from speedtest_core import SpeedTestEngine; print('Core imports OK')"
            ], check=True, capture_output=True)
            print("✓ Core modules OK")
        except subprocess.CalledProcessError:
            print("✗ Core modules import failed")
            return False
        
        return True
    
    def run_installation(self) -> bool:
        """Uruchom pełny proces instalacji."""
        print("Speed Test Tool Installer")
        print("=" * 30)
        
        if not self.check_python_version():
            return False
        
        if not self.create_virtual_environment():
            return False
        
        if not self.install_dependencies():
            return False
        
        if not self.create_executable_scripts():
            return False
        
        self.create_desktop_entry()  # Optional, don't fail if unsuccessful
        
        if not self.verify_installation():
            return False
        
        print("\n" + "=" * 30)
        print("✓ Installation completed successfully!")
        print("\nAvailable commands:")
        print(f"  {self.install_dir}/speedtest-cli          - CLI interface")
        print(f"  {self.install_dir}/speedtest-gui          - GUI interface") 
        print(f"  {self.install_dir}/speedtest-scheduler    - Background scheduler")
        print(f"  {self.install_dir}/speedtest-storage      - Results management")
        
        self.update_path_instructions()
        
        print("\nQuick start:")
        print(f"  {self.install_dir}/speedtest-cli --create-config")
        print(f"  {self.install_dir}/speedtest-cli")
        print(f"  {self.install_dir}/speedtest-gui")
        
        return True


def main():
    """Main function."""
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help"]:
        print("Speed Test Tool Installer")
        print("Usage: python3 install.py [--user]")
        print("")
        print("Options:")
        print("  --user    Install in user mode (~/. local/bin)")
        print("  --help    Show this help")
        print("")
        print("This installer will:")
        print("- Create virtual environment")
        print("- Install dependencies")
        print("- Create executable scripts")
        print("- Setup desktop entry (GUI)")
        return 0
    
    installer = SpeedTestInstaller()
    
    # Override install mode if requested
    if len(sys.argv) > 1 and sys.argv[1] == "--user":
        installer.user_mode = True
        installer.install_dir = Path.home() / ".local" / "bin"
        print("Forced user mode installation")
    
    try:
        success = installer.run_installation()
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\nInstallation interrupted by user")
        return 1
    except Exception as e:
        print(f"Installation failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())