#!/usr/bin/env python3
"""
Test script for configuration validation system.

Tests the new configuration validation features in speedtest_core.py
"""

import json
import tempfile
import os
from speedtest_core import SpeedTestConfig

def test_valid_config():
    """Test loading valid configuration."""
    print("🧪 Testing valid configuration...")
    
    valid_config = {
        "bits_to_mbps": 1000000,
        "connectivity_check_timeout": 15,
        "speedtest_timeout": 90,
        "max_retries": 5,
        "retry_delay": 3,
        "max_typical_speed_gbps": 2,
        "max_reasonable_speed_gbps": 20,
        "max_typical_ping_ms": 500,
        "max_reasonable_ping_ms": 5000,
        "show_detailed_progress": True
    }
    
    # Create temporary config file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(valid_config, f, indent=2)
        temp_file = f.name
    
    try:
        config = SpeedTestConfig(temp_file)
        print("✅ Valid configuration loaded successfully")
        
        # Verify values were loaded correctly
        assert config['bits_to_mbps'] == 1000000
        assert config['connectivity_check_timeout'] == 15
        assert config['max_retries'] == 5
        print("✅ Configuration values verified")
        
    finally:
        os.unlink(temp_file)

def test_invalid_values():
    """Test configuration with invalid values."""
    print("\n🧪 Testing invalid configuration values...")
    
    invalid_config = {
        "connectivity_check_timeout": 300,  # Too high
        "max_retries": 15,                  # Too high  
        "retry_delay": 0.5,                 # Too low
        "max_typical_speed_gbps": 200,      # Too high
        "show_detailed_progress": "yes"     # Wrong type
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(invalid_config, f, indent=2)
        temp_file = f.name
    
    try:
        print("Expected validation warnings:")
        config = SpeedTestConfig(temp_file)
        
        # Should fall back to defaults for invalid values
        assert config['connectivity_check_timeout'] == 10  # Default
        assert config['max_retries'] == 3                  # Default
        assert config['retry_delay'] == 2                  # Default
        assert config['show_detailed_progress'] == True    # Default
        
        print("✅ Invalid values properly handled with defaults")
        
    finally:
        os.unlink(temp_file)

def test_unknown_keys():
    """Test configuration with unknown keys."""
    print("\n🧪 Testing configuration with unknown keys...")
    
    config_with_unknown = {
        "bits_to_mbps": 1000000,
        "unknown_setting": "should be ignored",
        "another_unknown": 123,
        "connectivity_check_timeout": 20
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_with_unknown, f, indent=2)
        temp_file = f.name
    
    try:
        print("Expected validation warnings:")
        config = SpeedTestConfig(temp_file)
        
        # Known values should be loaded
        assert config['bits_to_mbps'] == 1000000
        assert config['connectivity_check_timeout'] == 20
        
        # Unknown keys should be ignored
        assert 'unknown_setting' not in config.config
        assert 'another_unknown' not in config.config
        
        print("✅ Unknown keys properly ignored")
        
    finally:
        os.unlink(temp_file)

def test_logical_consistency():
    """Test logical consistency validation."""
    print("\n🧪 Testing logical consistency validation...")
    
    inconsistent_config = {
        "max_typical_speed_gbps": 10,      # Higher than reasonable
        "max_reasonable_speed_gbps": 5,    # Lower than typical (invalid)
        "max_typical_ping_ms": 2000,       # Higher than reasonable
        "max_reasonable_ping_ms": 1000     # Lower than typical (invalid)
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(inconsistent_config, f, indent=2)
        temp_file = f.name
    
    try:
        print("Expected validation warnings:")
        config = SpeedTestConfig(temp_file)
        
        # Should fall back to defaults for inconsistent values
        assert config['max_typical_speed_gbps'] == 1     # Default
        assert config['max_reasonable_speed_gbps'] == 5  # User value kept
        assert config['max_typical_ping_ms'] == 1000     # Default
        assert config['max_reasonable_ping_ms'] == 1000  # User value kept
        
        print("✅ Logical consistency properly enforced")
        
    finally:
        os.unlink(temp_file)

def test_malformed_json():
    """Test handling of malformed JSON."""
    print("\n🧪 Testing malformed JSON handling...")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write('{ "bits_to_mbps": 1000000, invalid json }')
        temp_file = f.name
    
    try:
        print("Expected error messages:")
        config = SpeedTestConfig(temp_file)
        
        # Should fall back to all defaults
        assert config['bits_to_mbps'] == 1000000          # Default
        assert config['connectivity_check_timeout'] == 10 # Default
        assert config['max_retries'] == 3                 # Default
        
        print("✅ Malformed JSON properly handled with defaults")
        
    finally:
        os.unlink(temp_file)

def main():
    """Run all configuration validation tests."""
    print("🔧 Configuration Validation Test Suite")
    print("=" * 50)
    
    try:
        test_valid_config()
        test_invalid_values()
        test_unknown_keys()
        test_logical_consistency()
        test_malformed_json()
        
        print("\n🎉 All configuration validation tests passed!")
        print("✅ Configuration validation system is working correctly")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())