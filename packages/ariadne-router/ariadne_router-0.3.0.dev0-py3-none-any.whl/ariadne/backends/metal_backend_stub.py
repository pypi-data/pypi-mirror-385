"""
Metal/JAX Backend for Ariadne (Mac Development Stub)

This is a placeholder for the Metal backend that will be implemented
on the Mac development branch. The actual implementation will use
JAX with Metal acceleration on Apple Silicon.
"""

from typing import Any

from qiskit import QuantumCircuit


class MetalBackend:
    """
    Placeholder for Metal/JAX accelerated backend on Apple Silicon.

    This backend will be implemented on the metal-development branch
    and tested on M4 Mac hardware.
    """

    def __init__(self, device: str | None = None) -> None:
        """
        Initialize Metal backend.

        Args:
            device: Optional device specification (e.g., "gpu:0")
        """
        self.device = device or "cpu"
        self.backend_name = "metal"

        # Check if running on Apple Silicon
        import platform

        self.is_apple_silicon = platform.system() == "Darwin" and platform.machine() in [
            "arm64",
            "aarch64",
        ]

        if not self.is_apple_silicon:
            raise RuntimeError(
                "Metal backend requires Apple Silicon (M1/M2/M3/M4). "
                "Use metal-development branch on Mac for implementation."
            )

    def simulate(self, circuit: QuantumCircuit, shots: int = 1024) -> dict[str, int]:
        """
        Simulate quantum circuit using JAX with Metal acceleration.

        Args:
            circuit: Quantum circuit to simulate
            shots: Number of measurement shots

        Returns:
            Dictionary of measurement counts
        """
        raise NotImplementedError(
            "Metal backend implementation pending. Please use metal-development branch on Mac hardware."
        )

    def get_device_info(self) -> dict[str, Any]:
        """Get information about Metal device."""
        return {
            "backend": "metal",
            "status": "not_implemented",
            "message": "Implementation on metal-development branch",
            "is_apple_silicon": self.is_apple_silicon,
        }


# Placeholder for JAX backend
class JAXBackend:
    """
    Placeholder for JAX-based quantum simulation.

    Will provide GPU acceleration on both NVIDIA and Apple Silicon.
    """

    def __init__(self) -> None:
        raise NotImplementedError(
            "JAX backend pending implementation. Use metal-development branch for Apple Silicon support."
        )
