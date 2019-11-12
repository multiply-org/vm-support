import json
import logging
import os
import fnmatch

from typing import Optional, List

from multiply_core.util import AuxDataProvider, AuxDataProviderCreator

__author__ = "Tonio Fincke (Brockmann Consult GmbH)"

_MUNDI_SERVER = 'obs.otc.t-systems.com'


MUNDI_AUX_DATA_PROVIDER_NAME = 'MUNDI'


class MundiAuxDataProvider(AuxDataProvider):

    def __init__(self, parameters: dict):
        if 'access_key_id' not in parameters:
            raise ValueError('No access key id provided.')
        if 'secret_access_key' not in parameters:
            raise ValueError('No secret access key provided.')
        self._access_key_id = parameters['access_key_id']
        self._secret_access_key = parameters['secret_access_key']

    @classmethod
    def name(cls) -> str:
        return MUNDI_AUX_DATA_PROVIDER_NAME

    def list_elements(self, base_folder: str, pattern: [Optional[str]] = '*') -> List[str]:
        from obs import ObsClient
        path_to_bucket_info_file = f'{base_folder}/bucket_info.json'
        file_names = []
        with open(path_to_bucket_info_file, "r") as bucket_info_file:
            bucket_info = json.load(bucket_info_file)
            obs_client = ObsClient(access_key_id=self._access_key_id,
                                   secret_access_key=self._secret_access_key,
                                   server=_MUNDI_SERVER)
            objects = obs_client.listObjects(bucketName=bucket_info['bucket'], prefix=bucket_info['prefix'])
            if objects.status < 300:
                for content in objects.body.contents:
                    remote_file_name = content.key.split('/')[-1]
                    if fnmatch.fnmatch(remote_file_name, pattern):
                        file_names.append(os.path.join(base_folder, remote_file_name))
            else:
                logging.error(objects.errorCode)
            obs_client.close()
        return file_names

    def assure_element_provided(self, name: str) -> bool:
        if os.path.exists(name):
            return True
        from obs import ObsClient
        name = name.replace('\\', '/')
        base_folder = os.path.abspath(os.path.join(name, os.pardir))
        path_to_bucket_info_file = f'{base_folder}/bucket_info.json'
        with open(path_to_bucket_info_file, "r") as bucket_info_file:
            bucket_info = json.load(bucket_info_file)
            key = f"{bucket_info['prefix']}/{name.split('/')[-1]}"
            obs_client = ObsClient(access_key_id=self._access_key_id,
                                    secret_access_key=self._secret_access_key,
                                   server=_MUNDI_SERVER)
            resp = obs_client.getObject(bucketName=bucket_info['bucket'], objectKey=key, downloadPath=name)
            if resp.status >= 300:
                logging.error(resp.errorCode)
                obs_client.close()
        return os.path.exists(name)


class MundiAuxDataProviderCreator(AuxDataProviderCreator):

    @classmethod
    def name(cls):
        return MUNDI_AUX_DATA_PROVIDER_NAME

    @classmethod
    def create_aux_data_provider(self, parameters: dict):
        return MundiAuxDataProvider(parameters)
