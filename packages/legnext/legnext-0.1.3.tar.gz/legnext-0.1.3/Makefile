.PHONY: help install test lint format type-check clean build publish

help:
	@echo "Legnext Python SDK - Available commands:"
	@echo "  make install      Install package and dev dependencies"
	@echo "  make test         Run tests with coverage"
	@echo "  make lint         Run linters (ruff)"
	@echo "  make format       Format code (black, isort)"
	@echo "  make type-check   Run type checker (mypy)"
	@echo "  make clean        Clean build artifacts"
	@echo "  make build        Build distribution packages"
	@echo "  make publish      Publish to PyPI (requires credentials)"

install:
	uv pip install -e ".[dev]"

test:
	pytest --cov=legnext --cov-report=term-missing --cov-report=html

lint:
	ruff check src tests

format:
	black src tests examples
	isort src tests examples

type-check:
	mypy src

clean:
	rm -rf build dist *.egg-info
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	rm -rf htmlcov .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

publish: build
	twine check dist/*
	twine upload dist/*

# Development shortcuts
dev: format lint type-check test

all: clean install dev
