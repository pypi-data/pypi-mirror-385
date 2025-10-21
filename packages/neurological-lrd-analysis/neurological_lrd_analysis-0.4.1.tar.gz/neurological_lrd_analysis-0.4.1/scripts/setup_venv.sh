#!/bin/bash
# Setup script for the biomedical_hurst_factory project
# Creates and configures the 'biomedical_hurst_env' virtual environment

set -e  # Exit on any error

echo "Setting up biomedical_hurst_factory development environment..."
echo "=============================================================="

# Check if Python 3.11+ is available
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python 3.11+ is required, but found Python $python_version"
    echo "Please install Python 3.11 or later"
    exit 1
fi

echo "✓ Python version check passed: $python_version"

# Create virtual environment
echo "Creating virtual environment 'biomedical_hurst_env'..."
if [ -d "biomedical_hurst_env" ]; then
    echo "Virtual environment 'biomedical_hurst_env' already exists. Removing it..."
    rm -rf biomedical_hurst_env
fi

python3 -m venv biomedical_hurst_env
echo "✓ Virtual environment created"

# Activate virtual environment
echo "Activating virtual environment..."
source biomedical_hurst_env/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install project dependencies
echo "Installing project dependencies..."
pip install -e .

# Install development dependencies
echo "Installing development dependencies..."
pip install pytest pytest-cov pytest-html pytest-json-report pytest-timeout

# Install optional dependencies for enhanced functionality
echo "Installing optional dependencies..."
pip install jax jaxlib numba scikit-learn matplotlib seaborn

echo ""
echo "Setup completed successfully!"
echo "============================="
echo ""
echo "To activate the environment in the future, run:"
echo "  source biomedical_hurst_env/bin/activate"
echo ""
echo "To deactivate the environment, run:"
echo "  deactivate"
echo ""
echo "To run tests:"
echo "  python -m pytest estimator_testing_validation/ -v"
echo ""
echo "To run the demo:"
echo "  python biomedical_hurst_factory.py"
echo ""

