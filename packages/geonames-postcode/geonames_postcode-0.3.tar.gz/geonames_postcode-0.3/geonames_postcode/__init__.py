# -*- encoding:utf-8 -*-
#
# Copyright (C) 2018, 2025 André Wobst <project.geonames_postcode@wobsta.de>
#
# This file is part of geonames_postcode (https://github.com/wobsta/geonames_postcode).
#
# geonames_postcode is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# PyX is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with geonames_postcode; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA 

import collections, importlib, math, os, unicodedata

import sys

if sys.version_info[0] == 2:
    from itertools import izip_longest as zip_longest
else:
    from itertools import zip_longest

version = '0.3'
date = '2025/10/20'

#: Postcodes are mapped to postcode items.
postcode_item = collections.namedtuple('postcode_item', ['names', 'regions', 'latitude', 'longitude'])

#: Names are mapped to name items.
name_item = collections.namedtuple('name_item', ['postcodes', 'latitude', 'longitude'])

dataDir = os.path.join(os.path.dirname(__file__), 'data')

#: `_regions[country]` is a sorted list of regions. It is prefixed by an
#: underscore to prevent a name clash with the :func:`regions` function.
#: The later just returns the regions of a country as contained in
#: `_regions`, but includes the boilerplate code to :func:`load` the
#: `country` if not yet loaded.
_regions = {}

#: `postcodes[country]` is a mapping of postcodes to :attr:`postcode_item`.
postcodes = {}

#: `names[country]` is a mapping of names in lower case to :attr:`name_item`.
names = {}

def load(*countries):
    """Load `countries`, whose data has been prepared beforehand.

    This fills :attr:`_regions`, :attr:`postcodes` and :attr:`names` for the `countries`.

    >>> load('DE')
    """
    for country in countries:
        assert len(country) == 2
        assert country.isupper()
        try:
            country_data = importlib.import_module('geonames_postcode.data.%s' % country.lower())
        except ImportError:
            exc = ValueError('Failed to load the %(country)s postcode data. Install it by `geonames_postcode_fetch %(country)s`.' % dict(country=country))
            exc.__cause__ = None
            raise exc
        _regions[country] = country_data.regions
        postcodes[country] = country_data.postcodes
        names[country] = country_data.names

def valid_postcode(country, postcode):
    """Check validity of `(country, postcode)` combination.

    >>> valid_postcode('DE', '85716')
    True
    """
    if country not in _regions: load(country)
    return postcode in postcodes[country]

def valid_name(country, name):
    """Check validity of `(country, name)` combination.

    >>> valid_name('DE', 'Unterschleißheim')
    True
    """
    if country not in _regions: load(country)
    return name.lower() in names[country]

def valid(country, postcode_or_name):
    """Check validity of `(country, postcode_or_name)` combination where `postcode_or_name` can be a postcode or a name.

    >>> valid('DE', '85716')
    True
    >>> valid('DE', 'Unterschleißheim')
    True
    """
    return valid_postcode(country, postcode_or_name) or valid_name(country, postcode_or_name)

def coordinates_postcode(country, postcode):
    """Get coordinates `(latitude, longitude)` of `(country, postcode)`. Returns `(None, None)` when the `postcode` is invalid for `country`.

    >>> coordinates_postcode('DE', '85716')
    (48.2804, 11.5768)
    """
    if country not in _regions: load(country)
    r = postcodes[country].get(postcode)
    if r:
        return r.latitude, r.longitude
    return None, None

def coordinates_name(country, name):
    """Get coordinates `(latitude, longitude)` of `(country, name)`. Returns `(None, None)` when the `name` is invalid for `country`.

    >>> coordinates_name('DE', 'Unterschleißheim')
    (48.2804, 11.5768)
    """
    if country not in _regions: load(country)
    r = names[country].get(name.lower())
    if r:
        return r.latitude, r.longitude
    return None, None

def coordinates(country, postcode_or_name):
    """Get coordinates `(latitude, longitude)` of `(country, postcode_or_name)`. Returns `(None, None)` when `postcode_or_name` is neither a valid postcode nor name for `country`.

    >>> coordinates('DE', '85716')
    (48.2804, 11.5768)
    >>> coordinates('DE', 'Unterschleißheim')
    (48.2804, 11.5768)
    """
    r = coordinates_postcode(country, postcode_or_name)
    if r[0] is not None:
        return r
    return coordinates_name(country, postcode_or_name)

def distance(latitude1, longitude1, latitude2, longitude2):
    """Calculates the distance in km between the two coordinates `(latitude1, longitude1)` and `(latitude2, longitude2)`.

    >>> distance(*coordinates('DE', 'Unterschleißheim'), *coordinates('DE', 'München'))
    15.274244595433155
    """
    latitude1 *= math.pi/180
    longitude1 *= math.pi/180
    latitude2 *= math.pi/180
    longitude2 *= math.pi/180
    phi = math.sin(latitude2)*math.sin(latitude1)+math.cos(latitude2)*math.cos(latitude1)*math.cos(longitude2-longitude1)
    if phi >= 1:
        return 0
    elif phi <= -1:
        return math.pi * 6380
    else:
        return math.acos(phi) * 6380

def postcode_names(country, postcode):
    """Get names of `(country, postcode)`.

    The returned list is sorted alphabetically.

    >>> postcode_names('DE', '85716')
    ['Unterschleißheim']
    """
    if country not in _regions: load(country)
    r = postcodes[country].get(postcode)
    if r:
        return r.names
    return []

def postcode_regions(country, postcode):
    """Get regions of `(country, postcode)`.

    Most of the time exactly one region is returned, but as postcodes and
    region boundaries do not match in some cases, several regions might
    be returned. The returned list is sorted alphabetically.

    >>> postcode_regions('DE', '85716')
    ['Bayern']
    """
    if country not in _regions: load(country)
    r = postcodes[country].get(postcode)
    if r:
        return r.regions
    return []

def name_postcodes(country, name):
    """Get postcodes of `(country, name)`.

    >>> name_postcodes('DE', 'Unterschleißheim')
    ['85716']
    """
    if country not in _regions: load(country)
    r = names[country].get(name.lower())
    if r:
        return r.postcodes
    return []

def name_autocomplete(country, name_start, sort='size'):
    """Get names of `(country, name_start)`.

    Results are roughly sorted by size (by using the number of matching
    postcodes, largest first). You can also sort it alphabetically by
    `sort='alphabetical'`.

    >>> name_autocomplete('DE', 'Untersch')
    ['Unterschleißheim', 'Unterschneidheim', 'Unterschönau', 'Unterschwaningen']
    """
    if country not in _regions: load(country)
    name_start_lower = name_start.lower()
    r = [''.join(c.upper() if l is not None and l.isupper() else c for c, l in zip_longest(name, name_start))
         for name in names[country] if name.startswith(name_start_lower)]
    def alphabetical(s):
        r = s.lower()
        if country == 'DE':
            r = r.replace(u'ä', 'ae').replace(u'ö', 'oe').replace(u'ü', 'ue').replace(u'ß', 'ss')
        r = unicodedata.normalize('NFKD', r).encode('ASCII', 'ignore')
        return r
    if sort == 'size':
        r.sort(key=lambda name: (-len(names[country][name.lower()].postcodes), alphabetical(name)))
    elif sort == 'alphabetical':
        r.sort(key=alphabetical)
    else:
        assert sort is None
    return r

def name_substitutes(country, name, *substitutes):
    """Add name `substitutes` for `name` in `country`.

    >>> valid('DE', 'Frankfurt')
    False
    >>> name_substitutes('DE', 'Frankfurt am Main', 'Frankfurt')
    >>> valid('DE', 'Frankfurt')
    True
    """
    if country not in _regions: load(country)
    for substitute in substitutes:
        assert substitute.lower() not in names[country]
        names[country][substitute.lower()] = names[country][name.lower()]

def nearby_postcodes(country, latitude, longitude, dist):
    """Get postcodes closer than `dist` (in km) from the given coordinate.

    This is the preferred solution for a radius search in a database by using a
    filter with the SQL `in` operator.

    >>> nearby_postcodes('DE', *coordinates('DE', 'Unterschleißheim'), 5)
    ['85386', '85711', '85716', '85764', '85778']
    """
    if country not in _regions: load(country)
    return sorted(postcode for postcode, item in postcodes[country].items()
                  if distance(item.latitude, item.longitude, latitude, longitude) < dist)

def regions(country):
    """Get regions of `country`.

    The returned list is sorted alphabetically.

    >>> regions('DE')
    ['Baden-Württemberg', 'Bayern', 'Berlin', 'Brandenburg', 'Bremen', 'Hamburg', 'Hessen', 'Mecklenburg-Vorpommern', 'Niedersachsen', 'Nordrhein-Westfalen', 'Rheinland-Pfalz', 'Saarland', 'Sachsen', 'Sachsen-Anhalt', 'Schleswig-Holstein', 'Thüringen']
    """
    if country not in _regions: load(country)
    return _regions[country]
