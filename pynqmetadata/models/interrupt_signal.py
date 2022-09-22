# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

from enum import Enum
from typing import List

import pydantic

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

    @pydantic.validator("sensitivity")
    @classmethod
    def sensitivity_len_check(cls, value: List[SensitivityEnum]):
        """
        Check to make sure that the length of the sensitivity
        is the same as the width of the wire
        """
        if len(value) != cls.width:
            raise InterruptSensitivityListError(
                f"interrupt {cls.name} has a width {cls.width} but {len(value)} sensitivity were specified"
            )
