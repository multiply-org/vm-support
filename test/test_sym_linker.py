__author__ = "Tonio Fincke (Brockmann Consult GmbH)"

import os
import shutil
from multiply_core.util import FileRef
from vm_support.sym_linker import create_sym_link, create_sym_links

_FOLDER = './test/test_data/out'


def test_create_sym_link_single_file():
    file_ref = FileRef('./test/test_data/ASTGTM2_N36W006_dem.tif', None, None, 'image/tiff')
    expected_sym_link_name = os.path.join(_FOLDER, 'ASTGTM2_N36W006_dem.tif')
    try:
        assert not os.path.exists(_FOLDER)

        create_sym_link(file_ref, _FOLDER)

        new_list = os.listdir(_FOLDER)
        assert 1 == len(new_list)
        assert 'ASTGTM2_N36W006_dem.tif' in new_list
        assert os.path.islink(expected_sym_link_name)
    finally:
        if os.path.islink('./test/test_data/out/ASTGTM2_N36W006_dem.tif'):
            os.unlink('./test/test_data/out/ASTGTM2_N36W006_dem.tif')
        if os.path.exists(_FOLDER):
            shutil.rmtree(_FOLDER)


def test_create_sym_link_s2_aws_data():
    file_ref = FileRef('./test/test_data/29/S/QB/2017/9/4/0', None, None, 'application/x-directory')
    expected_sym_link_name = os.path.join(_FOLDER, '29/S/QB/2017/9/4/0/')
    try:
        assert not os.path.exists(_FOLDER)

        create_sym_link(file_ref, _FOLDER)

        new_list = os.listdir(expected_sym_link_name)
        assert 15 == len(new_list)
        assert 'B01.jp2' in new_list
        assert os.path.islink('./test/test_data/out/29/S/QB/2017/9/4/0/B01.jp2')
        assert 'B02.jp2' in new_list
        assert os.path.islink('./test/test_data/out/29/S/QB/2017/9/4/0/B02.jp2')
        assert 'B03.jp2' in new_list
        assert os.path.islink('./test/test_data/out/29/S/QB/2017/9/4/0/B03.jp2')
        assert 'B04.jp2' in new_list
        assert os.path.islink('./test/test_data/out/29/S/QB/2017/9/4/0/B04.jp2')
        assert 'B05.jp2' in new_list
        assert os.path.islink('./test/test_data/out/29/S/QB/2017/9/4/0/B05.jp2')
        assert 'B06.jp2' in new_list
        assert os.path.islink('./test/test_data/out/29/S/QB/2017/9/4/0/B06.jp2')
        assert 'B07.jp2' in new_list
        assert os.path.islink('./test/test_data/out/29/S/QB/2017/9/4/0/B07.jp2')
        assert 'B08.jp2' in new_list
        assert os.path.islink('./test/test_data/out/29/S/QB/2017/9/4/0/B08.jp2')
        assert 'B09.jp2' in new_list
        assert os.path.islink('./test/test_data/out/29/S/QB/2017/9/4/0/B09.jp2')
        assert 'B8A.jp2' in new_list
        assert os.path.islink('./test/test_data/out/29/S/QB/2017/9/4/0/B8A.jp2')
        assert 'B10.jp2' in new_list
        assert os.path.islink('./test/test_data/out/29/S/QB/2017/9/4/0/B10.jp2')
        assert 'B11.jp2' in new_list
        assert os.path.islink('./test/test_data/out/29/S/QB/2017/9/4/0/B11.jp2')
        assert 'B12.jp2' in new_list
        assert os.path.islink('./test/test_data/out/29/S/QB/2017/9/4/0/B12.jp2')
        assert 'metadata.xml' in new_list
        assert os.path.islink('./test/test_data/out/29/S/QB/2017/9/4/0/metadata.xml')
        assert 'qi' in new_list
        assert os.path.islink('./test/test_data/out/29/S/QB/2017/9/4/0/qi/some_file')
    finally:
        if os.path.exists('./test/test_data/out/29/S/QB/2017/9/4/0/'):
            shutil.rmtree('./test/test_data/out/')


def test_create_symlinks_ASTER():
    file_refs = [FileRef('./test/test_data/ASTGTM2_N36W006_dem.tif', None, None, 'image/tiff'),
                 FileRef('./test/test_data/ASTGTM2_N36W007_dem.tif', None, None, 'image/tiff')]

    expected_sym_link_name_1 = os.path.join(_FOLDER, 'ASTGTM2_N36W006_dem.tif')
    expected_sym_link_name_2 = os.path.join(_FOLDER, 'ASTGTM2_N36W006_dem.tif')
    try:
        assert not os.path.exists(_FOLDER)

        create_sym_links(file_refs, _FOLDER)

        new_list = os.listdir(_FOLDER)
        assert 2 == len(new_list)
        assert 'ASTGTM2_N36W006_dem.tif' in new_list
        assert os.path.islink(expected_sym_link_name_1)
        assert 'ASTGTM2_N36W007_dem.tif' in new_list
        assert os.path.islink(expected_sym_link_name_2)
    finally:
        if os.path.islink('./test/test_data/out/ASTGTM2_N36W006_dem.tif'):
            os.unlink('./test/test_data/out/ASTGTM2_N36W006_dem.tif')
        if os.path.islink('./test/test_data/out/ASTGTM2_N36W007_dem.tif'):
            os.unlink('./test/test_data/out/ASTGTM2_N36W007_dem.tif')
        if os.path.exists(_FOLDER):
            shutil.rmtree(_FOLDER)


def test_create_symlinks_ASTER_type_given():
    file_refs = [FileRef('./test/test_data/ASTGTM2_N36W006_dem.tif', None, None, 'image/tiff'),
                 FileRef('./test/test_data/ASTGTM2_N36W007_dem.tif', None, None, 'image/tiff')]

    expected_sym_link_name_1 = os.path.join(_FOLDER, 'ASTGTM2_N36W006_dem.tif')
    expected_sym_link_name_2 = os.path.join(_FOLDER, 'ASTGTM2_N36W006_dem.tif')
    try:
        assert not os.path.exists(_FOLDER)

        create_sym_links(file_refs, _FOLDER, 'ASTER')

        new_list = os.listdir(_FOLDER)
        assert 2 == len(new_list)
        assert 'ASTGTM2_N36W006_dem.tif' in new_list
        assert os.path.islink(expected_sym_link_name_1)
        assert 'ASTGTM2_N36W007_dem.tif' in new_list
        assert os.path.islink(expected_sym_link_name_2)
    finally:
        if os.path.islink('./test/test_data/out/ASTGTM2_N36W006_dem.tif'):
            os.unlink('./test/test_data/out/ASTGTM2_N36W006_dem.tif')
        if os.path.islink('./test/test_data/out/ASTGTM2_N36W007_dem.tif'):
            os.unlink('./test/test_data/out/ASTGTM2_N36W007_dem.tif')
        if os.path.exists(_FOLDER):
            shutil.rmtree(_FOLDER)


def test_create_symlinks_s2_aws_data_type_given():
    file_refs = [FileRef('./test/test_data/29/S/QB/2017/9/4/0', None, None, 'application/x-directory'),
                 FileRef('./test/test_data/30/T/XZ/2016/2/2/1/', None, None, 'application/x-directory')]
    expected_sym_links = [os.path.join(_FOLDER, '29/S/QB/2017/9/4/0/'), os.path.join(_FOLDER, '30/T/XZ/2016/2/2/1/')]
    try:
        assert not os.path.exists(_FOLDER)

        create_sym_links(file_refs, _FOLDER, 'AWS_S2_L1C')
        for expected_sym_link in expected_sym_links:
            new_list = os.listdir(expected_sym_link)
            assert 15 == len(new_list)
            assert 'B01.jp2' in new_list
            assert os.path.islink('{}/B01.jp2'.format(expected_sym_link))
            assert 'B02.jp2' in new_list
            assert os.path.islink('{}/B02.jp2'.format(expected_sym_link))
            assert 'B03.jp2' in new_list
            assert os.path.islink('{}/B03.jp2'.format(expected_sym_link))
            assert 'B04.jp2' in new_list
            assert os.path.islink('{}/B04.jp2'.format(expected_sym_link))
            assert 'B05.jp2' in new_list
            assert os.path.islink('{}/B05.jp2'.format(expected_sym_link))
            assert 'B06.jp2' in new_list
            assert os.path.islink('{}/B06.jp2'.format(expected_sym_link))
            assert 'B07.jp2' in new_list
            assert os.path.islink('{}/B07.jp2'.format(expected_sym_link))
            assert 'B08.jp2' in new_list
            assert os.path.islink('{}/B08.jp2'.format(expected_sym_link))
            assert 'B09.jp2' in new_list
            assert os.path.islink('{}/B09.jp2'.format(expected_sym_link))
            assert 'B8A.jp2' in new_list
            assert os.path.islink('{}/B8A.jp2'.format(expected_sym_link))
            assert 'B10.jp2' in new_list
            assert os.path.islink('{}/B10.jp2'.format(expected_sym_link))
            assert 'B11.jp2' in new_list
            assert os.path.islink('{}/B11.jp2'.format(expected_sym_link))
            assert 'B12.jp2' in new_list
            assert os.path.islink('{}/B12.jp2'.format(expected_sym_link))
            assert 'metadata.xml' in new_list
            assert os.path.islink('{}/metadata.xml'.format(expected_sym_link))
            assert 'qi' in new_list
            assert os.path.islink('{}/qi/some_file'.format(expected_sym_link))
    finally:
        if os.path.exists(_FOLDER):
            shutil.rmtree(_FOLDER)