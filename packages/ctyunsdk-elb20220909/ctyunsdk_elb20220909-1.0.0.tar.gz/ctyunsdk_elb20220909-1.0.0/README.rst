
=================
 CTyun OpenAPI SDK for Python
=================
Setup
-----

First, you need to create a virtual environment and activate it.

::

  $ pip install virtualenv
  $ virtualenv .venv
  $ . .venv/bin/activate
  (.venv)$

For Windows users:

::

  $ python -m pip install virtualenv
  $ python -m virtualenv .venv
  $ . .venv/Scripts/activate
  (.venv)$

Next, install ``pytest libs`` in the environment.

::
  (.venv)$ python -m pip install -r requirements.txt
  (.venv)$ python -m pip setuptools
  (.venv)$ python setup.py install

Or build wheel and then install with pip

::
  (.venv)$ python -m pip install build
  (.venv)$ python -m build -n
  (.venv)$ python -m pip install --force-reinstall dist/ctyunsdk_elb20220909-1.0.0-*.whl

Usage
-----

To see a list of commands available, run::

  (.venv)$ python ctyunsdk_elb20220909/tests/xxx.py

Cleaning Up
-----------

Finally, when done, deactivate your virtual environment::

::
  (.venv)$ deactivate
  $
