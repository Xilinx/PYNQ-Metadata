# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

from ..errors import BitAlreadyExists, MergeConflict
from .bit_field import BitField
from .metadata_object import MetadataObject


@dataclass(repr=False)
class Register(MetadataObject):
    """
    Model that describes a register associated with a subordinate port
    """

    type: str = "register"
    generic_type: str = "register"
    description: str = "A register"
    access: str = "read-write"
    offset: int = 0
    width: int = 32
    enabled: bool = True
    bitfields: Dict[str, BitField] = field(default_factory=lambda: ({}))

    def merge(self, a: Register) -> None:
        """Attempts to merge two registers together. Generates a conflict if there is a collision"""
        self._mo_merge(a)
        if self.access != a.access:
            raise MergeConflict(f"{self.access=} is not the same as {a.access=}")
        if self.offset != a.offset:
            raise MergeConflict(f"{self.offset=} is not the same as {a.offset=}")
        if self.width != a.width:
            raise MergeConflict(f"{self.width=} is not the same as {a.width=}")
        if self.enabled != a.enabled:
            raise MergeConflict(f"{self.enabled=} is not the same as {a.enabled=}")

        for bit in a.bitfields:
            if bit in self.bitfields:
                if a.bitfields[bit].dict() != self.bitfields[bit].dict():
                    raise MergeConflict(
                        f"{self.name} and {a.name} cannot be merged there is a conflict on {self.bitfields[bit].ref}"
                    )
            else:
                self.add(a.bitfields[bit])

    def exists(self, item: BitField) -> bool:
        """
        Checks to see if a bitfield exists in the model
        """
        return item.name in self.bitfields

    def add(self, item: BitField) -> None:
        """
        Adds a BitField to the Register model
        """
        if not self.exists(item):
            self.bitfields[item.name] = item
            item.set_parent(self)
        else:
            raise BitAlreadyExists(
                f"bit {item.name} already exists in the register map {self.ref}"
            )

    def _update_parents(self) -> None:
        """Walks down through the module and makes sure all parent references are accurate
        This is usually performed when we do an update, merge, or parse some json metadata"""
        for bit in self.bitfields.values():
            bit.set_parent(self)
