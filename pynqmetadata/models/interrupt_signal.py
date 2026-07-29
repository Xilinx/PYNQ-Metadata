# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

from enum import Enum
from typing import List

from ..errors import InterruptSensitivityListError
from .signal import Signal


class SensitivityEnum(Enum):
    """
    Enumeration for the sensitivity of an interrupt
    signal
    """

    null = "NULL"
    level_high = "LEVEL_HIGH"
    level_low = "LEVEL_LOW"
    edge_rising = "EDGE_RISING"
    edge_falling = "EDGE_FALLING"

class InterruptSignal(Signal):
    """
    A signal class for interrupts
    """

    type: str = "signal-interrupt"
    driver: bool
    sensitivity: List[SensitivityEnum]

    def __post_init__(self) -> None:
        super().__post_init__()
        if len(self.sensitivity) != self.width:
            raise InterruptSensitivityListError(
                f"interrupt {self.name} has a width {self.width} but {len(self.sensitivity)} sensitivity were specified"
            )
