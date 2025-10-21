.PHONY: help test test-integration lint fmt clean

PYTHON ?= python
PIP ?= $(PYTHON) -m pip
PYTEST ?= pytest

help:
	@echo "Common targets:"
	@echo "  make test              Run unit tests only"
	@echo "  make test-integration  Run integration tests (requires DB + AMDS client)"
	@echo "  make lint              Run ruff/flake8 linting"
	@echo "  make fmt               Auto-format with black"
	@echo "  make clean             Remove caches and build artifacts"

test:
	$(PYTEST) tests/unit -q

test-integration:
	@if [ -z "$$DATABASE_URL" ]; then \
		echo "DATABASE_URL not set; integration tests will fail."; \
	fi
	$(PYTEST) tests/integration -q

lint:
	@which ruff >/dev/null 2>&1 && ruff check src tests || echo "ruff not installed"

fmt:
	@which black >/dev/null 2>&1 && black src tests || echo "black not installed"

clean:
	rm -rf .pytest_cache __pycache__ build dist *.egg-info
