#!/usr/bin/env python3
"""
Setup script for Neurological LRD Analysis package.

This file is provided for backward compatibility with older pip versions
and tools that don't support pyproject.toml yet.
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "A comprehensive library for estimating Hurst exponents in neurological time series data"

# Read requirements
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(req_path):
        with open(req_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="neurological-lrd-analysis",
    version="0.4.1",
    description="A comprehensive library for estimating Hurst exponents in neurological time series data",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Davian R. Chin",
    author_email="d.r.chin@pgr.reading.ac.uk",
    url="https://github.com/dave2k77/neurological_lrd_analysis",
    project_urls={
        "Homepage": "https://github.com/dave2k77/neurological_lrd_analysis",
        "Documentation": "https://neurological-lrd-analysis.readthedocs.io",
        "Repository": "https://github.com/dave2k77/neurological_lrd_analysis.git",
        "Issues": "https://github.com/dave2k77/neurological_lrd_analysis/issues",
        "Changelog": "https://github.com/dave2k77/neurological_lrd_analysis/blob/main/CHANGELOG.md",
    },
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-html>=3.0.0",
            "pytest-json-report>=1.5.0",
            "pytest-timeout>=2.1.0",
            "psutil>=5.9.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=6.0.0",
            "sphinx-rtd-theme>=1.2.0",
            "myst-parser>=1.0.0",
        ],
        "gpu": [
            "jax[cuda12_pip]>=0.4.1",
            "cupy-cuda12x>=12.0.0",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Healthcare Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    keywords=[
        "hurst", "long-range-dependence", "neurological", "time-series", "fractal",
        "eeg", "ecg", "neuroscience", "parkinson", "epilepsy", "wavelet",
        "multifractal", "benchmarking", "biomedical"
    ],
    include_package_data=True,
    zip_safe=False,
)
