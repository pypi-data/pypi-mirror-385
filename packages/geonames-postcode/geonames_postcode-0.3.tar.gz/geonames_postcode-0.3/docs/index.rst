geonames_postcode usage
=======================

.. _high-level-interface-section:

High-level interface
--------------------

.. module:: geonames_postcode

.. autofunction:: valid_postcode
.. autofunction:: valid_name
.. autofunction:: valid

.. autofunction:: coordinates_postcode
.. autofunction:: coordinates_name
.. autofunction:: coordinates

.. autofunction:: regions

.. autofunction:: distance

.. autofunction:: postcode_names
.. autofunction:: postcode_regions

.. autofunction:: name_postcodes
.. autofunction:: name_autocomplete
.. autofunction:: name_substitutes

.. autofunction:: nearby_postcodes

Internals
---------

The :ref:`high-level-interface-section` is basically just reading data from the
following data structures:

.. autodata:: _regions
.. autodata:: postcodes
.. autoclass:: postcode_item
.. autodata:: names
.. autoclass:: name_item

Those data is available on the module level after calling :func:`load`.
It is identical to the data created from the geonames.org data (see
:ref:`fetch-section`), except for the additional country mapping.

.. autofunction:: load

.. _fetch-section:

Preparing geonames.org data
---------------------------

**Please respect the license of the geonames.org data (Creative Commons
Attribution 4.0 License), see geonames.org for details.**

Fetching the geonames.org databases and preparing it for use is where
the time consuming preparation of the postcode data takes place. This process
results in a Python module for each country containing the data for the
:attr:`regions <_regions>`, :attr:`postcodes`, and :attr:`names`. The fetch
function has a rather simple interface:

.. module:: geonames_postcode.fetch

.. autofunction:: fetch

The :func:`fetch` function can conveniently started by the
``geonames_postcode_fetch`` script created by ``setup.py`` and ``pip``::

    geonames_postcode_fetch DE

Note that the postcode data can also be fetched in-place (without script
installation) by::

    python -m geonames_postcode.fetch DE

The postcode data is downloaded as a zip file, cached (to not reload the
postcode data from geonames.org multiple times), analyzed and translated in a
python file named <country>.py in the data directory of the geonames_postcode
package. It can than be loaded and used blazingly fast by geonames_postcode.

Fetching and preparing the geonames_postcode data is subject to some
configuration done in the ``fetch.ini`` file:

.. include:: ../geonames_postcode/fetch.ini
   :literal:

The configuration options are:

``skip_for_names``
    Skip some postcode data when building the names. The data to be skipped is
    selected by ``name``, ``name_start`` (names starting with), ``latitude``,
    ``longitude``, and/or ``postcode``. Several selectors are given by a list
    of dictionaries (i.e. the option is parsed as json). Within each dictionary
    the conditions are combined with ``and``. The items of the list are taken
    as ``or`` conditions.

``postcode_remove_from``
    Throw away details in the postcodes by removing all the tail starting at
    the given string.

``max_distance``
    Combine equal names for different postcodes if their distance is not further
    apart than given distance (in km) from the center of all values with equal
    names.

``add_distance_per_item``
    An additional distance to be added to ``max_distance`` for each postcode in
    the list of equal names.

``name_postcode_chars``
    It turns out that the names alone are not necessarily enough to properly
    distinguish between locations. The :func:`fetch` function thus tries to add
    ``regions``, ``sub-regions``, and ``sub-sub-regions`` as given in the
    postcode data. However, this still might not be enough in all cases, and the
    postcodes might be taken into account up to the given number of characters.

Indices and tables
------------------

* :ref:`genindex`
* :ref:`search`
