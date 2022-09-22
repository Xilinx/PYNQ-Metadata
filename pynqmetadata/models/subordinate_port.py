# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

from pynqmetadata.errors.construction_errors import MergeConflict

from ..errors import UnexpectedPmdObject
from .metadata_object import MetadataObject
from .parameter import Parameter
from .port import Port
from .register import Register
from .signal import Signal


@dataclass(repr=False)
class SubordinatePort(Port):
    """
    Model that describes a subordinate port
    This is a port that has a register map associated with it
    """

    type: str = "port-subordinate"
    baseaddr: int = 9999999
    range: int = 16
    registers: Dict[str, Register] = field(default_factory=lambda: ({}))

    def merge(
        self,
        a: Port,
        skip_external: bool = False,
        inherit_signal_width: bool = False,
        inherit_addr_info: bool = False,
        ignore_addr_info: bool = False,
    ) -> None:
        """Attempts to merge two subordinate ports, if there is a conflict raise an exception

        param
        ---------
        * inherit_signal_width : use the width of the incoming model being merged (used when
        merging in from external BDC HWH files)
        * skip_external : skip the merge conflict check on the external port parameter
        * inherit_addr_info : for subordinate ports, get the addressing info from the object being merged, skip the conflict check

        """
        assert isinstance(a, SubordinatePort)
        self._merge(
            a, skip_external=skip_external, inherit_signal_width=inherit_signal_width
        )

        if not ignore_addr_info:
            if not inherit_addr_info:
                if self.baseaddr != a.baseaddr:
                    raise MergeConflict(f"{self.baseaddr=} conflict with {a.baseaddr=}")
                if self.range != a.range:
                    raise MergeConflict(f"{self.range=} conflict with {a.range=}")
            else:
                self.baseaddr = a.baseaddr
                self.range = a.range

        for r in a.registers:
            if r in self.registers:
                self.registers[r].merge(a.registers[r])
            else:
                self.registers[r] = a.registers[r]

    def exists(self, item: MetadataObject) -> bool:
        """
        Checks to see if a either a signal, register, or
        parameter exists within the model
        """
        return (
            (item.name in self.registers)
            or (item.name in self.parameters)
            or (item.name in self.signals)
        )

    def add(self, item: MetadataObject) -> None:
        """
        Adds either a register, a signal, or a parameter to the model
        """
        if isinstance(item, Signal) or isinstance(item, Parameter):
            self._add_signal_or_parameter(item)
        elif isinstance(item, Register):
            if not self.exists(item):
                self.registers[item.name] = item
                item.set_parent(self)
        else:
            raise UnexpectedPmdObject(
                f"{item.name} is not a Signal/Parameter/Register and cannot be added to {self.ref}"
            )

    def _update_parents(self) -> None:
        """Walks down through the module and makes sure all parent references are accurate
        This is usually performed when we do an update, merge, or parse some json metadata"""
        self._update_parents_base()

        for reg in self.registers.values():
            reg.set_parent(self)
            reg._update_parents()
