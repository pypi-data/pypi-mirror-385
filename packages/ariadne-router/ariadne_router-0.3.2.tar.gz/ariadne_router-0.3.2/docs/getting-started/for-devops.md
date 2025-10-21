# Getting Started for DevOps Engineers

This guide provides everything you need to integrate Ariadne into CI/CD pipelines, manage configurations across environments, and ensure reliable quantum simulation in production systems.

## Installation

Ariadne installs consistently across all platforms:

```bash
pip install ariadne-router
```

For minimal dependencies in containerized environments:
```bash
pip install ariadne-router --no-deps
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Quantum Simulation Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.11, 3.12]

    steps:
    - uses: actions/checkout@v3
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install Ariadne
      run: |
        pip install ariadne-router

    - name: Run quantum tests
      run: |
        python -c "from ariadne import simulate; print('Ariadne ready!')"
        python -m pytest tests/
```

### Docker Configuration

```dockerfile
FROM python:3.11-slim

# Install Ariadne with minimal dependencies
RUN pip install ariadne-router

# Copy your quantum code
COPY . /app
WORKDIR /app

# Run your quantum application
CMD ["python", "your_quantum_app.py"]
```

## Configuration Management

### 1. Programmatic Configuration

```python
from ariadne import configure_ariadne, get_config_manager

# Configure for production environments
config_manager = get_config_manager()
config_manager.set_backend_fallback(True)  # Enable fallbacks
config_manager.set_timeout(300)  # 5-minute timeout
config_manager.set_max_memory_gb(8)  # Limit memory usage

# Apply configuration
configure_ariadne(config_manager.get_config())
```

### 2. Configuration Files

```yaml
# config.yaml
ariadne:
  backends:
    fallback_enabled: true
    timeout_seconds: 300
    max_memory_gb: 8
  routing:
    strategy: "production_mode"
    explanation_enabled: true
  logging:
    level: "INFO"
    format: "json"
```

```python
# Load configuration from file
from ariadne.config import load_config

config = load_config(["config.yaml"])
configure_ariadne(config)
```

## Production-Ready Simulation

### 1. Robust Error Handling

```python
from ariadne import simulate
from ariadne.types import BackendType

def robust_simulation(circuit, retries=3, **kwargs):
    """Robust simulation with retries and error handling."""
    for i in range(retries):
        try:
            result = simulate(circuit, **kwargs)

            # Log routing decision for audit trail
            print(f"Backend used: {result.backend_used}")
            print(f"Execution time: {result.execution_time}s")
            print(f"Routing explanation: {result.routing_explanation}")

            return result
        except Exception as e:
            print(f"Simulation attempt {i+1} failed: {e}")
            if i == retries - 1:  # Last attempt
                raise
            # Try with different parameters
            if "backend" not in kwargs:
                # Force a specific backend on retry
                kwargs["backend"] = BackendType.QISKIT.value

    return None
```

### 2. Resource Management

```python
from ariadne import get_resource_manager

def manage_resources():
    """Monitor and manage system resources."""
    rm = get_resource_manager()

    # Check available memory
    available_memory = rm.get_available_memory()
    print(f"Available memory: {available_memory} GB")

    # Monitor backend pools
    pool_stats = rm.get_pool_statistics()
    print(f"Backend pools: {pool_stats}")

    # Clean up if needed
    if available_memory < 1.0:  # Less than 1GB available
        rm.cleanup_resources()
```

## Monitoring and Logging

### 1. Structured Logging

```python
from ariadne import configure_logging, get_logger

# Configure JSON logging for log aggregation
configure_logging(level="INFO", format="json")

logger = get_logger("quantum_simulation")

def log_simulation(circuit, shots=1000):
    """Log simulation with structured data."""
    logger.info("Starting quantum simulation", extra={
        "circuit_qubits": circuit.num_qubits,
        "circuit_depth": circuit.depth(),
        "shots": shots
    })

    result = simulate(circuit, shots=shots)

    logger.info("Simulation completed", extra={
        "backend_used": result.backend_used.value,
        "execution_time": result.execution_time,
        "unique_outcomes": len(result.counts),
        "routing_explanation": result.routing_explanation
    })

    return result
```

### 2. Health Checks

```python
from ariadne.backends import get_health_checker

def check_system_health():
    """Check backend health for production monitoring."""
    health_checker = get_health_checker()

    all_healthy = True
    for backend_type in health_checker.get_available_backends():
        metrics = health_checker.get_backend_metrics(backend_type)
        print(f"{backend_type.value}: {metrics.status.value}")

        if metrics.status.value != "healthy":
            all_healthy = False
            print(f"  Issues: {metrics.details}")

    return all_healthy
```

## Automation and Orchestration

### 1. Batch Processing

```python
from ariadne import simulate
from concurrent.futures import ThreadPoolExecutor
import time

def batch_simulate(circuits, shots=1000, max_workers=4):
    """Process multiple circuits in parallel."""
    def simulate_single(circuit):
        start = time.time()
        result = simulate(circuit, shots=shots)
        end = time.time()
        return {
            'result': result,
            'processing_time': end - start,
            'circuit_info': {
                'qubits': circuit.num_qubits,
                'depth': circuit.depth()
            }
        }

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(simulate_single, circuits))

    return results
```

### 2. Performance Monitoring

```python
import json
from datetime import datetime

def benchmark_backends(circuit, output_file="benchmark_results.json"):
    """Benchmark all available backends and save results."""
    from ariadne.types import BackendType

    results = {
        "timestamp": datetime.now().isoformat(),
        "circuit_info": {
            "qubits": circuit.num_qubits,
            "depth": circuit.depth(),
            "size": circuit.size()
        },
        "benchmark_results": {}
    }

    for backend in BackendType:
        try:
            import time
            start = time.time()
            result = simulate(circuit, shots=1000, backend=backend.value)
            end = time.time()

            results["benchmark_results"][backend.value] = {
                "success": True,
                "execution_time": end - start,
                "backend_used": result.backend_used.value,
                "throughput": 1000 / (end - start)  # shots per second
            }
        except Exception as e:
            results["benchmark_results"][backend.value] = {
                "success": False,
                "error": str(e)
            }

    # Save results
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    return results
```

## DevOps Best Practices

### 1. Environment Consistency

- Use the same Ariadne version across dev, staging, and production
- Pin dependencies in requirements.txt
- Use containerization to ensure consistent environments

### 2. Fail-Safe Operations

- Enable backend fallbacks in production
- Set appropriate timeouts to prevent hanging jobs
- Monitor resource usage to prevent system overload

### 3. Monitoring and Alerting

```bash
# CLI command for health checks
ariadne status --detailed

# Performance monitoring
ariadne benchmark --circuit test_circuit.qasm --output results.json
```

## Troubleshooting

- **Dependency Issues**: Use `pip check` to verify dependency consistency
- **Memory Usage**: Monitor with `ariadne status` and configure limits appropriately
- **Backend Failures**: Check `ariadne status` to identify unhealthy backends
- **Performance**: Run `ariadne benchmark` to establish baselines

## Next Steps

- Review the [Core Concepts](../user-guide/core-concepts.md) for system architecture
- Explore the [API Reference](../user-guide/api-reference.md) for automation tools
- Check the [Troubleshooting Guide](../reference/troubleshooting.md) for common issues
- Try the [Configuration Examples](../reference/configuration.md) for advanced setups
