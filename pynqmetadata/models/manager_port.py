# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from pydantic import Field

from ..errors import AddressMapAlreadyExists, AddrMapNotFound, MergeConflict
from .addrmap import AddressMap
from .port import Port
from .subordinate_port import SubordinatePort


@dataclass(repr=False)
class ManagerPort(Port):
    """
    Model that describes a Manager Port object
    This model includes an address map
    """

    type: str = "port-manager"
    # addrmap: Dict[str, AddressMap] = {}
    _addrmap_obj: Dict[str, SubordinatePort] = field(default_factory=lambda: ({}))
    addrmap: Dict[str, Dict[str, str]] = field(default_factory=lambda: ({}))

    def merge(
        self,
        a: Port,
        skip_external: bool = False,
        inherit_signal_width: bool = False,
        inherit_addr_info: bool = False,
        ignore_addr_info: bool = False,
    ) -> None:
        """Attempts to merge the manager port. Raises an error if there is a merge conflict"""
        assert isinstance(a, ManagerPort)
        self._merge(
            a, skip_external=skip_external, inherit_signal_width=inherit_signal_width
        )
        for i, adr in self.addrmap.items():
            if adr in self.addrmap:
                if a.addrmap[adr] != self.addrmap[adr]:
                    raise MergeConflict(
                        f"{a.addrmap[adr]=} conflicts with {self.addrmap[adr]=}"
                    )
            else:
                self.addrmap[i] = adr

    def addrmap_exists(self, subord_port: SubordinatePort) -> bool:
        """returns true if a SubordinatePort exists in the address map for this manager"""
        return subord_port.ref in self.addrmap

    def addrmap_remove(self, subord_port: SubordinatePort) -> None:
        """Removes an address mapping from this manager port"""
        if self.addrmap_exists(subord_port):
            del self._addrmap_obj[subord_port.ref]
            del self.addrmap[subord_port.ref]
        else:
            raise AddrMapNotFound(
                f"Could not find an address map from manager {self.ref} to subordinate {subord_port.ref}"
            )

    def addrmap_add(
        self, block: str, memtype: str, subord_port: SubordinatePort
    ) -> None:
        """Adds an address mapping to the manager port"""
        if not self.addrmap_exists(subord_port):
            self._addrmap_obj[subord_port.ref] = subord_port
            self.addrmap[subord_port.ref] = {}
            self.addrmap[subord_port.ref]["block"] = block
            self.addrmap[subord_port.ref]["memtype"] = memtype
            self.addrmap[subord_port.ref]["subord_port"] = subord_port.ref
        else:
            raise AddressMapAlreadyExists(
                f"{subord_port.ref} is already an address target of manager {self.ref}"
            )
