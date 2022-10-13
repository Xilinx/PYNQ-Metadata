# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

from pynqmetadata import Core, Module, Port, Signal, Vlnv


def test_simple_connection():
    """
    A simple test to check connecting different signals together
    """
    mod = Module(name="mod")

    cvlnv = Vlnv(vendor="c", library="i", name="p", version=(1, 0))
    c1 = Core(name="c1", vlnv=cvlnv)
    c1p1 = Port(name="p1")
    c1p1.add(Signal(name="s_in", width=1, driver=False))
    c1p1.add(Signal(name="s_out", width=1, driver=True))
    c1.add(c1p1)

    c2 = Core(name="c2", vlnv=cvlnv)
    c2p1 = Port(name="p1")
    c2p1.add(Signal(name="s_in", width=1, driver=False))
    c2p1.add(Signal(name="s_out", width=1, driver=True))
    c2.add(c2p1)

    mod.add(c2)
    mod.add(c1)

    sig1 = mod.lookup("c1[block]:p1[port]:s_in[signal]")
    sig2 = mod.lookup("c2[block]:p1[port]:s_out[signal]")
    if isinstance(sig1, Signal) and isinstance(sig2, Signal):
        sig1.connect(sig2)
    else:
        raise RuntimeError(f"Test failed: sig1 and sig2 are not both Signals")
