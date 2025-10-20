"""
Fault-tolerant quantum computing support.

This package provides tools and utilities for fault-tolerant quantum computing,
including resource estimation, error correction, and quantum error mitigation.
"""

from .resource_estimator import ResourceEstimate, estimate_circuit_resources

__all__ = ["ResourceEstimate", "estimate_circuit_resources"]
