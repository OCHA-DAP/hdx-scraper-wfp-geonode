### Collector for MIMU's Datasets
[![Build Status](https://travis-ci.org/OCHA-DAP/hdx-scraper-mimu.svg?branch=master&ts=1)](https://travis-ci.org/OCHA-DAP/hdx-scraper-mimu) [![Coverage Status](https://coveralls.io/repos/github/OCHA-DAP/hdx-scraper-mimu/badge.svg?branch=master&ts=1)](https://coveralls.io/github/OCHA-DAP/hdx-scraper-mimu?branch=master)

This script connects to the [MIMU API](https://geonode.themimu.info/layers/) and extracts data layer by layer creating a dataset per layer in HDX. It makes 1 read from MIMU and 250 read/writes (API calls) to HDX in a one hour period. It is run every year.

### Usage
python run.py

For the script to run, you will need to have a file called .hdx_configuration.yml in your home directory containing your HDX key eg.

    hdx_key: "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
    hdx_read_only: false
    hdx_site: prod
    
 You will also need to supply the universal .useragents.yml file in your home directory as specified in the parameter *user_agent_config_yaml* passed to facade in run.py. The collector reads the key **hdx-scraper-ucdp** as specified in the parameter *user_agent_lookup*.
 
 Alternatively, you can set up environment variables: USER_AGENT, HDX_KEY, HDX_SITE, TEMP_DIR, LOG_FILE_ONLY