# 06_mps_entanglement_demo.py
# Richard Feynman's Demonstration: Entanglement Scaling and MPS Efficiency

"""
A visual demonstration of why Matrix Product States (MPS) are the right tool
for simulating quantum circuits with low entanglement, based on the scaling
of the required bond dimension (D) versus the number of qubits (N).

In MPS, the computational cost scales polynomially with N but exponentially
with the maximum bond dimension D. Therefore, if D scales poorly with N,
MPS loses its advantage.
"""

import matplotlib.pyplot as plt
import numpy as np

# --- 1. Define the range of qubits (N) ---
# We choose a range where the difference in scaling becomes visually apparent.
N_qubits = np.arange(4, 20, 2)

# --- 2. Scenario A: High Entanglement Proxy (Exponential Scaling) ---
# This models a deep, random, or highly non-local circuit (e.g., a Quantum Fourier Transform)
# where entanglement grows rapidly, requiring an exponentially increasing bond dimension.
# D ~ 2^(N/2) is the theoretical maximum required bond dimension for a bipartition.
D_high_entanglement = 2 ** (N_qubits / 2)

# --- 3. Scenario B: Low Entanglement Proxy (Linear Scaling) ---
# This models a shallow circuit or one composed primarily of local operations
# (e.g., a 1D nearest-neighbor circuit) where entanglement is bounded or grows slowly.
# We model this as D ~ N (linear scaling).
D_low_entanglement = N_qubits

# --- 4. Visualization (The 'Aha!' Moment) ---

plt.figure(figsize=(10, 6))

# Plot Scenario A (Exponential)
plt.plot(
    N_qubits,
    D_high_entanglement,
    "ro-",
    label=r"Scenario A: High Entanglement ($D \propto 2^{N/2}$)",
)

# Plot Scenario B (Linear)
plt.plot(N_qubits, D_low_entanglement, "bs-", label=r"Scenario B: Low Entanglement ($D \propto N$)")

# Add a practical limit for D (e.g., D=1000 is often a practical limit for fast simulation)
D_limit = 1000
plt.axhline(y=D_limit, color="k", linestyle="--", alpha=0.6, label=f"Practical MPS Limit (D={D_limit})")

plt.yscale("log")  # Use a logarithmic scale for the y-axis to clearly show the exponential growth
plt.title("Required MPS Bond Dimension (D) vs. Number of Qubits (N)")
plt.xlabel("Number of Qubits (N)")
plt.ylabel("Required Bond Dimension (D) [Log Scale]")
plt.legend()
plt.grid(True, which="both", ls="--", alpha=0.7)
plt.tight_layout()

# Save the plot to a file (optional, but good practice for examples)
plt.savefig("mps_entanglement_scaling_demo.png")

# Show the plot (commented out for non-interactive environments, but useful for local execution)
# plt.show()

# --- 5. Feynman's Explanation ---
print("\n" + "=" * 80)
print("Feynman's Intuition: Why MPS is a 'Good Trick' for Low Entanglement")
print("=" * 80)
print("Observe the graph, my friends. It is a picture of computational reality.")
print("\nScenario A (High Entanglement):")
print("The required bond dimension D explodes exponentially with the number of qubits N.")
print("This means that even a modest increase in N quickly pushes D past any practical limit (D=1000).")
print("The computational cost of MPS, which scales as poly(N) * poly(D), becomes dominated by D,")
print("making the simulation impossible, just like a full state vector simulation.")

print("\nScenario B (Low Entanglement):")
print("The required bond dimension D grows only linearly with N. It stays far below the practical limit.")
print("In this regime, the MPS simulation cost remains polynomial in N and constant/polynomial in D.")
print("This is the 'sweet spot' where MPS provides an exponential speedup over full state vector methods.")
print("Our heuristic 'should_use_mps' is designed to detect circuits that fall into this Scenario B.")
print("It's not magic; it's physics: low entanglement means low information redundancy, which MPS exploits.")
print("The universe is not always maximally entangled, and that's our computational opportunity!")
print("=" * 80)
