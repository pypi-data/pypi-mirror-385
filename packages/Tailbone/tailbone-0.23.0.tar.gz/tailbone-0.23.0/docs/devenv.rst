
Development Environment
=======================

.. contents:: :local:

Base System
-----------

Development for Tailbone in particular is assumed to occur on a Linux machine.
This is because it's assumed that the web app would run on Linux.  It should be
possible (presumably) to do either on Windows or Mac but that is not officially
supported.

Furthermore it is assumed the Linux flavor in use is either Debian or Ubuntu,
or a similar alternative.  Presumably any Linux would work although some
details may differ from what's shown here.

Prerequisites
-------------

Python
^^^^^^

The only supported Python is 2.7.  Of course that should already be present on
Linux.

It usually is required at some point to compile C code for certain Python
extension modules.  In practice this means you probably want the Python header
files as well:

.. code-block:: sh

   sudo apt-get install python-dev

pip
^^^

The only supported Python package manager is ``pip``.  This can be installed a
few ways, one of which is:

.. code-block:: sh

   sudo apt-get install python-pip

virtualenvwrapper
^^^^^^^^^^^^^^^^^

While not technically required, it is recommended to use ``virtualenvwrapper``
as well.  There is more than one way to set this up, e.g.:

.. code-block:: sh

   sudo apt-get install python-virtualenvwrapper

The main variable as concerns these docs, is where your virtual environment(s)
will live.  If you install virtualenvwrapper via the above command, then most
likely your ``$WORKON_HOME`` environment variable will be set to
``~/.virtualenvs`` - however these docs will assume ``/srv/envs`` instead.
Please adjust any commands as needed.

PostgreSQL
^^^^^^^^^^

The other primary requirement is PostgreSQL.  Technically that may be installed
on a separate machine, which allows connection from the development machine.
But of course it will usually just be installed on the dev machine:

.. code-block:: sh

   sudo apt-get install postgresql

Regardless of where your PG server lives, you will probably need some extras in
order to compile extensions for the ``psycopg2`` package:

.. code-block:: sh

   sudo apt-get install libpq-dev
