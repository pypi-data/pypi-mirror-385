# Router Benchmark Summary

| Case | Category | Qubits | Router Backend | Backend | Mean (ms) | Std (ms) | Reps | Status |
|---|---|---|---|---|---|---|---|---|
| ghz_chain_10 | clifford | 10 | stim | ariadne_router | 17.87 | 10.41 | 3 | OK |
| ghz_chain_10 | clifford | 10 | stim | qiskit_basic | 1.47 | 0.88 | 3 | OK |
| ghz_chain_10 | clifford | 10 | stim | stim | 9.43 | 0.27 | 3 | OK |
| ghz_chain_10 | clifford | 10 | stim | tensor_network | 882.28 | 911.99 | 3 | OK |
| random_clifford_12 | clifford | 12 | stim | ariadne_router | 339.33 | 236.00 | 3 | OK |
| random_clifford_12 | clifford | 12 | stim | qiskit_basic | 13.16 | 5.57 | 3 | OK |
| random_clifford_12 | clifford | 12 | stim | stim | 61.39 | 1.00 | 3 | OK |
| random_clifford_12 | clifford | 12 | stim | tensor_network | 141.17 | 50.43 | 3 | OK |
| random_nonclifford_8 | non_clifford | 8 | tensor_network | ariadne_router | 110.61 | 35.90 | 3 | OK |
| random_nonclifford_8 | non_clifford | 8 | tensor_network | qiskit_basic | 1.65 | 0.08 | 3 | OK |
| random_nonclifford_8 | non_clifford | 8 | tensor_network | tensor_network | 62.34 | 18.46 | 3 | OK |
| qaoa_maxcut_8_p3 | algorithmic | 8 | tensor_network | ariadne_router | 67.65 | 18.72 | 3 | OK |
| qaoa_maxcut_8_p3 | algorithmic | 8 | tensor_network | qiskit_basic | 1.34 | 0.08 | 3 | OK |
| qaoa_maxcut_8_p3 | algorithmic | 8 | tensor_network | tensor_network | 80.03 | 30.07 | 3 | OK |
| vqe_ansatz_12 | algorithmic | 12 | tensor_network | ariadne_router | 68.31 | 20.70 | 3 | OK |
| vqe_ansatz_12 | algorithmic | 12 | tensor_network | qiskit_basic | 5.03 | 0.10 | 3 | OK |
| vqe_ansatz_12 | algorithmic | 12 | tensor_network | tensor_network | 63.15 | 18.27 | 3 | OK |
