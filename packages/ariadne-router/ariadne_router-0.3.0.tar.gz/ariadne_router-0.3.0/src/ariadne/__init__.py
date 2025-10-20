"""Ariadne: intelligent quantum circuit routing."""

from ._version import __version__

__all__ = ["__version__"]

# Configuration system data classes
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

# Core systems - always available
from .core import (
    AriadneError,
    BackendUnavailableError,
    CircuitAnalysisCache,
    CircuitTooLargeError,
    ResourceExhaustionError,
    ResourceManager,
    SimulationError,
    configure_logging,
    get_logger,
    get_resource_manager,
)

# Enhanced router
from .route.enhanced_router import EnhancedQuantumRouter

# Comprehensive routing tree (internal use)
from .route.routing_tree import ComprehensiveRoutingTree, explain_routing, show_routing_tree

# Main simulation interface
from .router import simulate
from .types import BackendCapacity, BackendType, RoutingDecision, SimulationResult

# Create alias for backward compatibility
QuantumRouter = EnhancedQuantumRouter

# Optional backends - may not be available
try:
    from .backends.cuda_backend import CUDABackend, get_cuda_info, simulate_cuda

    _CUDA_AVAILABLE = True
except ImportError:
    _CUDA_AVAILABLE = False
    from typing import Any

    CUDABackend: Any = None
    get_cuda_info: Any = None
    simulate_cuda: Any = None

try:
    from .backends.metal_backend import MetalBackend, get_metal_info, simulate_metal

    _METAL_AVAILABLE = True
except ImportError:
    _METAL_AVAILABLE = False
    from typing import Any

    MetalBackend: Any = None
    get_metal_info: Any = None
    simulate_metal: Any = None

__all__ = [
    # Core functionality
    "simulate",
    "BackendType",
    "RoutingDecision",
    "SimulationResult",
    "BackendCapacity",
    "EnhancedQuantumRouter",
    "QuantumRouter",  # Alias for backward compatibility
    # Advanced routing (for power users)
    "ComprehensiveRoutingTree",
    "explain_routing",
    "show_routing_tree",
    # Configuration system
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
    # Error handling
    "AriadneError",
    "BackendUnavailableError",
    "CircuitTooLargeError",
    "ResourceExhaustionError",
    "SimulationError",
    # Core systems
    "CircuitAnalysisCache",
    "ResourceManager",
    "get_logger",
    "get_resource_manager",
    "configure_logging",
]

# Add optional backends if available
if _CUDA_AVAILABLE:
    __all__.extend(
        [
            "CUDABackend",
            "simulate_cuda",
            "get_cuda_info",
        ]
    )

if _METAL_AVAILABLE:
    __all__.extend(
        [
            "MetalBackend",
            "simulate_metal",
            "get_metal_info",
        ]
    )
