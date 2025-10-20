# Ariadne Docker Container Guide

This guide covers how to use Ariadne's Docker containers for development, testing, and production workflows.

## Quick Start

### Pull Pre-built Images (Future)
```bash
# Pull latest production image
docker pull shannon-labs/ariadne:latest

# Pull development image
docker pull shannon-labs/ariadne:dev
```

### Build Locally
```bash
# Build all container variants
docker-compose build

# Build specific variant
docker build --target production -t ariadne:prod .
docker build --target development -t ariadne:dev .
```

## Container Variants

### 1. Development Container (`ariadne-dev`)
**Purpose:** Full development environment with all tools and dependencies.

```bash
# Start development environment
docker-compose up ariadne-dev

# Interactive development shell
docker-compose run --rm ariadne-dev

# Mount local code for development
docker run -it -v $(pwd):/home/ariadne/ariadne ariadne:dev
```

**Features:**
- Full Python development stack
- All Ariadne dependencies and optional backends
- Development tools (pytest, black, mypy, etc.)
- Interactive shell access
- Volume mounts for live code editing

### 2. Testing Container (`ariadne-test`)
**Purpose:** Automated testing and CI/CD validation.

```bash
# Run complete test suite
docker-compose up ariadne-test

# Run tests with custom options
docker-compose run --rm ariadne-test pytest tests/ -v -k "not slow"

# Generate coverage reports
docker-compose run --rm ariadne-test pytest --cov=ariadne --cov-report=html
```

**Features:**
- Standardized testing environment
- Pytest with coverage reporting
- JUnit XML output for CI integration
- Parallel test execution support

### 3. Benchmark Container (`ariadne-benchmark`)
**Purpose:** Performance validation and regression detection.

```bash
# Run reproducible benchmark suite
docker-compose up ariadne-benchmark

# Custom benchmark runs
docker-compose run --rm ariadne-benchmark python ariadne/benchmarks/reproducible_benchmark.py

# Resource-constrained benchmarks
docker run --cpus="2.0" --memory="4g" ariadne:benchmark
```

**Features:**
- Standardized performance testing environment
- Resource limits for consistent results
- Benchmark result export to volumes
- Memory and CPU usage monitoring

### 4. Production Container (`ariadne-prod`)
**Purpose:** Lightweight runtime for quantum circuit simulation.

```bash
# Run production service
docker-compose up ariadne-prod

# Process circuits from mounted directory
docker run -v /path/to/circuits:/home/ariadne/input \
           -v /path/to/results:/home/ariadne/results \
           ariadne:prod python -c "import ariadne; ariadne.process_directory('/home/ariadne/input')"
```

**Features:**
- Minimal dependencies for smaller image size
- Security hardened (non-root user)
- Optimized for production workloads
- Health checks and monitoring

## Usage Examples

### Development Workflow
```bash
# 1. Start development environment
docker-compose up -d ariadne-dev

# 2. Enter interactive shell
docker-compose exec ariadne-dev bash

# 3. Run tests
pytest tests/ -v

# 4. Run benchmarks
python benchmarks/reproducible_benchmark.py

# 5. Format code
black src/ariadne/
isort src/ariadne/
```

### CI/CD Integration
```yaml
# GitHub Actions example
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests in container
        run: docker-compose run --rm ariadne-test
      - name: Upload test results
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: test-results/
```

### Benchmark Validation
```bash
# Run benchmarks and save results
docker-compose run --rm ariadne-benchmark
docker cp $(docker-compose ps -q ariadne-benchmark):/home/ariadne/benchmark_results ./results

# Compare against baseline
python scripts/compare_benchmarks.py results/current.json results/baseline.json
```

## Environment Configuration

### Environment Variables
| Variable | Default | Description |
|----------|---------|-------------|
| `ARIADNE_LOG_LEVEL` | `INFO` | Logging verbosity (DEBUG, INFO, WARNING, ERROR) |
| `ARIADNE_BACKEND_PREFERENCE` | `"stim,tensor_network,qiskit"` | Preferred backend order |
| `ARIADNE_MEMORY_LIMIT_MB` | `2048` | Memory limit for large circuits |
| `ARIADNE_ENABLE_BENCHMARKS` | `false` | Enable performance profiling |
| `ARIADNE_CACHE_DIR` | `/tmp/ariadne_cache` | Circuit analysis cache location |

### Volume Mounts
| Mount Point | Purpose | Example |
|-------------|---------|---------|
| `/home/ariadne/ariadne` | Source code (development) | `-v $(pwd):/home/ariadne/ariadne` |
| `/home/ariadne/results` | Output results | `-v ./results:/home/ariadne/results` |
| `/home/ariadne/benchmark_results` | Benchmark outputs | `-v ./benchmarks:/home/ariadne/benchmark_results` |
| `/home/ariadne/test_results` | Test outputs | `-v ./test-results:/home/ariadne/test_results` |

## Performance Considerations

### Resource Limits
```yaml
# docker-compose.yml example
services:
  ariadne-benchmark:
    deploy:
      resources:
        limits:
          cpus: '4.0'
          memory: 8G
        reservations:
          cpus: '2.0'
          memory: 4G
```

### Memory Management
- Quantum simulations can be memory-intensive
- Use `ARIADNE_MEMORY_LIMIT_MB` to control memory usage
- Monitor container memory with `docker stats`
- Consider swapping for large circuits (development only)

## Platform Support

### CPU-Only Environments
All containers work in CPU-only environments with automatic fallback:
```bash
# Force CPU-only operation
docker run -e ARIADNE_BACKEND_PREFERENCE="stim,qiskit" ariadne:prod
```

### Apple Silicon Support
JAX-Metal support is available on Apple Silicon Macs:
```bash
# Build with Apple Silicon optimizations
docker build --platform linux/arm64 -t ariadne:arm64 .

# Note: Metal acceleration not available in containers
# Use native installation for Metal support
```

### GPU Support (Future)
CUDA support will be available in future versions:
```bash
# Future GPU-enabled container
docker run --gpus all ariadne:cuda
```

## Troubleshooting

### Common Issues

**Container won't start:**
```bash
# Check container logs
docker-compose logs ariadne-dev

# Verify image build
docker build --target development -t ariadne:dev .
```

**Tests failing in container:**
```bash
# Run specific test
docker-compose run --rm ariadne-test pytest tests/test_specific.py -v

# Check environment
docker-compose run --rm ariadne-test env
```

**Performance issues:**
```bash
# Monitor resource usage
docker stats

# Check memory limits
docker inspect ariadne-benchmark | grep -i memory

# Adjust resource limits in docker-compose.yml
```

### Debug Mode
```bash
# Enable debug logging
docker run -e ARIADNE_LOG_LEVEL=DEBUG ariadne:dev

# Interactive debugging
docker run -it --entrypoint=/bin/bash ariadne:dev
```

## Security Considerations

### Best Practices
- Containers run as non-root user (`ariadne`)
- No unnecessary privileges required
- Minimal attack surface in production image
- Regular security updates via base image updates

### Vulnerability Scanning
```bash
# Scan for vulnerabilities (if using security tools)
docker scan ariadne:prod

# Update base images regularly
docker-compose build --pull
```

## Contributing

### Building and Testing
```bash
# Build all variants
docker-compose build

# Test all services
docker-compose up ariadne-test ariadne-benchmark

# Verify production image
docker run --rm ariadne:prod python -c "import ariadne; print('OK')"
```

### Adding New Container Variants
1. Add new stage to `Dockerfile`
2. Add service to `docker-compose.yml`
3. Update this documentation
4. Test across platforms

## Support

For container-related issues:
1. Check container logs: `docker-compose logs <service>`
2. Verify environment variables and mounts
3. Test with fresh build: `docker-compose build --no-cache`
4. Report issues with container and host information
