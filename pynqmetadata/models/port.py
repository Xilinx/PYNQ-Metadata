# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Dict, Optional

from ..errors import (
    FeatureNotYetImplemented,
    MergeConflict,
    ParentIsNone,
    PortNotFound,
    PortSignalAlreadyExists,
    UnexpectedMetadataObjectType,
    UnexpectedPmdObject,
)
from .metadata_object import MetadataObject
from .parameter import Parameter
from .signal import Signal
from .vlnv import Vlnv


@dataclass(repr=False)
class Port(MetadataObject):
    """
    A model for a Port Base Type
    """

    type: str = "port"
    generic_type: str = "port"
    vlnv: Optional[Vlnv] = None
    signals: Dict[str, Signal] = field(default_factory=lambda: ({}))
    parameters: Dict[str, Parameter] = field(default_factory=lambda: ({}))
    external: bool = False
    _destinations: Dict[str, Port] = field(default_factory=lambda: ({}))

    def _merge(
        self, a: Port, skip_external: bool = False, inherit_signal_width: bool = False
    ) -> None:
        """Attempts to merge two ports together. Generates a confilict if there is a collision."""
        self._mo_merge(a)
        if self.vlnv is not None and a.vlnv is not None:
            if self.vlnv.dict() != a.vlnv.dict():
                raise MergeConflict(f"{self.vlnv=} conflicts with {a.vlnv=}")

        # Skip over external ports (used when a separate BDC is being merged into a module)
        if not skip_external:
            if self.external != a.external:
                raise MergeConflict(f"{self.external=} conflicts with {a.external=}")
        else:
            self.external = a.external

        # Merge in signals
        for s in a.signals:
            if s in self.signals:
                self.signals[s].merge(
                    a.signals[s],
                    skip_external=skip_external,
                    inherit_signal_width=inherit_signal_width,
                )
            else:
                self.add(a.signals[s])

        # Merge in parameters
        for p in a.parameters:
            if p in self.parameters:
                self.parameters[p].merge(a.parameters[p])
            else:
                self.add(a.parameters[p])

    def merge(
        self,
        a: Port,
        skip_external: bool = False,
        inherit_signal_width: bool = False,
        inherit_addr_info: bool = False,
        ignore_addr_info: bool = False,
    ) -> None:
        """in the base case just do _merge. This is overloaded in subclasses

        param
        ---------
        * inherit_signal_width : use the width of the incoming model being merged (used when
        merging in from external BDC HWH files)
        * skip_external : skip the merge conflict check on the external port parameter
        * inherit_addr_info : for subordinate ports, get the addressing info from the object being merged, skip the conflict check
        * ignore_addr_info : for subordinate ports don't do any merging of address info

        """
        self._merge(
            a,
            skip_external=skip_external,
            inherit_signal_width=inherit_signal_width,
        )

    def exists(self, item: MetadataObject) -> bool:
        """
        Returns true if the port or the parameter object exists
        in the object false otherwise
        """
        if isinstance(item, Signal):
            return item.name in self.signals
        if isinstance(item, Parameter):
            return item.name in self.parameters
        else:
            raise UnexpectedPmdObject(
                f"{item.name} is not either a port or a parameter so cannot exist in {self.ref}"
            )

    def _add_destination(self, dst: Port) -> None:
        """
        Adds a port to the _destination dict, this
        is called whenever a signal is added to the
        model
        """
        self._destinations[dst.name] = dst

    def destinations(self) -> Dict[str, Port]:
        """
        Returns the port-level destinations for this port
        """
        r = {}
        for sig in self.signals.values():
            for con in sig._connections.values():
                if con.parent().name not in r:
                    r[con.parent().name] = con.parent()
        return r
        # return self._destinations

    def _add_signal(self, item: Signal) -> None:
        """
        Adds a signal to the model
        """
        if not self.exists(item):
            self.signals[item.name] = item
            item.set_parent(self)

            if item.parent() is not None:
                dst_port = item.parent()
                if isinstance(dst_port, Port):
                    self._destinations[dst_port.name] = dst_port
                else:
                    raise PortNotFound(
                        f"Parent of {item.ref} is not a Port type when adding connection to {self.ref}"
                    )
            else:
                raise ParentIsNone(
                    f"{item.ref} has no parent when adding it to {self.ref}"
                )
        else:
            raise PortSignalAlreadyExists(f"{item.ref} already exists in {self.ref}")

    def _add_parameter(self, item: Parameter) -> None:
        """
        Adds a parameter to the model
        """
        if not self.exists(item):
            self.parameters[item.name] = item
            item.set_parent(self)

    def _add_signal_or_parameter(self, item: MetadataObject) -> None:
        """
        Adds either a parameter of a signal to the model
        """
        if isinstance(item, Signal):
            self._add_signal(item)
        elif isinstance(item, Parameter):
            self._add_parameter(item)
        else:
            raise UnexpectedPmdObject(
                f"unable to add {item} to {self.ref} was expecting either a parameter or a port"
            )

    def _get_root(self) -> MetadataObject:
        """
        Returns the root module that this is a part of, otherwise raises an error if it can't find it
        or there are type issues
        """
        core_or_module = self._parent
        if isinstance(core_or_module, MetadataObject):
            if core_or_module.type.split("-")[0] == "core":
                module = core_or_module.parent()
                if isinstance(module, MetadataObject):
                    if module.type.split("-")[0] == "module":
                        return module
            else:
                if core_or_module.type.split("-")[0] == "module":
                    return core_or_module
        raise UnexpectedMetadataObjectType(f"Could not find root from {self.ref}")

    def _update_parents_base(self) -> None:
        """Walks down through the module and makes sure all parent references are accurate
        This is usually performed when we do an update, merge, or parse some json metadata"""
        for param in self.parameters.values():
            param.set_parent(self)
        for signal in self.signals.values():
            signal.set_parent(self)

    def _update_parents(self) -> None:
        """Walks down through the module and makes sure all parent references are accurate
        This is usually performed when we do an update, merge, or parse some json metadata"""
        self._update_parents_base()

    def _remove(
        self, item: Optional[MetadataObject] = None, refresh: bool = True
    ) -> None:
        """Removes this port from the wider design, common base class operation"""
        if item is not None:
            raise FeatureNotYetImplemented(
                f"Item {item.ref} cannot be removed from {self.ref}. Objects can currently only remove themselves from the wider metadata object"
            )
        else:
            sigs = [key for key in self.signals.keys()]
            for sig in sigs:
                self.signals[sig].remove(refresh=False)

            if isinstance(self._parent, MetadataObject):
                del self._parent.ports[self.name]
            else:
                raise UnexpectedMetadataObjectType(
                    f"Expecting parent of Port {self.ref} to be either a Core or a Module"
                )

            if refresh:
                self._get_root().refresh()

    def remove(
        self, item: Optional[MetadataObject] = None, refresh: bool = True
    ) -> None:
        """Removes this port from the wider design"""
        self._remove(item, refresh)

    def add(self, item: MetadataObject) -> None:
        """
        Add a Signal object or a Parameter to the port
        """
        self._add_signal_or_parameter(item)
