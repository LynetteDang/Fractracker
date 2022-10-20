'''
config.py
'''

import os
import yaml
from constants import DEV, ROOT_DIRECTORY, TEST


class Config:
    '''
    Reads and stores values from the configuration file
    that corresponds to the current development environment.
    '''

    def __init__(self) -> None:
        '''
        The public constructor. Looks for configuration files
        saved under the root of the project as 'config.{env}.yaml'.
        If the environmental variable representing the development
        environment, 'PROD_ENV', is missing, 'config.dev.yaml' is
        read in by default.
        
        NOTE: Values in 'config.local.yaml' will override those in 
        'config.dev.yaml' or 'config.test.yaml'.
        '''
        # Determine config file paths
        env = os.getenv("PROD_ENV", DEV)
        env_config_path = f"{ROOT_DIRECTORY}/config.{env}.yaml"
        local_config_path = f"{ROOT_DIRECTORY}/config.local.yaml"

        # Load in config file corresponding to environment
        with open(env_config_path, 'r') as f:
            env_config = yaml.load(f, Loader=yaml.Loader)

        # If using non-production environment with local config file, override values
        if env in (DEV, TEST) and os.path.exists(local_config_path):
            with open(local_config_path) as f:
                local_config = yaml.load(f, Loader=yaml.Loader)

            for key, val in local_config.items():
                env_config[key] = val

        # Set configuration as attribute
        self._config = env_config



    @property
    def cc_email(self) -> str:
        '''
        The CC'd email address to use when composing complaint
        emails to governmental agencies.
        '''
        return self._config['email']['cc']

    
    @property
    def cloud_blob_name(self) -> str:
        '''
        The name of the cloud blob (file).
        '''
        return self._config['cloud']['blob_name']


    @property
    def cloud_bucket_name(self) -> str:
        '''
        The name of the cloud bucket.
        '''
        return self._config['cloud']['bucket_name']
    

    @property
    def cloud_metadata_path(self) -> str:
        '''
        The filepath of the metadata downloaded from the cloud.
        '''
        return self._config['paths']['cloud_metadata']


    @property
    def default_app_host(self) -> str:
        '''
        The default host address to use for the Flask app.
        '''
        return self._config['flask']['host']


    @property
    def default_app_port(self) -> str:
        '''
        The default port to use for the Flask app.
        '''
        return self._config['flask']['port']

    @property
    def fractracker_base_api_url(self) -> str:
        '''
        The base URL for retrieving reports from the FracTracker API.
        '''
        return self._config['api']['fractracker_base_url']


    @property
    def from_email(self) -> str:
        '''
        The sender email address to use when composing complaint
        emails to governmental agencies.
        '''
        return self._config['email']['from']


    @property
    def metadata_path(self) -> str:
        '''
        The filepath of the metadata.
        '''
        return self._config['paths']['metadata']


    @property
    def to_email(self) -> str:
        '''
        The sender email address to use when composing complaint
        emails to governmental agencies.
        '''
        return self._config['email']['to']


    @property
    def colorado_email(self) -> str:
        '''
        The email address to use for the Colorado Oil and
        Gas Conservation Commission.
        '''
        return self._config['email']['to']['co']


    @property
    def kentucky_email(self) -> str:
        '''
        The email address to use for the Kentucky Energy and Environment.
        '''
        return self._config['email']['to']['ky']


    @property
    def nebraska_email(self) -> str:
        '''
        The email address to use for the Nebraska Department of Environmental Quality.
        '''
        return self._config['email']['to']['ne']


    @property
    def north_dakota_email(self) -> str:
        '''
        The email address to use for the North Dakota Department of Environmental Quality.
        '''
        return self._config['email']['to']['nd']


    @property
    def tennessee_email(self) -> str:
        '''
        The email address to use for the Tennessee Department of Environment and Conservation.
        '''
        return self._config['email']['to']['tn']


    @property
    def west_virginia_email(self) -> str:
        '''
        The email address to use for the Tennessee Department of Environment and Conservation.
        '''
        return self._config['email']['to']['wv']
    

    @property
    def begin_date(self) -> str:
        '''
        Test begin_date.
        '''
        return self._config['dates']['begin_date']

    
    @property
    def end_date(self) -> str:
        '''
        Test end_date.
        '''
        return self._config['dates']['end_date']

