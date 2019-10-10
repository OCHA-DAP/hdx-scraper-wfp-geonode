#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
WFP GeoNode:
-----------

Reads WFP JSON and creates datasets.

"""

import logging
from urllib.parse import  quote_plus

from hdx.data.dataset import Dataset
from hdx.data.resource import Resource
from hdx.data.showcase import Showcase
from slugify import slugify

logger = logging.getLogger(__name__)

tag_mapping = {'Elevation': 'elevation - topography - altitude', 'Boundaries': 'geodata',
               'Location': 'populated places - settlements', 'Transportation': 'transportation',
               'Structure': 'facilities and infrastructure', 'Environment': 'environment',
               'Inland Waters': 'river', 'Physical Features, Land Cover, Land Use, DEM': 'land use and land cover',
               'Farming': 'food production', 'Natural Hazards': 'hazards and risk'
               }


def get_locationsdata(base_url, downloader):
    response = downloader.download('%s/api/regions' % base_url)
    jsonresponse = response.json()
    locations = list()
    for location in jsonresponse['objects']:
        if location['count'] is not None:
            locations.append(location)
    return locations


def get_layersdata(base_url, downloader, countryiso):
    response = downloader.download('%s/api/layers/?regions__code__in=%s' % (base_url, countryiso))
    jsonresponse = response.json()
    return jsonresponse['objects']


def generate_dataset_and_showcase(base_url, countrycode, layerdata):
    """Parse json of the form:
{
"abstract": "south sudan access constraints Roads shp for 20191004",
"category__gn_description": "Logistics",
"csw_type": "dataset",
"csw_wkt_geometry": "POLYGON((25.407030556 3.59982146700003,25.407030556 11.724645635,34.633678076 11.724645635,34.633678076 3.59982146700003,25.407030556 3.59982146700003))",
"date": "2019-10-04T09:56:00",
"detail_url": "/layers/geonode%3Asouth_sudan_access_constraints_shp_20190927",
"distribution_description": "Web address (URL)",
"distribution_url": "https://geonode.wfp.org/layers/geonode%3Asouth_sudan_access_constraints_shp_20190927",
"id": 10161,
"owner__username": "kevin.ketchmen",
"popular_count": 32,
"rating": 0,
"share_count": 0,
"srid": "EPSG:4326",
"supplemental_information": "No information provided",
"thumbnail_url": "https://geonode.wfp.org/uploaded/thumbs/layer-5509fda2-e0ee-11e9-81cf-005056822e38-thumb.png",
"title": "south sudan access constraints Roads shp for 20191004",
"uuid": "5509fda2-e0ee-11e9-81cf-005056822e38"
}
    """
    title = layerdata['title']
    notes = layerdata['abstract']
    if 'Humanitarian Data Exchange' in notes:
        logger.warning('Ignoring %s as source is HDX!' % title)
        return None, None
    if 'DEPRECATED' in notes:
        logger.warning('Ignoring %s as it is deprecated!' % title)
        return None, None
    logger.info('Creating dataset: %s' % title)
    name = 'WFP %s' % title
    slugified_name = slugify(name).lower()
    if len(slugified_name) > 90:
        slugified_name = slugified_name[:90]
    supplemental_information = layerdata['supplemental_information']
    if supplemental_information.lower()[:7] != 'no info':
        notes = '%s\n\n%s' % (notes, supplemental_information)
    dataset = Dataset({
        'name': slugified_name,
        'title': title,
        'notes': notes
    })
    dataset.set_maintainer('d7a13725-5cb5-48f4-87ac-a70b5cea531e')
    dataset.set_organization('3ecac442-7fed-448d-8f78-b385ef6f84e7')
    dataset.set_dataset_date(layerdata['date'])
    dataset.set_expected_update_frequency('Adhoc')
    dataset.set_subnational(True)
    dataset.add_country_location(countrycode)
    tag = layerdata['category__gn_description']
    if tag in tag_mapping:
        tag = tag_mapping[tag]
    tags = ['geodata', tag]
    title_notes = ('%s %s' % (title, notes)).lower()
    if 'land cover' in title_notes or 'forest' in title_notes:
        tags.append('land use and land cover')
    if 'landslide' in title_notes:
        tags.append('landslides')
    if 'flood' in title_notes:
        tags.append('floods')
    if 'drought' in title_notes:
        tags.append('drought')
    if 'ffa' in title_notes or 'food for assets' in title_notes:
        tags.append('food assistance')
    if 'emergency levels' in title_notes:
        tags.append('hazards and risk')
    if 'admin' in title_notes and 'boundaries' in title_notes:
        tags.append('administrative divisions')
    if 'security' in title_notes:
        if 'food' in title_notes:
            tags.append('food security')
        else:
            tags.append('security')
    if 'refugee' in title_notes:
        if 'camp' in title_notes:
            tags.append('displaced persons locations - camps - shelters')
        tags.append('refugees')
    if 'idp' in title_notes:
        if 'camp' in title_notes:
            tags.append('displaced persons locations - camps - shelters')
        tags.append('internally displaced persons - idp')
    if 'nutrition' in title_notes:
        if 'malnutrition' in title_notes:
            tags.append('malnutrition')
        else:
            tags.append('nutrition')
    if 'food distribution' in title_notes:
        tags.append('food assistance')
    if 'streets' in title_notes or 'roads' in title_notes:
        tags.extend(['roads', 'transportation'])
    if 'airport' in title_notes or 'airstrip' in title_notes:
        tags.extend(['aviation', 'facilities and infrastructure'])
    if 'bridges' in title_notes:
        tags.extend(['bridges', 'transportation', 'facilities and infrastructure'])
    if 'frost' in title_notes:
        tags.append('cold wave')
    if 'erosion' in title_notes or 'mudflow' in title_notes or 'mudslide' in title_notes:
        tags.append('mudslide')
    dataset.add_tags(tags)
    srid = quote_plus(layerdata['srid'])
    typename = layerdata['detail_url'].rsplit('/', 1)[-1]
    resource = Resource({
        'name': '%s shapefile' % title,
        'url': '%s/geoserver/wfs?format_options=charset:UTF-8&typename=%s&outputFormat=SHAPE-ZIP&version=1.0.0&service=WFS&request=GetFeature' % (base_url, typename),
        'description': 'Zipped Shapefile. %s' % notes
    })
    resource.set_file_type('zipped shapefile')
    dataset.add_update_resource(resource)
    resource = Resource({
        'name': '%s geojson' % title,
        'url': '%s/geoserver/wfs?srsName=%s&typename=%s&outputFormat=json&version=1.0.0&service=WFS&request=GetFeature' % (base_url, srid, typename),
        'description': 'GeoJSON file. %s' % notes
    })
    resource.set_file_type('GeoJSON')
    dataset.add_update_resource(resource)

    showcase = Showcase({
        'name': '%s-showcase' % slugified_name,
        'title': title,
        'notes': notes,
        'url': '%s%s' % (base_url, layerdata['detail_url']),
        'image_url': layerdata['thumbnail_url']
    })
    showcase.add_tags(tags)
    return dataset, showcase
