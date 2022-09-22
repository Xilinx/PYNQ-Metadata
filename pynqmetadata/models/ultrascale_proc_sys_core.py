# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

from dataclasses import dataclass, field
from typing import Dict

from .proc_sys_core import ProcSysCore


@dataclass(repr=False)
class UltrascaleProcSysCore(ProcSysCore):
    """A specialised pydantic model for the Ultrascale Zynq processing system"""

    type: str = "core-zynq_aarch64"
    ps_name: str = "zynq_ultra_ps_e"
    gpio_name: str = "GPIO_0"
    irq: Dict[str, object] = field(
        default_factory=lambda: ({"pl_ps_irq0": ((121, 8),), "pl_ps_irq1": ((136, 8),)})
    )

    def clk_div_param_name(self, clk_id: int, div_id: int) -> str:
        """Returns the name of the clock div parameter for this PS"""
        return f"PSU__CRL_APB__PL{clk_id}_REF_CTRL__DIVISOR{div_id}"

    def clk_enable_param_name(self, clk_id: int) -> str:
        """Returns the parameter for the clock enable for clock with id clk_id on this PS"""
        return f"PSU__FPGA_PL{clk_id}_ENABLE"
