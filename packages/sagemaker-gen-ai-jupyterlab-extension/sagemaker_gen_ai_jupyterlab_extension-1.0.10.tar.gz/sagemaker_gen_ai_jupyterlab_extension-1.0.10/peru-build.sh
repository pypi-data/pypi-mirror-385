#!/bin/bash
set -e

echo "Starting Peru build for SageMaker GenAI JupyterLab Extension"

# Rename pyproject.toml to avoid conflicts with setup.py
mv pyproject.toml pyproject.toml.bak 2>/dev/null || true

# Build using setuptools (no network access in Peru)
python setup.py sdist

# Restore pyproject.toml
mv pyproject.toml.bak pyproject.toml 2>/dev/null || true

echo "Peru build completed successfully"