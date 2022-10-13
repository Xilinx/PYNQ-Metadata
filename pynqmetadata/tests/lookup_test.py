# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

import os

from pynqmetadata.frontends import HwhFrontend

TEST_DIR = os.path.dirname(__file__)


def test_lookups():
    """Test for checking that lookups are working as expected"""
    md = HwhFrontend(_hwhfile=f"{TEST_DIR}/hwhs/resizer.hwh")
    dma = md.lookup("axi_dma_0[block]")
    saxi = md.lookup("axi_dma_0[block]:S_AXI_LITE[port]")
    saxi_bvalid = md.lookup("axi_dma_0[block]:S_AXI_LITE[port]:BVALID[signal]")
    saxi = dma.lookup("S_AXI_LITE[port]")
    saxi_bvalid = dma.lookup("S_AXI_LITE[port]:BVALID[signal]")
    saxi_bvali = saxi.lookup("BVALID[signal]")
