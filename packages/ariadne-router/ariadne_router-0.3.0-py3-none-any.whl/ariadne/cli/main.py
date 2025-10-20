"""
Command-line interface for Ariadne.

This module provides a comprehensive CLI for all Ariadne functionality,
including simulation, configuration management, and system monitoring.
"""

import argparse
import logging
import os
import sys
import time
from argparse import ArgumentParser, _SubParsersAction
from pathlib import Path
from typing import TYPE_CHECKING, Any

from qiskit import QuantumCircuit

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    from ariadne.types import BackendType
except ImportError:  # pragma: no cover - fallback for script execution
    if PROJECT_ROOT not in sys.path:
        sys.path.append(PROJECT_ROOT)
    from ariadne.types import BackendType

if TYPE_CHECKING:
    from ariadne.backends.health_check import HealthMetrics
    from ariadne.core.logging import AriadneLogger
    from ariadne.results import SimulationResult


BACKEND_ALIASES: dict[str, str] = {"metal": BackendType.JAX_METAL.value}

CLI_BACKEND_CHOICES = sorted(
    {
        BackendType.QISKIT.value,
        BackendType.STIM.value,
        BackendType.CUDA.value,
        BackendType.JAX_METAL.value,
        BackendType.TENSOR_NETWORK.value,
        BackendType.MPS.value,
        BackendType.DDSIM.value,
    }
    | set(BACKEND_ALIASES.keys())
    | set(BACKEND_ALIASES.values())
)

# Check if YAML is available
yaml: Any | None
try:
    import yaml as _yaml_module
except ImportError:
    YAML_AVAILABLE = False
    yaml = None
else:
    YAML_AVAILABLE = True
    yaml = _yaml_module


def _describe_config_keys(config: object) -> str:
    """Return a readable list of configuration keys for logging/display."""

    if isinstance(config, dict):
        return ", ".join(sorted(str(key) for key in config.keys()))

    if hasattr(config, "model_dump"):
        try:
            data = config.model_dump()
        except Exception:  # pragma: no cover - defensive fallback
            data = getattr(config, "__dict__", {})
        if isinstance(data, dict):
            return ", ".join(sorted(str(key) for key in data.keys()))

    if hasattr(config, "__dict__"):
        return ", ".join(sorted(str(key) for key in vars(config)))

    return ""


try:
    from ariadne import __version__, simulate
    from ariadne.backends import (
        get_health_checker,
        get_pool_manager,
    )
    from ariadne.config import (
        ConfigFormat,
        create_default_template,
        create_development_template,
        create_production_template,
        load_config,
    )
    from ariadne.core import configure_logging, get_logger
except ImportError:
    # Fallback for when running as a script
    if PROJECT_ROOT not in sys.path:
        sys.path.append(PROJECT_ROOT)
    from ariadne import __version__, simulate
    from ariadne.backends import (
        get_health_checker,
        get_pool_manager,
    )
    from ariadne.config import (
        ConfigFormat,
        create_default_template,
        create_development_template,
        create_production_template,
        load_config,
    )
    from ariadne.core import configure_logging, get_logger


class ProgressIndicator:
    """Simple progress indicator for long-running operations."""

    def __init__(self, description: str = "Processing"):
        """Initialize progress indicator."""
        self.description = description
        self.start_time: float | None = None
        self.last_update: float = 0

    def start(self) -> None:
        """Start the progress indicator."""
        self.start_time = time.time()
        print(f"{self.description}...", end="", flush=True)

    def update(self, message: str = "") -> None:
        """Update the progress indicator."""
        current_time = time.time()
        if self.start_time is not None and current_time - self.last_update > 0.5:  # Update every 0.5 seconds
            elapsed = current_time - self.start_time
            print(f"\r{self.description}... ({elapsed:.1f}s){message}", end="", flush=True)
            self.last_update = current_time

    def finish(self, message: str = "done") -> None:
        """Finish the progress indicator."""
        if self.start_time is not None:
            elapsed = time.time() - self.start_time
            print(f"\r{self.description}... {message} ({elapsed:.1f}s)")
        else:
            print(f"\r{self.description}... {message} (0.0s)")


class AriadneCLI:
    """Main CLI class for Ariadne."""

    def __init__(self) -> None:
        """Initialize the CLI."""
        self.logger: AriadneLogger | None = None

    def run(self, args: list[str] | None = None) -> int:
        """
        Run the CLI with the given arguments.

        Args:
            args: Command-line arguments (uses sys.argv if None)

        Returns:
            Exit code
        """
        parser = self._create_parser()
        parsed_args = parser.parse_args(args)

        # Configure logging
        log_level_name = getattr(parsed_args, "log_level", "INFO")
        log_level = getattr(logging, log_level_name.upper(), logging.INFO)
        configure_logging(level=log_level)
        self.logger = get_logger("cli")

        # Execute command
        try:
            cmd_method = getattr(self, f"_cmd_{parsed_args.command.replace('-', '_')}")
            result: int = cmd_method(parsed_args)
            return result
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            return 130
        except Exception as e:
            if self.logger:
                self.logger.error(f"Command failed: {e}")
            return 1

    def _create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser."""
        parser = argparse.ArgumentParser(
            prog="ariadne",
            description="Ariadne quantum circuit simulation framework",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  ariadne simulate circuit.qc --shots 1000 --backend qiskit
  ariadne config create --template production --output config.yaml
  ariadne status --backend metal
  ariadne benchmark --circuit circuit.qc --shots 1000
            """,
        )

        # Add global arguments
        parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

        parser.add_argument(
            "--log-level",
            choices=["DEBUG", "INFO", "WARNING", "ERROR"],
            default="INFO",
            help="Set logging level",
        )

        # Add subcommands
        subparsers = parser.add_subparsers(dest="command", help="Available commands", metavar="COMMAND")

        # Simulate command
        self._add_simulate_command(subparsers)

        # Config command
        self._add_config_command(subparsers)

        # Status command
        self._add_status_command(subparsers)

        # Benchmark command
        self._add_benchmark_command(subparsers)

        # Benchmark suite command
        self._add_benchmark_suite_command(subparsers)

        return parser

    def _add_simulate_command(self, subparsers: "_SubParsersAction[ArgumentParser]") -> None:
        """Add the simulate command."""
        parser = subparsers.add_parser(
            "simulate",
            help="Simulate a quantum circuit",
            description="Simulate a quantum circuit using the specified backend",
        )

        parser.add_argument("circuit", help="Path to quantum circuit file (QASM or QPY format)")

        parser.add_argument("--shots", type=int, default=1024, help="Number of measurement shots (default: 1024)")

        parser.add_argument(
            "--backend",
            choices=CLI_BACKEND_CHOICES,
            help="Backend to use for simulation",
        )

        parser.add_argument("--output", help="Output file for results (JSON format)")

        parser.add_argument("--config", help="Configuration file path")

    def _add_config_command(self, subparsers: "_SubParsersAction[ArgumentParser]") -> None:
        """Add the config command."""
        parser = subparsers.add_parser(
            "config",
            help="Manage configuration",
            description="Create, validate, or show configuration",
        )

        config_subparsers = parser.add_subparsers(dest="config_action", help="Configuration actions")

        # Create command
        create_parser = config_subparsers.add_parser("create", help="Create a configuration file")

        create_parser.add_argument(
            "--template",
            choices=["default", "development", "production"],
            default="default",
            help="Configuration template to use",
        )

        create_parser.add_argument(
            "--format",
            choices=["yaml", "json", "toml"],
            default="yaml",
            help="Configuration file format",
        )

        create_parser.add_argument("--output", required=True, help="Output file path")

        # Validate command
        validate_parser = config_subparsers.add_parser("validate", help="Validate a configuration file")

        validate_parser.add_argument("config_file", help="Configuration file to validate")

        # Show command
        show_parser = config_subparsers.add_parser("show", help="Show current configuration")

        show_parser.add_argument("--format", choices=["yaml", "json"], default="yaml", help="Output format")

    def _add_status_command(self, subparsers: "_SubParsersAction[ArgumentParser]") -> None:
        """Add the status command."""
        parser = subparsers.add_parser(
            "status",
            help="Show system status",
            description="Show status of backends, pools, and system resources",
        )

        parser.add_argument("--backend", help="Show status for specific backend only")

        parser.add_argument("--detailed", action="store_true", help="Show detailed status information")

    def _add_benchmark_command(self, subparsers: "_SubParsersAction[ArgumentParser]") -> None:
        """Add the benchmark command."""
        parser = subparsers.add_parser(
            "benchmark",
            help="Run performance benchmarks",
            description="Run performance benchmarks for backends",
        )

        parser.add_argument("--circuit", help="Path to quantum circuit file for benchmarking")

        parser.add_argument("--shots", type=int, default=1000, help="Number of measurement shots (default: 1000)")

        parser.add_argument(
            "--backend",
            choices=CLI_BACKEND_CHOICES,
            help="Backend to benchmark (default: all available)",
        )

        parser.add_argument("--iterations", type=int, default=5, help="Number of benchmark iterations (default: 5)")

        parser.add_argument("--output", help="Output file for benchmark results (JSON format)")

    def _add_benchmark_suite_command(self, subparsers: "_SubParsersAction[ArgumentParser]") -> None:
        """Add the benchmark-suite command."""
        # Get available algorithms for help text
        try:
            from ..algorithms import list_algorithms

            available_algorithms = list_algorithms()
        except Exception:
            available_algorithms = ["bell", "qaoa", "vqe", "stabilizer"]

        parser = subparsers.add_parser(
            "benchmark-suite",
            help="Run comprehensive benchmark suite",
            description="Run comprehensive benchmark suite across algorithms and backends",
        )

        parser.add_argument(
            "--algorithms",
            help=f"Comma-separated list of algorithms to test (e.g., bell,qaoa,vqe,qft,grover,qpe,steane). Available: {', '.join(available_algorithms)}",
        )

        parser.add_argument(
            "--backends",
            help="Comma-separated list of backends to test (e.g., auto,stim,qiskit,mps)",
        )

        parser.add_argument("--shots", type=int, default=1000, help="Number of measurement shots (default: 1000)")

        parser.add_argument("--output", help="Output file for benchmark results (JSON format)")

    def _cmd_simulate(self, args: argparse.Namespace) -> int:
        """Execute the simulate command."""
        progress = ProgressIndicator("Loading circuit")
        progress.start()

        try:
            # Load circuit
            circuit = self._load_circuit(args.circuit)
            progress.update(f" ({circuit.num_qubits} qubits, {circuit.depth()} depth)")
            progress.finish("loaded")
        except Exception as e:
            progress.finish("failed")
            if self.logger:
                self.logger.error(f"Failed to load circuit: {e}")
            return 1

        # Load configuration if specified
        config = {}
        if args.config:
            try:
                config = load_config(config_paths=[args.config])
                if self.logger:
                    self.logger.info(f"Loaded configuration from {args.config}")
                config_keys = _describe_config_keys(config)
                if config_keys:
                    print(f"Using configuration keys: {config_keys}")
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"Failed to load configuration: {e}")

        # Simulate circuit
        progress = ProgressIndicator("Simulating circuit")
        progress.start()

        try:
            kwargs = {"shots": args.shots}
            if args.backend:
                kwargs["backend"] = self._resolve_backend_name(args.backend)

            result = simulate(circuit, **kwargs)
            progress.finish("complete")

            # Display results
            print("\nSimulation Results:")
            print(f"  Backend: {result.backend_used.value}")
            print(f"  Execution time: {result.execution_time:.4f}s")
            print(f"  Shots: {args.shots}")
            print(f"  Counts: {dict(list(result.counts.items())[:5])}")

            if len(result.counts) > 5:
                print(f"  ... and {len(result.counts) - 5} more")

            # Save results if requested
            if args.output:
                self._save_results(result, args.output)
                print(f"  Results saved to: {args.output}")

            return 0

        except Exception as e:
            progress.finish("failed")
            if self.logger:
                self.logger.error(f"Simulation failed: {e}")
            return 1

    def _cmd_config(self, args: argparse.Namespace) -> int:
        """Execute the config command."""
        if args.config_action == "create":
            return self._cmd_config_create(args)
        elif args.config_action == "validate":
            return self._cmd_config_validate(args)
        elif args.config_action == "show":
            return self._cmd_config_show(args)
        else:
            if self.logger:
                self.logger.error(f"Unknown config action: {args.config_action}")
            return 1

    def _cmd_config_create(self, args: argparse.Namespace) -> int:
        """Execute the config create command."""
        progress = ProgressIndicator("Creating configuration")
        progress.start()

        try:
            # Get template
            if args.template == "default":
                template = create_default_template()
            elif args.template == "development":
                template = create_development_template()
            elif args.template == "production":
                template = create_production_template()
            else:
                progress.finish("failed")
                if self.logger:
                    self.logger.error(f"Unknown template: {args.template}")
                return 1

            # Get format
            if args.format == "yaml":
                format = ConfigFormat.YAML
            elif args.format == "json":
                format = ConfigFormat.JSON
            elif args.format == "toml":
                format = ConfigFormat.TOML
            else:
                progress.finish("failed")
                if self.logger:
                    self.logger.error(f"Unknown format: {args.format}")
                return 1

            # Save template
            template.save(args.output, format)
            progress.finish("created")

            print(f"Configuration template created: {args.output}")
            return 0

        except Exception as e:
            progress.finish("failed")
            if self.logger:
                self.logger.error(f"Failed to create configuration: {e}")
            return 1

    def _cmd_config_validate(self, args: argparse.Namespace) -> int:
        """Execute the config validate command."""
        progress = ProgressIndicator("Validating configuration")
        progress.start()

        try:
            # Load configuration
            config = load_config(config_paths=[args.config_file])
            progress.finish("valid")

            config_keys = _describe_config_keys(config)
            if config_keys:
                print(f"Configuration is valid: {args.config_file} (keys: {config_keys})")
            else:
                print(f"Configuration is valid: {args.config_file}")
            return 0

        except Exception as e:
            progress.finish("invalid")
            if self.logger:
                self.logger.error(f"Configuration validation failed: {e}")
            return 1

    def _cmd_config_show(self, args: argparse.Namespace) -> int:
        """Execute the config show command."""
        try:
            # Load current configuration
            config = load_config()

            # Display configuration
            if args.format == "json" or not YAML_AVAILABLE or yaml is None:
                import json

                print(json.dumps(config, indent=2))
            else:
                print(yaml.dump(config, default_flow_style=False, sort_keys=False))

            return 0

        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to show configuration: {e}")
            return 1

    def _cmd_status(self, args: argparse.Namespace) -> int:
        """Execute the status command."""
        print("Ariadne System Status")
        print("=" * 50)

        # Show backend status
        health_checker = get_health_checker()

        if args.backend:
            # Show specific backend status
            backend_type = self._parse_backend_type(args.backend)
            if backend_type:
                metrics = health_checker.get_backend_metrics(backend_type)
                if metrics:
                    self._print_backend_status(backend_type, metrics, args.detailed)
                else:
                    print(f"No status available for backend: {args.backend}")
            else:
                print(f"Unknown backend: {args.backend}")
                return 1
        else:
            # Show all backend status
            print("\nBackend Status:")
            print("-" * 30)

            for backend_type in self._get_available_backends():
                metrics = health_checker.get_backend_metrics(backend_type)
                if metrics:
                    self._print_backend_status(backend_type, metrics, args.detailed)

        # Show pool status
        print("\nBackend Pool Status:")
        print("-" * 30)

        pool_manager = get_pool_manager()
        pool_stats = pool_manager.get_all_statistics()

        if pool_stats:
            for backend_name, stats in pool_stats.items():
                print(f"{backend_name}:")
                print(f"  Total instances: {stats.total_instances}")
                print(f"  Active instances: {stats.active_instances}")
                print(f"  Available instances: {stats.available_instances}")
                print(f"  Success rate: {stats.success_rate:.2%}")
                print(f"  Average wait time: {stats.average_wait_time:.3f}s")
                print()
        else:
            print("No active pools")

        return 0

    def _cmd_benchmark(self, args: argparse.Namespace) -> int:
        """Execute the benchmark command."""
        # Load or create circuit
        if args.circuit:
            progress = ProgressIndicator("Loading circuit")
            progress.start()

            try:
                circuit = self._load_circuit(args.circuit)
                progress.update(f" ({circuit.num_qubits} qubits, {circuit.depth()} depth)")
                progress.finish("loaded")
            except Exception as e:
                progress.finish("failed")
                if self.logger:
                    self.logger.error(f"Failed to load circuit: {e}")
                return 1
        else:
            # Create benchmark circuit
            circuit = self._create_benchmark_circuit()
            print(f"Using benchmark circuit: {circuit.num_qubits} qubits, {circuit.depth()} depth")

        # Run benchmarks
        print(f"\nRunning benchmarks ({args.iterations} iterations, {args.shots} shots)...")
        print("=" * 60)

        backends = self._get_available_backends()
        if args.backend:
            backend_type = self._parse_backend_type(args.backend)
            if backend_type:
                backends = [backend_type]
            else:
                print(f"Unknown backend: {args.backend}")
                return 1

        results = {}

        for backend_type in backends:
            print(f"\nBenchmarking {backend_type.value}...")

            try:
                # Run benchmark iterations
                times = []
                success_count = 0

                for i in range(args.iterations):
                    try:
                        start_time = time.time()
                        result = simulate(circuit, shots=args.shots, backend=backend_type.value)
                        end_time = time.time()

                        times.append(end_time - start_time)
                        success_count += 1

                        print(f"  Iteration {i + 1}: {end_time - start_time:.4f}s")
                        if i == 0:
                            counts_preview = dict(list(result.counts.items())[:3])
                            print(f"    Sample counts: {counts_preview}")
                    except Exception as e:
                        print(f"  Iteration {i + 1}: Failed - {e}")

                # Calculate statistics
                if times:
                    avg_time = sum(times) / len(times)
                    min_time = min(times)
                    max_time = max(times)

                    results[backend_type.value] = {
                        "success_rate": success_count / args.iterations,
                        "avg_time": avg_time,
                        "min_time": min_time,
                        "max_time": max_time,
                        "iterations": args.iterations,
                        "shots": args.shots,
                    }

                    print(f"  Success rate: {success_count}/{args.iterations} ({success_count / args.iterations:.2%})")
                    print(f"  Average time: {avg_time:.4f}s")
                    print(f"  Min time: {min_time:.4f}s")
                    print(f"  Max time: {max_time:.4f}s")
                    print(f"  Throughput: {args.shots / avg_time:.0f} shots/s")
                else:
                    print("  All iterations failed")

            except Exception as e:
                print(f"  Benchmark failed: {e}")

        # Save results if requested
        if args.output and results:
            self._save_benchmark_results(results, args.output)
            print(f"\nBenchmark results saved to: {args.output}")

        # Print summary
        if len(results) > 1:
            print("\nBenchmark Summary:")
            print("-" * 30)

            # Sort by average time
            sorted_results = sorted(results.items(), key=lambda x: x[1]["avg_time"])

            for backend, stats in sorted_results:
                print(f"{backend}: {stats['avg_time']:.4f}s avg, {stats['throughput']:.0f} shots/s")

        return 0

    def _cmd_benchmark_suite(self, args: argparse.Namespace) -> int:
        """Execute the benchmark-suite command."""
        from ariadne.benchmarking import export_benchmark_report

        # Parse algorithms
        try:
            from ..algorithms import list_algorithms

            available_algorithms = list_algorithms()
            algorithms = available_algorithms[:4]  # Use first 4 as default
        except Exception:
            # Fallback to original algorithms if module not available
            algorithms = ["bell", "qaoa", "vqe", "stabilizer"]  # default

        if args.algorithms:
            algorithms = [alg.strip() for alg in args.algorithms.split(",")]

        # Parse backends
        backends = ["auto", "stim", "qiskit", "mps"]  # default
        if args.backends:
            backends = [backend.strip() for backend in args.backends.split(",")]

        print("Running benchmark suite...")
        print(f"Algorithms: {', '.join(algorithms)}")
        print(f"Backends: {', '.join(backends)}")
        print(f"Shots: {args.shots}")
        print("=" * 50)

        progress = ProgressIndicator("Running benchmark suite")
        progress.start()

        try:
            # Generate benchmark report
            report = export_benchmark_report(algorithms, backends, args.shots, "json")
            progress.finish("complete")

            # Display summary
            print("\nBenchmark Results Summary:")
            print("-" * 40)

            for alg_name, alg_data in report["results"].items():
                circuit_info = alg_data["circuit_info"]
                print(f"\n{alg_name.upper()} ({circuit_info['qubits']} qubits, {circuit_info['depth']} depth):")

                successful_backends = []
                failed_backends = []

                for backend_name, backend_data in alg_data["backends"].items():
                    if backend_data["success"]:
                        execution_time = backend_data["execution_time"]
                        throughput = backend_data["throughput"]
                        successful_backends.append(f"{backend_name} ({execution_time:.3f}s, {throughput:.0f} shots/s)")
                    else:
                        failed_backends.append(f"{backend_name} ({backend_data.get('error', 'Unknown')})")

                if successful_backends:
                    print("  ✓ Working:", ", ".join(successful_backends))
                if failed_backends:
                    print("  ✗ Failed:", ", ".join(failed_backends))

            # Save results if requested
            if args.output:
                import json

                with open(args.output, "w") as f:
                    json.dump(report, f, indent=2, default=str)
                print(f"\nResults saved to: {args.output}")

            return 0

        except Exception as e:
            progress.finish("failed")
            if self.logger:
                self.logger.error(f"Benchmark suite failed: {e}")
            return 1

    def _load_circuit(self, path: str) -> QuantumCircuit:
        """Load a quantum circuit from file."""
        circuit_path = Path(path)

        if not circuit_path.exists():
            raise FileNotFoundError(f"Circuit file not found: {path}")

        if circuit_path.suffix == ".qasm":
            # Load QASM file
            return QuantumCircuit.from_qasm_file(str(circuit_path))
        elif circuit_path.suffix == ".qpy":
            # Load QPY file
            from qiskit.qpy import load

            with open(circuit_path, "rb") as f:
                loaded_circuits = load(f)

            if isinstance(loaded_circuits, QuantumCircuit):
                return loaded_circuits

            try:
                iterator = iter(loaded_circuits)
            except TypeError as exc:
                raise ValueError(
                    "Loaded QPY data must be a QuantumCircuit or an iterable of QuantumCircuit objects."
                ) from exc

            for candidate in iterator:
                if isinstance(candidate, QuantumCircuit):
                    return candidate

            raise ValueError("QPY file does not contain any QuantumCircuit objects.")
        else:
            raise ValueError(f"Unsupported circuit file format: {circuit_path.suffix}")

    def _save_results(self, result: "SimulationResult", output_path: str) -> None:
        """Save simulation results to file."""
        import json

        # Convert result to dictionary
        result_dict = {
            "backend_used": result.backend_used.value,
            "execution_time": result.execution_time,
            "counts": result.counts,
            "metadata": result.metadata or {},
        }

        # Add fallback reason if present
        if result.fallback_reason:
            result_dict["fallback_reason"] = result.fallback_reason

        # Add warnings if present
        if result.warnings:
            result_dict["warnings"] = result.warnings

        # Save to file
        with open(output_path, "w") as f:
            json.dump(result_dict, f, indent=2)

    def _save_benchmark_results(self, results: dict[str, Any], output_path: str) -> None:
        """Save benchmark results to file."""
        import json
        from datetime import datetime

        # Create results dictionary
        benchmark_results = {"timestamp": datetime.now().isoformat(), "results": results}

        # Save to file
        with open(output_path, "w") as f:
            json.dump(benchmark_results, f, indent=2)

    def _resolve_backend_name(self, backend_name: str) -> str:
        """Resolve a backend name to its canonical value if an alias is provided."""

        return BACKEND_ALIASES.get(backend_name, backend_name)

    def _parse_backend_type(self, backend_name: str) -> "BackendType | None":
        """Parse backend name to BackendType enum."""

        resolved_name = self._resolve_backend_name(backend_name)

        try:
            return BackendType(resolved_name)
        except ValueError:
            return None

    def _get_available_backends(self) -> list["BackendType"]:
        """Get list of available backends."""
        from ariadne.types import BackendType

        return list(BackendType)

    def _print_backend_status(
        self, backend_type: "BackendType", metrics: "HealthMetrics", detailed: bool = False
    ) -> None:
        """Print status for a specific backend."""
        print(f"{backend_type.value}:")
        print(f"  Status: {metrics.status.value}")
        print(f"  Total checks: {metrics.total_checks}")
        print(f"  Success rate: {metrics.success_rate:.2%}")
        print(f"  Average response time: {metrics.average_response_time:.3f}s")
        print(f"  Uptime: {metrics.uptime_percentage:.1f}%")

        if detailed:
            print(f"  Last check: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(metrics.last_check))}")
            print(f"  Consecutive failures: {metrics.consecutive_failures}")

            if metrics.details:
                print("  Details:")
                for key, value in metrics.details.items():
                    print(f"    {key}: {value}")

        print()

    def _create_benchmark_circuit(self) -> QuantumCircuit:
        """Create a benchmark circuit."""
        # Create a moderately complex circuit for benchmarking
        circuit = QuantumCircuit(5)

        # Add some gates
        for i in range(5):
            circuit.h(i)

        # Add some entangling gates
        for i in range(4):
            circuit.cx(i, i + 1)

        # Add some single-qubit rotations
        for i in range(5):
            circuit.rz(0.5, i)
            circuit.sx(i)

        # Add measurement
        circuit.measure_all()

        return circuit


def main() -> int:
    """Main entry point for the CLI."""
    cli = AriadneCLI()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())
