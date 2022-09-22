# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

from dataclasses import dataclass

from .core import Core
from .vlnv import Vlnv


@dataclass(repr=False)
class DFXCore(Core):
    """
    A core to define a dynamic function exchange (DFX) region (treated like a core)
    """

    type: str = "core-dfx"
    vlnv: Vlnv = Vlnv(vendor="xilinx.com", library="ip", name="dfx", version=(1, 0))
