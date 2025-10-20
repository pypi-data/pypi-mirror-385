.PHONY: help install dev test lint format type-check clean build run pre-commit pre-commit-all

help:
	@echo "Nuha Development Commands"
	@echo ""
	@echo "  make install      - Install dependencies"
	@echo "  make dev          - Install in development mode"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run linter (ruff)"
	@echo "  make format       - Format code with ruff"
	@echo "  make type-check   - Run type checker (pyrefly)"
	@echo "  make pre-commit   - Run pre-commit hooks on staged files"
	@echo "  make pre-commit-all - Run pre-commit hooks on all files"
	@echo "  make clean        - Clean build artifacts"
	@echo "  make build        - Build binary"
	@echo "  make run          - Run nuha in development mode"
	@echo "  make all          - Run format, lint, type-check, and test"

install:
	uv sync

dev:
	uv sync
	uv pip install -e .

test:
	uv pip install -e ".[dev]"
	uv run pytest -v

test-cov:
	uv run pytest --cov=nuha --cov-report=html --cov-report=term

lint:
	uv pip install -e ".[dev]"
	uv run ruff check .

lint-fix:
	uv pip install -e ".[dev]"
	uv run ruff check --fix .

format:
	uv pip install -e ".[dev]"
	uv run ruff format .

format-check:
	uv pip install -e ".[dev]"
	uv run ruff format --check .

type-check:
	uv pip install -e ".[dev]"
	uv run pyrefly check .

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .pyrefly_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build:
	python setup_binary.py production

build-dev:
	python setup_binary.py dev

run:
	uv run nuha --help

pre-commit:
	pre-commit run

pre-commit-all:
	pre-commit run --all-files

all: format lint test
	@echo "✓ All checks passed!"
