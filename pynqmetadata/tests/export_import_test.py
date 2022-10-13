# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

import os
import shutil
import tempfile

from pynqmetadata.frontends import Metadata

TEST_DIR = os.path.dirname(__file__)
TMPDIR = tempfile.mkdtemp()


def test_export_then_import_metadata():
    """A test where:
    * we load a hwh
    * export the module as metadata
    * reimport the module from the json
    * then test for equivalence"""

    md1 = Metadata(input=f"{TEST_DIR}/hwhs/resizer.hwh")
    md1.export(path=f"{TMPDIR}/exported.json")
    md2 = Metadata(input=f"{TMPDIR}/exported.json")

    if md1.dict() != md2.dict():
        from deepdiff import DeepDiff

        diff = DeepDiff(md1.dict(), md2.dict(), ignore_order=True)
        print(diff)
        raise RuntimeError(
            "Reloading a parsed HWH from a JSON does not produce an equivalent metadata object"
        )

    shutil.rmtree(TMPDIR)
