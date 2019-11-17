import os
import pytest

from vm_support import MundiAuxDataProvider, MundiAuxDataProviderCreator

PARAMETERS = {
    'access_key_id': '',        # place actual key id to run tests
    'secret_access_key': ''     # place actual secret access key
}
BASE_FOLDER = './test/test_data/base_folder'


def test_name():
    provider = MundiAuxDataProvider(PARAMETERS)

    assert 'MUNDI' == provider.name()


@pytest.mark.skip(reason='Test requires MUNDI keys')
def test_list_elements():
    mundi_aux_data_provider = MundiAuxDataProvider(PARAMETERS)
    elements = mundi_aux_data_provider.list_elements(BASE_FOLDER, return_absolute_paths=False)
    assert 12 == len(elements)
    assert './test/test_data/base_folder/ESA_CCI_SM_clim_01.tiff' in elements
    assert './test/test_data/base_folder/ESA_CCI_SM_clim_02.tiff' in elements
    assert './test/test_data/base_folder/ESA_CCI_SM_clim_03.tiff' in elements
    assert './test/test_data/base_folder/ESA_CCI_SM_clim_04.tiff' in elements
    assert './test/test_data/base_folder/ESA_CCI_SM_clim_05.tiff' in elements
    assert './test/test_data/base_folder/ESA_CCI_SM_clim_06.tiff' in elements
    assert './test/test_data/base_folder/ESA_CCI_SM_clim_07.tiff' in elements
    assert './test/test_data/base_folder/ESA_CCI_SM_clim_08.tiff' in elements
    assert './test/test_data/base_folder/ESA_CCI_SM_clim_09.tiff' in elements
    assert './test/test_data/base_folder/ESA_CCI_SM_clim_10.tiff' in elements
    assert './test/test_data/base_folder/ESA_CCI_SM_clim_11.tiff' in elements
    assert './test/test_data/base_folder/ESA_CCI_SM_clim_12.tiff' in elements


@pytest.mark.skip(reason='Test requires MUNDI keys')
def test_list_elements_pattern_1():
    mundi_aux_data_provider = MundiAuxDataProvider(PARAMETERS)
    elements = mundi_aux_data_provider.list_elements(BASE_FOLDER, '*_clim_0*', return_absolute_paths=False)
    assert 9 == len(elements)
    assert './test/test_data/base_folder/ESA_CCI_SM_clim_01.tiff' in elements
    assert './test/test_data/base_folder/ESA_CCI_SM_clim_02.tiff' in elements
    assert './test/test_data/base_folder/ESA_CCI_SM_clim_03.tiff' in elements
    assert './test/test_data/base_folder/ESA_CCI_SM_clim_04.tiff' in elements
    assert './test/test_data/base_folder/ESA_CCI_SM_clim_05.tiff' in elements
    assert './test/test_data/base_folder/ESA_CCI_SM_clim_06.tiff' in elements
    assert './test/test_data/base_folder/ESA_CCI_SM_clim_07.tiff' in elements
    assert './test/test_data/base_folder/ESA_CCI_SM_clim_08.tiff' in elements
    assert './test/test_data/base_folder/ESA_CCI_SM_clim_09.tiff' in elements


@pytest.mark.skip(reason='Test requires MUNDI keys')
def test_list_elements_pattern_2():
    mundi_aux_data_provider = MundiAuxDataProvider(PARAMETERS)
    elements = mundi_aux_data_provider.list_elements(BASE_FOLDER, '*_clim_1*', return_absolute_paths=False)
    assert 3 == len(elements)
    assert './test/test_data/base_folder/ESA_CCI_SM_clim_10.tiff' in elements
    assert './test/test_data/base_folder/ESA_CCI_SM_clim_11.tiff' in elements
    assert './test/test_data/base_folder/ESA_CCI_SM_clim_12.tiff' in elements


def test_assure_element_provided_set():
    mundi_aux_data_provider = MundiAuxDataProvider(PARAMETERS)

    provided = mundi_aux_data_provider.assure_element_provided('./test/test_data/base_folder/ESA_CCI_SM_clim_02.tiff')
    assert provided
    assert os.path.exists('./test/test_data/base_folder/ESA_CCI_SM_clim_02.tiff')


@pytest.mark.skip(reason='Test requires MUNDI keys')
def test_assure_element_provided_download():
    try:
        mundi_aux_data_provider = MundiAuxDataProvider(PARAMETERS)

        provided = mundi_aux_data_provider.\
            assure_element_provided('./test/test_data/base_folder/ESA_CCI_SM_clim_10.tiff')
        assert provided
        assert os.path.exists('./test/test_data/base_folder/ESA_CCI_SM_clim_10.tiff')
    finally:
        if os.path.exists('./test/test_data/base_folder/ESA_CCI_SM_clim_10.tiff'):
            os.remove('./test/test_data/base_folder/ESA_CCI_SM_clim_10.tiff')


@pytest.mark.skip(reason='Test requires MUNDI keys')
def test_assure_element_provided_not():
    mundi_aux_data_provider = MundiAuxDataProvider(PARAMETERS)

    provided = mundi_aux_data_provider.assure_element_provided('./test/test_data/base_folder/ESA_CCI_SM_clim_13.tiff')
    assert not provided
    assert not os.path.exists('./test/test_data/base_folder/ESA_CCI_SM_clim_13.tiff')


def test_mundi_aux_data_provider_creator_name():
    assert 'MUNDI' == MundiAuxDataProviderCreator().name()


def test_mundi_aux_data_provider_creator_create_aux_data_provider():
    provider = MundiAuxDataProviderCreator().create_aux_data_provider({'access_key_id': '', 'secret_access_key': ''})

    assert provider is not None
    assert 'MUNDI' == provider.name()
