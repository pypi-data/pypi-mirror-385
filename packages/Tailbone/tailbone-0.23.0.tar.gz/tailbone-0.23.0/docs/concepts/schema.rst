
Database Schema
===============

.. contents:: :local:

Rattail provides a "core" schema which is assumed to be the foundation of any
Poser app database.


Core Tables
-----------

All tables which are considered part of the Rattail "core" schema, are defined
as ORM classes within the ``rattail.db.model`` package.

.. note::

   The Rattail project has its roots in retail grocery-type stores, and its
   schema reflects that to a large degree.  In practice however the software
   may be used to support a wide variety of apps.  The next section describes
   that a bit more.


Customizing the Schema
----------------------

Almost certainly a custom app will need some of the core tables, but just as
certainly, it will *not* need others.  And to make things even more
interesting, it may need some tables but also need to "supplement" them
somehow, to track additional data for each record etc.

Any table in the core schema which is *not* needed, may simply be ignored,
i.e. hidden from the app UI etc.

Any table which is "missing" from core schema, from the custom app's
perspective, should be added as a custom table.

Also, any table which is "present but missing columns" from the app's
perspective, will require a custom table.  In this case each record in the
custom table will "tie back to" the core table record.  The custom record will
then supply any additional data for the core record.

Defining custom tables, and associated tasks, are documented in
:doc:`../schemachange`.
