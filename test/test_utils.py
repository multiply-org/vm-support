import os
import pytest
import shutil
import stat
import yaml
from vm_support.utils import create_config_file, create_sar_config_file, _set_earth_data_authentication_to_file, \
    set_permissions, _set_mundi_authentication_to_file

ALL_PERMISSIONS = stat.S_IRUSR + stat.S_IWUSR + stat.S_IXUSR + stat.S_IRGRP + stat.S_IWGRP + stat.S_IXGRP + \
                  stat.S_IROTH + stat.S_IWOTH + stat.S_IXOTH
BARRAX_POLYGON = "POLYGON((-2.20397502663252 39.09868106889479,-1.9142106223355313 39.09868106889479," \
                 "-1.9142106223355313 38.94504502508093,-2.20397502663252 38.94504502508093," \
                 "-2.20397502663252 39.09868106889479))"
TEST_DIR = './test/test_data/'
DATA_STORES_FILE = 'dummy_data_stores'
DATA_STORES_FILE_EXTENSION = '.yaml'


def test_create_config_file_default():
    config_file = '{}/config.yaml'.format(TEST_DIR)
    if os.path.exists(config_file):
        os.remove(config_file)
    try:
        priors_dir = '{}/priors'.format(TEST_DIR)
        create_config_file(TEST_DIR, BARRAX_POLYGON, '2017-06-01', '2017-06-30', '10', priors_dir)
        assert os.path.exists(config_file)
        with open(config_file) as config_stream:
            config = yaml.safe_load(config_stream)
            expected_config = {"General": {'end_time': '2017-06-30',
                                           'roi': 'POLYGON((-2.20397502663252 39.09868106889479,'
                                                  '-1.9142106223355313 39.09868106889479,'
                                                  '-1.9142106223355313 38.94504502508093,'
                                                  '-2.20397502663252 38.94504502508093,'
                                                  '-2.20397502663252 39.09868106889479))',
                                           'start_time': '2017-06-01', 'time_interval': '10'},
                               'Prior': {'General': {'directory_data': "/data/auxiliary/priors/Static/Vegetation/"},
                                         'ala': {'database': {'static_dir': 'same as General directory_data'}},
                                         'bsoil': {'database': {'static_dir': 'same as General directory_data'}},
                                         'cab': {'database': {'static_dir': 'same as General directory_data'}},
                                         'car': {'database': {'static_dir': 'same as General directory_data'}},
                                         'cb': {'database': {'static_dir': 'same as General directory_data'}},
                                         'cdm': {'database': {'static_dir': 'same as General directory_data'}},
                                         'cw': {'database': {'static_dir': 'same as General directory_data'}},
                                         'lai': {'database': {'static_dir': 'same as General directory_data'}},
                                         'n': {'database': {'static_dir': 'same as General directory_data'}},
                                         'psoil': {'database': {'static_dir': 'same as General directory_data'}},
                                         'output_directory': './test/test_data//priors'}}
            _assert_dict_equals(expected_config, config)
    finally:
        if os.path.exists(config_file):
            os.remove(config_file)


def _assert_dict_equals(expected: dict, actual: dict):
    assert expected.keys() == actual.keys()
    for key in expected:
        _assert_key_equals(expected[key], actual[key])


def _assert_key_equals(expected_key, actual_key):
    if type(expected_key) is dict:
        _assert_dict_equals(expected_key, actual_key)
    elif type(expected_key) is list:
        for i, item in enumerate(expected_key):
            _assert_key_equals(item, actual_key[i])
    else:
        assert expected_key == actual_key


def test_create_config_file_user_specified():
    config_file = '{}/config.yaml'.format(TEST_DIR)
    if os.path.exists(config_file):
        os.remove(config_file)
    try:
        priors_dir = '{}/priors'.format(TEST_DIR)
        variables = ['ala', 'bsoil', 'cab', 'car']
        user_priors = {'ala': {'unc': 0.1}, 'bsoil': {'mu': 0.6}, 'cab': {'mu': 70., 'unc': 10}, 'fg': {'unc': 24}}
        create_config_file(TEST_DIR, BARRAX_POLYGON, '2017-06-01', '2017-06-30', '10', priors_dir, variables,
                           user_priors)
        assert os.path.exists(config_file)
        with open(config_file) as config_stream:
            actual_config = yaml.safe_load(config_stream)
            expected_config = {"General": {'end_time': '2017-06-30',
                                           'roi': 'POLYGON((-2.20397502663252 39.09868106889479,'
                                                  '-1.9142106223355313 39.09868106889479,'
                                                  '-1.9142106223355313 38.94504502508093,'
                                                  '-2.20397502663252 38.94504502508093,'
                                                  '-2.20397502663252 39.09868106889479))',
                                           'start_time': '2017-06-01', 'time_interval': '10'},
                               'Prior': {'General': {'directory_data': "/data/auxiliary/priors/Static/Vegetation/"},
                                         'ala': {'database': {'static_dir': 'same as General directory_data'},
                                                 'user': {'unc': 0.1}},
                                         'bsoil': {'user': {'mu': 0.6}},
                                         'cab': {'user': {'mu': 70., 'unc': 10}},
                                         'car': {'database': {'static_dir': 'same as General directory_data'}},
                                         'output_directory': './test/test_data//priors'}}
        _assert_dict_equals(expected_config, actual_config)
    finally:
        if os.path.exists(config_file):
            os.remove(config_file)


def test_create_sar_config_file():
    sar_config_file = '{}sar_config.yaml'.format(TEST_DIR)
    if os.path.exists(sar_config_file):
        os.remove(sar_config_file)
    try:
        s1_slc_dir = '{}s1_slc'.format(TEST_DIR)
        s1_grd_dir = '{}s1_grd'.format(TEST_DIR)
        create_sar_config_file(TEST_DIR, BARRAX_POLYGON, '2017-06-01', '2017-06-30', s1_slc_dir, s1_grd_dir)
        assert os.path.exists(sar_config_file)
        with open(sar_config_file) as config_stream:
            actual_config = yaml.safe_load(config_stream)
            expected_config = \
                {"SAR": {
                    'input_folder': './test/test_data/s1_slc',
                    'output_folder': './test/test_data/s1_grd',
                    'gpt': '/software/snap/bin/gpt',
                    'speckle_filter': {'multi_temporal': {'apply': 'yes'}},
                    'region':
                        {'ul': {
                            'lat': 39.09868106889479,
                            'lon': -2.20397502663252
                        }, 'lr': {
                            'lat': 38.94504502508093,
                            'lon': -1.9142106223355313}},
                    'year': 2017}}
            _assert_dict_equals(expected_config, actual_config)
    finally:
        if os.path.exists(sar_config_file):
            os.remove(sar_config_file)


def test_set_earth_data_authentication():
    data_stores_file = '{}/{}{}'.format(TEST_DIR, DATA_STORES_FILE, DATA_STORES_FILE_EXTENSION)
    data_stores_file_2 = '{}/{}2{}'.format(TEST_DIR, DATA_STORES_FILE, DATA_STORES_FILE_EXTENSION)
    shutil.copyfile(data_stores_file, data_stores_file_2)
    try:
        _set_earth_data_authentication_to_file('fecvghf', 'tvhbg', data_stores_file_2)
        stream = open(data_stores_file_2, 'r')
        data_store_lists = yaml.safe_load(stream)
        for data_store_entry in data_store_lists:
            if data_store_entry['DataStore']['Id'] == 'modis_mcd43a1':
                assert data_store_entry['DataStore']['FileSystem']['parameters']['username'] == 'fecvghf'
                assert data_store_entry['DataStore']['FileSystem']['parameters']['password'] == 'tvhbg'
        stream.close()
    finally:
        os.remove(data_stores_file_2)


def test_set_mundi_authentication():
    data_stores_file = '{}/{}{}'.format(TEST_DIR, DATA_STORES_FILE, DATA_STORES_FILE_EXTENSION)
    data_stores_file_2 = '{}/{}2{}'.format(TEST_DIR, DATA_STORES_FILE, DATA_STORES_FILE_EXTENSION)
    shutil.copyfile(data_stores_file, data_stores_file_2)
    try:
        _set_mundi_authentication_to_file('fgezn', 'khjuzv', data_stores_file_2)
        stream = open(data_stores_file_2, 'r')
        data_store_lists = yaml.safe_load(stream)
        for data_store_entry in data_store_lists:
            if data_store_entry['DataStore']['Id'] == 'Mundi':
                assert data_store_entry['DataStore']['FileSystem']['parameters']['access_key_id'] == 'fgezn'
                assert data_store_entry['DataStore']['FileSystem']['parameters']['secret_access_key'] == 'khjuzv'
        stream.close()
    finally:
        os.remove(data_stores_file_2)


@pytest.mark.skip('Works only in Unix machines')
def test_set_permissions():
    new_test_dir = '{}{}'.format(TEST_DIR, 'dir1')
    try:
        os.mkdir(new_test_dir)
        newer_test_dir = '{}/{}'.format(new_test_dir, 'dir2')
        os.mkdir(newer_test_dir)
        file_name = '{}/{}'.format(newer_test_dir, 'file')
        open(file_name, "w+").close()
        set_permissions([file_name])
        assert os.stat(file_name).st_mode & ALL_PERMISSIONS == ALL_PERMISSIONS
        assert os.stat(new_test_dir).st_mode & ALL_PERMISSIONS == ALL_PERMISSIONS
        assert os.stat(newer_test_dir).st_mode & ALL_PERMISSIONS == ALL_PERMISSIONS
    finally:
        shutil.rmtree(new_test_dir)
