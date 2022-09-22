# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

from dataclasses import dataclass, field
from typing import Dict

from .proc_sys_core import ProcSysCore


@dataclass(repr=False)
class ZynqProcSysCore(ProcSysCore):
    """A specialised pydantic model the the Zynq 7000 processing system"""

    type: str = "core-zynq_arm"
    ps_name: str = "processing_system7"
    gpio_name: str = "GPIO_0"
    irq: Dict[str, object] = field(
        default_factory=lambda: (
            {
                "IRQ_F2P": ((61, 8), (84, 8)),
            }
        )
    )

    def clk_div_param_name(self, clk_id: int, div_id: int) -> str:
        """Returns the name of the clock div parameters for this PS"""
        return f"PCW_FCLK{clk_id}_PERIPHERAL_DIVISOR{div_id}"

    def clk_enable_param_name(self, clk_id: int) -> str:
        """Returns the parameter for the clock enable for clock with ID clk_id on this PS"""
        return f"PCW_FPGA_FCLK{clk_id}_ENABLE"
