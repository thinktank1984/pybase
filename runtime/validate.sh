#!/bin/bash
# Wrapper script to run model validation with proper environment

# Change to runtime directory
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -f "../venv/bin/activate" ]; then
    source ../venv/bin/activate
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Run validation
python validate_models.py "$@"

