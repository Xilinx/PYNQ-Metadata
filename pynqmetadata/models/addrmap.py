# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

from pydantic import Field

from .metadata_object import MetadataObject
from .subordinate_port import SubordinatePort


class AddressMap(MetadataObject):
    """A model for the address mapping associated with a manager port"""

    block: str = Field(..., description="A text reference to this memory block")
    # baseaddr: int = Field(..., description="The base address of this memory region")
    memtype: str = Field(
        ..., description="The type of this memory region either Memory or Register"
    )
    subord_port: str = Field(
        ..., decription="A string reference to the subord port linked to this region"
    )
    subord_port_obj: SubordinatePort = Field(
        ...,
        exclude=True,
        description="An object reference to the subord port in this address map",
    )
