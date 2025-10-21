#!/usr/bin/env python3
"""
Ariadne Production-Ready Demo

This example demonstrates the production-ready features of Ariadne,
including enhanced configuration, CLI, plugin system, and usability improvements.
"""

import os
import tempfile
import time

from qiskit import QuantumCircuit

# Import Ariadne components
from ariadne import simulate
from ariadne.cli.main import AriadneCLI
from ariadne.config import (
    ConfigFormat,
    create_production_template,
    load_config,
)
from ariadne.core import configure_logging, get_logger
from ariadne.plugins import (
    BackendPlugin,
    PluginInfo,
    PluginType,
    get_plugin_manager,
    list_plugins,
    load_plugin,
)


def demo_configuration_system():
    """Demonstrate the enhanced configuration system."""
    print("\n=== Enhanced Configuration System Demo ===")

    logger = get_logger("config_demo")

    # Create a temporary directory for demo files
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = os.path.join(temp_dir, "ariadne_config.yaml")

        # Create a production configuration template
        print("Creating production configuration template...")
        template = create_production_template()
        template.save(config_path, ConfigFormat.YAML)
        print(f"Configuration template created: {config_path}")

        # Load and validate configuration
        print("\nLoading configuration...")
        try:
            config = load_config(config_paths=[config_path])
            print("Configuration loaded successfully")

            # Display configuration
            print("\nConfiguration contents:")
            for section, values in config.items():
                print(f"  {section}:")
                for key, value in values.items():
                    print(f"    {key}: {value}")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return

        # Demonstrate environment variable override
        print("\nDemonstrating environment variable override...")
        os.environ["ARIADNE_LOGGING_LEVEL"] = "DEBUG"
        os.environ["ARIADNE_BACKENDS_DEFAULT_BACKEND"] = "stim"

        try:
            config_with_env = load_config(config_paths=[config_path])
            print("Configuration with environment overrides loaded")
            print(f"  Logging level: {config_with_env.get('logging', {}).get('level')}")
            print(f"  Default backend: {config_with_env.get('backends', {}).get('default_backend')}")
        except Exception as e:
            logger.error(f"Failed to load configuration with environment overrides: {e}")

        # Clean up environment variables
        if "ARIADNE_LOGGING_LEVEL" in os.environ:
            del os.environ["ARIADNE_LOGGING_LEVEL"]
        if "ARIADNE_BACKENDS_DEFAULT_BACKEND" in os.environ:
            del os.environ["ARIADNE_BACKENDS_DEFAULT_BACKEND"]


def demo_cli_system():
    """Demonstrate the CLI system."""
    print("\n=== CLI System Demo ===")

    # Create a temporary circuit for CLI demo
    with tempfile.TemporaryDirectory() as temp_dir:
        circuit_path = os.path.join(temp_dir, "bell_circuit.qasm")
        results_path = os.path.join(temp_dir, "results.json")

        # Create a Bell state circuit
        bell = QuantumCircuit(2, 2)
        bell.h(0)
        bell.cx(0, 1)
        bell.measure_all()

        # Save circuit to QASM
        with open(circuit_path, "w") as f:
            f.write(bell.qasm())

        print(f"Created test circuit: {circuit_path}")

        # Create CLI instance
        cli = AriadneCLI()

        # Run CLI simulate command
        print("\nRunning CLI simulate command...")
        try:
            exit_code = cli._cmd_simulate(
                cli._create_parser().parse_args(
                    [
                        "simulate",
                        circuit_path,
                        "--shots",
                        "100",
                        "--backend",
                        "qiskit",
                        "--output",
                        results_path,
                    ]
                )
            )

            if exit_code == 0:
                print("CLI simulation completed successfully")

                # Display results
                if os.path.exists(results_path):
                    import json

                    with open(results_path) as f:
                        results = json.load(f)

                    print(f"  Backend: {results['backend_used']}")
                    print(f"  Execution time: {results['execution_time']:.4f}s")
                    print(f"  Counts: {results['counts']}")
            else:
                print(f"CLI simulation failed with exit code: {exit_code}")
        except Exception as e:
            print(f"CLI simulation error: {e}")

        # Run CLI config command
        print("\nRunning CLI config create command...")
        try:
            config_path = os.path.join(temp_dir, "cli_config.yaml")
            exit_code = cli._cmd_config_create(
                cli._create_parser().parse_args(
                    [
                        "config",
                        "create",
                        "--template",
                        "development",
                        "--format",
                        "yaml",
                        "--output",
                        config_path,
                    ]
                )
            )

            if exit_code == 0:
                print("CLI config creation completed successfully")
                print(f"  Configuration created: {config_path}")
            else:
                print(f"CLI config creation failed with exit code: {exit_code}")
        except Exception as e:
            print(f"CLI config creation error: {e}")


class DemoBackendPlugin(BackendPlugin):
    """Demo backend plugin for demonstration."""

    def get_info(self) -> PluginInfo:
        """Get plugin information."""
        return PluginInfo(
            name="demo_backend",
            version="1.0.0",
            description="Demo backend plugin for demonstration",
            author="Ariadne Team",
            plugin_type=PluginType.BACKEND,
            dependencies=["qiskit"],
            tags=["demo", "backend"],
        )

    def initialize(self, config: dict) -> None:
        """Initialize the plugin."""
        self._config = config
        self.logger.info("Demo backend plugin initialized")

    def activate(self) -> None:
        """Activate the plugin."""
        self.logger.info("Demo backend plugin activated")

    def deactivate(self) -> None:
        """Deactivate the plugin."""
        self.logger.info("Demo backend plugin deactivated")

    def cleanup(self) -> None:
        """Clean up plugin resources."""
        self.logger.info("Demo backend plugin cleaned up")

    def get_backend_class(self):
        """Get the backend class provided by this plugin."""

        # Return a mock backend class for demonstration
        class DemoBackend:
            def __init__(self):
                self.name = "demo_backend"

            def simulate(self, circuit, shots=1000):
                # Return mock results
                return {"0": shots // 2, "1": shots // 2}

        return DemoBackend

    def is_available(self) -> bool:
        """Check if the backend is available."""
        return True


def demo_plugin_system():
    """Demonstrate the plugin system."""
    print("\n=== Plugin System Demo ===")

    logger = get_logger("plugin_demo")
    logger.info("Demonstrating plugin discovery and lifecycle")

    # Get plugin manager
    plugin_manager = get_plugin_manager()

    # List discovered plugins
    print("Discovered plugins:")
    plugins = list_plugins()
    for plugin in plugins:
        print(f"  - {plugin.name} v{plugin.version} ({plugin.plugin_type.value})")
        print(f"    {plugin.description}")

    # Register our demo plugin
    print("\nRegistering demo plugin...")
    plugin_manager._discovered_plugins["demo_backend"] = DemoBackendPlugin().get_info()
    plugin_manager._plugin_classes["demo_backend"] = DemoBackendPlugin

    # Load the demo plugin
    print("\nLoading demo plugin...")
    if load_plugin("demo_backend"):
        print("Demo plugin loaded successfully")

        # Get the loaded plugin
        plugin = plugin_manager.get_plugin("demo_backend")
        if plugin:
            print(f"Plugin state: {plugin.status.state.value}")
            print(f"Plugin info: {plugin.info.name} v{plugin.info.version}")
    else:
        print("Failed to load demo plugin")

    # List loaded plugins
    print("\nLoaded plugins:")
    loaded_plugins = plugin_manager.list_loaded_plugins()
    for plugin in loaded_plugins:
        print(f"  - {plugin.info.name} ({plugin.status.state.value})")


def demo_usability_improvements():
    """Demonstrate usability improvements."""
    print("\n=== Usability Improvements Demo ===")

    logger = get_logger("usability_demo")
    logger.info("Showcasing logging and progress helpers")

    # Configure logging with different levels
    print("Configuring logging with different levels...")

    # Configure INFO level
    configure_logging(level="INFO")
    logger.info("This is an INFO level message")

    # Configure DEBUG level
    configure_logging(level="DEBUG")
    logger.debug("This is a DEBUG level message")

    # Demonstrate context-aware error messages
    print("\nDemonstrating context-aware error messages...")

    try:
        # Try to simulate with an invalid backend
        circuit = QuantumCircuit(2)
        circuit.h(0)
        circuit.cx(0, 1)
        circuit.measure_all()

        result = simulate(circuit, shots=100, backend="invalid_backend")
    except Exception as e:
        print(f"Error with context: {e}")
        print("  Suggestion: Check available backends with 'ariadne status'")
    else:
        print("Simulation unexpectedly succeeded; result counts:", result.counts)

    # Demonstrate progress indicators
    print("\nDemonstrating progress indicators...")

    from ariadne.cli.main import ProgressIndicator

    progress = ProgressIndicator("Processing circuit")
    progress.start()

    # Simulate some work
    for i in range(5):
        time.sleep(0.2)
        progress.update(f" (step {i + 1}/5)")

    progress.finish("complete")

    # Demonstrate performance tips
    print("\nPerformance tips:")
    print("  - Use Clifford circuits with Stim backend for optimal performance")
    print("  - Enable backend pooling for repeated simulations")
    print("  - Use circuit optimization for large circuits")
    print("  - Monitor backend health for early issue detection")


def main():
    """Run all production-ready demonstrations."""
    print("=== Ariadne Production-Ready Features Demo ===")

    # Configure logging
    configure_logging(level="INFO")

    # Run demonstrations
    demo_configuration_system()
    demo_cli_system()
    demo_plugin_system()
    demo_usability_improvements()

    print("\n=== Production-Ready Features Demo Complete ===")
    print("✓ Enhanced configuration system with validation and progressive loading")
    print("✓ Comprehensive CLI with progress indicators and error handling")
    print("✓ Plugin system for extending Ariadne functionality")
    print("✓ Usability improvements with context-aware error messages")
    print("\nThese features make Ariadne more user-friendly and extensible for production use.")


if __name__ == "__main__":
    main()
