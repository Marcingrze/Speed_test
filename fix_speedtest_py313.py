#!/usr/bin/env python3
"""
Fix speedtest-cli for Python 3.13 compatibility

This script patches speedtest-cli to work with Python 3.13 in Kivy environments
by handling AttributeError when sys.stderr.fileno() is not available.
"""

import sys
from pathlib import Path
import speedtest

def fix_speedtest_py313():
    """Apply patch to speedtest-cli for Python 3.13 compatibility."""
    
    speedtest_file = Path(speedtest.__file__)
    print(f"Patching {speedtest_file}")
    
    # Read the file
    with open(speedtest_file, 'r') as f:
        content = f.read()
    
    # Check if already patched
    if 'except (OSError, AttributeError):' in content:
        print("✅ speedtest-cli already patched for Python 3.13")
        return True
    
    # Apply the patch
    old_code = "    except OSError:"
    new_code = "    except (OSError, AttributeError):"
    
    if old_code not in content:
        print("❌ Patch pattern not found - speedtest-cli may have changed")
        return False
    
    # Create backup
    backup_file = speedtest_file.with_suffix('.py.backup')
    with open(backup_file, 'w') as f:
        f.write(content)
    print(f"📁 Backup created: {backup_file}")
    
    # Apply patch
    patched_content = content.replace(old_code, new_code)
    
    with open(speedtest_file, 'w') as f:
        f.write(patched_content)
    
    print("✅ speedtest-cli successfully patched for Python 3.13")
    print("🔧 Patch: Added AttributeError handling to _Py3Utf8Output initialization")
    return True

def main():
    """Main function."""
    print("🔧 speedtest-cli Python 3.13 Compatibility Patcher")
    print("=" * 50)
    
    if sys.version_info < (3, 13):
        print(f"⚠️  This patch is for Python 3.13+, you have {sys.version}")
        print("Patch may not be necessary for your Python version.")
    
    try:
        success = fix_speedtest_py313()
        if success:
            print("\n🎉 Patch applied successfully!")
            print("You can now run the GUI and CLI applications.")
        else:
            print("\n❌ Patch failed. You may need to update this script.")
            return 1
    except Exception as e:
        print(f"\n❌ Error applying patch: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())