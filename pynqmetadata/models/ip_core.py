# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

from dataclasses import dataclass

from .core import Core


@dataclass(repr=False)
class IPCore(Core):
    """
    Specialised core class for standard PL IP cores
    """

    type: str = "core-ip"
