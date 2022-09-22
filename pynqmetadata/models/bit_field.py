# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

from dataclasses import dataclass

from .metadata_object import MetadataObject


@dataclass(repr=False)
class BitField(MetadataObject):
    """
    Model that describes a bit field
    """

    type: str = "bitfield"
    generic_type: str = "bitfield"
    LSB: int = 0
    MSB: int = 0
    description: str = "A field in the register"
    access: str = "read-write"
