.PHONY: help install install-dev sync build clean test lint format type-check publish publish-test run-example

# Default target
help:
	@echo "SAM Mask CLI - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  install      Install package in development mode"
	@echo "  install-dev  Install with development dependencies"
	@echo "  sync         Sync dependencies from lock file"
	@echo ""
	@echo "Development:"
	@echo "  test         Run tests"
	@echo "  lint         Run linting (flake8)"
	@echo "  format       Format code (black + isort)"
	@echo "  type-check   Run type checking (mypy)"
	@echo "  check-all    Run all quality checks"
	@echo ""
	@echo "Build & Publish:"
	@echo "  build        Build wheel and source distribution"
	@echo "  clean        Clean build artifacts"
	@echo "  publish-test Publish to TestPyPI"
	@echo "  publish      Publish to PyPI"
	@echo ""
	@echo "Examples:"
	@echo "  run-example  Run CLI with test image"

# Installation
install:
	uv pip install -e .

install-dev:
	uv pip install -e ".[dev]"

sync:
	uv pip sync uv.lock

# Development
test:
	uv run pytest

lint:
	uv run flake8 sam_mask_cli/

format:
	uv run black sam_mask_cli/
	uv run isort sam_mask_cli/

type-check:
	uv run mypy sam_mask_cli/

check-all: format lint type-check test

# Build and publish
build: clean
	uv build

clean:
	rm -rf dist/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

publish-test: build
	uv tool run twine upload --repository testpypi dist/*

publish: build
	uv tool run twine upload dist/*

# Example usage
run-example:
	@if [ ! -f test.webp ]; then \
		echo "test.webp not found. Please ensure test image exists."; \
		exit 1; \
	fi
	sam-mask-cli test.webp "981,57,1261,720" ./ example_output.png
	@echo "Example completed. Check example_output.png"

# Development environment setup
dev-setup: install-dev
	@echo "Development environment setup complete!"
	@echo "Run 'make help' to see available commands."

# Version bump helpers
version-patch:
	@echo "Current version: $$(grep '^version = ' pyproject.toml | cut -d'"' -f2)"
	@echo "Please manually update version in pyproject.toml"

version-minor:
	@echo "Current version: $$(grep '^version = ' pyproject.toml | cut -d'"' -f2)"
	@echo "Please manually update version in pyproject.toml"

version-major:
	@echo "Current version: $$(grep '^version = ' pyproject.toml | cut -d'"' -f2)"
	@echo "Please manually update version in pyproject.toml"
