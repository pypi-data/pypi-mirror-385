geonames_postcode
=================

geonames_postcode is a Python package to make geonames.org postcode
databases accessible in Python. It provides a command line tool to
fetch, preprocess, and store the data in a Python file per country.
In the result very fast (in-memory) queries by postcodes and names are
available using just a few MB per country. Some helper functions are
part of the package to solve common tasks like getting distances and
finding postcodes nearby.

Quickstart
----------

**Please respect the license of the geonames.org data (Creative Commons
Attribution 4.0 License), see geonames.org for details.**

On the console::

    pip install geonames_postcode
    geonames_postcode_fetch DE

In Python::

    >>> import geonames_postcode
    >>> latlong1 = geonames_postcode.coordinates('DE', 'Unterschleißheim')
    >>> latlong1
    (48.2804, 11.5768)
    >>> latlong2 = geonames_postcode.coordinates('DE', 'München')
    >>> geonames_postcode.distance(*latlong1, *latlong2)
    15.289746063637923
    >>> geonames_postcode.nearby_postcodes('DE', *latlong1, 5)
    ['85386', '85716', '85764', '85778']
    >>> geonames_postcode.postcode_names('DE', '85764')
    ['Oberschleißheim']
    >>> geonames_postcode.name_autocomplete('DE', 'Münche')
    ['München', 'Müncheberg', 'Münchehofe', 'Münchenbernsdorf']

Usage
-----

see https://geonames-postcode.readthedocs.io/

License
-------

The project is licensed under the GPLv2+.

