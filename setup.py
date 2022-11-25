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
from pathlib import Path


def attempt_download(url:str, path:Path)->None:
    """" Attempts to download a file and place it in the path. Stops siliently if it is not able to """
    import urllib.request
    try:
        opener = urllib.request.build_opener()
        opener.addheaders = [(('User-Agent', 'Mozilla/5.0'))]
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(url, path) 
    except:
        pass



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

attempt_download(url='http://d3js.org/d3.v4.min.js', path=Path('pynqmetadata/frontends/visualisations/lib/d3.v4.min.js'))
attempt_download(url='https://www.xilinx.com/bin/public/openDownload?filename=pynqhelloworld.resizer.pynqz2.hwh', path=Path('pynqmetadata/tests/hwhs/resizer.hwh'))
attempt_download(url='https://raw.githubusercontent.com/strath-sdr/rfsoc_sam/master/boards/RFSoC4x2/rfsoc_sam/bitstream/rfsoc_sam.hwh', path=Path('pynqmetadata/tests/hwhs/rfsoc_sam.hwh'))


# Get the version
ver_file = open("./pynqmetadata/version.txt", "r")
ver_str = ver_file.readline();

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Get the files
pynq_metadata_files=[]

extend_pynq_metadata_package([
        'pynqmetadata/models/',
        'pynqmetadata/errors/',
        'pynqmetadata/frontends/',
        'pynqmetadata/frontends/visualisations',
        'pynqmetadata/frontends/visualisations/lib',
        'pynqmetadata/version.txt',
        'pynqmetadata/tests'
    ])

# Required packages
required = [
        "jsonschema>=3.2.0",
        "pydantic"
]


setup(  name='pynqmetadata',
        version=ver_str,
        description="Extensible, Modular, Metadata layer for PYNQ projects",
        long_description=long_description,
        long_description_content_type='text/markdown',
        url='http://github.com/Xilinx/PYNQ-Metadata',
        author='Pynq',
        author_email='pynq_support@xilinx.com',
        packages=find_packages(),
        install_requires=required,
        python_requires='>=3.8',
        package_data = {
            'pynqmetadata': pynq_metadata_files,
            },
        zip_safe=False,
        license="BSD 3-Clause"
        )
