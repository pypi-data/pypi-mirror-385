.. -*- coding: utf-8 -*-

Data Batches
============

This document briefly outlines what comprises a batch in terms of the Tailbone
user interface etc.


Batch Views
-----------

Adding support for a new batch type is mostly a matter of providing some custom
views for the batch and its rows.  In fact you must define four different view
classes, inheriting from each of the following:

* :class:`tailbone.views.batch.BatchGrid`
* :class:`tailbone.views.batch.BatchCrud`
* :class:`tailbone.views.batch.BatchRowGrid`
* :class:`tailbone.views.batch.BatchRowCrud`

It would sure be nice to only require two view classes instead of four, hopefully
that can happen "soon".  In the meantime that's what it takes.  Note that as with
batch data models, there are some more specialized parent classes which you may
want to inherit from instead of the core classes mentioned above:

* :class:`tailbone.views.batch.FileBatchGrid`
* :class:`tailbone.views.batch.FileBatchCrud`
* :class:`tailbone.views.batch.ProductBatchRowGrid`

Here are the vendor catalog views as examples:

* :class:`tailbone.views.vendors.catalogs.VendorCatalogGrid`
* :class:`tailbone.views.vendors.catalogs.VendorCatalogCrud`
* :class:`tailbone.views.vendors.catalogs.VendorCatalogRowGrid`
* :class:`tailbone.views.vendors.catalogs.VendorCatalogRowCrud`


Pyramid Config
--------------

In addition to defining the batch views, the Pyramid Configurator object must be
told of the views and their routes.  This also could probably stand to be simpler
somehow, but for now the easiest thing is to apply default configuration with:

* :func:`tailbone.views.batch.defaults()`

See the source behind the vendor catalog for an example:

* :func:`tailbone.views.vendors.catalogs.includeme()`

Note of course that your view config must be included by the core/upstream
config process of your application's startup to take effect.  At this point
your views should be accessible by navigating to the URLs directly, e.g. for
the vendor catalog views:

* List Uploaded Catalogs - http://example.com/vendors/catalogs/
* Upload New Catlaog - http://example.com/vendors/catalogs/new


Menu and Templates
------------------

Providing access to the batch views is (I think) the last step.  You must add
links to the views, wherever that makes sense for your app.  In case it's
helpful, here's a Mako template snippet which would show some links to the main
vendor catalog views:

.. code-block:: mako

   <ul>
     <li>${h.link_to("Vendor Catalogs", url('vendors.catalogs'))}</li>
     <li>${h.link_to("Upload new Vendor Catalog", url('vendors.catalogs.create'))}</li>
   </ul>
