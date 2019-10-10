### Collector for WFP's Datasets

This script connects to the [WFP API](https://geonode.wfp.org/layers/) and extracts data layer by layer creating a dataset per layer in HDX. It makes 200 reads from WFP and 2500 read/writes (API calls) to HDX in a one hour period. It is run every year.

### Usage
python run.py

For the script to run, you will need to have a file called .hdx_configuration.yml in your home directory containing your HDX key eg.

    hdx_key: "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
    hdx_read_only: false
    hdx_site: prod
    
 You will also need to supply the universal .useragents.yml file in your home directory as specified in the parameter *user_agent_config_yaml* passed to facade in run.py. The collector reads the key **hdx-scraper-wfp-geonode** as specified in the parameter *user_agent_lookup*.
 
 Alternatively, you can set up environment variables: USER_AGENT, HDX_KEY, HDX_SITE, TEMP_DIR, LOG_FILE_ONLY