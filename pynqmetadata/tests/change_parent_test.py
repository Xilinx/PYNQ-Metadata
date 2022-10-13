# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

import os

from pynqmetadata import Core, MetadataObject, Module, Vlnv
from pynqmetadata.errors import MetadataObjectNotFound
from pynqmetadata.frontends import HwhFrontend

TEST_DIR = os.path.dirname(__file__)


def test_parent_move():
    """
    Test to see if moving a core to a different parent happens correctly
    """
    pmd = HwhFrontend(_hwhfile=f"{TEST_DIR}/hwhs/resizer.hwh")
    md = pmd

    dma_saxi_lite = md.lookup("axi_dma_0[block]:S_AXI_LITE[port]")
    if dma_saxi_lite is None:
        raise RuntimeError(
            "Test failed: could not lookup resizer:axi_dma_0:S_AXI_LITE "
        )

    new_module = Module(name="test")
    new_core = Core(
        name="testcore", vlnv=Vlnv(vendor="s", library="t", name="f", version=(1, 0))
    )
    new_module.add(new_core)
    dma_saxi_lite.set_parent(new_core)

    if new_module.lookup("testcore[block]:S_AXI_LITE[port]") is None:
        raise RuntimeError("Test failed, cannot be looked up in new module")
