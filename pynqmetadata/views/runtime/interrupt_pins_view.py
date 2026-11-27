# Copyright (C) 2022 Xilinx, Inc
# Copyright (C) 2022-2026 Advanced Micro Devices, Inc.
# SPDX-License-Identifier: BSD-3-Clause

from pydantic import Field
from pynqmetadata import MetadataExtension

from .interrupt_controllers_view import _interrupt_metadata
from .metadata_view import MetadataView


class InterruptIndex(MetadataExtension):
    index: int = Field(..., description="The interrupt input index")
    controller: str = Field(default="unknown", description="The parent interrupt controller")


class InterruptPinsView(MetadataView):
    """Interrupt pins connected to the processing system or AXI controllers."""

    def __init__(self, module, controllers):
        super().__init__(module=module)
        self._state = {}

    @property
    def view(self):
        _, pins, signals = _interrupt_metadata(self._md)
        for path, entry in pins.items():
            signals[path].ext["interrupt_index"] = InterruptIndex(
                index=entry["index"], controller=entry["controller"]
            )
        return pins

    def __setitem__(self, key, value):
        self._state[key] = value
