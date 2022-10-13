# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

import os
import shutil
import tempfile

from pynqmetadata import ManagerPort, Module
from pynqmetadata.frontends import Metadata

TEST_DIR = os.path.dirname(__file__)
TMPDIR = tempfile.mkdtemp()

md1 = Metadata(input=f"{TEST_DIR}/hwhs/resizer.hwh")


def check_object_references(meta: Module) -> None:
    for block in meta.blocks.values():
        for port in block.ports.values():

            if isinstance(port, ManagerPort):
                assert len(port.addrmap) == len(port.addrmap_obj)

            for sig in port.signals.values():
                assert len(sig.con_refs) == len(sig._connections)


def test_obj_ref_hwh_parsed():
    check_object_references(md1)


def test_obj_ref_imported_json():
    """A test where:
    * we load a hwh
    * export the module as metadata
    * reimport the module from the json
    * then test for equivalence"""
    md1.export(path=f"{TMPDIR}/exported.json")
    md2 = Metadata(input=f"{TMPDIR}/exported.json")
    check_object_references(md2)
    shutil.rmtree(TMPDIR)
