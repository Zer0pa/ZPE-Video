.PHONY: install install-producer install-all test test-core test-all lint format build clean verify-package

PYTHON ?= python3.11
PIP ?= $(PYTHON) -m pip
PYTEST ?= $(PYTHON) -m pytest

# -----------------------------------------------------------------------------
# Install
# -----------------------------------------------------------------------------

install:
	$(PIP) install -e '.[dev]'

install-producer:
	$(PIP) install -e '.[dev,producer]'

install-all:
	$(PIP) install -e '.[all]'

# -----------------------------------------------------------------------------
# Test
# -----------------------------------------------------------------------------

test: test-core

test-core:
	$(PYTEST) tests/test_receipt.py -v

test-all:
	$(PYTEST) tests -v

# -----------------------------------------------------------------------------
# Lint / format
# -----------------------------------------------------------------------------

lint:
	$(PYTHON) -m ruff check src tests

format:
	$(PYTHON) -m ruff format src tests
	$(PYTHON) -m ruff check --fix src tests

# -----------------------------------------------------------------------------
# Build
# -----------------------------------------------------------------------------

build:
	$(PIP) install --upgrade build
	$(PYTHON) -m build

verify-package: build
	$(PYTHON) -m venv .venv-wheel
	. .venv-wheel/bin/activate && $(PIP) install --upgrade pip && $(PIP) install dist/*.whl && $(PYTHON) -c "import zpe_video; assert sorted(zpe_video.__all__); print('wheel OK', zpe_video.__version__)"
	rm -rf .venv-wheel

# -----------------------------------------------------------------------------
# Housekeeping
# -----------------------------------------------------------------------------

clean:
	rm -rf build dist *.egg-info src/*.egg-info .pytest_cache .coverage htmlcov .ruff_cache
