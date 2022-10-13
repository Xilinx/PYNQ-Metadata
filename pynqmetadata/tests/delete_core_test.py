# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

import os

from pynqmetadata import MetadataObject
from pynqmetadata.frontends import HwhFrontend

TEST_DIR = os.path.dirname(__file__)


def test_core_removal():
    md = HwhFrontend(_hwhfile=f"{TEST_DIR}/hwhs/resizer.hwh")
    md.blocks["axi_dma_0"].remove()

    for core in md.blocks.values():
        for port in core.ports.values():
            for dest in port.destinations().values():
                if isinstance(dest.parent(), MetadataObject):
                    if dest.parent().name == "axi_dma_0":
                        raise RuntimeError(
                            f"Port {port.ref} is still connected to axi_dma_0 after it has been removed"
                        )
