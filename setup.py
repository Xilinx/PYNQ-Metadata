# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

from setuptools import setup, Extension, find_packages, Distribution
from setuptools.command.build_ext import build_ext
from distutils.dir_util import copy_tree
from distutils.file_util import copy_file, move_file
from shutil import rmtree
import shutil
import glob
import re
import subprocess
import os
import warnings

# extend the package files by directory or by file
def extend_pynq_metadata_package(data_list):
    for data in data_list:
        if os.path.isdir(data):
            pynq_metadata_files.extend(
                [os.path.join("..", root, f)
                 for root, _, files in os.walk(data) for f in files]
            )
        elif os.path.isfile(data):
            pynq_metadata_files.append(os.path.join("..", data))

# Download d3 dependency
import urllib.request
from pathlib import Path
try:
    opener = urllib.request.build_opener()
    opener.addheaders = [(('User-Agent', 'Mozilla/5.0'))]
    urllib.request.install_opener(opener)
    urllib.request.urlretrieve('http://d3js.org/d3.v4.min.js', 
                                Path('pynqmetadata/frontends/visualisations/lib/d3.v4.min.js'))
except:
    pass

# Get the version
ver_file = open("./pynqmetadata/version.txt", "r")
ver_str = ver_file.readline();
with open("README.md", encoding='utf-8') as fh:
    readme_lines = fh.readlines()[:]
long_description = (''.join(readme_lines))

# Get the files
pynq_metadata_files=[]

extend_pynq_metadata_package([
        'pynqmetadata/models/',
        'pynqmetadata/errors/',
        'pynqmetadata/frontends/',
        'pynqmetadata/frontends/visualisations',
        'pynqmetadata/frontends/visualisations/lib',
        'pynqmetadata/version.txt'
    ])

# Required packages
required = [
        "jsonschema>=3.2.0",
        "pydantic"
]


setup(  name='pynqmetadata',
        version=ver_str,
        description="Extensible, Modular, Metadata layer for PYNQ projects",
        url='',
        author='Pynq',
        author_email='pynq_support@xilinx.com',
        packages=find_packages(),
        install_requires=required,
        python_requires='>=3.5.2',
        package_data = {
            'pynqmetadata': pynq_metadata_files,
            },
        zip_safe=False,
        license="BSD 3-Clause"
        )
