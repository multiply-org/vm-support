#!/usr/bin/env python

from setuptools import setup

requirements = [
    'git',
    'pytest',
    'pyyaml',
]

__version__ = None
with open('vm_support/version.py') as f:
    exec(f.read())

setup(name='vm-support',
      version=__version__,
      description='Support for MULTIPLY VM',
      author='MULTIPLY Team',
      packages=['vm_support'],
      install_requires=requirements
)
