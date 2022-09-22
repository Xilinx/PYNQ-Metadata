# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

from dataclasses import dataclass

from .core import Core


@dataclass(repr=False)
class MicroblazeCore(Core):
    """
    A microblaze core type
    """

    type: str = "core-microblaze"
