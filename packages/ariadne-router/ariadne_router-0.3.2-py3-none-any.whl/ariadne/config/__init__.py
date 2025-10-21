"""
Configuration system for Ariadne.

This module provides comprehensive configuration management, including validation,
progressive loading from multiple sources, and template generation.
"""

from .config import (
    AnalysisConfig,
    AriadneConfig,
    BackendConfig,
    ConfigManager,
    ErrorMitigationConfig,
    OptimizationConfig,
    PerformanceConfig,
    configure_ariadne,
    get_config,
    get_config_manager,
)
from .loader import (
    ConfigFormat,
    ConfigLoadError,
    ConfigSource,
    ConfigTemplate,
    ProgressiveConfigLoader,
    create_default_template,
    create_development_template,
    create_production_template,
    get_config_loader,
    load_config,
)
from .validation import (
    ChoiceRule,
    ConfigurationSchema,
    ConfigurationValidator,
    CustomRule,
    FieldSchema,
    PathRule,
    RangeRule,
    RegexRule,
    TypeRule,
    ValidationIssue,
    ValidationResult,
    ValidationRule,
    ValidationSeverity,
    get_validator,
    register_schema,
    validate_config,
)

__all__ = [
    # Configuration data classes
    "AriadneConfig",
    "BackendConfig",
    "OptimizationConfig",
    "ErrorMitigationConfig",
    "AnalysisConfig",
    "PerformanceConfig",
    "ConfigManager",
    "get_config",
    "get_config_manager",
    "configure_ariadne",
    # Configuration loading
    "ConfigFormat",
    "ConfigLoadError",
    "ConfigSource",
    "ConfigTemplate",
    "ProgressiveConfigLoader",
    "create_default_template",
    "create_development_template",
    "create_production_template",
    "get_config_loader",
    "load_config",
    # Configuration validation
    "ChoiceRule",
    "ConfigurationSchema",
    "ConfigurationValidator",
    "CustomRule",
    "FieldSchema",
    "PathRule",
    "RangeRule",
    "RegexRule",
    "TypeRule",
    "ValidationIssue",
    "ValidationResult",
    "ValidationRule",
    "ValidationSeverity",
    "get_validator",
    "register_schema",
    "validate_config",
]
