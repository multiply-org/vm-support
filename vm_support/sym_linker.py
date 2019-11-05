"""
Description
===========

This module contains functionality to create symbolic links. This is only supported for unix-based systems.
"""

from typing import List, Optional, Union
from multiply_core.observations import get_data_type_path, get_valid_type
from multiply_core.util import FileRef
import glob
import os

__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'


def create_sym_link(file_ref: Union[str, FileRef], folder: str, data_type: Optional[str] = None):
    """
    Puts a symbolic link to the file referenced by the fileref object into the designated folder. Only supported for
    linux.
    :param file_ref: A file to be referenced from another folder. Might either come as a file ref or a url.
    :param folder: The folder into which the data shall be placed.
    :param data_type: The data type of the file ref. Will be determined if not given.
    """
    if type(file_ref) == FileRef:
        file_ref = file_ref.url
    if not os.path.exists(folder):
        os.makedirs(folder)
    if data_type is None:
        data_type = get_valid_type(file_ref)
    relative_path = get_data_type_path(data_type, file_ref)
    if os.path.isdir(file_ref):
        # new_file is folder, too
        new_file = os.path.join(folder, relative_path)
        if not os.path.exists(new_file):
            os.makedirs(new_file)
        globbed_files = glob.glob('{}/**'.format(file_ref), recursive=True)
        for file in globbed_files:
            if os.path.isdir(file):
                continue
            relative_file_name = file.replace(file_ref, '')
            if relative_file_name.startswith('/'):
                relative_file_name = relative_file_name[1:]
            split_relative_file_name = relative_file_name.split('/')
            if len(split_relative_file_name) > 1:
                new_sub_dir = os.path.join(new_file, '/'.join(split_relative_file_name[:-1]))
                if not os.path.exists(new_sub_dir):
                    os.makedirs(new_sub_dir)
            new_sub_file = os.path.join(new_file, relative_file_name)
            if os.path.exists(new_sub_file):
                os.remove(new_sub_file)
            os.symlink(file, new_sub_file)
    else:
        file_name = file_ref.split('/')[-1]
        new_file = os.path.join(folder, relative_path, file_name)
        if os.path.exists(new_file):
            os.remove(new_file)
        os.symlink(file_ref, new_file)


def create_sym_links(file_refs: List[Union[str, FileRef]], folder: str, data_type: Optional[str] = None):
    """
    Puts symbolic links to the files referenced by the fileref object into the designated folder. Only supported for
    linux.
    :param file_ref: A list of files to be referenced from another folder.
    :param folder: The folder into which the data shall be placed.
    :param data_type: The data type of the file refs. Will be determined if not given. It is assumed that all data is
    of the same data type.
    """
    if len(file_refs) == 0:
        return
    if data_type is None:
        file_ref = file_refs[0]
        if type(file_ref) is FileRef:
            file_ref = file_ref.url
        data_type = get_valid_type(file_ref)
    for file_ref in file_refs:
        create_sym_link(file_ref, folder, data_type)
