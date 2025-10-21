"""
Command-line interface for Ariadne.

This module provides a comprehensive CLI for all Ariadne functionality,
including simulation, configuration management, and system monitoring.
"""

from .main import AriadneCLI, main

__all__ = [
    "AriadneCLI",
    "main",
]
