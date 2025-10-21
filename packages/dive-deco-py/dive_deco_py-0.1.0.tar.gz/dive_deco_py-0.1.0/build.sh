#!/bin/zsh
# Build script for maturin develop

# Activate virtual environment if it exists
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

# Run maturin develop
maturin develop

