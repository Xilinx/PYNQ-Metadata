# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

from pynqmetadata import DFXCore, IPCore, Module, Port, Vlnv


def test_gen_simple_core():
    md = Module(name="hello")

    core_1 = IPCore(
        name="core_1",
        vlnv=Vlnv(vendor="xilinx.com", library="ip", name="core1", version=(1, 0)),
    )

    port_saxi = Port(name="saxi", type="subordinate")
    port_maxi = Port(name="maxi", type="manager")

    core_1.add(port_saxi)
    core_1.add(port_maxi)
    md.add(core_1)

    core_2 = DFXCore(name="dfx_region")
    md.add(core_2)

    print(md.json())
