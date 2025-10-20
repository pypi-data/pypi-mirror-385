"""Lightweight topology analysis for routing heuristics.

Detect simple layout patterns that influence backend selection, e.g.,
chain-like structures that are MPS-friendly.
"""

from __future__ import annotations

from dataclasses import dataclass

from qiskit import QuantumCircuit

from .analyze import interaction_graph


@dataclass
class TopologyProperties:
    chain_like: bool
    grid_like: bool
    depth: int
    max_degree: int


def detect_layout_properties(circuit: QuantumCircuit) -> dict[str, int | bool]:
    """Detect coarse topology/layout properties of the circuit's interaction graph.

    Heuristics:
    - chain_like: graph is a path (max degree <= 2, and #edges ≈ #nodes-1)
    - grid_like: simple proxy (not implemented, always False for now)
    - depth: circuit depth (qiskit-reported)
    - max_degree: maximum node degree in interaction graph
    """
    g = interaction_graph(circuit)

    n = g.number_of_nodes()
    m = g.number_of_edges()

    max_deg = max((deg for _, deg in g.degree()), default=0)
    chain_like = False
    if n > 0:
        # Path-like graphs typically have max degree <= 2 and are sparse
        chain_like = (max_deg <= 2) and (m >= n - 1) and (m <= n)

    props = TopologyProperties(
        chain_like=bool(chain_like),
        grid_like=False,
        depth=int(circuit.depth()),
        max_degree=int(max_deg),
    )
    return {
        "chain_like": props.chain_like,
        "grid_like": props.grid_like,
        "depth": props.depth,
        "max_degree": props.max_degree,
    }
