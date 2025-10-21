"""
Progressive configuration loading system for Ariadne.

This module provides flexible configuration loading from multiple sources,
with support for environment-specific configurations and progressive overrides.
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

try:
    from ariadne.core import ConfigurationError
except ImportError:
    # Fallback for when running as a script
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from ariadne.core import ConfigurationError

if TYPE_CHECKING:
    from .validation import ConfigurationValidator
else:
    try:
        from .validation import ConfigurationValidator
    except ImportError:  # pragma: no cover
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from validation import ConfigurationValidator


class ConfigFormat(Enum):
    """Supported configuration file formats."""

    JSON = "json"
    YAML = "yaml"
    TOML = "toml"
    INI = "ini"
    ENV = "env"


@dataclass
class ConfigSource:
    """A configuration source with metadata."""

    name: str
    path: str | None = None
    format: ConfigFormat | None = None
    data: dict[str, Any] | None = None
    priority: int = 0  # Higher priority sources override lower ones
    environment: str | None = None  # Environment-specific source
    required: bool = False  # Whether this source is required

    def __post_init__(self) -> None:
        """Post-initialization processing."""
        # Auto-detect format from path if not specified
        if self.path and not self.format:
            if self.path.endswith(".json"):
                self.format = ConfigFormat.JSON
            elif self.path.endswith((".yaml", ".yml")):
                self.format = ConfigFormat.YAML
            elif self.path.endswith(".toml"):
                self.format = ConfigFormat.TOML
            elif self.path.endswith(".ini"):
                self.format = ConfigFormat.INI
            elif self.path.endswith(".env"):
                self.format = ConfigFormat.ENV


class ConfigLoadError(ConfigurationError):
    """Raised when configuration loading fails."""

    pass


class ProgressiveConfigLoader:
    """
    Progressive configuration loader that loads from multiple sources.

    This class loads configuration from multiple sources in priority order,
    with later sources overriding earlier ones. It supports environment-specific
    configurations and progressive overrides.
    """

    def __init__(self, validator: ConfigurationValidator | None = None) -> None:
        """
        Initialize the progressive config loader.

        Args:
            validator: Configuration validator to use
        """
        self.validator = validator or ConfigurationValidator()
        self.sources: list[ConfigSource] = []
        self.loaded_config: dict[str, Any] = {}
        self.load_history: list[dict[str, Any]] = []

    def add_source(self, source: ConfigSource) -> None:
        """
        Add a configuration source.

        Args:
            source: Configuration source to add
        """
        self.sources.append(source)
        # Sort sources by priority (higher first)
        self.sources.sort(key=lambda s: s.priority, reverse=True)

    def add_file_source(
        self, path: str, priority: int = 0, environment: str | None = None, required: bool = False
    ) -> None:
        """
        Add a file-based configuration source.

        Args:
            path: Path to configuration file
            priority: Source priority
            environment: Environment-specific source
            required: Whether this source is required
        """
        source = ConfigSource(
            name=f"file:{path}",
            path=path,
            priority=priority,
            environment=environment,
            required=required,
        )
        self.add_source(source)

    def add_dict_source(
        self, name: str, data: dict[str, Any], priority: int = 0, environment: str | None = None
    ) -> None:
        """
        Add a dictionary-based configuration source.

        Args:
            name: Source name
            data: Configuration data
            priority: Source priority
            environment: Environment-specific source
        """
        source = ConfigSource(name=name, data=data, priority=priority, environment=environment)
        self.add_source(source)

    def add_env_source(self, prefix: str = "ARIADNE_", priority: int = 0, required: bool = False) -> None:
        """
        Add an environment variable-based configuration source.

        Args:
            prefix: Environment variable prefix
            priority: Source priority
            required: Whether this source is required
        """
        # Load environment variables with prefix
        env_data = {}
        for key, value in os.environ.items():
            if key.startswith(prefix):
                # Remove prefix and convert to lowercase
                config_key = key[len(prefix) :].lower()

                # Try to parse as JSON, fall back to string
                try:
                    env_data[config_key] = json.loads(value)
                except (json.JSONDecodeError, ValueError):
                    env_data[config_key] = value

        source = ConfigSource(
            name=f"env:{prefix}",
            data=env_data,
            format=ConfigFormat.ENV,
            priority=priority,
            required=required,
        )
        self.add_source(source)

    def load(self, environment: str | None = None, schema_name: str | None = None) -> dict[str, Any]:
        """
        Load configuration from all sources.

        Args:
            environment: Environment to load configuration for
            schema_name: Schema name to validate against

        Returns:
            Loaded configuration

        Raises:
            ConfigLoadError: If configuration loading fails
        """
        self.loaded_config = {}
        self.load_history = []

        # Filter sources by environment if specified
        sources = self.sources
        if environment:
            sources = [s for s in sources if s.environment is None or s.environment == environment]

        # Load from each source in priority order
        for source in sources:
            try:
                config_data = self._load_source(source)
                if config_data:
                    # Merge with existing configuration
                    self._merge_config(self.loaded_config, config_data)

                    # Record in history
                    self.load_history.append(
                        {
                            "source": source.name,
                            "data": config_data.copy(),
                            "merged": self.loaded_config.copy(),
                        }
                    )
            except Exception as e:
                if source.required:
                    raise ConfigLoadError(
                        "source",
                        source.name,
                        f"Required source {source.name} failed to load: {e}",
                    ) from e
                else:
                    # Log warning but continue
                    print(f"Warning: Failed to load source {source.name}: {e}")

        # Validate against schema if specified
        if schema_name:
            result = self.validator.validate(self.loaded_config, schema_name)
            if not result.is_valid:
                error_messages = [issue.message for issue in result.error_issues]
                raise ConfigLoadError(
                    schema_name or "config",
                    self.loaded_config,
                    f"Configuration validation failed: {'; '.join(error_messages)}",
                )

        return self.loaded_config

    def _load_source(self, source: ConfigSource) -> dict[str, Any]:
        """Load configuration from a specific source."""
        if source.data:
            # Direct data source
            return source.data
        elif source.path:
            # File-based source
            return self._load_file(source.path, source.format)
        else:
            raise ConfigLoadError("source", source.name, "Source has no path or data")

    def _load_file(self, path: str, format: ConfigFormat | None = None) -> dict[str, Any]:
        """Load configuration from a file."""
        file_path = Path(path)

        if not file_path.exists():
            raise ConfigLoadError("file", path, "Configuration file not found")

        if not file_path.is_file():
            raise ConfigLoadError("file", path, "Configuration path is not a file")

        # Auto-detect format if not specified
        if not format:
            if path.endswith(".json"):
                format = ConfigFormat.JSON
            elif path.endswith((".yaml", ".yml")):
                format = ConfigFormat.YAML
            elif path.endswith(".toml"):
                format = ConfigFormat.TOML
            elif path.endswith(".ini"):
                format = ConfigFormat.INI
            elif path.endswith(".env"):
                format = ConfigFormat.ENV
            else:
                raise ConfigLoadError("file_format", path, "Cannot determine format for file")

        # Load based on format
        try:
            with open(file_path, encoding="utf-8") as f:
                if format == ConfigFormat.JSON:
                    data = json.load(f)
                    if not isinstance(data, dict):
                        raise ConfigLoadError(
                            "file",
                            path,
                            "JSON configuration must be a JSON object",
                        )
                    return cast(dict[str, Any], data)
                elif format == ConfigFormat.YAML:
                    if not YAML_AVAILABLE:
                        raise ConfigLoadError(
                            "file_format",
                            "yaml",
                            "YAML support not available. Install PyYAML.",
                        )
                    data = yaml.safe_load(f) or {}
                    if not isinstance(data, dict):
                        raise ConfigLoadError(
                            "file",
                            path,
                            "YAML configuration must be a mapping",
                        )
                    return cast(dict[str, Any], data)
                elif format == ConfigFormat.TOML:
                    try:
                        import tomllib

                        with open(file_path, "rb") as fb:
                            data = tomllib.load(fb)
                            if not isinstance(data, dict):
                                raise ConfigLoadError(
                                    "file",
                                    path,
                                    "TOML configuration must be a mapping",
                                )
                            return cast(dict[str, Any], data)
                    except ImportError:
                        try:
                            import toml

                            data = toml.load(f)
                            if not isinstance(data, dict):
                                raise ConfigLoadError(
                                    "file",
                                    path,
                                    "TOML configuration must be a mapping",
                                )
                            return cast(dict[str, Any], data)
                        except ImportError as exc:
                            raise ConfigLoadError(
                                "file_format",
                                "toml",
                                "TOML support not available. Install tomli or toml.",
                            ) from exc
                elif format == ConfigFormat.INI:
                    import configparser

                    parser = configparser.ConfigParser()
                    parser.read(file_path)
                    # Convert to nested dictionary
                    return {section: dict(parser[section]) for section in parser.sections()}
                elif format == ConfigFormat.ENV:
                    # Parse .env file format
                    env_data: dict[str, Any] = {}
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            if "=" in line:
                                key, value = line.split("=", 1)
                                key = key.strip()
                                value = value.strip()
                                # Remove quotes if present
                                if value.startswith('"') and value.endswith('"'):
                                    value = value[1:-1]
                                elif value.startswith("'") and value.endswith("'"):
                                    value = value[1:-1]
                                env_data[key] = value
                    return env_data
                else:
                    raise ConfigLoadError(
                        "file_format",
                        format.value if isinstance(format, ConfigFormat) else str(format),
                        "Unsupported configuration format",
                    )
        except Exception as e:
            raise ConfigLoadError("file", path, f"Failed to load file {path}: {e}") from e

    def _merge_config(self, base: dict[str, Any], override: dict[str, Any]) -> None:
        """Merge override configuration into base configuration."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                # Recursively merge nested dictionaries
                self._merge_config(base[key], value)
            else:
                # Override or add new key
                base[key] = value

    def get_load_history(self) -> list[dict[str, Any]]:
        """Get the configuration load history."""
        return self.load_history.copy()

    def get_sources(self) -> list[ConfigSource]:
        """Get all configuration sources."""
        return self.sources.copy()


class ConfigTemplate:
    """Template for generating configuration files."""

    def __init__(self, name: str, description: str = "") -> None:
        """
        Initialize configuration template.

        Args:
            name: Template name
            description: Template description
        """
        self.name = name
        self.description = description
        self.sections: dict[str, dict[str, Any]] = {}

    def add_section(self, name: str, data: dict[str, Any], description: str = "") -> None:
        """
        Add a section to the template.

        Args:
            name: Section name
            data: Section data
            description: Section description
        """
        self.sections[name] = {"data": data, "description": description}

    def generate(self, format: ConfigFormat = ConfigFormat.YAML) -> str:
        """
        Generate configuration file content.

        Args:
            format: Output format

        Returns:
            Configuration file content
        """
        # Combine all sections
        config_data: dict[str, Any] = {}
        for section_name, section_info in self.sections.items():
            config_data[section_name] = section_info["data"]

        # Convert to requested format
        if format == ConfigFormat.JSON:
            return json.dumps(config_data, indent=2)
        elif format == ConfigFormat.YAML:
            if not YAML_AVAILABLE:
                raise ConfigLoadError(
                    "format",
                    "yaml",
                    "YAML support not available. Install PyYAML.",
                )
            return str(yaml.dump(config_data, default_flow_style=False, sort_keys=False))
        elif format == ConfigFormat.TOML:
            try:
                import tomli_w

                return str(tomli_w.dumps(config_data))
            except ImportError:
                try:
                    import toml

                    return str(toml.dumps(config_data))
                except ImportError as exc:
                    raise ConfigLoadError(
                        "format",
                        "toml",
                        "TOML support not available. Install tomli-w or toml.",
                    ) from exc
        else:
            raise ConfigLoadError(
                "format",
                format.value if isinstance(format, ConfigFormat) else str(format),
                "Unsupported format for template generation",
            )

    def save(self, path: str, format: ConfigFormat | None = None) -> None:
        """
        Save template to file.

        Args:
            path: Output file path
            format: Output format (auto-detected if None)
        """
        # Auto-detect format if not specified
        if not format:
            if path.endswith(".json"):
                format = ConfigFormat.JSON
            elif path.endswith((".yaml", ".yml")):
                format = ConfigFormat.YAML
            elif path.endswith(".toml"):
                format = ConfigFormat.TOML
            else:
                format = ConfigFormat.YAML  # Default to YAML

        # Generate content
        content = self.generate(format)

        # Write to file
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)


# Common configuration templates
def create_default_template() -> ConfigTemplate:
    """Create a default configuration template."""
    template = ConfigTemplate(name="default", description="Default Ariadne configuration")

    # Backend configuration
    template.add_section(
        name="backends",
        data={
            "default_backend": "qiskit",
            "fallback_enabled": True,
            "health_check_interval": 60.0,
            "pool_min_instances": 1,
            "pool_max_instances": 5,
        },
        description="Backend configuration settings",
    )

    # Logging configuration
    template.add_section(
        name="logging",
        data={
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "file": None,
            "console": True,
        },
        description="Logging configuration",
    )

    # Performance configuration
    template.add_section(
        name="performance",
        data={
            "cache_enabled": True,
            "cache_size": 100,
            "cache_ttl": 3600.0,
            "monitoring_enabled": True,
        },
        description="Performance settings",
    )

    return template


def create_development_template() -> ConfigTemplate:
    """Create a development configuration template."""
    template = ConfigTemplate(name="development", description="Development environment configuration")

    # Backend configuration
    template.add_section(
        name="backends",
        data={
            "default_backend": "qiskit",
            "fallback_enabled": True,
            "health_check_interval": 30.0,
            "pool_min_instances": 1,
            "pool_max_instances": 2,
        },
        description="Backend configuration for development",
    )

    # Logging configuration
    template.add_section(
        name="logging",
        data={
            "level": "DEBUG",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "file": None,
            "console": True,
        },
        description="Verbose logging for development",
    )

    # Performance configuration
    template.add_section(
        name="performance",
        data={
            "cache_enabled": True,
            "cache_size": 50,
            "cache_ttl": 1800.0,
            "monitoring_enabled": True,
        },
        description="Performance settings for development",
    )

    return template


def create_production_template() -> ConfigTemplate:
    """Create a production configuration template."""
    template = ConfigTemplate(name="production", description="Production environment configuration")

    # Backend configuration
    template.add_section(
        name="backends",
        data={
            "default_backend": "auto",
            "fallback_enabled": True,
            "health_check_interval": 60.0,
            "pool_min_instances": 2,
            "pool_max_instances": 10,
        },
        description="Backend configuration for production",
    )

    # Logging configuration
    template.add_section(
        name="logging",
        data={
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "file": "ariadne.log",
            "console": False,
        },
        description="Logging configuration for production",
    )

    # Performance configuration
    template.add_section(
        name="performance",
        data={
            "cache_enabled": True,
            "cache_size": 200,
            "cache_ttl": 7200.0,
            "monitoring_enabled": True,
        },
        description="Performance settings for production",
    )

    return template


# Global loader instance
_global_loader: ProgressiveConfigLoader | None = None


def get_config_loader() -> ProgressiveConfigLoader:
    """Get the global configuration loader."""
    global _global_loader
    if _global_loader is None:
        _global_loader = ProgressiveConfigLoader()
    return _global_loader


def load_config(
    environment: str | None = None,
    schema_name: str | None = None,
    config_paths: list[str] | None = None,
    env_prefix: str = "ARIADNE_",
) -> dict[str, Any]:
    """
    Load configuration using the global loader.

    Args:
        environment: Environment to load configuration for
        schema_name: Schema name to validate against
        config_paths: List of configuration file paths
        env_prefix: Environment variable prefix

    Returns:
        Loaded configuration
    """
    loader = get_config_loader()

    # Add default sources
    loader.add_env_source(prefix=env_prefix, priority=10)

    # Add file sources
    if config_paths:
        for path in config_paths:
            if os.path.exists(path):
                loader.add_file_source(path, priority=20)

    # Load configuration
    return loader.load(environment=environment, schema_name=schema_name)
