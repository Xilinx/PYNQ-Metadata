# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from ..errors import (FeatureNotYetImplemented, MergeConflict,
                      UnexpectedMetadataObjectType, UnexpectedPmdObject)
from .metadata_object import MetadataObject
from .parameter import Parameter
from .port import Port


@dataclass(repr=False)
class Block(MetadataObject):
    """
    The block class that is used to describe core in the design or modules
    """

    type: str = "block"
    generic_type: str = "block"
    hierarchy_name: Optional[str] = None
    ports: Dict[str, Port] = field(default_factory=lambda: ({}))
    parameters: Dict[str, Parameter] = field(default_factory=lambda: ({}))

    def _block_merge(
        self,
        a: Block,
        skip_external: bool = False,
        inherit_signal_width: bool = False,
        inherit_addr_info: bool = False,
        ignore_addr_info: bool = False,
    ) -> None:
        """Base merge for block objects

        param
        ---------
        * inherit_signal_width : use the width of the incoming model being merged (used when
        merging in from external BDC HWH files)
        * skip_external : skip the merge conflict check on the external port parameter
        * inherit_addr_info : for subordinate ports, get the addressing info from the object being merged, skip the conflict check
        * ignore_addr_info : for subordinate ports don't do any merging of address info

        """
        self._mo_merge(a)

        if self.hierarchy_name is not None and a.hierarchy_name is not None:
            if self.hierarchy_name != a.hierarchy_name:
                raise MergeConflict(
                    f"{self.hierarchy_name=} conflicts with {a.hierarchy_name=}"
                )
        else:
            self.hierarchy_name = a.hierarchy_name

        for p in a.ports:
            if p in self.ports:
                self.ports[p].merge(
                    a.ports[p],
                    skip_external=skip_external,
                    inherit_signal_width=inherit_signal_width,
                    inherit_addr_info=inherit_addr_info,
                    ignore_addr_info=ignore_addr_info,
                )
            else:
                self.ports[p] = a.ports[p]

        for param in a.parameters:
            if param in self.parameters:
                self.parameters[param].merge(a.parameters[param])
            else:
                self.parameters[param] = a.parameters[param]

    def merge(
        self,
        a: Block,
        skip_external: bool = False,
        inherit_signal_width: bool = False,
        inherit_addr_info: bool = False,
        ignore_addr_info: bool = False,
    ):
        """Basic merge of blocks, overridden in the subclasses

        param
        ---------
        * inherit_signal_width : use the width of the incoming model being merged (used when
        merging in from external BDC HWH files)
        * skip_external : skip the merge conflict check on the external port parameter
        * inherit_addr_info : for subordinate ports, get the addressing info from the object being merged, skip the conflict check
        * ignore_addr_info : for subordinate ports don't do any merging of address info

        """
        self._block_merge(
            a,
            skip_external=skip_external,
            inherit_signal_width=inherit_signal_width,
            inherit_addr_info=inherit_addr_info,
            ignore_addr_info=ignore_addr_info,
        )

    def _exists(self, item: MetadataObject) -> bool:
        """
        Returns true if the port or the parameter object exists
        in the object false otherwise
        """
        if isinstance(item, Port):
            return item.name in self.ports
        elif isinstance(item, Parameter):
            return item.name in self.parameters
        else:
            raise UnexpectedPmdObject(
                f"{item.name} is not either a port or a parameter so cannot exist in {self.ref}"
            )

    def _add(self, item: MetadataObject) -> None:
        """
        Adds either a port or a parameter to the Core
        """
        if isinstance(item, Port):
            if not self._exists(item):
                self.ports[item.name] = item
                item.set_parent(self)
        elif isinstance(item, Parameter):
            if not self._exists(item):
                self.parameters[item.name] = item
                item.set_parent(self)
        else:
            raise UnexpectedPmdObject(
                f"unable to add {item} to {self.ref} was expecting either a parameter or a port"
            )

    def _update_parents_base(self) -> None:
        """Walks down through the module and makes sure all parent references are accurate
        This is usually performed when we do an update, merge, or parse some json metadata"""
        for port in self.ports.values():
            port.set_parent(self)
            port._update_parents()
        for param in self.parameters.values():
            param.set_parent(self)

    def _update_parents(self) -> None:
        """Walks down through the module and makes sure all parent references are accurate
        This is usually performed when we do an update, merge, or parse some json metadata"""
        self._update_parents_base()

    def _get_root(self) -> MetadataObject:
        """Gets the root module for this block"""
        module = self._parent
        if isinstance(module, MetadataObject):
            if module.type.split("-")[0] == "module":
                return module
        raise UnexpectedMetadataObjectType(
            f"{self.ref} has no parent when we are trying to find the root module from {self.ref}"
        )

    def _remove(self, item: Optional[MetadataObject], refresh: bool = True) -> None:
        """Removes this core from the wider design"""
        if item is not None:
            raise FeatureNotYetImplemented(
                f"Item {item.ref} cannot be removed from {self.ref}. Objects can currently only remove themselves from the wider metadata object"
            )
        else:
            ports = [key for key in self.ports.keys()]
            for p in ports:
                self.ports[p].remove(refresh=False)

            if isinstance(self._parent, MetadataObject):
                del self._parent.blocks[self.name]
            else:
                raise UnexpectedMetadataObjectType(
                    f"Expecting the parent of Core {self.ref} to be of type Module"
                )

            if refresh:
                self._get_root().refresh()

    def remove(
        self, item: Optional[MetadataObject] = None, refresh: bool = True
    ) -> None:
        """Removes this block from the wider design"""
        self._remove(item, refresh)
