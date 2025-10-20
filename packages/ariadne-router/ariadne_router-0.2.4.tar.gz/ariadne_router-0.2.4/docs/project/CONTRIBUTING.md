# Contributing to Ariadne 🤝

Thank you for your interest in contributing to Ariadne! We're building the future of intelligent quantum circuit routing, and we'd love your help.

## 🎯 Our Mission

Ariadne aims to democratize quantum computing by automatically routing circuits to their optimal simulators. Every contribution, no matter how small, helps achieve this goal.

## 🚀 Quick Start for Contributors

1. **Fork & Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/ariadne.git
   cd ariadne
   ```

2. **Set Up Development Environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install in development mode
   pip install -e ".[dev]"

   # Install pre-commit hooks
   pre-commit install
   ```

3. **Run Tests**
   ```bash
   pytest tests/
   python -m pytest tests/ -v  # Verbose output
   ```

## 📝 What Can You Contribute?

### 🐛 Bug Fixes
- Found a bug? Check if it's already reported in [Issues](https://github.com/Hmbown/ariadne/issues)
- Not reported? Create a new issue with a minimal reproduction example
- Want to fix it? Comment on the issue and submit a PR!

### ✨ New Features
- **New Backend Support**: Add support for more quantum simulators
- **Performance Optimizations**: Make routing decisions faster
- **Circuit Analysis**: Improve our circuit entropy calculations
- **Documentation**: Help others understand Ariadne better

### 📚 Documentation
- Fix typos, clarify explanations
- Add examples and tutorials
- Translate documentation
- Improve API documentation

### 🧪 Testing
- Add test cases for edge conditions
- Improve test coverage
- Add performance benchmarks
- Validate on different hardware

## 🔧 Development Process

### 1. Before You Start
- Check existing issues and PRs to avoid duplicates
- For major changes, open an issue for discussion first
- Ensure your fork is up to date with main

### 2. Making Changes
```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Make your changes
# ... edit files ...

# Run tests
pytest tests/

# Check code style
black ariadne/
ruff check ariadne/

# Commit with descriptive message
git commit -m "feat: add support for XYZ backend"
```

### 3. Commit Message Convention
We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test additions/modifications
- `perf:` Performance improvements
- `refactor:` Code refactoring
- `style:` Code style changes
- `chore:` Maintenance tasks

Examples:
```
feat: add IBM Qiskit Runtime backend support
fix: correct Clifford circuit detection for controlled gates
docs: add quantum teleportation example
perf: optimize circuit entropy calculation by 50%
```

### 4. Testing Requirements

Your PR must:
- ✅ Pass all existing tests
- ✅ Include tests for new functionality
- ✅ Maintain or improve code coverage (aim for >90%)
- ✅ Pass performance benchmarks

### 5. Pull Request Process

1. **Update your branch**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create Pull Request**
   - Use a clear, descriptive title
   - Reference any related issues
   - Include benchmark results if relevant
   - Add screenshots for UI changes

4. **PR Template** (automatically applied):
   ```markdown
   ## Description
   Brief description of changes

   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update

   ## Testing
   - [ ] Tests pass locally
   - [ ] Added new tests
   - [ ] Updated documentation

   ## Performance Impact
   - [ ] Benchmarks show no regression
   - [ ] Performance improvements measured

   ## Related Issues
   Fixes #123
   ```

## 🏗️ Architecture Overview

```
src/ariadne/
├── backends/      # Simulator backends (e.g., cuda, metal, cirq)
├── passes/        # Circuit transformation passes
├── route/         # Core routing logic and circuit analysis
├── __main__.py    # Command-line entry point
├── router.py      # Main QuantumRouter class
└── simulation.py  # Unified simulate() function
```

### Key Components

1. **QuantumRouter**: Main entry point for circuit routing
2. **CircuitAnalyzer**: Analyzes circuit properties
3. **BackendSelector**: Chooses optimal backend
4. **Converters**: Transform circuits between formats

## 💻 Code Style Guidelines

### Python Style
- Follow [PEP 8](https://pep8.org/)
- Use [Black](https://github.com/psf/black) for formatting
- Use [Ruff](https://github.com/astral-sh/ruff) for linting
- Type hints are required for all public APIs

### Documentation Style
- Use Google-style docstrings
- Include examples in docstrings
- Keep README examples working

Example:
```python
def route_circuit(circuit: QuantumCircuit, shots: int = 1024) -> Result:
    """Route a quantum circuit to the optimal backend.

    Args:
        circuit: The quantum circuit to route
        shots: Number of measurement shots

    Returns:
        Result object containing counts and metadata

    Example:
        >>> qc = QuantumCircuit(2)
        >>> qc.h(0)
        >>> qc.cx(0, 1)
        >>> result = route_circuit(qc, shots=1000)
        >>> print(result.counts)
        {'00': 512, '11': 488}
    """
```

## 🧪 Testing Guidelines

### Test Structure
```python
def test_feature_specific_behavior():
    """Test that feature X produces expected output Y."""
    # Arrange
    circuit = create_test_circuit()

    # Act
    result = route_circuit(circuit)

    # Assert
    assert result.backend_used == "expected_backend"
```

### Performance Tests
```python
@pytest.mark.benchmark
def test_routing_performance(benchmark):
    """Ensure routing decision takes < 10ms."""
    circuit = create_large_circuit(100)
    result = benchmark(route_circuit, circuit)
    assert benchmark.stats["mean"] < 0.01  # 10ms
```

## 🔒 Security

- Never commit credentials or API keys
- Report security vulnerabilities through [GitHub Security Advisories](https://github.com/Hmbown/ariadne/security/advisories)
- Use environment variables for sensitive configuration

## 📈 Performance Contributions

When claiming performance improvements:
1. Provide reproducible benchmarks
2. Test on multiple hardware configurations
3. Compare against current main branch
4. Document the optimization technique

## 🌐 Community

- **GitHub Discussions:** [Ask questions and share ideas](https://github.com/Hmbown/ariadne/discussions)
- **Issue Tracker:** [Report bugs and request features](https://github.com/Hmbown/ariadne/issues)

## 📜 License

By contributing, you agree that your contributions will be licensed under the Apache 2.0 License, the same license as the project.

## 🙏 Recognition

Contributors are recognized in:
- [CONTRIBUTORS.md](CONTRIBUTORS.md)
- Release notes
- Project website

## 📮 Getting Help

- 💬 [GitHub Discussions](https://github.com/Hmbown/ariadne/discussions): Ask questions and get help
- 🐛 [GitHub Issues](https://github.com/Hmbown/ariadne/issues): Bug reports and feature requests

---

**Thank you for making Ariadne better! 🚀**

*"The best way to predict the future is to invent it."* - Alan Kay
