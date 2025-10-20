"""
Backend Preference and Configuration System

This module provides comprehensive configuration management for Ariadne's
quantum simulation platform, including backend preferences, optimization
settings, and hardware-specific configurations.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import yaml


class ConfigFormat(Enum):
    """Supported configuration file formats."""

    JSON = "json"
    YAML = "yaml"
    TOML = "toml"


@dataclass
class BackendConfig:
    """Configuration for a specific backend."""

    # Priority and preference
    priority: int = 5  # 1-10 scale, higher = more preferred
    enabled: bool = True

    # Performance tuning
    capacity_boost: float = 1.0
    memory_limit_mb: int | None = None
    timeout_seconds: float | None = None

    # Hardware-specific options
    device_id: int = 0
    use_gpu: bool = True

    # Backend-specific parameters
    custom_options: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BackendConfig:
        """Create from dictionary."""
        custom_options = data.pop("custom_options", {})
        config = cls(**data)
        config.custom_options = custom_options
        return config


@dataclass
class OptimizationConfig:
    """Circuit optimization configuration."""

    # Optimization levels
    default_level: int = 2  # 0-3 scale
    enable_synthesis: bool = True
    enable_commutation_analysis: bool = True
    enable_gate_fusion: bool = True

    # Transpiler options
    basis_gates: list[str] | None = None
    coupling_map: list[list[int]] | None = None
    seed_transpiler: int | None = None

    # Advanced options
    max_optimization_passes: int = 100
    optimization_timeout: float = 30.0


@dataclass
class ErrorMitigationConfig:
    """Error mitigation configuration."""

    # Mitigation techniques
    enable_zne: bool = False
    enable_cdr: bool = False
    enable_symmetry_verification: bool = False

    # ZNE parameters
    zne_noise_factors: list[float] = field(default_factory=lambda: [1.0, 1.5, 2.0])
    zne_extrapolation_method: str = "linear"

    # CDR parameters
    cdr_clifford_fraction: float = 0.1
    cdr_num_training_circuits: int = 100


@dataclass
class AnalysisConfig:
    """Circuit analysis configuration."""

    # Analysis options
    enable_quantum_advantage_detection: bool = True
    enable_resource_estimation: bool = True
    enable_performance_prediction: bool = True

    # Quantum advantage thresholds
    advantage_confidence_threshold: float = 0.7
    classical_intractability_threshold: int = 30  # qubits

    # Resource estimation options
    include_fault_tolerant_estimates: bool = False
    target_error_rate: float = 1e-6


@dataclass
class PerformanceConfig:
    """Performance and monitoring configuration."""

    # Caching
    enable_result_caching: bool = True
    cache_size_mb: int = 1024
    cache_ttl_hours: int = 24

    # Monitoring
    enable_performance_tracking: bool = True
    enable_calibration: bool = True
    calibration_interval_simulations: int = 10

    # Memory management
    memory_pool_size_mb: int = 4096
    enable_memory_mapping: bool = True
    cleanup_interval_minutes: int = 30


@dataclass
class AriadneConfig:
    """Complete Ariadne configuration."""

    # Backend configurations
    backends: dict[str, BackendConfig] = field(default_factory=dict)

    # Component configurations
    optimization: OptimizationConfig = field(default_factory=OptimizationConfig)
    error_mitigation: ErrorMitigationConfig = field(default_factory=ErrorMitigationConfig)
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)

    # Global settings
    default_shots: int = 1000
    random_seed: int | None = None
    log_level: str = "INFO"

    # Paths
    cache_dir: str | None = None
    data_dir: str | None = None

    def __post_init__(self) -> None:
        """Initialize default backend configurations."""
        if not self.backends:
            self._initialize_default_backends()

    def _initialize_default_backends(self) -> None:
        """Initialize default backend configurations."""
        self.backends = {
            "stim": BackendConfig(
                priority=9,  # Highest priority for Clifford circuits
                enabled=True,
                capacity_boost=1.0,
                custom_options={"tableau_method": "auto", "allow_measurement": True},
            ),
            "metal": BackendConfig(
                priority=8,  # High priority for Apple Silicon
                enabled=True,
                capacity_boost=1.7,  # Measured speedup
                use_gpu=True,
                custom_options={
                    "enable_unified_memory": True,
                    "enable_metal_shaders": True,
                    "memory_pool_size_mb": 2048,
                },
            ),
            "cuda": BackendConfig(
                priority=7,  # High priority for NVIDIA GPUs
                enabled=True,
                capacity_boost=2.0,
                use_gpu=True,
                custom_options={"enable_multi_gpu": False, "memory_pool_fraction": 0.8},
            ),
            "tensor_network": BackendConfig(
                priority=6,  # Good for structured circuits
                enabled=True,
                capacity_boost=1.0,
                custom_options={"contraction_method": "auto", "max_bond_dimension": 1024},
            ),
            "qiskit": BackendConfig(
                priority=3,  # Fallback option
                enabled=True,
                capacity_boost=1.0,
                custom_options={"method": "statevector"},
            ),
            "ddsim": BackendConfig(
                priority=5,  # Medium priority
                enabled=True,
                capacity_boost=1.0,
                custom_options={"mode": "dd"},
            ),
        }

    def get_backend_priority_list(self) -> list[str]:
        """Get backends sorted by priority (highest first)."""
        enabled_backends = {name: config for name, config in self.backends.items() if config.enabled}

        return sorted(enabled_backends.keys(), key=lambda name: enabled_backends[name].priority, reverse=True)

    def update_backend_config(self, backend_name: str, **kwargs: Any) -> None:
        """Update configuration for a specific backend."""
        if backend_name not in self.backends:
            self.backends[backend_name] = BackendConfig()

        config = self.backends[backend_name]
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
            else:
                config.custom_options[key] = value

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "backends": {name: config.to_dict() for name, config in self.backends.items()},
            "optimization": asdict(self.optimization),
            "error_mitigation": asdict(self.error_mitigation),
            "analysis": asdict(self.analysis),
            "performance": asdict(self.performance),
            "default_shots": self.default_shots,
            "random_seed": self.random_seed,
            "log_level": self.log_level,
            "cache_dir": self.cache_dir,
            "data_dir": self.data_dir,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AriadneConfig:
        """Create configuration from dictionary."""
        # Extract backend configs
        backend_data = data.pop("backends", {})
        backends = {name: BackendConfig.from_dict(config_data) for name, config_data in backend_data.items()}

        # Extract component configs
        optimization_data = data.pop("optimization", {})
        error_mitigation_data = data.pop("error_mitigation", {})
        analysis_data = data.pop("analysis", {})
        performance_data = data.pop("performance", {})

        # Create main config
        config = cls(
            backends=backends,
            optimization=OptimizationConfig(**optimization_data),
            error_mitigation=ErrorMitigationConfig(**error_mitigation_data),
            analysis=AnalysisConfig(**analysis_data),
            performance=PerformanceConfig(**performance_data),
            **data,
        )

        return config


class ConfigManager:
    """Configuration manager for Ariadne."""

    def __init__(self, config_file: Path | None = None) -> None:
        """Initialize configuration manager."""
        self.config_file = config_file or self._get_default_config_path()
        self.config = AriadneConfig()

        # Load configuration if file exists
        if self.config_file.exists():
            self.load_config()

    def _get_default_config_path(self) -> Path:
        """Get default configuration file path."""
        # Check for config in various standard locations
        possible_paths = [
            Path.cwd() / "ariadne.yaml",
            Path.cwd() / "ariadne.json",
            Path.home() / ".ariadne" / "config.yaml",
            Path.home() / ".config" / "ariadne" / "config.yaml",
        ]

        for path in possible_paths:
            if path.exists():
                return path

        # Default to user config directory
        config_dir = Path.home() / ".ariadne"
        config_dir.mkdir(exist_ok=True)
        return config_dir / "config.yaml"

    def load_config(self, file_path: Path | None = None) -> None:
        """Load configuration from file."""
        file_path = file_path or self.config_file

        if not file_path.exists():
            return

        try:
            with open(file_path) as f:
                if file_path.suffix.lower() == ".json":
                    data = json.load(f)
                elif file_path.suffix.lower() in [".yaml", ".yml"]:
                    data = yaml.safe_load(f)
                else:
                    raise ValueError(f"Unsupported config format: {file_path.suffix}")

            self.config = AriadneConfig.from_dict(data)

        except Exception as e:
            print(f"Warning: Failed to load config from {file_path}: {e}")
            print("Using default configuration.")

    def save_config(self, file_path: Path | None = None) -> None:
        """Save configuration to file."""
        file_path = file_path or self.config_file

        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            data = self.config.to_dict()

            with open(file_path, "w") as f:
                if file_path.suffix.lower() == ".json":
                    json.dump(data, f, indent=2)
                elif file_path.suffix.lower() in [".yaml", ".yml"]:
                    yaml.dump(data, f, default_flow_style=False, indent=2)
                else:
                    # Default to YAML
                    yaml.dump(data, f, default_flow_style=False, indent=2)

            print(f"Configuration saved to {file_path}")

        except Exception as e:
            print(f"Error saving config to {file_path}: {e}")

    def get_backend_config(self, backend_name: str) -> BackendConfig | None:
        """Get configuration for a specific backend."""
        return self.config.backends.get(backend_name)

    def set_backend_preference(self, backend_name: str, priority: int) -> None:
        """Set priority for a backend."""
        self.config.update_backend_config(backend_name, priority=priority)

    def enable_backend(self, backend_name: str, enabled: bool = True) -> None:
        """Enable or disable a backend."""
        self.config.update_backend_config(backend_name, enabled=enabled)

    def get_preferred_backends(self) -> list[str]:
        """Get list of backends in preference order."""
        return self.config.get_backend_priority_list()

    def configure_for_platform(self, platform: str = "auto") -> None:
        """Configure settings for specific platform."""
        if platform == "auto":
            platform = self._detect_platform()

        if platform == "apple_silicon":
            self._configure_for_apple_silicon()
        elif platform == "nvidia_gpu":
            self._configure_for_nvidia_gpu()
        elif platform == "cpu_only":
            self._configure_for_cpu_only()

    def _detect_platform(self) -> str:
        """Auto-detect platform type."""
        import platform

        # Check for Apple Silicon
        if platform.system() == "Darwin" and platform.machine() in ["arm64", "aarch64"]:
            return "apple_silicon"

        # Check for NVIDIA GPU
        try:
            import cupy

            if cupy.cuda.runtime.getDeviceCount() > 0:
                return "nvidia_gpu"
        except (ImportError, Exception):
            pass

        return "cpu_only"

    def _configure_for_apple_silicon(self) -> None:
        """Optimize configuration for Apple Silicon."""
        # Prioritize Metal backend
        self.config.update_backend_config("metal", priority=9, enabled=True)
        self.config.update_backend_config("stim", priority=10)  # Still highest for Clifford

        # Configure Metal-specific options
        self.config.update_backend_config(
            "metal", enable_unified_memory=True, enable_metal_shaders=True, memory_pool_size_mb=4096
        )

        # Disable CUDA
        self.config.update_backend_config("cuda", enabled=False)

    def _configure_for_nvidia_gpu(self) -> None:
        """Optimize configuration for NVIDIA GPU systems."""
        # Prioritize CUDA backend
        self.config.update_backend_config("cuda", priority=9, enabled=True)
        self.config.update_backend_config("stim", priority=10)  # Still highest for Clifford

        # Configure CUDA-specific options
        self.config.update_backend_config("cuda", enable_multi_gpu=True, memory_pool_fraction=0.9)

        # Lower priority for Metal
        self.config.update_backend_config("metal", priority=3)

    def _configure_for_cpu_only(self) -> None:
        """Optimize configuration for CPU-only systems."""
        # Disable GPU backends
        self.config.update_backend_config("metal", enabled=False)
        self.config.update_backend_config("cuda", enabled=False)

        # Prioritize CPU-efficient backends
        self.config.update_backend_config("stim", priority=10)
        self.config.update_backend_config("tensor_network", priority=8)
        self.config.update_backend_config("qiskit", priority=6)

    def create_template_config(self, file_path: Path) -> None:
        """Create a template configuration file with comments."""
        template = {
            "# Ariadne Quantum Simulation Configuration": None,
            "# Backend configurations": None,
            "backends": {
                "stim": {
                    "priority": 10,
                    "enabled": True,
                    "capacity_boost": 1.0,
                    "# Stim is perfect for Clifford circuits": None,
                    "custom_options": {"tableau_method": "auto"},
                },
                "metal": {
                    "priority": 8,
                    "enabled": True,
                    "capacity_boost": 1.7,
                    "use_gpu": True,
                    "# Apple Silicon optimizations": None,
                    "custom_options": {"enable_unified_memory": True, "enable_metal_shaders": True},
                },
            },
            "# Circuit optimization settings": None,
            "optimization": {
                "default_level": 2,
                "enable_synthesis": True,
                "max_optimization_passes": 100,
            },
            "# Performance settings": None,
            "performance": {
                "enable_result_caching": True,
                "cache_size_mb": 1024,
                "enable_calibration": True,
            },
            "# Global settings": None,
            "default_shots": 1000,
            "log_level": "INFO",
        }

        # Filter out comment entries for actual saving
        clean_template = {k: v for k, v in template.items() if not k.startswith("#")}

        with open(file_path, "w") as f:
            yaml.dump(clean_template, f, default_flow_style=False, indent=2)


# Global configuration manager instance
_config_manager: ConfigManager | None = None


def get_config() -> AriadneConfig:
    """Get the global configuration."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager.config


def get_config_manager() -> ConfigManager:
    """Get the global configuration manager."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def configure_ariadne(config_file: Path | None = None) -> None:
    """Initialize Ariadne with configuration file."""
    global _config_manager
    _config_manager = ConfigManager(config_file)


# Convenience functions
def set_backend_preference(backend_name: str, priority: int) -> None:
    """Set backend preference globally."""
    get_config_manager().set_backend_preference(backend_name, priority)


def get_preferred_backends() -> list[str]:
    """Get globally preferred backends."""
    return get_config_manager().get_preferred_backends()


def save_config(file_path: Path | None = None) -> None:
    """Save global configuration."""
    get_config_manager().save_config(file_path)
