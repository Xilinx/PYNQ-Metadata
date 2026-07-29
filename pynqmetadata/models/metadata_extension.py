# Copyright (C) 2022 Xilinx, Inc.
# Copyright (C) 2022 - 2026 Advanced Micro Devices, Inc.
# SPDX-License-Identifier: BSD-3-Clause

import pydantic
from pydantic import ConfigDict


class MetadataExtension(pydantic.BaseModel):
    """
    A basic object for the extension space of
    a metadata object.

    The idea here is that passes inherit from
    this class to define how they are extending
    the extension space (along with the schema)
    of that space
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
