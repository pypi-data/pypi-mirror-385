# Ariadne Benchmark Report
**Timestamp:** 2025-09-27 10:12:19
**Environment:** macOS-26.0-arm64-arm-64bit
**Tests:** 13/13 passed

**Average execution time:** 0.0150s
## Backend Usage
- **jax_metal:** 4 circuits (30.8%)
- **stim:** 9 circuits (69.2%)
## Detailed Results
| Circuit | Backend | Time (s) | Status |
|---------|---------|----------|--------|
| small_clifford_ghz | stim | 0.0220 | ✅ Pass |
| small_clifford_ladder | stim | 0.0097 | ✅ Pass |
| medium_clifford_ghz | stim | 0.0139 | ✅ Pass |
| medium_clifford_stabilizer | stim | 0.0156 | ✅ Pass |
| large_clifford_ghz | stim | 0.0343 | ✅ Pass |
| large_clifford_surface_code | stim | 0.0521 | ✅ Pass |
| small_non_clifford | jax_metal | 0.0069 | ✅ Pass |
| medium_non_clifford | jax_metal | 0.0197 | ✅ Pass |
| mixed_vqe_ansatz | jax_metal | 0.0074 | ✅ Pass |
| mixed_qaoa | jax_metal | 0.0068 | ✅ Pass |
| single_qubit | stim | 0.0018 | ✅ Pass |
| no_gates | stim | 0.0024 | ✅ Pass |
| measurement_only | stim | 0.0025 | ✅ Pass |
