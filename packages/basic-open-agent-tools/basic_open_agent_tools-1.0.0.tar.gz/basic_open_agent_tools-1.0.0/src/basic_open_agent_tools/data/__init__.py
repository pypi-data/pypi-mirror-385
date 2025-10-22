"""Data tools for AI agents.

This module provides data processing and manipulation tools organized into logical submodules:

- json_tools: JSON serialization, compression, and validation
- csv_tools: CSV file processing, parsing, and cleaning
- validation: Data validation and schema checking
- config_processing: Configuration file processing (YAML, TOML, INI)
"""

# Import all functions from submodules
from .config_processing import (
    merge_config_files,
    read_ini_file,
    read_toml_file,
    read_yaml_file,
    validate_config_schema,
    write_ini_file,
    write_toml_file,
    write_yaml_file,
)
from .csv_tools import (
    clean_csv_data,
    csv_to_dict_list,
    detect_csv_delimiter,
    dict_list_to_csv,
    read_csv_simple,
    validate_csv_structure,
    write_csv_simple,
)
from .json_tools import (
    safe_json_deserialize,
    safe_json_serialize,
    validate_json_string,
)
from .validation import (
    check_required_fields,
    create_validation_report,
    validate_data_types_simple,
    validate_range_simple,
    validate_schema_simple,
)

# Re-export all functions at module level for convenience
__all__: list[str] = [
    # JSON processing
    "safe_json_serialize",
    "safe_json_deserialize",
    "validate_json_string",
    # CSV processing
    "read_csv_simple",
    "write_csv_simple",
    "csv_to_dict_list",
    "dict_list_to_csv",
    "detect_csv_delimiter",
    "validate_csv_structure",
    "clean_csv_data",
    # Validation
    "validate_schema_simple",
    "check_required_fields",
    "validate_data_types_simple",
    "validate_range_simple",
    "create_validation_report",
    # Configuration processing
    "read_yaml_file",
    "write_yaml_file",
    "read_toml_file",
    "write_toml_file",
    "read_ini_file",
    "write_ini_file",
    "validate_config_schema",
    "merge_config_files",
]
