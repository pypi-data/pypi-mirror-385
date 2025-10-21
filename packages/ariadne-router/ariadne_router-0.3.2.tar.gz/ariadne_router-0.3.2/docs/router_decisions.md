**How We Decide Which Simulator To Use (Enhanced Router)**

Ariadne now uses a two-phase routing architecture to minimize latency and maximize extensibility, ensuring the fastest possible backend is selected first.

### Phase 1: Prioritized Filter Chain (Specialized Triage)

This phase runs a sequence of fast, specialized checks. If a circuit matches a specialized backend's criteria, routing terminates immediately, avoiding the overhead of full circuit analysis and scoring.

1.  **STIM Check (Highest Priority):** Is the circuit purely Clifford? If yes, select STIM.
2.  **MPS Check (High Priority):** Is the circuit small and low-entanglement (using `mps_analyzer.should_use_mps`)? If yes, select MPS.
3.  **Future Specialized Checks:** New specialized backends (e.g., Stabilizer) can be added here without modifying core scoring logic.

### Phase 2: General Backend Scoring (Strategy Pattern)

If Phase 1 yields no specialized match, the router proceeds to multi-objective scoring using the full circuit analysis.

1.  **Full Analysis:** The circuit is analyzed for comprehensive metrics (e.g., treewidth, gate entropy).
2.  **Strategy Application:** The selected routing strategy (e.g., `HybridOptimizerStrategy`) scores all available general backends (Tensor Network, CUDA, Qiskit, DDSIM, JAX_METAL) based on user preferences (speed, accuracy, memory).
3.  **Optimal Selection:** The backend with the highest weighted score is selected.

This architecture ensures **low latency** for specialized circuits and **high extensibility** for future backends.

---

Logging and Segmentation details remain as previously defined.
