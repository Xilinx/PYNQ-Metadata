# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

from dataclasses import dataclass
from typing import Optional

from .metadata_object import MetadataObject
from .port import Port


@dataclass(repr=False)
class BusConnection(MetadataObject):
    """
    A Metadata model that describes a bus
    connection between two ports within a module
    """

    type: str = "bus"
    generic_type = "bus"
    src_port: str = ""
    dst_port: str = ""
    _src_port: Optional[Port] = None
    _dst_port: Optional[Port] = None
