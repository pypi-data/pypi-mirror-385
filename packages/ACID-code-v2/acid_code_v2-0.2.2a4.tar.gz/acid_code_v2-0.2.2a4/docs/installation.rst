.. _installation:

Installation
--------------

Installing the package
=======================

ACID_v2 has been tested in Python 3.11, and is currently incompatible with 3.12. It is recommended to install ACID in a new conda environment to avoid dependency conflicts.

In this example we create an environment named 'acid' and activate it using:

.. code-block:: bash

    conda create -n acid python=3.11
    conda activate acid

Once the environment has been activated ACID can be installed using pip_:

.. _pip: https://pip.pypa.io/en/stable/ 

.. code-block:: bash

    pip install ACID_code_v2

.. _source:

Installing from the source
===========================
In order to use the example data (for the tutorials) or the test suite ACID will need to be installed from the source (i.e. directly from the GitHub repository).
This can be done by cloning the source repository and installing from there.

.. code-block:: bash

    git clone https://github.com/ldolan05/ACID.git
    cd ACID
    python -m pip install -e .

.. _test:

Testing the installation
==========================

Test your installation by running our test file in the test directory using pytest_. This may take a while (~1-2 min) but should run without any errors if the installation has gone smoothly.

.. _pytest: https://docs.pytest.org/en/7.4.x/contents.html

.. code-block:: bash
    
    pytest tests.py


