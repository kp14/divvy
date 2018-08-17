.. _installation:

Installing Divvy
================

Divvy is packaged as a wheel and can be installed using `pip <https://pip.pypa.io/en/stable/>`_.
This will also install all the dependencies.
Divvy has been run on Python 3.6.
As usual, it probably best to install Divvy and its dependencies into a dedicated virtual environment.

#. Create a virtual environment

    Using ``conda`` from the `Anaconda Python distribution <https://www.continuum.io/downloads>`_ :

        * Create a new environment (env) called *divvy* which runs Python 3.6 and has ``pip`` installed::

            conda create -n divvy python=3.6 pip

        * Activate the env::

            conda activate divvy

    In a regular Python installation, *venv* can be used to create such an environment.

#. In the dedicated virtual env, install divvy with its dependencies::

        pip install Divvy-<version-py3-none-any.whl>

