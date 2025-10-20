# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2025-10-17

### Added

-   **Comprehensive Routing Tree**: Introduced `ariadne.ComprehensiveRoutingTree`, a new, powerful way to control and inspect routing decisions.
-   **Advanced Routing Strategies**: Added new routing strategies like `SPEED_FIRST`, `MEMORY_EFFICIENT`, `CLIFFORD_OPTIMIZED`, `APPLE_SILICON_OPTIMIZED`, and `CUDA_OPTIMIZED`.
-   **Routing Explanations**: Added `ariadne.explain_routing` to provide detailed, human-readable explanations for routing decisions.
-   **Routing Visualization**: Added `ariadne.show_routing_tree` to visualize the entire routing decision tree.

### Changed

-   **Public API**: `ariadne.ComprehensiveRoutingTree` is now the recommended entry point for advanced routing control. `QuantumRouter` is maintained as an alias for backward compatibility.
-   **Documentation**: Updated `README.md` and other documentation to reflect the new routing system.

## [0.1.0] - 2025-10-15

- macOS-first launch; Apple Silicon supported via Metal (falls back to CPU gracefully).
- Automatic backend routing:
  - Clifford → Stim
  - Low entanglement → MPS
  - Apple Silicon → Metal (when available)
  - General → Qiskit (CPU)
- CLI wired to `ariadne.cli.main:main`; `ariadne --help` now exposes subcommands.
- Fixed Metal backend sampling without JAX by converting statevector to NumPy.
- Docs: added Use Cases and Routing Matrix to README; added routing rules page and examples gallery.
- Packaging verified: `python -m build` and `twine check` pass.
- Docker: development and production stages updated for editable and standard installs.
