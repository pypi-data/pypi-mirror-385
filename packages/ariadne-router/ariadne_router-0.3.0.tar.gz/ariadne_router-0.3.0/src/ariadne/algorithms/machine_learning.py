"""
Quantum machine learning algorithms in Ariadne.

This module contains quantum algorithms for machine learning tasks,
including quantum support vector machines and related algorithms.
"""

import numpy as np
from qiskit import QuantumCircuit

from .base import AlgorithmMetadata, QuantumAlgorithm


class QSVM(QuantumAlgorithm):
    """Quantum Support Vector Machine for classification."""

    @property
    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            name="QSVM",
            description="Quantum Support Vector Machine for quantum-enhanced classification",
            category="machine_learning",
            tags=["qsvm", "classification", "kernel", "quantum_machine_learning"],
            min_qubits=2,
            complexity="high",
            classical_complexity="O(n³)",
            quantum_advantage=True,
            educational_value="high",
            use_cases=["pattern recognition", "data classification", "feature mapping"],
            references=["Rebentrost, P., et al. (2014). 'Quantum support vector machine for big data classification'"],
        )

    def create_circuit(self) -> QuantumCircuit:
        """Create a QSVM circuit with quantum kernel evaluation."""
        circuit = QuantumCircuit(self.params.n_qubits, self.params.n_qubits)

        # Get QSVM parameters
        use_feature_map = self.params.custom_params.get("use_feature_map", True)
        use_variational = self.params.custom_params.get("use_variational", False)
        data_point = self.params.custom_params.get("data_point", [0.5] * self.params.n_qubits)

        # Ensure data point has correct length
        if len(data_point) < self.params.n_qubits:
            data_point = data_point + [0.5] * (self.params.n_qubits - len(data_point))
        else:
            data_point = data_point[: self.params.n_qubits]

        # Apply feature map to encode classical data
        if use_feature_map:
            self._apply_feature_map(circuit, data_point)

        # Apply variational circuit if specified
        if use_variational:
            self._apply_variational_circuit(circuit)

        # For demonstration, add a simple measurement pattern
        circuit.measure_all()

        return circuit

    def _apply_feature_map(self, circuit: QuantumCircuit, data_point: list[float]) -> None:
        """Apply quantum feature map to encode classical data."""
        # Use ZZ feature map (common in QSVM)
        for i in range(self.params.n_qubits):
            circuit.h(i)
            circuit.rz(2 * data_point[i], i)

        # Entangling layers
        for i in range(self.params.n_qubits):
            for j in range(i + 1, self.params.n_qubits):
                circuit.rzz(2 * data_point[i] * data_point[j], i, j)

    def _apply_variational_circuit(self, circuit: QuantumCircuit) -> None:
        """Apply variational circuit for trainable parameters."""
        # Simple variational circuit with fixed parameters for demonstration
        for i in range(self.params.n_qubits):
            circuit.ry(np.pi / 4, i)

        # Entangling layer
        for i in range(self.params.n_qubits - 1):
            circuit.cx(i, i + 1)

        # Second layer of rotations
        for i in range(self.params.n_qubits):
            circuit.rz(np.pi / 6, i)

    def _get_mathematical_background(self) -> str:
        return """
        Quantum Support Vector Machine uses quantum kernel estimation:

        Classical SVM: f(x) = sign(Σ_i α_i y_i K(x_i, x) + b)

        Quantum enhancement: K(x_i, x_j) = |⟨φ(x_i)|φ(x_j)⟩|²
        where |φ(x)⟩ is the quantum feature map encoding classical data

        Key components:
        1. Feature map: Φ: ℝ^d → Hilbert space (quantum circuit)
        2. Kernel evaluation: Inner product in high-dimensional feature space
        3. Classical optimization: Training on quantum kernel matrix

        Quantum advantage comes from accessing high-dimensional feature spaces
        that are computationally expensive classically.
        """

    def _get_implementation_notes(self) -> str:
        return """
        This implementation uses the ZZ feature map for data encoding.
        The feature map creates entanglement between qubits based on data correlations.
        For actual QSVM, you would:
        1. Compute kernel matrix using quantum circuits
        2. Train classical SVM on quantum kernel
        3. Classify new data points using quantum kernel evaluation

        The variational circuit option allows for trainable feature maps.
        """

    def _get_applications(self) -> str:
        return """
        - Pattern recognition in high-dimensional data
        - Quantum chemistry classification (molecule properties)
        - Financial data analysis and risk assessment
        - Image and signal processing with quantum enhancement
        - Drug discovery and molecular classification
        """


class VQC(QuantumAlgorithm):
    """Variational Quantum Classifier."""

    @property
    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            name="VQC",
            description="Variational Quantum Classifier for hybrid quantum-classical machine learning",
            category="machine_learning",
            tags=["vqc", "variational", "classifier", "hybrid"],
            min_qubits=2,
            complexity="high",
            classical_complexity="O(n²)",
            quantum_advantage=True,
            educational_value="high",
            use_cases=["classification", "pattern recognition", "hybrid quantum computing"],
            references=["Schuld, M., et al. (2019). 'Evaluating analytic gradients on quantum hardware'"],
        )

    def create_circuit(self) -> QuantumCircuit:
        """Create a VQC circuit."""
        circuit = QuantumCircuit(self.params.n_qubits, self.params.n_qubits)

        # Get VQC parameters
        data_point = self.params.custom_params.get("data_point", [0.5] * self.params.n_qubits)
        trainable_params = self.params.custom_params.get("trainable_params", [0.1] * (self.params.n_qubits * 2))

        # Ensure data point has correct length
        if len(data_point) < self.params.n_qubits:
            data_point = data_point + [0.5] * (self.params.n_qubits - len(data_point))
        else:
            data_point = data_point[: self.params.n_qubits]

        # Encode data
        self._encode_data(circuit, data_point)

        # Apply variational layers
        self._apply_variational_layers(circuit, trainable_params)

        # Measurement for classification
        circuit.measure_all()

        return circuit

    def _encode_data(self, circuit: QuantumCircuit, data_point: list[float]) -> None:
        """Encode classical data into quantum state."""
        # Angle encoding
        for i, x in enumerate(data_point):
            circuit.ry(x, i)

    def _apply_variational_layers(self, circuit: QuantumCircuit, params: list[float]) -> None:
        """Apply variational layers with trainable parameters."""
        n_layers = len(params) // (2 * self.params.n_qubits)

        for layer in range(n_layers):
            # Rotation layer
            for i in range(self.params.n_qubits):
                idx = layer * 2 * self.params.n_qubits + i
                if idx < len(params):
                    circuit.ry(params[idx], i)

            # Entangling layer
            for i in range(self.params.n_qubits - 1):
                circuit.cx(i, i + 1)

            # Second rotation layer
            for i in range(self.params.n_qubits):
                idx = layer * 2 * self.params.n_qubits + self.params.n_qubits + i
                if idx < len(params):
                    circuit.rz(params[idx], i)

    def _get_mathematical_background(self) -> str:
        return """
        Variational Quantum Classifier uses parameterized quantum circuits:

        Architecture:
        1. Data encoding: |x⟩ → U_enc(x)|0⟩
        2. Variational transformation: U(θ) with trainable parameters
        3. Measurement: Classification based on measurement outcomes

        Training:
        - Classical optimizer updates quantum parameters θ
        - Cost function based on classification accuracy
        - Hybrid quantum-classical optimization loop

        Loss function: L(θ) = (1/N) Σ_i ℓ(f(x_i; θ), y_i)
        where ℓ is the classification loss (e.g., cross-entropy)
        """

    def _get_implementation_notes(self) -> str:
        return """
        This implementation uses angle encoding for data input.
        The variational circuit consists of alternating rotation and entangling layers.
        For actual VQC training, you would:
        1. Initialize random parameters
        2. Run circuit forward pass
        3. Compute loss based on classification results
        4. Update parameters using classical optimizer
        5. Repeat until convergence

        The number of trainable parameters scales with qubits and layers.
        """


class QuantumNeuralNetwork(QuantumAlgorithm):
    """Quantum Neural Network for machine learning tasks."""

    @property
    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            name="Quantum Neural Network",
            description="Quantum neural network with parameterized quantum gates",
            category="machine_learning",
            tags=["qnn", "neural_network", "parameterized", "machine_learning"],
            min_qubits=2,
            complexity="high",
            classical_complexity="O(n³)",
            quantum_advantage=True,
            educational_value="high",
            use_cases=["function approximation", "pattern recognition", "quantum AI"],
            references=["Witte, R., et al. (2022). 'Quantum neural networks'"],
        )

    def create_circuit(self) -> QuantumCircuit:
        """Create a Quantum Neural Network circuit."""
        circuit = QuantumCircuit(self.params.n_qubits, self.params.n_qubits)

        # Get QNN parameters
        input_data = self.params.custom_params.get("input_data", [0.5] * self.params.n_qubits)
        weights = self.params.custom_params.get("weights", [0.1] * (self.params.n_qubits * 3))
        layers = self.params.custom_params.get("layers", 2)

        # Ensure input data has correct length
        if len(input_data) < self.params.n_qubits:
            input_data = input_data + [0.5] * (self.params.n_qubits - len(input_data))
        else:
            input_data = input_data[: self.params.n_qubits]

        # Initialize input state
        for i, x in enumerate(input_data):
            circuit.ry(x, i)

        # Apply neural network layers
        for layer in range(layers):
            self._apply_neural_layer(circuit, weights, layer)

        circuit.measure_all()
        return circuit

    def _apply_neural_layer(self, circuit: QuantumCircuit, weights: list[float], layer: int) -> None:
        """Apply a single neural network layer."""
        # Rotation gates with trainable weights
        for i in range(self.params.n_qubits):
            weight_idx = layer * 3 * self.params.n_qubits + i
            if weight_idx < len(weights):
                circuit.ry(weights[weight_idx], i)

        # Entanglement as "neural connections"
        for i in range(self.params.n_qubits - 1):
            weight_idx = layer * 3 * self.params.n_qubits + self.params.n_qubits + i
            if weight_idx < len(weights):
                circuit.crx(weights[weight_idx], i, i + 1)

        # Additional rotations
        for i in range(self.params.n_qubits):
            weight_idx = layer * 3 * self.params.n_qubits + 2 * self.params.n_qubits + i
            if weight_idx < len(weights):
                circuit.rz(weights[weight_idx], i)

    def _get_mathematical_background(self) -> str:
        return """
        Quantum Neural Networks use parameterized quantum circuits as neural layers:

        Forward pass: |y⟩ = U(θ, x)|0⟩
        where U(θ, x) is the parameterized quantum circuit with weights θ and input x

        Key components:
        1. Input encoding: Classical data → quantum state
        2. Neural layers: Parameterized quantum gates
        3. Non-linearity: Quantum interference and entanglement
        4. Measurement: Classical output extraction

        Training uses gradient-based optimization with parameter-shift rule:
        ∂⟨O⟩/∂θ = (⟨O⟩(θ + π/2) - ⟨O⟩(θ - π/2))/2
        """

    def _get_implementation_notes(self) -> str:
        return """
        This QNN uses rotation gates for neurons and CNOT/CRX gates for connections.
        The parameter-shift rule enables gradient calculation on quantum hardware.
        For training, you would:
        1. Initialize random weights
        2. Forward pass through quantum circuit
        3. Compute loss and gradients
        4. Update weights using gradient descent
        5. Repeat until convergence

        The expressivity increases with more qubits and layers.
        """
