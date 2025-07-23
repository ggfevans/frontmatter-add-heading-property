# Makefile for add_headings.py project
# Provides convenient commands for testing and development

.PHONY: help test test-unit test-integration test-coverage test-fast lint format install-dev clean all

# Default target
help:
	@echo "Available commands:"
	@echo "  test            - Run all tests"
	@echo "  test-unit       - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-coverage   - Run tests with coverage report"
	@echo "  test-fast       - Run fast tests only (exclude slow tests)"
	@echo "  lint            - Run code quality checks"
	@echo "  format          - Format code with black and isort"
	@echo "  install-dev     - Install development dependencies"
	@echo "  clean           - Clean up generated files"
	@echo "  all             - Run all tests and quality checks"

# Install development dependencies
install-dev:
	pip install -r requirements-dev.txt

# Run all tests
test:
	python -m pytest

# Run unit tests only
test-unit:
	python -m pytest -m unit

# Run integration tests only
test-integration:
	python -m pytest -m integration

# Run tests with coverage
test-coverage:
	python -m pytest --cov=add_headings --cov-report=html --cov-report=term

# Run fast tests only
test-fast:
	python -m pytest -m "not slow"

# Run code quality checks
lint:
	python -m flake8 add_headings.py tests/
	python -m black --check add_headings.py tests/
	python -m isort --check-only add_headings.py tests/
	python -m mypy add_headings.py

# Format code
format:
	python -m black add_headings.py tests/
	python -m isort add_headings.py tests/

# Clean up generated files
clean:
	rm -rf __pycache__/
	rm -rf tests/__pycache__/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .mypy_cache/
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name "*~" -delete

# Run everything
all: test-coverage lint
	@echo "All checks completed!"

# Quick smoke test
smoke:
	python -m pytest -m smoke -x