# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Set

from pydantic import Field
from pynqmetadata.errors.construction_errors import (
    CoreAlreadyExists,
    HierarchyAlreadyExists,
)
from pynqmetadata.errors.metadata_type_errors import UnexpectedMetadataObjectType

from .core import Core
from .metadata_object import MetadataObject


@dataclass(repr=False)
class Hierarchy(MetadataObject):
    """A metadata object for hierarchies for groups of IP Cores"""

    type: str = "hierarchy"
    generic_type: str = "hierarchy"

    hierarchies_ref: Set[str] = field(default_factory=set)
    _hierarchies_obj: Dict[str, Hierarchy] = field(default_factory=lambda: ({}))
    core_ref: Set[str] = field(default_factory=set)
    _core_obj: Dict[str, Core] = field(default_factory=lambda: ({}))
    path: str = ""
    pr_region: bool = False

    def exists(self, item: MetadataObject) -> bool:
        """
        Checks to see if a block exists in this hierarchy already, or checks
        to see if a sub-hierarchy is already present, returns true if present
        false otherwise.
        """
        if isinstance(item, Core):
            if item.ref in self._core_obj:
                return True
            else:
                for h in self._hierarchies_obj.values():
                    if h.exists(item):
                        return True
            return False
        elif isinstance(item, Hierarchy):
            if item.ref in self._hierarchies_obj:
                return True
            else:
                for h in self._hierarchies_obj.values():
                    if h.exists(item):
                        return True
            return False
        else:
            raise UnexpectedMetadataObjectType(
                f"Checking {item.ref} exists in {self.ref} but did not expect type {type(item)}"
            )

    def add(self, item: MetadataObject) -> None:
        """
        Adds either a sub-hierarchy or a block to this hierarchy model
        """
        if isinstance(item, Core):
            if not self.exists(item):
                self.core_ref.add(item.ref)
                self._core_obj[item.ref] = item
            else:
                raise CoreAlreadyExists(
                    f"Adding {item.ref} to hierarchy {self.ref} but it already exists"
                )
        elif isinstance(item, Hierarchy):
            if not self.exists(item):
                self.hierarchies_ref.add(item.ref)
                self._hierarchies_obj[item.ref] = item
            else:
                raise HierarchyAlreadyExists(
                    f"Adding Hierarchy {item.ref} as a sub-hierarchy to {self.ref} but it already exists"
                )
        else:
            raise UnexpectedMetadataObjectType(
                f"Trying to add {item.ref} to hierarchy {self.ref} but it is of type {type(item)} which is not a hierarchy or a block"
            )
