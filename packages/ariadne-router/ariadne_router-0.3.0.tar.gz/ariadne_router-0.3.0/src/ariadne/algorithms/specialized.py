"""
Specialized quantum algorithms in Ariadne.

This module contains specialized quantum algorithms that demonstrate
specific quantum phenomena and algorithmic techniques.
"""

from qiskit import QuantumCircuit

from .base import AlgorithmMetadata, QuantumAlgorithm


class DeutschJozsa(QuantumAlgorithm):
    """Deutsch-Jozsa algorithm for distinguishing constant vs balanced functions."""

    @property
    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            name="Deutsch-Jozsa",
            description="Determines whether a function is constant or balanced with one query",
            category="specialized",
            tags=["deutsch_jozsa", "oracle", "constant_balanced", "black_box"],
            min_qubits=2,
            complexity="low",
            classical_complexity="O(2^(n-1) + 1)",
            quantum_advantage=True,
            educational_value="high",
            use_cases=["oracle complexity", "algorithmic separation", "quantum advantage demonstration"],
            references=["Deutsch, D., Jozsa, R. (1992). 'Rapid solution of problems by quantum computation'"],
        )

    def create_circuit(self) -> QuantumCircuit:
        """Create a Deutsch-Jozsa circuit."""
        circuit = QuantumCircuit(self.params.n_qubits, self.params.n_qubits)

        # Get function type (constant or balanced)
        function_type = self.params.custom_params.get("function_type", "balanced")

        # Initialize last qubit to |1⟩ and apply Hadamard
        circuit.x(self.params.n_qubits - 1)
        circuit.h(self.params.n_qubits - 1)

        # Apply Hadamard to input qubits
        for i in range(self.params.n_qubits - 1):
            circuit.h(i)

        # Apply oracle
        self._apply_deutsch_jozsa_oracle(circuit, function_type)

        # Apply Hadamard to input qubits
        for i in range(self.params.n_qubits - 1):
            circuit.h(i)

        circuit.measure_all()
        return circuit

    def _apply_deutsch_jozsa_oracle(self, circuit: QuantumCircuit, function_type: str) -> None:
        """Apply the Deutsch-Jozsa oracle."""
        if function_type == "constant_0":
            # Constant function f(x) = 0
            pass  # Do nothing
        elif function_type == "constant_1":
            # Constant function f(x) = 1
            circuit.x(self.params.n_qubits - 1)
        elif function_type == "balanced":
            # Balanced function: f(x) = x_0 (first input bit)
            circuit.cx(0, self.params.n_qubits - 1)
        else:
            # Another balanced function: parity of all input bits
            for i in range(self.params.n_qubits - 1):
                circuit.cx(i, self.params.n_qubits - 1)

    def _get_mathematical_background(self) -> str:
        return """
        The Deutsch-Jozsa algorithm distinguishes constant vs balanced functions:

        Problem: Given black-box function f: {0,1}^n → {0,1}, determine if f is:
        - Constant: f(x) is the same for all inputs
        - Balanced: f(x) = 0 for exactly half the inputs, 1 for the other half

        Classical solution requires O(2^(n-1) + 1) queries in worst case
        Quantum solution requires only 1 query

        Algorithm:
        1. Prepare state |0⟩^⊗(n-1)|1⟩
        2. Apply H^⊗n: (1/√2^n) Σ_x (-1)^f(x)|x⟩|1⟩
        3. Apply H^⊗(n-1) to first n-1 qubits
        4. Measure: |0⟩^⊗(n-1) indicates constant, other results indicate balanced
        """

    def _get_implementation_notes(self) -> str:
        return """
        The algorithm uses n qubits: n-1 input qubits and 1 output qubit.
        Four oracle types are implemented:
        - constant_0: f(x) = 0 for all x
        - constant_1: f(x) = 1 for all x
        - balanced: f(x) = x_0 (depends on first input bit)
        - parity: f(x) = parity of all input bits

        The measurement of the first n-1 qubits determines the function type.
        All zeros = constant, any other result = balanced.
        """


class SimonsAlgorithm(QuantumAlgorithm):
    """Simon's algorithm for finding period of black-box function."""

    @property
    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            name="Simon's Algorithm",
            description="Finds the period of a 2-to-1 function with exponential speedup",
            category="specialized",
            tags=["simon", "period_finding", "black_box", "exponential_speedup"],
            min_qubits=4,
            complexity="medium",
            classical_complexity="O(2^(n-1))",
            quantum_advantage=True,
            educational_value="high",
            use_cases=["period finding", "cryptanalysis", "hidden subgroup problems"],
            references=["Simon, D.R. (1994). 'On the power of quantum computation'"],
        )

    def create_circuit(self) -> QuantumCircuit:
        """Create Simon's algorithm circuit."""
        # Simon's algorithm requires 2n qubits: n input + n output
        n_input = self.params.n_qubits // 2
        circuit = QuantumCircuit(self.params.n_qubits, n_input)

        # Get the hidden period string
        hidden_period = self.params.custom_params.get("hidden_period", "001")
        if len(hidden_period) < n_input:
            hidden_period = hidden_period.ljust(n_input, "0")
        else:
            hidden_period = hidden_period[:n_input]

        # Initialize input qubits to superposition
        for i in range(n_input):
            circuit.h(i)

        # Apply Simon's oracle
        self._apply_simons_oracle(circuit, n_input, hidden_period)

        # Apply Hadamard to input qubits
        for i in range(n_input):
            circuit.h(i)

        # Measure input qubits
        for i in range(n_input):
            circuit.measure(i, i)

        return circuit

    def _apply_simons_oracle(self, circuit: QuantumCircuit, n_input: int, hidden_period: str) -> None:
        """Apply Simon's oracle with hidden period."""
        # Simplified Simon's oracle implementation
        # For demonstration, implement a simple 2-to-1 function

        for i in range(n_input):
            if hidden_period[i] == "1":
                # Create entanglement based on hidden period
                circuit.cx(i, n_input + i)

        # Additional operations to ensure 2-to-1 mapping
        for i in range(n_input - 1):
            circuit.cx(i, n_input + i + 1)

    def _get_mathematical_background(self) -> str:
        return """
        Simon's algorithm finds the period s of a function f: {0,1}^n → {0,1}^n
        where f(x) = f(y) iff y = x ⊕ s for some unknown s ≠ 0:

        Classical complexity: O(2^(n-1)) queries required
        Quantum complexity: O(n) queries sufficient

        Algorithm:
        1. Prepare state |0⟩^⊗n|0⟩^⊗n
        2. Apply H^⊗n to first register: (1/√2^n) Σ_x |x⟩|0⟩
        3. Apply oracle f: (1/√2^n) Σ_x |x⟩|f(x)⟩
        4. Measure second register, collapse to |x⟩|f(x)⟩ or |x⊕s⟩|f(x)⟩
        5. Apply H^⊗n to first register
        6. Repeat to get n-1 independent equations
        7. Solve linear system to find s

        This was the first algorithm to show exponential quantum speedup.
        """

    def _get_implementation_notes(self) -> str:
        return """
        This implementation uses a simplified oracle for demonstration.
        The algorithm requires 2n qubits: n input and n output qubits.
        Multiple runs are needed to collect enough equations to solve for s.
        After collecting n-1 independent measurements, classical linear
        algebra (Gaussian elimination) is used to find the hidden period.

        The hidden period string determines the structure of the oracle.
        """

    def _get_applications(self) -> str:
        return """
        - Cryptanalysis: Breaking certain cryptographic primitives
        - Hidden subgroup problems: Foundation for Shor's algorithm
        - Collision finding: Finding collisions in hash functions
        - Quantum complexity theory: Demonstrating exponential separation
        """


class QuantumWalk(QuantumAlgorithm):
    """Quantum walk algorithm for quantum search and simulation."""

    @property
    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            name="Quantum Walk",
            description="Quantum analogue of classical random walk with quadratic speedup",
            category="specialized",
            tags=["quantum_walk", "search", "simulation", "quantum_speedup"],
            min_qubits=3,
            complexity="medium",
            classical_complexity="O(N)",
            quantum_advantage=True,
            educational_value="medium",
            use_cases=["search algorithms", "graph traversal", "quantum simulation"],
            references=["Farhi, E., Gutmann, S. (1998). 'Quantum computation and decision trees'"],
        )

    def create_circuit(self) -> QuantumCircuit:
        """Create a quantum walk circuit."""
        circuit = QuantumCircuit(self.params.n_qubits, self.params.n_qubits)

        # Get walk parameters
        steps = self.params.custom_params.get("steps", 3)
        graph_type = self.params.custom_params.get("graph_type", "line")

        # Initialize position register
        for i in range(self.params.n_qubits):
            circuit.h(i)

        # Apply quantum walk steps
        for _step in range(steps):
            self._apply_walk_step(circuit, graph_type)

        circuit.measure_all()
        return circuit

    def _apply_walk_step(self, circuit: QuantumCircuit, graph_type: str) -> None:
        """Apply one step of quantum walk."""
        if graph_type == "line":
            # Quantum walk on a line
            for i in range(self.params.n_qubits - 1):
                # Coin operation
                circuit.h(i)
                # Shift operation (conditional)
                circuit.cx(i, i + 1)
        elif graph_type == "cycle":
            # Quantum walk on a cycle
            for i in range(self.params.n_qubits):
                circuit.h(i)
                next_qubit = (i + 1) % self.params.n_qubits
                circuit.cx(i, next_qubit)

    def _get_mathematical_background(self) -> str:
        return """
        Quantum walk is the quantum analogue of classical random walk:

        Classical random walk: Spreads as √t steps
        Quantum walk: Spreads linearly as t steps

        Components:
        1. Coin qubit: Determines direction of walk
        2. Position register: Represents walker position
        3. Coin operation: Quantum superposition of directions
        4. Shift operation: Conditional move based on coin

        Applications:
        - Search: O(√N) vs O(N) for classical random walk
        - Element distinctness: O(N^(2/3)) vs O(N^(1/2))
        - Graph traversal and property testing
        - Quantum simulation of transport phenomena
        """

    def _get_implementation_notes(self) -> str:
        return """
        This implementation uses a simplified discrete-time quantum walk.
        The walker position is encoded in binary using qubits.
        Coin operations use Hadamard gates for equal superposition.
        Shift operations use CNOT gates for conditional movement.

        For spatial search, the quantum walk provides quadratic speedup
        over classical random walk search algorithms.
        """


class AmplitudeAmplification(QuantumAlgorithm):
    """General amplitude amplification algorithm."""

    @property
    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            name="Amplitude Amplification",
            description="General technique for amplifying target states in quantum algorithms",
            category="specialized",
            tags=["amplitude_amplification", "grover", "quantum_speedup", "generalization"],
            min_qubits=2,
            complexity="medium",
            classical_complexity="O(N)",
            quantum_advantage=True,
            educational_value="medium",
            use_cases=["algorithm optimization", "search enhancement", "quantum speedup"],
            references=["Brassard, G., et al. (2002). 'Quantum Amplitude Amplification and Estimation'"],
        )

    def create_circuit(self) -> QuantumCircuit:
        """Create an amplitude amplification circuit."""
        circuit = QuantumCircuit(self.params.n_qubits, self.params.n_qubits)

        # Get amplification parameters
        iterations = self.params.custom_params.get("iterations", 2)
        target_state = self.params.custom_params.get("target_state", "11")

        # Initialize uniform superposition
        for i in range(self.params.n_qubits):
            circuit.h(i)

        # Apply amplitude amplification iterations
        for _ in range(iterations):
            # Oracle for target state
            self._apply_oracle(circuit, target_state)

            # Diffusion operator
            self._apply_diffusion(circuit)

        circuit.measure_all()
        return circuit

    def _apply_oracle(self, circuit: QuantumCircuit, target_state: str) -> None:
        """Apply oracle that marks the target state."""
        for i, bit in enumerate(target_state):
            if bit == "0":
                circuit.x(i)

        # Multi-controlled Z
        if self.params.n_qubits == 2:
            circuit.cz(0, 1)
        else:
            circuit.h(self.params.n_qubits - 1)
            circuit.mcx(list(range(self.params.n_qubits - 1)), self.params.n_qubits - 1)
            circuit.h(self.params.n_qubits - 1)

        for i, bit in enumerate(target_state):
            if bit == "0":
                circuit.x(i)

    def _apply_diffusion(self, circuit: QuantumCircuit) -> None:
        """Apply diffusion operator (inversion about the mean)."""
        for i in range(self.params.n_qubits):
            circuit.h(i)
            circuit.x(i)

        if self.params.n_qubits == 2:
            circuit.cz(0, 1)
        else:
            circuit.h(self.params.n_qubits - 1)
            circuit.mcx(list(range(self.params.n_qubits - 1)), self.params.n_qubits - 1)
            circuit.h(self.params.n_qubits - 1)

        for i in range(self.params.n_qubits):
            circuit.x(i)
            circuit.h(i)

    def _get_mathematical_background(self) -> str:
        return """
        Amplitude amplification generalizes Grover's algorithm:

        Given initial state |ψ⟩ = α|w⟩ + β|r⟩ where |w⟩ are target states:

        Amplification operator: Q = -A S_0 A† S_w

        Where:
        - A prepares initial state
        - S_w flips phase of target states
        - S_0 flips phase of |0⟩ state

        After k iterations: sin((2k+1)θ)|w⟩ + cos((2k+1)θ)|r⟩
        where sin(θ) = α

        Optimal iterations: k ≈ π/(4θ) - 1/2

        Applications:
        - Grover's search (special case)
        - Quantum counting
        - Optimizing other quantum algorithms
        """

    def _get_implementation_notes(self) -> str:
        return """
        This implementation demonstrates amplitude amplification for a specific target state.
        The oracle marks the target state by flipping its phase.
        The diffusion operator inverts amplitudes about the mean.
        The number of iterations determines the amplification strength.

        Too many iterations can lead to over-rotation and reduced success probability.
        """
