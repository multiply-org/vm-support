#!/usr/bin/env python

from setuptools import setup

# requirements = [
#     'pytest',
#     'pyyaml',
# ]
requirements = []

__version__ = None
with open('vm_support/version.py') as f:
    exec(f.read())

setup(name='vm-support',
      version=__version__,
      description='Support for MULTIPLY VM',
      author='MULTIPLY Team',
      packages=['vm_support', 'vm_support.tools'],
      entry_points={
            'aux_data_provider_creators': ['mundi_aux_data_provider_creator = '
                                           'vm_support:mundi_aux_data_provider.MundiAuxDataProviderCreator']
      },
      install_requires=requirements
)
