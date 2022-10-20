from abc import ABC, abstractmethod
import os
from google.cloud import storage
from io import StringIO
import pandas as pd
from utilities.logger import logger

class IDatastore(ABC):
    '''
    Interface for Datastore class
    '''

    @abstractmethod
    def write_data(self):
        '''
        Write data
        '''
        raise NotImplementedError


    @abstractmethod
    def read_data(self):
        '''
        Read data
        '''
        raise NotImplementedError


class CloudDatastore(IDatastore):
    '''
    Class for working with data on cloud
    '''
    def __init__(self, bucket_name:str, cloud_blob_name:str):
        '''
        Constructor for cloud datastore
        '''
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        self._blob = bucket.blob(cloud_blob_name)   

    def write_data(self, df):
        '''
        Write data to cloud
        '''
        # Write records
        csv_str = df.to_csv(header=True, encoding='utf-8', index=False)

        # Upload data
        self._blob.upload_from_string(csv_str, content_type='text/csv')
        logger.info(f'Saved metadata to Google Cloud.')

    def read_data(self):
        '''
        Read data from Cloud
        '''
        # if blob exists, read data from blob into df
        # else return blank dataframe
        if self._blob.exists():
            bytes_file = self.blob.download_as_bytes(timeout=(3, 60))
            # Parse downloaded bytes into in-memory text stream 
            s = str(bytes_file, encoding='utf-8')
            df = pd.read_csv(StringIO(s))
            return df
        else:
            return pd.Dataframe()


class LocalDatastore(IDatastore):
    '''
    Class for working with datastore locally
    '''
    def __init__(self, filepath):
        '''
        Constructor for local datastore
        '''
        self._filepath = filepath

    def write_data(self, df):
        '''
        Write data to local CSV
        '''
        df.to_csv(self._filepath, index=False)
        logger.info(f'Saved metadata locally.')

    def read_data(self):
        '''
        Read data from CSV
        '''
        # # if CSV exists, read in metadata CSV
        # else, return blank dataframe
        if os.path.exists(self._filepath):
            return pd.read_csv(self._filepath)
        else:
            return pd.DataFrame()

