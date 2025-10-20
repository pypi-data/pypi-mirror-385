
Configuration
=============

.. contents:: :local:

Configuration for an app can come from two sources: configuration file(s), and
the Settings table in the database.


Config File Inheritance
-----------------------

An important thing to understand regarding Rattail config files, is that one
file may "include" another file(s), which in turn may "include" others etc.
Invocation of the app will often require only a single config file to be
specified, since that file may include others as needed.

For example ``web.conf`` will typically include ``rattail.conf`` but the web
app need only be invoked with ``web.conf`` - config from both files will inform
the app's behavior.


Typical Config Files
--------------------

A typical Poser (Rattail-based) app will have at the very least, one file named
``rattail.conf`` - this is considered the most fundamental config file.  It
will usually define database connections, logging config, and any other "core"
things which would be required for any invocation of the app, regardless of the
environment (e.g. console vs. web).

Note that even ``rattail.conf`` is free to include other files.  This may be
useful for instance, if you have a single site-wide config file which is shared
among all Rattail apps.

There is no *strict* requirement for having a ``rattail.conf`` file, but these
docs will assume its presence.  Here are some other typical files, which the
docs also may reference occasionally:

**web.conf** - This is the "core" config file for the web app, although it
still includes the ``rattail.conf`` file.  In production (running on Apache
etc.) it is specified within the WSGI module which is responsible for
instantiating the web app.  When running the development server, it is
specified via command line.

**quiet.conf** - This is a slight wrapper around ``rattail.conf`` for the sake
of a "quieter" console, when running app commands via console.  It may be used
in place of ``rattail.conf`` - i.e. you would specify ``-c quiet.conf`` when
running the command.  The only function of this wrapper is to set the level to
INFO for the console logging handler.  In practice this hides DEBUG logging
messages which are shown by default when using ``rattail.conf`` as the app
config file.

**cron.conf** - Another wrapper around ``rattail.conf`` which suppresses
logging even further.  The idea is that this config file would be used by cron
jobs; that way the only actual output is warnings and errors, hence cron would
not send email unless something actually went wrong.  It may be used in place
of ``rattail.conf`` - i.e. you would specify ``-c cron.conf`` when running the
command.  The only function of this wrapper is to set the level to WARNING for
the console logging handler.

**ignore-changes.conf** - This file is only relevant if your ``rattail.conf``
says to "record changes" when write activity occurs in the database(s).  Note
that this file does *not* include ``rattail.conf`` because it is meant to be
supplemental only.  For instance on the command line, you would need to specify
two config files, first ``rattail.conf`` or a suitable alternative, but then
``ignore-changes.conf`` also.  If specified, this file will cause changes to be
ignored, i.e. **not recorded** when write activity occurs.

**without-versioning.conf** - This file is only relevant if your
``rattail.conf`` says to enable "data versioning" when write activity occurs in
the database(s).  Note that this file does *not* include ``rattail.conf``
because it is meant to be supplemental only.  For instance on the command line,
you would need to specify two config files, first ``rattail.conf`` or a
suitable alternative, but then ``without-versioning.conf`` also.  If specified,
this file will disable the data versioning system entirely.  Note that if
versioning is undesirable for a given app run, this is the only way to
effectively disable it; once loaded that feature cannot be disabled.


Settings from Database
----------------------

The other (often more convenient) source of app configuration is the Settings
table within the app database.  Whether or not this table is a valid source for
app configuration, ultimately depends on what the config file(s) has to say
about it.

Assuming the config file(s) defines a database connection and declares it a
valid source for config values, then the Settings table may contribute to the
running app config.  The nice thing about this is that these settings are
checked in real-time.  So whereas changing a config file will require an app
restart, any edits to the settings table should take effect immediately.

Usually the settings table will *override* values found in the config file.
This behavior also is configurable to some extent, and in some cases a config
value may *only* come from a config file and never the settings table.

An example may help here.  If the config file contained the following value:

.. code-block:: ini

   [poser]
   foo = bar

Then you could create a new Setting in the database with the following fields:

* **name** = poser.foo
* **value** = baz

Assuming typical setup, i.e. where settings table may override config file, the
app would consider 'baz' to be the config value.  So basically the setting name
must correspond to a combination of the config file "section" name, then a dot,
then the "option" name.
