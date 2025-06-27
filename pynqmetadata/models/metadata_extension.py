# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

import pydantic


class MetadataExtension(pydantic.BaseModel):
    """
    A basic object for the extension space of
    a metadata object.

    The idea here is that passes inherit from
    this class to define how they are extending
    the extension space (along with the schema)
    of that space
    """

    # In Pydantic v2+, underscore attrs are private by default
    if int(pydantic.__version__.split('.')[0]) < 2:
        class Config:
            underscore_attrs_are_private = True
