#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Top level script. Calls other functions that generate datasets that this script then creates in HDX.

"""
import logging
from os.path import join, expanduser

from hdx.hdx_configuration import Configuration
from hdx.location.country import Country
from hdx.utilities.downloader import Download

from wfp import generate_dataset_and_showcase, get_layersdata, get_locationsdata

from hdx.facades.simple import facade

logger = logging.getLogger(__name__)

lookup = 'hdx-scraper-wfp-geonode'


def main():
    """Generate dataset and create it in HDX"""

    with Download() as downloader:
        base_url = Configuration.read()['base_url']
        countriesdata = get_locationsdata(base_url, downloader)
        logger.info('Number of countries: %d' % len(countriesdata))
        for location in countriesdata:
            countrycode = location['code']
            countryname = Country.get_country_name_from_iso3(countrycode)
            if countryname is None:
                continue
            layersdata = get_layersdata(base_url, downloader, countrycode)
            logger.info('Number of datasets to upload in %s: %d' % (countryname, len(layersdata)))
            for layerdata in layersdata:
                dataset, showcase = generate_dataset_and_showcase(base_url, countrycode, layerdata)
                if dataset:
                    dataset.update_from_yaml()
                    dataset.create_in_hdx(remove_additional_resources=True)
                    showcase.create_in_hdx()
                    showcase.add_dataset(dataset)


if __name__ == '__main__':
    facade(main, user_agent_config_yaml=join(expanduser('~'), '.useragents.yml'), user_agent_lookup=lookup, project_config_yaml=join('config', 'project_configuration.yml'))


