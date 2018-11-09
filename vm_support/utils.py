import getpass
import yaml

from pathlib import Path
from typing import List, Optional

MULTIPLY_DIR_NAME = '.multiply'
DATA_STORES_FILE_NAME = 'data_stores.yml'


def get_working_dir() -> str:
    username = getpass.getuser()
    return '/Data/{}/'.format(username)


def create_config_file(temp_dir: str, roi: str, start_time: str, end_time: str, time_interval: str,
                       priors_directory: str, parameter_list: Optional[List[str]] =
                       {'n', 'cab', 'car', 'cb', 'cw', 'cdm', 'lai', 'ala', 'bsoil', 'psoil'}):
    config = {'General': {}}
    config['General']['roi'] = roi
    config['General']['start_time'] = start_time
    config['General']['end_time'] = end_time
    config['General']['time_interval'] = time_interval
    config['Prior'] = {}
    config['Prior']['output_directory'] = priors_directory
    config['Prior']['General'] = {}
    config['Prior']['General']['directory_data'] = '/data/auxiliary/priors/Static/Vegetation/'
    for parameter in parameter_list:
        config['Prior'][parameter] = {}
        config['Prior'][parameter]['database'] = {}
        config['Prior'][parameter]['database']['static_dir'] = 'same as General directory_data'
    config_file_name = '{}/config.yaml'.format(temp_dir)
    with open(config_file_name, 'w') as config_file:
        yaml.dump(config, config_file, default_flow_style=False)


def set_earth_data_authentication(username: str, password: str):
    home_dir = str(Path.home())
    data_stores_file = '{0}/{1}/{2}'.format(home_dir, MULTIPLY_DIR_NAME, DATA_STORES_FILE_NAME)
    _set_earth_data_authentication_to_file(username, password, data_stores_file)


def _set_earth_data_authentication_to_file(username: str, password: str, data_stores_file: str):
    stream = open(data_stores_file, 'r')
    data_store_lists = yaml.load(stream)
    for data_store_entry in data_store_lists:
        if data_store_entry['DataStore']['Id'] == 'modis_mcd43a1':
            data_store_entry['DataStore']['FileSystem']['parameters']['username'] = username
            data_store_entry['DataStore']['FileSystem']['parameters']['password'] = password
    stream.close()
    with open(data_stores_file, 'w') as file:
        yaml.dump(data_store_lists, file, default_flow_style=False)
