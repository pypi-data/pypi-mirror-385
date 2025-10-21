Installation
============

Requirements
------------

* Python 3.11 or higher
* pip package manager

Basic Installation
------------------

Install the latest stable version from PyPI:

.. code-block:: bash

   pip install neurological-lrd-analysis

Development Installation
------------------------

For development or to get the latest features, install from the GitHub repository:

.. code-block:: bash

   git clone https://github.com/dave2k77/neurological_lrd_analysis.git
   cd neurological_lrd_analysis
   pip install -e .

Optional Dependencies
---------------------

GPU Support
~~~~~~~~~~~

For GPU acceleration with JAX:

.. code-block:: bash

   pip install neurological-lrd-analysis[gpu]

This installs JAX with CUDA support and CuPy for GPU computations.

Development Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~

For development and testing:

.. code-block:: bash

   pip install neurological-lrd-analysis[dev]

This includes:
* pytest for testing
* black and isort for code formatting
* flake8 for linting
* mypy for type checking
* Sphinx for documentation

Documentation Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~

For building documentation:

.. code-block:: bash

   pip install neurological-lrd-analysis[docs]

This includes Sphinx and related documentation tools.

Verification
------------

Verify the installation:

.. code-block:: python

   import neurological_lrd_analysis
   print(neurological_lrd_analysis.__version__)

   # Test basic functionality
   from neurological_lrd_analysis import BiomedicalHurstEstimatorFactory
   factory = BiomedicalHurstEstimatorFactory()
   print("Installation successful!")

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**ImportError: No module named 'neurological_lrd_analysis'**

Make sure you're using the correct Python environment and the package is installed:

.. code-block:: bash

   python -c "import sys; print(sys.path)"
   pip list | grep neurological

**CUDA/JAX Issues**

If you encounter CUDA-related issues:

.. code-block:: bash

   # Check CUDA installation
   nvidia-smi
   
   # Reinstall JAX with correct CUDA version
   pip uninstall jax jaxlib
   pip install jax[cuda12_pip]  # or cuda11_pip depending on your CUDA version

**Memory Issues**

For large datasets, consider:

.. code-block:: python

   # Use smaller batch sizes
   config = BenchmarkConfig(
       n_bootstrap=50,  # Reduce from default 100
       # ... other parameters
   )

Performance Optimization
------------------------

CPU Optimization
~~~~~~~~~~~~~~~~

For CPU-only systems, Numba can provide significant speedups:

.. code-block:: bash

   pip install numba

GPU Optimization
~~~~~~~~~~~~~~~~

For GPU systems, ensure proper CUDA installation:

.. code-block:: bash

   # Check CUDA version
   nvcc --version
   
   # Install appropriate JAX version
   pip install jax[cuda12_pip]  # For CUDA 12.x
   pip install jax[cuda11_pip]  # For CUDA 11.x

Environment Setup
-----------------

Virtual Environment
~~~~~~~~~~~~~~~~~~~

It's recommended to use a virtual environment:

.. code-block:: bash

   # Create virtual environment
   python -m venv neurological_env
   
   # Activate (Linux/macOS)
   source neurological_env/bin/activate
   
   # Activate (Windows)
   neurological_env\Scripts\activate
   
   # Install package
   pip install neurological-lrd-analysis

Conda Environment
~~~~~~~~~~~~~~~~~

Using conda:

.. code-block:: bash

   # Create conda environment
   conda create -n neurological python=3.11
   conda activate neurological
   
   # Install package
   pip install neurological-lrd-analysis

Docker
~~~~~~

For containerized deployment:

.. code-block:: dockerfile

   FROM python:3.11-slim
   
   RUN pip install neurological-lrd-analysis
   
   # Add your application code here
   COPY . /app
   WORKDIR /app
   
   CMD ["python", "your_script.py"]

Platform-Specific Notes
-----------------------

Linux
~~~~~

Most dependencies should install without issues. For GPU support, ensure NVIDIA drivers are installed.

macOS
~~~~~

For Apple Silicon (M1/M2) Macs, JAX may have limited GPU support. Use CPU-only installations for best compatibility.

Windows
~~~~~~~

Use WSL2 or a Linux-like environment for best compatibility. Native Windows support is limited.

Getting Help
------------

If you encounter issues:

1. Check the `troubleshooting section <#troubleshooting>`_
2. Search existing `issues <https://github.com/dave2k77/neurological_lrd_analysis/issues>`_
3. Create a new issue with detailed information about your environment and error messages
