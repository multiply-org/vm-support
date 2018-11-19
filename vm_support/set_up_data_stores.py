__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'

import pkg_resources
import shutil
from vm_support.utils import _get_data_stores_file

PATH_TO_VM_DATA_STORES_FILE = pkg_resources.resource_filename(__name__, 'vm_data_stores.yml')

shutil.copyfile(PATH_TO_VM_DATA_STORES_FILE, _get_data_stores_file())
