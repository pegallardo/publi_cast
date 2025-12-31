.PHONY: help install install-dev test clean run lint format

help:
	@echo "PubliCast - Makefile Commands"
	@echo "=============================="
	@echo "install       - Install production dependencies"
	@echo "install-dev   - Install development dependencies"
	@echo "test          - Run tests with pytest"
	@echo "test-cov      - Run tests with coverage report"
	@echo "clean         - Remove build artifacts and cache files"
	@echo "run           - Run the application"
	@echo "lint          - Run code linters (flake8, pylint)"
	@echo "format        - Format code with black"
	@echo "format-check  - Check code formatting without changes"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

test:
	pytest

test-cov:
	pytest --cov=publi_cast --cov-report=html --cov-report=term

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

run:
	python -m publi_cast.main

lint:
	flake8 publi_cast/
	pylint publi_cast/

format:
	black publi_cast/

format-check:
	black --check publi_cast/

