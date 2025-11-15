#!/usr/bin/env python3
"""
Configuration Validation Module

Provides schema validation and type checking for speedtest configuration.
"""

from typing import Dict, Any, List, Tuple, Union
import json
from pathlib import Path
from speedtest_core import SpeedTestConfig


class ConfigValidator:
    """Configuration validator with schema checking."""

    @staticmethod
    def _build_schema() -> Dict[str, Any]:
        """Build schema dynamically from SpeedTestConfig.VALIDATION_RULES.

        This ensures the validator always stays in sync with the core config.
        """
        schema = {}

        # Schema descriptions for each field
        descriptions = {
            'bits_to_mbps': 'Conversion factor from bits to Mbps',
            'connectivity_check_timeout': 'Timeout for network connectivity check (seconds)',
            'speedtest_timeout': 'Timeout for speed test execution (seconds)',
            'max_retries': 'Maximum number of retry attempts',
            'retry_delay': 'Delay between retry attempts (seconds)',
            'max_typical_speed_gbps': 'Threshold for typical internet speed (Gbps)',
            'max_reasonable_speed_gbps': 'Maximum reasonable internet speed (Gbps)',
            'max_typical_ping_ms': 'Threshold for typical ping latency (ms)',
            'max_reasonable_ping_ms': 'Maximum reasonable ping latency (ms)',
        }

        # Build schema from VALIDATION_RULES
        for key, (min_val, max_val) in SpeedTestConfig.VALIDATION_RULES.items():
            # Determine type based on key
            if key == 'max_retries':
                field_type = int
            else:
                field_type = (int, float)

            schema[key] = {
                'type': field_type,
                'min': min_val,
                'max': max_val,
                'description': descriptions.get(key, f'Configuration for {key}')
            }

        # Add boolean fields (not in VALIDATION_RULES)
        schema['show_detailed_progress'] = {
            'type': bool,
            'description': 'Show detailed progress information'
        }
        schema['save_results_to_database'] = {
            'type': bool,
            'description': 'Save test results to SQLite database'
        }

        return schema

    # Build schema at class definition time
    SCHEMA = _build_schema.__func__()

    @classmethod
    def sync_schema_from_core(cls) -> List[str]:
        """Verify schema consistency with SpeedTestConfig.

        Returns:
            List of warnings/errors if drift detected (now always empty since schema is dynamic)
        """
        # Schema is now built dynamically from VALIDATION_RULES, so no sync needed
        # This method is kept for backward compatibility
        return []

    @classmethod
    def validate_config(cls, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate configuration against schema.

        Args:
            config: Configuration dictionary to validate

        Returns:
            Tuple of (is_valid, error_messages)
        """
        # Auto-sync schema on first use
        cls.sync_schema_from_core()

        errors = []
        
        # Check for unknown keys
        unknown_keys = set(config.keys()) - set(cls.SCHEMA.keys())
        if unknown_keys:
            errors.append(f"Unknown configuration keys: {', '.join(unknown_keys)}")
        
        # Validate each known key
        for key, rules in cls.SCHEMA.items():
            if key in config:
                value = config[key]
                
                # Type validation
                if not isinstance(value, rules['type']):
                    expected_types = rules['type'] if isinstance(rules['type'], tuple) else (rules['type'],)
                    type_names = [t.__name__ for t in expected_types]
                    errors.append(f"{key}: Expected {' or '.join(type_names)}, got {type(value).__name__}")
                    continue
                
                # Range validation for numeric types
                if isinstance(value, (int, float)):
                    if 'min' in rules and value < rules['min']:
                        errors.append(f"{key}: Value {value} is below minimum {rules['min']}")
                    if 'max' in rules and value > rules['max']:
                        errors.append(f"{key}: Value {value} is above maximum {rules['max']}")
        
        # Logical consistency checks
        if 'max_typical_speed_gbps' in config and 'max_reasonable_speed_gbps' in config:
            if config['max_typical_speed_gbps'] > config['max_reasonable_speed_gbps']:
                errors.append("max_typical_speed_gbps cannot be greater than max_reasonable_speed_gbps")
        
        if 'max_typical_ping_ms' in config and 'max_reasonable_ping_ms' in config:
            if config['max_typical_ping_ms'] > config['max_reasonable_ping_ms']:
                errors.append("max_typical_ping_ms cannot be greater than max_reasonable_ping_ms")
        
        return len(errors) == 0, errors
    
    @classmethod
    def validate_config_file(cls, file_path: Union[str, Path]) -> Tuple[bool, List[str], Dict[str, Any]]:
        """Validate configuration file.
        
        Args:
            file_path: Path to configuration file
            
        Returns:
            Tuple of (is_valid, error_messages, config_dict)
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            return False, [f"Configuration file {file_path} does not exist"], {}
        
        try:
            with open(file_path, 'r') as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            return False, [f"Invalid JSON in configuration file: {e}"], {}
        except Exception as e:
            return False, [f"Error reading configuration file: {e}"], {}
        
        # Validate the loaded config
        is_valid, errors = cls.validate_config(config)
        return is_valid, errors, config
    
    @classmethod
    def get_schema_documentation(cls) -> str:
        """Get human-readable schema documentation."""
        doc_lines = ["Configuration Schema:", "=" * 50]
        
        for key, rules in cls.SCHEMA.items():
            type_info = rules['type'] if isinstance(rules['type'], tuple) else (rules['type'],)
            type_names = [t.__name__ for t in type_info]
            
            doc_lines.append(f"\n{key}:")
            doc_lines.append(f"  Type: {' or '.join(type_names)}")
            
            if 'min' in rules or 'max' in rules:
                range_info = []
                if 'min' in rules:
                    range_info.append(f"min: {rules['min']}")
                if 'max' in rules:
                    range_info.append(f"max: {rules['max']}")
                doc_lines.append(f"  Range: {', '.join(range_info)}")
            
            doc_lines.append(f"  Description: {rules['description']}")
        
        return "\\n".join(doc_lines)
    
    @classmethod
    def create_valid_config_template(cls) -> Dict[str, Any]:
        """Create a valid configuration template with default values."""
        template = {}
        
        # Use defaults from SpeedTestConfig to ensure a single source of truth
        defaults = SpeedTestConfig.DEFAULT_CONFIG
        
        for key in cls.SCHEMA.keys():
            template[key] = defaults.get(key)
        
        return template


def main():
    """CLI interface for configuration validation."""
    import sys

    # Synchronize schema with SpeedTestConfig on startup
    warnings = ConfigValidator.sync_schema_from_core()
    if warnings:
        print("Schema synchronization warnings:")
        for warning in warnings:
            print(f"  {warning}")
        print()

    if len(sys.argv) < 2:
        print("Usage: python config_validator.py <config_file>")
        print("       python config_validator.py --schema")
        return 1

    if sys.argv[1] == "--schema":
        print(ConfigValidator.get_schema_documentation())
        return 0
    
    config_file = sys.argv[1]
    is_valid, errors, config = ConfigValidator.validate_config_file(config_file)
    
    if is_valid:
        print(f"✅ Configuration file {config_file} is valid!")
        print(f"Loaded {len(config)} configuration parameters.")
    else:
        print(f"❌ Configuration file {config_file} has errors:")
        for error in errors:
            print(f"  - {error}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())