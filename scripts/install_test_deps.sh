#!/usr/bin/env bash
# Install dependencies required for running the test suite.
# Run from the repository root.
set -e

# Upgrade pip to reduce possible install issues.
pip install --upgrade pip

# Install project and runtime dependencies
if [ -f requirements.txt ]; then
    pip install -r requirements.txt
fi

# Install the package itself in editable mode
if [ -f pyproject.toml ]; then
    pip install -e .
fi

# PyQt6-stubs provides type information for PyQt and is small enough for CI
pip install PyQt6-stubs
