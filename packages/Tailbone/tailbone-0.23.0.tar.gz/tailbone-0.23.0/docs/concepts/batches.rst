
Data Batches
============

.. contents:: :local:

Data "batches" are one of the most powerful features of Rattail / Tailbone.
However each "batch type" is different, and they usually require custom
development.  In all cases they require a Rattail-based app database, for
storage.


General Overview
----------------

You can think of data batches as a sort of "temporary spreadsheet" feature.
When a batch is created, it is usually populated with rows, from some data
source.  The user(s) may then manipulate the batch data as needed, with the
final goal being to "execute" the batch.  What execution specifically means
will depend on context, e.g. type of batch, but generally it will "commit" the
"pending changes" which are represented by the batch.

Note that when a batch is executed, it becomes read-only ("frozen in time") and
at that point may be considered part of an audit trail of sorts.  The utility
of this may vary depending on the nature of the batch data.

Beyond that it's difficult to describe batches very well at this level,
precisely because they're all different.

..
   This graphic tries to show how batches are created and executed over time.
   Note that each batch type is free to target a different system(s) upon
   execution.

   TODO: need graphic


Batch Tables
------------

In most cases the table(s) underlying a particular batch type, have a "static"
schema and must be defined as ORM classes, e.g. within the ``poser.db.model``
package.

In some rare cases the batch data (row) table may be dynamic; however the batch
header table must still be defined.


Batch Handlers
--------------

Once the batch table(s) are present, the next puzzle piece is the batch
handler.  Again there is generally (at least) one handler defined for each
batch type.

The batch "handler" is considered part of the data layer and provides logic for
populating the batch, executing it etc.


Batch Views
-----------

This discussion would not be complete without mentioning the web views for the
batch.  Again each batch type will require a custom view(s) although these
"usually" are simple wrappers as most logic is provided by the base view.
