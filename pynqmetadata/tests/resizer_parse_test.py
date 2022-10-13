# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

import os

from pynqmetadata import SubordinatePort
from pynqmetadata.frontends import HwhFrontend

TEST_DIR = os.path.dirname(__file__)


class IncorrectRegisterNumber(Exception):
    pass


def test_parse_resizer():
    md = HwhFrontend(_hwhfile=f"{TEST_DIR}/hwhs/resizer.hwh")


def test_hls_core_register_parse():
    """Test to make sure that the registers have been parsed correctly"""
    md = HwhFrontend(_hwhfile=f"{TEST_DIR}/hwhs/resizer.hwh")
    resizer = md.blocks["resize_accel_0"]
    saxi = resizer.ports["s_axi_AXILiteS"]
    if isinstance(saxi, SubordinatePort):
        if len(saxi.registers) <= 0:
            raise IncorrectRegisterNumber(
                f"Error, no registers were found for the HLS IP in resizer"
            )
    else:
        raise ValueError("Expecting a subordinate port for saxi on the resizer")
