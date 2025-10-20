
Migrating the Schema
====================

.. contents:: :local:

As development progresses for your custom app, you may need to migrate the
database schema from time to time.

See also this general discussion of the :doc:`concepts/schema`.

.. note::

   The only "safe" migrations are those which add or modify (or remove)
   "custom" tables, i.e. those *not* provided by the ``rattail.db.model``
   package.  This doc assumes you are aware of this and are only attempting a
   safe migration.


Modify ORM Classes
------------------

First step is to modify the ORM classes defined by your app, so they reflect
the "desired" schema.  Typically this will mean editing files under the
``poser.db.model`` package within your source.  In particular when adding new
tables, you must be sure to include them within ``poser/db/model/__init__.py``.

As noted above, only those classes *not* provided by ``rattail.db.model``
should be modified here, to be safe.  If you wish to "extend" an existing
table, you must create a secondary table which ties back to the first via
one-to-one foreign key relationship.


Create Migration Script
-----------------------

Next you will create the Alembic script which is responsible for performing the
schema migration against a database.  This is typically done like so:

.. code-block:: sh

   workon poser
   cdvirtualenv
   bin/alembic -c app/rattail.conf revision --autogenerate --head poser@head -m "describe migration here"

This will create a new file under
e.g. ``~/src/poser/poser/db/alembic/versions/``.  You should edit this file as
needed to ensure it performs all steps required for the migration.  Technically
it should support downgrade as well as upgrade, although in practice that isn't
always required.


Upgrade Database Schema
-----------------------

Once you're happy with the new script, you can apply it against your dev
database with something like:

.. code-block:: sh

   workon poser
   cdvirtualenv
   bin/alembic -c app/rattail.conf upgrade heads
