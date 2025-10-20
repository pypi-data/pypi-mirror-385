
App Organization & Structure
============================

.. contents:: :local:

Tailbone doesn't try to be an "app" proper.  But it does try to provide just
about everything you'd need to make one.  These docs assume you are making a
custom app, and will refer to the app as "Poser" to be consistent.  In practice
you would give your app a unique name which is meaningful to you.  Please
mentally replace "Poser" with your app name as you read.

.. note::

   Technically it *is possible* to use Tailbone directly as the app.  You may
   do so for basic testing of the concepts, but you'd be stuck with Tailbone
   logic, with far fewer customization options.  All docs will assume a custom
   "Poser" app which wraps and (as necessary) overrides Tailbone and Rattail.


Architecture
------------

In terms of how the Poser app hangs together, here is a conceptual diagram.
Note that all systems on the right-hand side are *external* to Poser, i.e. they
are not "plugins" although Poser may use plugin-like logic for the sake of
integrating with these systems.

.. image:: images/poser-architecture.png


Data Layer vs. Web Layer
^^^^^^^^^^^^^^^^^^^^^^^^

While the above graphic doesn't do a great job highlighting the difference, it
will (presumably) help to understand the difference in purpose and function of
Tailbone vs. Rattail packages.

**Rattail** is the data layer, and is responsible for database connectivity,
table schema information, and some business rules logic (among other things).

**Tailbone** is the web app layer, and is responsible for presentation and
management of data objects which are made available by Rattail (and others).

**Poser** is a custom layer which can make use of both data and web app layers,
supplementing each as necessary.  In practice the lines may get blurry within
Poser.

The reason for this distinction between layers, is to allow creation of custom
apps which use only the data layer but not the web app layer.  This can be
useful for console-based apps; a traditional GUI app would also be possible
although none is yet planned.


File Layout
-----------

Below is an example file layout for a Poser app project.  This tries to be
"complete" and show most kinds of files a typical project may need.  In
practice you can usually ignore anything which doesn't apply to your app,
i.e. relatively few of the files shown here are actually required.  Of course
some apps may need many more files than this to achieve their goals.

Note that all files in the root ``poser`` package namespace would correspond to
the "data layer" mentioned above, whereas everything under ``poser.web`` would
of course supply the web app layer.

.. code-block:: none

   ~/src/poser/
   ├── CHANGELOG.md
   ├── docs/
   ├── fabfile.py
   ├── MANIFEST.in
   ├── poser/
   │   ├── __init__.py
   │   ├── batch/
   │   │   ├── __init__.py
   │   │   └── foobatch.py
   │   ├── commands.py
   │   ├── config.py
   │   ├── datasync/
   │   ├── db/
   │   │   ├── __init__.py
   │   │   ├── alembic/
   │   │   └── model/
   │   │       ├── __init__.py
   │   │       ├── batch/
   │   │       │   ├── __init__.py
   │   │       │   └── foobatch.py
   │   │       └── customers.py
   │   ├── emails.py
   │   ├── enum.py
   │   ├── importing/
   │   │   ├── __init__.py
   │   │   ├── model.py
   │   │   ├── poser.py
   │   │   └── versions.py
   │   ├── problems.py
   │   ├── templates/
   │   │   └── mail/
   │   │       └── warn_about_foo.html.mako
   │   ├── _version.py
   │   └── web/
   │       ├── __init__.py
   │       ├── app.py
   │       ├── static/
   │       │   ├── __init__.py
   │       │   ├── css/
   │       │   ├── favicon.ico
   │       │   ├── img/
   │       │   └── js/
   │       ├── subscribers.py
   │       ├── templates/
   │       │   ├── base.mako
   │       │   ├── batch/
   │       │   │   └── foobatch/
   │       │   ├── customers/
   │       │   ├── menu.mako
   │       │   └── products/
   │       └── views/
   │           ├── __init__.py
   │           ├── batch/
   │           │   ├── __init__.py
   │           │   └── foobatch.py
   │           ├── common.py
   │           ├── customers.py
   │           └── products.py
   ├── README.rst
   └── setup.py
