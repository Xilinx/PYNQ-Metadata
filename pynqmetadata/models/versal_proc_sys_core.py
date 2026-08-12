# Copyright (C) 2026 Advanced Micro Devices, Inc.
# SPDX-License-Identifier: BSD-3-Clause

import re
from dataclasses import dataclass

from ..errors import ParameterNotFound
from .proc_sys_core import ProcSysCore


@dataclass(repr=False)
class VersalProcSysCore(ProcSysCore):
    """A specialised model for the Versal CIPS processing system.

    Versal PL clocks are frequency-based (set in PS_PMC_CONFIG_INTERNAL)
    rather than divisor-based like Zynq/Ultrascale.
    """

    type: str = "core-versal"
    ps_name: str = "versal_cips"

    def _ps_pmc_config(self) -> str:
        if "PS_PMC_CONFIG_INTERNAL" in self.parameters:
            return self.parameters["PS_PMC_CONFIG_INTERNAL"].value or ""
        raise ParameterNotFound(f"PS_PMC_CONFIG_INTERNAL not found for {self.ref}")

    def find_clock_frequency(self, clk_id: int) -> float:
        """Return the PL clock reference frequency in MHz."""
        m = re.search(
            rf"PMC_CRP_PL{clk_id}_REF_CTRL_FREQMHZ\s+([0-9.]+)", self._ps_pmc_config()
        )
        return float(m.group(1)) if m else 0.0

    def find_clock_enable(self, clk_id: int) -> bool:
        return self.find_clock_frequency(clk_id) > 0

    def find_clock_divisor(self, clk_id: int, div_id: int) -> int:
        """Return the PL clock divisor. For Versal only DIVISOR0 exists."""
        m = re.search(
            rf"PMC_CRP_PL{clk_id}_REF_CTRL_DIVISOR{div_id}\s+([0-9]+)",
            self._ps_pmc_config(),
        )
        return int(m.group(1)) if m else 1
