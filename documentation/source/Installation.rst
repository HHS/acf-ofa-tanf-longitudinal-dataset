Installation
============

Requirements
------------

-  Python 3.12 or greater.
-  Git
-  A GitHub account

Creating a virtual environment
------------------------------

To keep the OFA TANF Longitudinal Dataset (OTLD) project separate from
your other projects and avoid conflicting package installations, it is
best to install the project in a virtual environment. With Python
installed on your computer (and assuming a Windows environment), the
following command can be used to create a virtual environment:

.. code-block::

   py -m venv <name of virtual environment>

.. note::

   If you find that the above command does not work for you when trying to setup a virtual environment,
   please try:

   .. code-block::
      
      python -m venv <name of virtual environment>

Activate the virtual environment before installing any packages.
Assuming a virtual environment named .venv:

.. code-block::
   
   .venv\Scripts\Activate

See the `venv
documentation <https://docs.python.org/3/library/venv.html>`__ for
additional details.

Option 1: Cloning the repository
--------------------------------

First, clone the
`OTLD <https://github.com/HHS/acf-ofa-tanf-longitudinal-dataset>`__
repository from GitHub. Follow the steps in the GitHub documentation for
`cloning
repositories <https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository>`__
if you are unsure of how to proceed. Once you have the repository
cloned, create a virtual environment in the repository’s directory and
activate it. To install the OTLD package, use the following commands:

.. code-block::

   py -m pip install -U pip # (Optionally) Upgrade your installation of pip
   pip install . # Install the OTLD package 

Option 2: Installing directly from GitHub
-----------------------------------------

Navigate to the directory in which you would like to install the OTLD
package. Create and activate a virtual environment, or ensure a virtual
environment is active if one already exists. Run the following commands:

.. code-block::

   py -m pip install -U pip # (Optionally) Upgrade your installation of pip
   pip install git+https://github.com/HHS/acf-ofa-tanf-longitudinal-dataset@main # Install the OTLD package

You may be asked to authenticate your GitHub account. After
authentication, installation will begin.
