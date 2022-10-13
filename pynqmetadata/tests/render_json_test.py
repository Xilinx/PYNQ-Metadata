# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

import os

from pynqmetadata.frontends import HwhFrontend

TEST_DIR = os.path.dirname(__file__)


def test_json_generate():
    md = HwhFrontend(_hwhfile=f"{TEST_DIR}/hwhs/resizer.hwh")
    print(md.json())
