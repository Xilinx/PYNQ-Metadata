# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

import os

from pynqmetadata.frontends import HwhFrontend

TEST_DIR = os.path.dirname(__file__)


def test_timestamp():
    """Test for checking that editing a field updates the timestamps appropriately"""
    md = HwhFrontend(hwhfile=f"{TEST_DIR}/hwhs/resizer.hwh")
    dma = md.lookup("axi_dma_0[block]")
    saxi_bvalid = dma.lookup("S_AXI_LITE[port]:BVALID[signal]")

    initial_ts = saxi_bvalid.timestamp
    # change something
    saxi_bvalid.name = "testtest"

    # check to see if the timestamp has updated
    assert saxi_bvalid.timestamp > initial_ts
