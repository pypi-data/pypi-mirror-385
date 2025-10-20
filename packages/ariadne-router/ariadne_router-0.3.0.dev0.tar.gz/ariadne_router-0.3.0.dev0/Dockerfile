# Ariadne Quantum Circuit Router - Multi-Platform Container
#
# This Dockerfile creates a containerized environment for Ariadne that supports:
# - CPU-based quantum simulation (all platforms)
# - Automated testing and benchmarking
# - Development and research workflows
#
# Multi-stage build optimized for different use cases

# =============================================================================
# Stage 1: Base Python Environment
# =============================================================================
FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash ariadne
WORKDIR /home/ariadne

# =============================================================================
# Stage 2: Development Environment
# =============================================================================
FROM base AS development

# Install development dependencies
RUN apt-get update && apt-get install -y \
    vim \
    nano \
    htop \
    tree \
    && rm -rf /var/lib/apt/lists/*

# Copy source code
COPY --chown=ariadne:ariadne . ./ariadne/

# Install Ariadne in development mode
RUN cd ariadne && pip install -e ".[dev]"

# Switch to non-root user
USER ariadne

# Set up environment
ENV ARIADNE_LOG_LEVEL=INFO
ENV ARIADNE_BACKEND_PREFERENCE="stim,tensor_network,qiskit"
ENV PYTHONPATH=/home/ariadne/ariadne/src

# Default command for development
CMD ["/bin/bash"]

# =============================================================================
# Stage 3: Testing Environment
# =============================================================================
FROM development AS testing

# Copy test configuration
COPY --chown=ariadne:ariadne pytest.ini pyproject.toml ./ariadne/

# Set environment for testing
ENV ARIADNE_ENABLE_BENCHMARKS=true
ENV PYTEST_TIMEOUT=30

# Default command runs test suite
CMD ["python", "-m", "pytest", "ariadne/tests/", "-v", "--tb=short"]

# =============================================================================
# Stage 4: Benchmark Environment
# =============================================================================
FROM development AS benchmark

# Create benchmark results directory
RUN mkdir -p /home/ariadne/benchmark_results

# Set environment for benchmarking
ENV ARIADNE_ENABLE_BENCHMARKS=true
ENV ARIADNE_MEMORY_LIMIT_MB=4096

# Default command runs benchmark suite
CMD ["python", "ariadne/benchmarks/reproducible_benchmark.py"]

# =============================================================================
# Stage 5: Production Environment (Lightweight)
# =============================================================================
FROM base AS production

# Copy source code
COPY --chown=ariadne:ariadne src/ ./ariadne/src/
COPY --chown=ariadne:ariadne pyproject.toml ./ariadne/

# Install Ariadne
RUN cd ariadne && pip install .

# Switch to non-root user
USER ariadne

# Set up production environment
ENV ARIADNE_LOG_LEVEL=WARNING
ENV ARIADNE_BACKEND_PREFERENCE="stim,qiskit"

# Create volume mount point for results
VOLUME ["/home/ariadne/results"]

# Default production command
CMD ["python", "-c", "import ariadne; print('Ariadne Quantum Router ready')"]

# =============================================================================
# Metadata and Labels
# =============================================================================

# Add labels for container metadata
LABEL org.opencontainers.image.title="Ariadne Quantum Circuit Router"
LABEL org.opencontainers.image.description="Intelligent quantum circuit routing with automatic backend selection"
LABEL org.opencontainers.image.authors="Hmbown"
LABEL org.opencontainers.image.url="https://github.com/Hmbown/ariadne"
LABEL org.opencontainers.image.source="https://github.com/Hmbown/ariadne"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.licenses="Apache-2.0"

# Expose port for potential web interface (future)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import ariadne; print('OK')" || exit 1
