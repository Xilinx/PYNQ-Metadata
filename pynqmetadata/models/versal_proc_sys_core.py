# Copyright (C) 2026 Advanced Micro Devices, Inc.
# SPDX-License-Identifier: BSD-3-Clause

from dataclasses import dataclass, field
from typing import Dict

from ..errors import ParameterNotFound
from .parameter import Parameter
from .proc_sys_core import ProcSysCore


def unpack_cips_config(config: str) -> Dict[str, str]:
    """Expand a packed CIPS configuration string into its key value pairs.

    The string is a Tcl style stream of "KEY VALUE" pairs, where a value
    containing spaces is wrapped in braces that may nest.
    """
    pairs: Dict[str, str] = {}
    pos = 0
    end = len(config)

    while pos < end:
        while pos < end and config[pos].isspace():
            pos += 1
        if pos >= end:
            break

        start = pos
        while pos < end and not config[pos].isspace():
            pos += 1
        key = config[start:pos]

        while pos < end and config[pos].isspace():
            pos += 1

        if pos < end and config[pos] == "{":
            start = pos
            depth = 0
            while pos < end:
                if config[pos] == "{":
                    depth += 1
                elif config[pos] == "}":
                    depth -= 1
                    if depth == 0:
                        pos += 1
                        break
                pos += 1
            pairs[key] = config[start + 1 : pos - 1]
        else:
            start = pos
            while pos < end and not config[pos].isspace():
                pos += 1
            pairs[key] = config[start:pos]

    return pairs


@dataclass(repr=False)
class VersalProcSysCore(ProcSysCore):
    """A specialised pydantic model for the Versal CIPS processing system"""

    type: str = "core-versal"
    ps_name: str = "versal_cips"
    # PL to PS interrupts are one bit per port rather than a bus. Devices
    # either expose one family, or split it by power domain with a different
    # range for each. A design only carries the ports of its own family.
    irq: Dict[str, object] = field(
        default_factory=lambda: (
            {f"pl_ps_irq{i}": ((116 + i, 1),) for i in range(16)}
            | {f"pl_lpd_irq{i}": ((136 + i, 1),) for i in range(8)}
            | {f"pl_fpd_irq{i}": ((175 + i, 1),) for i in range(8)}
        )
    )

    # Which parameter holds the packed configuration varies between boards and
    # cannot be told from the module type, so both are tried.
    _config_parameters = ("PS_PMC_CONFIG_INTERNAL", "PS11_CONFIG_INTERNAL")

    def expand_parameters(self) -> None:
        """Expands the packed configuration into individually named parameters.

        Versal packs the whole processing system configuration into one string
        where Zynq and Ultrascale get a PARAMETER tag per setting. Existing
        parameters keep their value: the HWH tags take precedence over the
        copies inside the string.
        """
        for config_name in self._config_parameters:
            if config_name not in self.parameters:
                continue
            config = self.parameters[config_name].value or ""
            for name, value in unpack_cips_config(config).items():
                self.add(Parameter(name=name, value=value))

    def clk_div_param_name(self, clk_id: int, div_id: int) -> str:
        """Returns the name of the clock div parameter for this PS"""
        return f"PMC_CRP_PL{clk_id}_REF_CTRL_DIVISOR{div_id}"

    def clk_enable_param_name(self, clk_id: int) -> str:
        """Returns the parameter for the clock enable for clock with id clk_id on this PS"""
        return f"PS_USE_PMCPL_CLK{clk_id}"

    def clk_freq_param_name(self, clk_id: int) -> str:
        """Returns the name of the PL clock frequency parameter for given clk_id."""
        return f"PMC_CRP_PL{clk_id}_REF_CTRL_FREQMHZ"

    def find_clock_frequency(self, clk_id: int) -> float:
        """For a given clock id return the PL clock frequency in MHz.

        Versal PL clocks are requested by frequency and the divisors are
        worked out by the tools, so the frequency is recorded directly
        rather than being derived from a divisor and a PLL source.
        """
        clk_freq = self.clk_freq_param_name(clk_id)
        if clk_freq in self.parameters:
            frequency = self.parameters[clk_freq].value
            if frequency is not None:
                return float(frequency)
            else:
                raise ValueError(
                    f"Clock frequency {clk_freq} for ps {self.ref} has no value"
                )
        else:
            raise ParameterNotFound(
                f"Unable to find a clock frequency {clk_freq} for ps {self.ref}"
            )
