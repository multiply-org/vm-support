__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'

import getpass
import glob
import os
import pkg_resources
import shutil
import stat
import yaml

from multiply_core.util import FileRef, get_time_from_string
from pathlib import Path
from typing import List, Optional, Union
from shapely.wkt import loads

MULTIPLY_DIR_NAME = '.multiply'
DATA_STORES_FILE_NAME = 'data_stores.yml'
ALL_PERMISSIONS = stat.S_IRUSR + stat.S_IWUSR + stat.S_IXUSR + stat.S_IRGRP + stat.S_IWGRP + stat.S_IXGRP + \
                  stat.S_IROTH + stat.S_IWOTH + stat.S_IXOTH
PATH_TO_VM_DATA_STORES_FILE = pkg_resources.resource_filename(__name__, 'vm_data_stores.yml')


def get_working_dir(dir_name: str) -> str:
    username = getpass.getuser()
    working_dir = '/data/{}/{}'.format(username, dir_name)
    if os.path.exists(working_dir):
        shutil.rmtree(working_dir)
    os.makedirs(working_dir)
    return working_dir


def create_config_file(temp_dir: str, roi: str, start_time: str, end_time: str, time_interval: str,
                       priors_directory: str, parameter_list: Optional[List[str]] =
                       {'n', 'cab', 'car', 'cb', 'cw', 'cdm', 'lai', 'ala', 'bsoil', 'psoil'},
                       user_prior_data: Optional[dict] = None) -> str:
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
        data_base_required = True
        if user_prior_data is not None and parameter in user_prior_data:
            config['Prior'][parameter]['user'] = user_prior_data[parameter]
            if 'mu' in user_prior_data[parameter]:
                data_base_required = False
        if data_base_required:
            config['Prior'][parameter]['database'] = {}
            config['Prior'][parameter]['database']['static_dir'] = 'same as General directory_data'
    config_file_name = '{}/config.yaml'.format(temp_dir)
    with open(config_file_name, 'w') as config_file:
        yaml.dump(config, config_file, default_flow_style=False)
    return config_file_name


def create_sar_config_file(temp_dir: str, roi: str, start_time: str, end_time: str, s1_slc_directory: str,
                           s1_grd_directory: str) -> str:
    config = {'SAR': {}}
    config['SAR']['input_folder'] = s1_slc_directory
    config['SAR']['output_folder'] = s1_grd_directory
    config['SAR']['gpt'] = '/software/snap/bin/gpt'
    config['SAR']['speckle_filter'] = {'multi_temporal': {'apply': 'yes'}}
    minx, miny, maxx, maxy = loads(roi).bounds
    config['SAR']['region'] = {'ul': {'lat': maxy, 'lon': minx}, 'lr': {'lat': miny, 'lon': maxx}}
    start_time = get_time_from_string(start_time)
    if start_time is not None:
        config['SAR']['year'] = start_time.year
    else:
        end_time = get_time_from_string(end_time)
        if end_time is not None:
            config['SAR']['year'] = end_time.year
    config_file_name = '{}/sar_config.yaml'.format(temp_dir)
    with open(config_file_name, 'w') as config_file:
        yaml.dump(config, config_file, default_flow_style=False)
    return config_file_name


def _get_data_stores_file() -> str:
    home_dir = str(Path.home())
    return '{0}/{1}/{2}'.format(home_dir, MULTIPLY_DIR_NAME, DATA_STORES_FILE_NAME)


def set_earth_data_authentication(username: str, password: str):
    data_stores_file = _get_data_stores_file()
    _set_earth_data_authentication_to_file(username, password, data_stores_file)


def _set_earth_data_authentication_to_file(username: str, password: str, data_stores_file: str):
    stream = open(data_stores_file, 'r')
    data_store_lists = yaml.safe_load(stream)
    for data_store_entry in data_store_lists:
        if data_store_entry['DataStore']['FileSystem']['type'] == 'LpDaacFileSystem':
            data_store_entry['DataStore']['FileSystem']['parameters']['username'] = username
            data_store_entry['DataStore']['FileSystem']['parameters']['password'] = password
    stream.close()
    with open(data_stores_file, 'w') as file:
        yaml.dump(data_store_lists, file, default_flow_style=False)


def set_permissions(file_refs: List[Union[str, FileRef]]):
    for file_ref in file_refs:
        if type(file_ref) == FileRef:
            file_ref = file_ref.url
        if os.path.isdir(file_ref):
            globbed_files = glob.glob('{}/**'.format(file_ref), recursive=True)
            for item in globbed_files:
                _set_permissions_for_file(item)
        else:
            _set_permissions_for_file(file_ref)
        parent_dir = _get_parent_dir(file_ref)
        while _need_to_set_permissions(parent_dir) and parent_dir != '/':
            _set_permissions_for_file(parent_dir)
            parent_dir = _get_parent_dir(parent_dir)


def _get_parent_dir(file: str):
    return os.path.abspath(os.path.join(file, os.pardir))


def _set_permissions_for_file(path: str):
    if _need_to_set_permissions(path):
        stat = os.stat(path)
        os.chmod(path, stat.st_mode | ALL_PERMISSIONS)


def _need_to_set_permissions(file_ref: str) -> bool:
    stat = os.stat(file_ref)
    return stat.st_mode & ALL_PERMISSIONS != ALL_PERMISSIONS and stat.st_uid == os.getuid()


def set_up_data_stores():
    data_stores_file = _get_data_stores_file()
    shutil.copyfile(PATH_TO_VM_DATA_STORES_FILE, data_stores_file)
    username = getpass.getuser()
    stream = open(data_stores_file, 'r')
    data_store_lists = yaml.safe_load(stream)
    for data_store_entry in data_store_lists:
        if 'temp_dir' in data_store_entry['DataStore']['FileSystem']['parameters']:
            temp_dir = data_store_entry['DataStore']['FileSystem']['parameters']['temp_dir'].replace('{user}', username)
            data_store_entry['DataStore']['FileSystem']['parameters']['temp_dir'] = temp_dir
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
        if 'path_to_json_file' in data_store_entry['DataStore']['MetaInfoProvider']['parameters']:
            data_store_entry['DataStore']['MetaInfoProvider']['parameters']['path_to_json_file'] = \
                data_store_entry['DataStore']['MetaInfoProvider']['parameters']['path_to_json_file'].\
                replace('{user}', username)

    stream.close()
    with open(data_stores_file, 'w') as file:
        yaml.dump(data_store_lists, file, default_flow_style=False)
