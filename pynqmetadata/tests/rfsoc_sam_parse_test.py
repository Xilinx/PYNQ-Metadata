# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

import os

from pynqmetadata import SubordinatePort
from pynqmetadata.frontends import HwhFrontend

TEST_DIR = os.path.dirname(__file__)


class IncorrectRegisterNumber(Exception):
    pass


def test_parse_rfsoc_sam():
    md = HwhFrontend(_hwhfile=f"{TEST_DIR}/hwhs/rfsoc_sam.hwh")

