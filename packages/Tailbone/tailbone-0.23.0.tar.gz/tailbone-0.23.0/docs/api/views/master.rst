
``tailbone.views.master``
=========================

.. module:: tailbone.views.master

Model Master View
------------------

This module contains the "model master" view class.  This is a convenience
abstraction which provides some patterns/consistency for the typical set of
views needed to expose a table's data for viewing/editing/etc.  Usually this
means providing something like the following view methods for a model:

* index (list/filter)
* create
* view
* edit
* delete

The actual list of provided view methods will depend on usage.  Generally
speaking, each view method which is provided by the master class may be
configured in some way by the subclass (e.g. add extra filters to a grid).

.. autoclass:: MasterView

   .. automethod:: index

   .. automethod:: create

   .. automethod:: view

   .. automethod:: edit

   .. automethod:: delete

Attributes to Override
----------------------

The following is a list of attributes which you can (and in some cases must)
override when defining your subclass.

   .. attribute:: MasterView.model_class

      All master view subclasses *must* define this attribute.  Its value must
      be a data model class which has been mapped via SQLAlchemy, e.g.
      ``rattail.db.model.Product``.

   .. attribute:: MasterView.normalized_model_name

      Name of the model class which has been "normalized" for the sake of usage
      as a key (for grid settings etc.).  If not defined by the subclass, the
      default will be the lower-cased model class name, e.g. 'product'.

   .. attribute:: grid_key

      Unique value to be used as a key for the grid settings, etc.  If not
      defined by the subclass, the normalized model name will be used.

   .. attribute:: MasterView.route_prefix

      Value with which all routes provided by the view class will be prefixed.
      If not defined by the subclass, a default will be constructed by simply
      adding an 's' to the end of the normalized model name, e.g. 'products'.
      
   .. attribute:: MasterView.grid_factory

      Factory callable to be used when creating new grid instances; defaults to
      :class:`tailbone.grids.Grid`.

   .. attribute:: MasterView.results_downloadable_csv

      Flag indicating whether the view should allow CSV download of grid data,
      i.e. primary search results.

   .. attribute:: MasterView.help_url

      If set, this defines the "default" help URL for all views provided by the
      master.  Default value for this is simply ``None`` which would mean the
      Help button is not shown at all.  Note that the master may choose to
      override this for certain views, if so that should be done within
      :meth:`get_help_url()`.

   .. attribute:: MasterView.version_diff_factory

      Optional factory to use for version diff objects.  By default
      this is *not set* but a subclass is free to set it.  See also
      :meth:`get_version_diff_factory()`.


Methods to Override
-------------------

The following is a list of methods which you can override when defining your
subclass.

   .. automethod:: MasterView.editable_instance

   .. .. automethod:: MasterView.get_settings

   .. automethod:: MasterView.get_csv_fields

   .. automethod:: MasterView.get_csv_row

   .. automethod:: MasterView.get_help_url

   .. automethod:: MasterView.get_model_key

   .. automethod:: MasterView.get_version_diff_enums

   .. automethod:: MasterView.get_version_diff_factory

   .. automethod:: MasterView.make_version_diff

   .. automethod:: MasterView.title_for_version


Support Methods
---------------

The following is a list of methods you should (probably) not need to
override, but may find useful:

   .. automethod:: MasterView.default_edit_url

   .. automethod:: MasterView.get_action_route_kwargs
