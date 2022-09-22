# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations
from dataclasses import dataclass
from .scalar_port import ScalarPort

@dataclass(repr=False)
class RstPort(ScalarPort):
    """
    A reset port model, inherits from the scalar port model
    """
    type: str = "port-rst"
