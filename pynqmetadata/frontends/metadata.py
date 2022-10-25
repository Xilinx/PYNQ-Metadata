# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

import json
import os
from distutils.command.install_headers import install_headers
from typing import Optional

from pydantic import Field

from ..models.metadata_extension import MetadataExtension
from ..models.metadata_object import MetadataObject
from ..models.module import Module
from .hwh_frontend import HwhFrontend
from .json_frontend import JsonFrontend
from .xsa_frontend import XsaFrontend


class ExpectedFileInput(Exception):
    pass


class UnknownInputFileExtension(Exception):
    pass


def Metadata(input: str) -> MetadataObject:
    """
    Can accept:
        * An XSA file
        * A HWH file
        * A JSON file of the metadata

        and will produce a metadata module
    """

    if os.path.isfile(input):
        if str(input).endswith(".hwh"):
            return HwhFrontend(_hwhfile=input)
        elif str(input).endswith(".xsa"):
            return XsaFrontend(input=input) 
        elif str(input).endswith(".json"):
            return JsonFrontend(input=input)
        else:
            raise UnknownInputFileExtension(f"{input} is not a valid input")
    else:
        raise ExpectedFileInput(f"{input} is not a valid path to a file")
