.PHONY: test install dev-install lint format clean help

help:
	@echo "Ariadne Development Commands"
	@echo ""
	@echo "  make install      Install package in production mode"
	@echo "  make dev-install  Install package with development dependencies"
	@echo "  make test         Run test suite"
	@echo "  make lint         Check code quality with ruff and mypy"
	@echo "  make format       Format code with ruff and isort"
	@echo "  make clean        Remove build artifacts and cache files"

install:
	pip install -e .

dev-install:
	pip install -e ".[dev,apple,viz]"

test:
	pytest tests/ -v -n auto

lint:
	@echo "Running ruff..."
	ruff check src/ tests/
	@echo ""
	@echo "Running mypy..."
	mypy src/ariadne/
	@echo ""
	@echo "Lint check complete!"

format:
	@echo "Formatting with ruff..."
	ruff format src/ tests/
	@echo ""
	@echo "Formatting complete!"

clean:
	@echo "Cleaning build artifacts..."
	find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	rm -rf build/ dist/ htmlcov/ .coverage
	@echo "Clean complete!"
