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

import sys

if sys.version_info[0] == 2:
    import ConfigParser as configparser
    from codecs import open
    from urllib2 import urlopen
else:
    import configparser
    from urllib.request import urlopen

import collections, datetime, importlib, io, itertools, json, os, pprint, unicodedata, zipfile

from . import dataDir, postcode_item, name_item, distance

def fetch(*countries):
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), 'fetch.ini'))
    if os.path.exists('fetch.ini'):
        print('load local fetch.ini in addition to the distributed one')
        config.read('fetch.ini')
    for country in countries:
        if country not in config.sections():
            config.add_section(country)
        assert len(country) == 2
        assert country.isupper()

        url = 'http://download.geonames.org/export/zip/%s.zip' % country
        zip = os.path.join(os.path.dirname(__file__), 'data', '%s.zip' % country)
        if not os.path.exists(zip):
            print('Downloading geonames postcode data from %s ...' % url)
            print('PLEASE RESPECT THE LICENCE OF THIS DATA (CREATIVE COMMONS ATTRIBUTION 4.0 LICENSE), SEE GEONAMES.ORG FOR DETAILS.')
            geonames_file = urlopen(url)
            with open(zip, 'wb') as cache:
                data = geonames_file.read()
                while data:
                    cache.write(data)
                    data = geonames_file.read()
            print('(Download is cached at %s.)' % zip)

        geonames_item = collections.namedtuple('geonames_item', ['postcode', 'name',
            'region', 'subregion', 'subsubregion', 'latitude', 'longitude'])
        geonames_data = []

        postcode_remove_from = config.get(country, 'postcode_remove_from')
        with zipfile.ZipFile(zip) as z:
            with z.open('%s.txt' % country) as f:
                for line in f:
                    (verify_country, postcode, name,
                        region, region_code, subregion, subregion_code, subsubregion, subsubregion_code,
                        latitude, longitude, accuracy) = line.decode('utf-8').split('\t')
                    assert verify_country == country
                    assert (len(accuracy) == 1 or (len(accuracy) == 2 and accuracy[0] in '123456')) and accuracy[-1] == '\n'
                    assert postcode
                    assert name
                    if postcode_remove_from:
                        postcode = postcode[:postcode.index(postcode_remove_from)]
                    latitude = float(latitude)
                    longitude = float(longitude)
                    geonames_data.append(geonames_item(postcode, name,
                        region or None, subregion or None, subsubregion or None, latitude, longitude))

        def mean(items):
            sum = count = 0
            for item in items:
                sum += item
                count += 1
            return sum/count
        def alphabetical(s):
            r = s.lower()
            if country == 'DE':
                r = r.replace(u'ä', 'ae').replace(u'ö', 'oe').replace(u'ü', 'ue').replace(u'ß', 'ss')
            r = unicodedata.normalize('NFKD', r).encode('ASCII', 'ignore')
            return r
        def match(item, terms):
            for term in terms:
                for key, value in term.items():
                    if ((key == 'name' and item.name != value) or
                        (key == 'name_start' and not item.name.startswith(value)) or
                        (key == 'postcode' and item.postcode != value) or
                        (key == 'region' and item.region != value) or
                        (key == 'latitude' and item.latitude != value) or
                        (key == 'longitude' and item.longitude != value)):
                        break
                else:
                    return True
            return False

        items_per_postcode = collections.defaultdict(list)
        for item in geonames_data:
            items_per_postcode[item.postcode].append(item)
        postcodes = {}
        for postcode, items in items_per_postcode.items():
            postcodes[postcode] = postcode_item(sorted(set(item.name for item in items), key=alphabetical),
                                                sorted(set(item.region for item in items if item.region is not None), key=alphabetical),
                                                mean(item.latitude for item in items),
                                                mean(item.longitude for item in items))

        remaining_geonames_data = [item for item in geonames_data
                                   if not match(item, json.loads(config.get(country, 'skip_for_names')))]

        regions = set(item.region for item in remaining_geonames_data if item.region is not None)

        names = {}
        max_distance = config.getfloat(country, 'max_distance')
        add_distance_per_item = config.getfloat(country, 'add_distance_per_item')
        for add_details_to_name in range(4+config.getint(country, 'name_postcode_chars')):
            # remaining_geonames_data = list(remaining_geonames_data)
            # print(country, add_details_to_name, len(remaining_geonames_data))
            items_per_name = collections.defaultdict(list)
            for item in remaining_geonames_data:
                if add_details_to_name:
                    add_to_name = []
                    if item.region:
                        add_to_name.append(item.region)
                    if add_details_to_name > 1 and item.subregion:
                        add_to_name.append(item.subregion)
                    if add_details_to_name > 2 and item.subsubregion:
                        add_to_name.append(item.subsubregion)
                    if add_details_to_name > 3:
                        add_to_name.append(item.postcode[:add_details_to_name-3])
                    if add_to_name:
                        name = '%s (%s)' % (item.name, ', '.join(add_to_name))
                    else:
                        name = item.name
                else:
                    name = item.name
                items_per_name[name].append(item)
            failed_names = {}
            for name, items in items_per_name.items():
                mean_latitude = mean(item.latitude for item in items)
                mean_longitude = mean(item.longitude for item in items)
                if max(distance(item.latitude, item.longitude, mean_latitude, mean_longitude)
                       for item in items) > max_distance + add_distance_per_item*len(items):
                    failed_names[name] = items
                else:
                    names[name.lower()] = name_item(sorted(set(item.postcode for item in items)), mean_latitude, mean_longitude)
            remaining_geonames_data = itertools.chain(*failed_names.values())
        if failed_names:
            print('Combining of the following name and points is out of bound:')
            for name, items in failed_names.items():
                print(name)
                for item in items:
                    print('%f,%f,%s' % (item.latitude, item.longitude, item.postcode))
            print('-> abort')
            sys.exit(1)

        with open(os.path.join(dataDir, 'template'), 'r') as f:
            template = f.read()
        data = {'url': url,
                'now': datetime.datetime.now(datetime.UTC).isoformat()}
        with open(os.path.join(dataDir, '%s.py' % country.lower()), 'w') as f:
            f.write(template.format(url=url,
                                    now=datetime.datetime.now(datetime.UTC).isoformat(),
                                    regions=pprint.pformat(sorted(list(regions), key=alphabetical)),
                                    postcodes=pprint.pformat(postcodes),
                                    names=pprint.pformat(names)))
        importlib.import_module('geonames_postcode.data.%s' % country.lower())

def main():
    fetch(*sys.argv[1:])

if __name__ == '__main__':
    main()
