# Zero-config reproducible quantum-algorithm benchmarking across commercial simulators

## Abstract

Quantum computing research faces a critical reproducibility challenge: algorithm performance varies dramatically across simulators (Stim, Qiskit, MPS, Metal, CUDA), yet researchers lack standardized tools for cross-platform benchmarking. We present Ariadne, a zero-configuration quantum simulator bundle that automatically routes circuits to optimal backends while generating citable, reproducible benchmark reports.

## Introduction

The rapid proliferation of quantum simulators has created a fragmented ecosystem where researchers must manually select backends, manage conflicting dependencies, and struggle with platform-specific issues. This fragmentation undermines reproducibility and creates barriers to entry for education and industry adoption. Current benchmarking approaches require extensive domain expertise and significant engineering overhead.

## Methods

Ariadne implements intelligent circuit analysis that automatically determines optimal backend selection based on circuit characteristics: Clifford ratio, entanglement patterns, depth, and qubit count. The system routes pure Clifford circuits to Stim (enabling 1000x speedups), low-entanglement circuits to MPS tensor networks, and general circuits to appropriate backends (Qiskit, Metal, CUDA) based on hardware availability.

We developed a comprehensive benchmarking framework that executes identical quantum algorithms across multiple simulators, generating standardized reports in JSON, CSV, and LaTeX formats. The framework supports canonical algorithms including Bell states, GHZ states, QAOA, VQE ansätze, and stabilizer circuits.

## Results

Evaluation across 6 quantum simulators on macOS, Linux, and Windows platforms demonstrates:

- **Performance**: Stim achieved 1000x speedups for Clifford circuits compared to statevector simulators
- **Reproducibility**: Cross-backend statistical consistency within 5% tolerance for all tested algorithms
- **Accessibility**: Zero-configuration deployment reduced setup time from hours to minutes
- **Scalability**: Automatic backend selection extended feasible circuit sizes beyond individual simulator limits

Benchmark results show that QAOA circuits on 8 qubits achieve 226k shots/s on JAX-Metal, while VQE ansätze perform optimally on MPS backends for low-entanglement regimes.

## Impact

Ariadne addresses three critical community needs:

1. **Education**: University instructors can deploy quantum computing curricula without managing complex environments. The Docker classroom image enables instant lab setup across institutions.

2. **Research**: Researchers generate citable benchmark reports for publication, ensuring algorithm performance claims are reproducible across platforms.

3. **Industry**: DevOps teams integrate quantum regression testing into CI/CD pipelines using GitHub Actions, ensuring algorithm consistency across development environments.

## Innovation

Key innovations include:
- Deterministic routing algorithm with explainable decisions
- Cross-platform benchmarking with statistical validation
- Zero-configuration deployment model
- Integrated CLI and Python APIs for diverse workflows

## Future Work

Ongoing development focuses on expanding backend support, incorporating error mitigation strategies, and developing cloud-based benchmarking services. Community contributions are encouraged through the open-source repository.

## Conclusion

Ariadne democratizes access to quantum computing resources by eliminating configuration complexity while ensuring reproducible, citable benchmarking across commercial simulators. This work advances the field toward standardized quantum algorithm evaluation, benefiting education, research, and industry applications.

## Keywords

Quantum computing, simulator benchmarking, reproducible research, quantum algorithms, automated routing, cross-platform performance, quantum education

## Target Venue

IEEE Quantum Computing and Engineering (QCE) 2025 - Emphasizing practical quantum engineering solutions and reproducibility challenges.

## Presentation Format

- 15-minute oral presentation with live demonstration
- Benchmark results visualization across platforms
- Education case studies from university implementations
- Open-source community engagement strategies

## Supplementary Materials

- Open-source repository: github.com/Hmbown/ariadne
- Docker classroom image for hands-on demonstration
- Benchmark dataset spanning 6 simulators × 5 algorithms × 3 platforms
- Educational notebooks for classroom deployment
