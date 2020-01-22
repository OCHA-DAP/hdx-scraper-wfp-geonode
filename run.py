#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Top level script. Calls other functions that generate datasets that this script then creates in HDX.

"""
import argparse
import logging
from os.path import join

from hdx.hdx_configuration import Configuration
from hdx.scraper.geonode.geonodetohdx import GeoNodeToHDX
from hdx.utilities.downloader import Download

from hdx.facades.simple import facade

logger = logging.getLogger(__name__)

lookup = 'hdx-scraper-wfp-geonode'


def create_dataset_showcase(dataset, showcase):
    logger.info('Dataset date is %s' % dataset['dataset_date'])


def main():
    """Generate dataset and create it in HDX"""

    with Download() as downloader:
        base_url = Configuration.read()['base_url']
        geonodetohdx = GeoNodeToHDX(base_url, downloader)
        geonodetohdx.get_ignore_data().extend(Configuration.read()['ignore_data'])
        geonodetohdx.get_titleabstract_mapping().update(Configuration.read()['titleabstract_mapping'])
        metadata = {'maintainerid': 'd7a13725-5cb5-48f4-87ac-a70b5cea531e',
                    'orgid': '3ecac442-7fed-448d-8f78-b385ef6f84e7'}
        datasets = geonodetohdx.generate_datasets_and_showcases(metadata, get_date_from_title=True,
                                                                updated_by_script='HDX Scraper: WFP GeoNode run by WFP')
        geonodetohdx.delete_other_datasets(datasets, metadata)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='hdx-scraper-wfp-geonode')
    parser.add_argument('-hk', '--hdx_key', default=None, help='HDX api key')
    parser.add_argument('-hs', '--hdx_site', default=None, help='HDX site to use')
    args = parser.parse_args()
    hdx_site = args.hdx_site
    if hdx_site is None:
        hdx_site = 'feature'
    facade(main, hdx_key=args.hdx_key, hdx_site=hdx_site, user_agent='WFPGeoNode', project_config_yaml=join('config', 'project_configuration.yml'))


