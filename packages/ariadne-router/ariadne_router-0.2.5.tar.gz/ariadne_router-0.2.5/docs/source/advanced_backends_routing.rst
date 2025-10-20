Advanced Backends and Routing
=============================

Ariadne utilizes a sophisticated two-phase routing architecture designed to minimize latency and maximize extensibility, ensuring the fastest possible backend is selected first.

Phase 1: Prioritized Filter Chain (Specialized Triage)
-----------------------------------------------------

This phase runs a sequence of fast, specialized checks. If a circuit matches a specialized backend's criteria, routing terminates immediately, avoiding the overhead of full circuit analysis and scoring.

1. **STIM Check (Highest Priority):** Is the circuit purely Clifford? If yes, select STIM.
2. **MPS Check (High Priority):** Is the circuit small and low-entanglement (using :py:func:`ariadne.route.mps_analyzer.should_use_mps`)? If yes, select MPS.
3. **Future Specialized Checks:** New specialized backends (e.g., Stabilizer) can be added here without modifying core scoring logic.

Phase 2: General Backend Scoring (Strategy Pattern)
--------------------------------------------------

If Phase 1 yields no specialized match, the router proceeds to multi-objective scoring using the full circuit analysis.

1. **Full Analysis:** The circuit is analyzed for comprehensive metrics (e.g., treewidth, gate entropy).
2. **Strategy Application:** The selected routing strategy (e.g., ``HybridOptimizerStrategy``) scores all available general backends (Tensor Network, CUDA, Qiskit, DDSIM, JAX_METAL) based on user preferences (speed, accuracy, memory).
3. **Optimal Selection:** The backend with the highest weighted score is selected.

This architecture ensures **low latency** for specialized circuits and **high extensibility** for future backends.

The Necessity of Low Entanglement for MPS Efficiency
---------------------------------------------------

The Matrix Product State (MPS) backend is a powerful tool for simulating quantum circuits, but its efficiency is fundamentally tied to the circuit's entanglement structure.

As explained in the implementation of :py:func:`ariadne.route.mps_analyzer.should_use_mps`, the core physical intuition is the **Area Law**. While a system of N qubits lives in an exponentially large Hilbert space ($2^N$), most physically relevant states are *sparse* in a way that limits the entanglement between two halves of the system.

MPS exploits this by representing the quantum state as a chain of matrices. The size of these matrices, known as the **bond dimension** ($D$), determines the maximum entanglement the state can represent.

*   **Low Entanglement:** If the entanglement is low (e.g., constant or logarithmic in the number of qubits $N$), the required bond dimension $D$ is small, and the simulation scales polynomially with $N$. This is the ideal scenario for MPS.
*   **High Entanglement:** If the circuit generates high entanglement, $D$ must grow exponentially with $N$, causing the MPS simulation to revert to exponential scaling, defeating its purpose.

The :py:func:`ariadne.route.mps_analyzer.should_use_mps` function uses a heuristic to check for low entanglement, specifically by limiting the number of two-qubit gates (which generate entanglement) relative to the system size ($N < 15$ and two-qubit gates $< 2 \cdot N^{1.5}$).

.. literalinclude:: ../../src/ariadne/route/mps_analyzer.py
   :language: python
   :lines: 6-40
   :caption: Excerpt from mps_analyzer.py explaining the MPS intuition.

Interpreting the Router Decision Visualization
---------------------------------------------

The router provides a detailed, step-by-step log of its decision process via the :py:func:`ariadne.visualization.visualize_decision` function. This output is crucial for understanding why a specific backend was chosen.

The visualization is structured as a sequence of checks performed by the router's filter chain (Phase 1) and scoring mechanism (Phase 2).

Each step in the ``decision_path`` list (provided to the function) is displayed with three key pieces of information:

1.  **Analyzer:** The name of the specialized check or general scoring strategy being executed (e.g., ``STIM Check``, ``MPS Check``, ``General Backend Scoring``).
2.  **Result:** A detailed description of the outcome of the analysis (e.g., ``Circuit is purely Clifford. ROUTE IMMEDIATELY.``, ``Circuit is too large or highly entangled. PASS to next check.``).
3.  **Decision:** The router's action based on the result:
    *   ``ROUTE IMMEDIATELY``: A specialized backend was found, and routing stops here.
    *   ``CONTINUE CHAIN``: The circuit did not match the specialized criteria, proceeding to the next check in Phase 1.
    *   ``REJECT BACKEND``: (Typically seen in Phase 2 scoring) A backend was deemed unsuitable based on resource constraints or performance metrics.
    *   ``ANALYSIS COMPLETE``: The final decision has been made, usually leading to the selection of the optimal general backend.

The output concludes with the ``FINAL BACKEND`` selected and the ``PERFORMANCE GAIN`` estimate, quantifying the benefit of the chosen route.
