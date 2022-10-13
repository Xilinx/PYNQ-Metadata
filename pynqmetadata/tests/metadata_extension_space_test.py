# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

import os

from pydantic import Field
from pynqmetadata import MetadataExtension, MetadataObject, ProcSysCore
from pynqmetadata.frontends import HwhFrontend

TEST_DIR = os.path.dirname(__file__)


class TagAllCores_PS(MetadataExtension):
    """Simple extension to PS metadata"""

    ps: bool


def test_ps_tag_extension():
    """Tests if metadata extension can be read properly"""
    md = HwhFrontend(_hwhfile=f"{TEST_DIR}/hwhs/resizer.hwh")
    for core in md.blocks.values():
        core.ext["procsys"] = TagAllCores_PS(ps=isinstance(core, ProcSysCore))

    for core in md.blocks.values():
        if core.ext["procsys"].ps:
            assert isinstance(core, ProcSysCore)


class DummyDriver:
    def __init__(self):
        self.name: str = "driver"
        pass


class HiddenDriverExt(MetadataExtension):
    """Simple extension but storing an object that we don't want to be rendered"""

    driver: object = Field(..., exclude=True)


def test_tag_cores_hidden():
    """Testing the extension storing a hidden object"""
    md = HwhFrontend(_hwhfile=f"{TEST_DIR}/hwhs/resizer.hwh")
    for core in md.blocks.values():
        core.ext["driver"] = HiddenDriverExt(driver=DummyDriver())

    for core in md.blocks.values():
        if core.ext["driver"].driver.name != "driver":
            raise RuntimeError("Test failed, could not access the driver")


def test_tag_cores_hidden_json_render():
    """Tests that when we have an object in a field that we can still generate the json from the pydantic model"""
    md = HwhFrontend(_hwhfile=f"{TEST_DIR}/hwhs/resizer.hwh")
    for core in md.blocks.values():
        core.ext["driver"] = HiddenDriverExt(driver=DummyDriver())

    md.json()
