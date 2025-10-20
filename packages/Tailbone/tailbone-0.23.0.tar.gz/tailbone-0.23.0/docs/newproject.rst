
Creating a New Project
======================

.. contents:: :local:

.. highlight:: bash

This describes the process of creating a new app project based on
Rattail/Tailbone.  It assumes you are working from a supported :doc:`devenv`.

Per convention, this doc uses "Poser" (and ``poser``) to represent the custom
app.  Please adjust commands etc. accordingly.  See also :doc:`structure`.


Create the Virtual Environment
------------------------------

First step is simple enough::

   mkvirtualenv poser

Then with your new environment activated, install the Tailbone package::

   pip install Tailbone


Create the Project
------------------

Now with your environment still activated, ``cd`` to wherever you like
(e.g. ``~/src``) and create a new project skeleton like so::

   mkdir -p ~/src
   cd ~/src
   pcreate -s rattail poser

This will have created a new project at ``~/src/poser`` which you can then edit
as you wish.  At some point you will need to "install" this project to the
environment like so (again with environment active)::

   cd ~/src/poser
   pip install -e .


Setup the App Environment
-------------------------

Any project based on Rattail will effectively be its own "app" (usually), but
Rattail itself provides some app functionality as well.  However all such apps
require config files, usually.  If running a web app then you may also need to
have configured a folder for session storage, etc.  To hopefully simplify all
this, there are a few commands you should now run, with your virtual
environment still active::

   rattail make-appdir
   cdvirtualenv app
   rattail make-config -T rattail
   rattail make-config -T quiet
   rattail make-config -T web

This will have created a new 'app' folder in your environment (e.g. at
``/srv/envs/poser/app``) and then created ``rattail.conf`` and ``web.conf``
files within that app dir.  Note that there will be other folders inside the
app dir as well; these are referenced by the config files.

But you're not done yet...  You should likely edit the config files, at the
very least edit ``rattail.conf`` and change the ``default.url`` value (under
``[rattail.db]`` section) which defines the Rattail database connection.


Create the Database
-------------------

If applicable, it's time for that.  First you must literally create the user
and database on your PostgreSQL server, e.g.::

   sudo -u postgres createuser --no-createdb --no-createrole --no-superuser poser
   sudo -u postgres psql -c "alter user poser password 'mypassword'"
   sudo -u postgres createdb --owner poser poser

Then you can install the schema; with your virtual environment activated::

   cdvirtualenv
   alembic -c app/rattail.conf upgrade heads

At this point your 'poser' database should have some empty tables.  To confirm,
on your PG server do::

   sudo -u postgres psql -c '\d' poser


Create Admin User
-----------------

If your intention is to have a web app, or at least to test one, you'll
probably want to create the initial admin user.  With your env active::

   cdvirtualenv
   rattail -c app/quiet.conf make-user --admin myusername

This should prompt you for a password, then create a single user and assign it
to the Administrator role.


Install Sample Data
-------------------

If desired, you can install a bit of sample data to your fresh Rattail
database.  With your env active do::

   cdvirtualenv
   rattail -c app/quiet.conf -P import-sample


Run Dev Web Server
------------------

With all the above in place, you may now run the web server in dev mode::

   cdvirtualenv
   pserve --reload app/web.conf

And finally..you may browse your new project dev site at http://localhost:9080/
(unless you changed the port etc.)


Schema Migrations
-----------------

Often a new project will require custom schema additions to track/manage data
unique to the project.  Rattail uses `Alembic`_ for handling schema migrations.
General usage of that is documented elsewhere, but a little should be said here
regarding new projects.

.. _Alembic: https://pypi.python.org/pypi/alembic

The new project template includes most of an Alembic "repo" for schema
migrations.  However there is one step required to really bootstrap it, i.e. to
the point where normal Alembic usage will work: you must create the initial
version script.  Before you do this, you should be reasonably happy with any
ORM classes you've defined, as the initial version script will be used to
create that schema.  Once you're ready for the script, this command should do
it::

   cdvirtualenv
   bin/alembic -c app/rattail.conf revision --autogenerate --version-path ~/src/poser/poser/db/alembic/versions/ -m 'initial Poser tables'

You should of course look over and edit the generated script as needed.  One
change in particular you should make is to add a branch label, e.g.:

.. code-block:: python

   branch_labels = ('poser',)
