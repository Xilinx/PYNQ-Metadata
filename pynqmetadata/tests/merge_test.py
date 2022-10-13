# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

import os

from pynqmetadata import (BitField, Core, Module, Parameter, Port, Register,
                          Signal, SubordinatePort, Vlnv)
from pynqmetadata.errors import MergeConflict
from pynqmetadata.frontends import HwhFrontend

TEST_DIR = os.path.dirname(__file__)


def test_signal_merge():
    """Attempts to merge two signals together: expected to pass"""
    a = Signal(name="test", width=1, driver=True)
    b = Signal(name="test", width=1, driver=True)
    c = Signal(name="c_sig", width=1, driver=False)
    a.connect(c)
    b.merge(a)
    assert len(b.con_refs) > 0


def test_signal_merge_conflict_width():
    """Attempts to merge two signals where there is a known metadata conflict. Expect an error to be thrown"""
    a = Signal(name="test", width=1, driver=True)
    b = Signal(name="test", width=2, driver=True)
    try:
        a.merge(b)
    except MergeConflict:
        pass
    except:
        raise RuntimeError(f"Test failed. unexpected error outcome")


def test_register_merge():
    r1 = Register(name="r1", description="", offset=0, width=32, access="read")
    r1_dupe = Register(name="r1", description="", offset=0, width=32, access="read")
    r1.add(BitField(name="b1", LSB=0, MSB=5, access="read", description=""))
    r1_dupe.merge(r1)
    assert len(r1_dupe.bitfields) > 0


def test_port_merge():
    sp1 = SubordinatePort(name="sp1", baseaddr=0xDEADBEEF, range=65535)
    sp2 = SubordinatePort(name="sp1", baseaddr=0xDEADBEEF, range=65535)
    sp1.add(Register(name="r1", description="", offset=0, width=32, access="read"))
    sp1.add(Register(name="r2", description="", offset=0, width=32, access="read"))
    sp2.merge(sp1)
    assert len(sp2.registers) > 1


def test_port_merge_conflict():
    sp1 = SubordinatePort(name="sp1", baseaddr=0xDEADBEEF, range=65535)
    sp2 = SubordinatePort(name="sp1", baseaddr=0xDEADBEEF, range=65535)
    param1 = Parameter(name="p1", value="wibble")
    param2 = Parameter(name="p1", value="wobble")
    sp1.add(param1)
    sp2.add(param2)
    try:
        sp1.merge(sp2)
    except MergeConflict:
        pass
    except:
        raise RuntimeError(f"Test failed in an unexpected way")


def test_module_merge():
    """Test merging two artificial modules"""
    m1 = Module(name="m")
    vlnv = Vlnv(vendor="a", library="b", name="c1", version=(1, 0))
    c1 = Core(name="c1", vlnv=vlnv)
    sp1 = SubordinatePort(name="sp1", baseaddr=0xDEADBEEF, range=65535)
    sp1.add(Register(name="r1", description="", offset=0, width=32, access="read"))
    sp1.add(Register(name="r2", description="", offset=0, width=32, access="read"))
    c1.add(sp1)
    m1.add(c1)

    m2 = Module(name="m")
    vlnv = Vlnv(vendor="a", library="b", name="c1", version=(1, 0))
    c2 = Core(name="c1", vlnv=vlnv)
    sp2 = SubordinatePort(name="sp1", baseaddr=0xDEADBEEF, range=65535)
    c2.add(sp2)
    m2.add(c2)

    m2.merge(m1)
    assert len(m2.blocks["c1"].ports["sp1"].registers) > 1


def test_module_merge_conflict():
    m1 = Module(name="m")
    vlnv = Vlnv(vendor="a", library="b", name="c1", version=(1, 0))
    c1 = Core(name="c1", vlnv=vlnv)
    sp1 = SubordinatePort(name="sp1", baseaddr=0xDEADBEEF, range=65535)
    sp1.add(Register(name="r1", description="", offset=0, width=32, access="read"))
    sp1.add(Register(name="r2", description="", offset=0, width=32, access="read"))
    c1.add(sp1)
    m1.add(c1)

    m2 = Module(name="m")
    vlnv = Vlnv(vendor="a", library="b", name="c1", version=(1, 0))
    c2 = Core(name="c1", vlnv=vlnv)
    sp2 = SubordinatePort(name="sp1", baseaddr=0xDEADBEEF, range=65536)
    c2.add(sp2)
    m2.add(c2)

    try:
        m2.merge(m1)
    except MergeConflict:
        pass
    except:
        raise RuntimeError("Test failed! unexpected error")
