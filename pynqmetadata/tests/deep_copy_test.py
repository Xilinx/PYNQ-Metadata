# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

import os

from pynqmetadata.frontends import HwhFrontend

TEST_DIR = os.path.dirname(__file__)


def test_deep_copy():
    md1 = HwhFrontend(_hwhfile=f"{TEST_DIR}/hwhs/resizer.hwh")
    md2 = md1.copy()

    if md1.dict() != md2.dict():
        raise RuntimeError("Both copies of the metadata are not equivalent")

    # md1.blocks["axi_dma_0"].remove()

    # if md1.dict() == md2.dict():
    #    raise RuntimeError("Both copies are identical even after a core was removed")
