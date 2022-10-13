# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Dict, List, Optional, Set

from ..errors import (
    FeatureNotYetImplemented,
    MergeConflict,
    PortSignalAlreadyExists,
    PortSignalNotFound,
    UnexpectedMetadataObjectType,
    WrongPolarityConnection,
)
from .metadata_object import MetadataObject


@dataclass(repr=False)
class Signal(MetadataObject):
    """
    A signal object. These are nets that
    are grouped together to form a port.
    They keep track of what they are connected
    to in the metadata.
    """

    type: str = "signal"
    generic_type: str = "signal"
    _connections: Dict[str, Signal] = field(default_factory=lambda: ({}))
    con_refs: List[str] = field(default_factory=lambda: ([]))
    width: int = 1
    driver: bool = True
    external: bool = False

    def merge(
        self, a: Signal, skip_external: bool = False, inherit_signal_width: bool = False
    ) -> None:
        """
        Merges signal a into this signal. If there are any conflicts raise an exception

        param
        ---------
        * inherit_signal_width : use the width of the incoming model being merged (used when
        merging in from external BDC HWH files)
        * skip_external : skip the merge conflict check on the external port parameter
        """

        self._mo_merge(a)  # Merges the base metadata object attributes

        if not inherit_signal_width:
            if self.width != a.width:
                raise MergeConflict(
                    f"{self.ref}  {self.width=} is not the same as {a.ref}  {a.width=}"
                )
        else:
            self.width = a.width

        if self.driver != a.driver:
            raise MergeConflict(f"{self.driver=} is not the same as {a.driver=}")

        if not skip_external:
            if self.external != a.external:
                raise MergeConflict(
                    f"{self.external=} is not the same as {a.external=}"
                )
        else:
            self.external = a.external

        for c in a.con_refs:
            if c not in self.con_refs:
                self.con_refs.append(c)

    def connection_exists(self, sig: Signal) -> bool:
        """
        return true if the connection between this signal
        and sig exists, false otherwise
        """
        return sig.ref in self._connections

    def _con_ref_exists(self, ref: str) -> bool:
        """
        returns true if the connection reference already
        exists, false otherwise
        """
        return ref in self.con_refs

    def _remove_con_ref(self, ref: str):
        """
        Removes a connection from the references
        """
        if self._con_ref_exists(ref):
            self.con_refs.remove(ref)
            del self._connections[ref]
        else:
            raise PortSignalNotFound(
                f"Could not find reference connection to {ref} in {self.ref}"
            )

    def _check_polarity(self, sig: Signal) -> None:
        """
        Checks to make sure that the polarity of sig
        means that it is able to connect to this signal
        """
        if not (self.external or sig.external):
            if sig.driver == self.driver:
                raise WrongPolarityConnection(
                    f"{sig.ref} cannot be connected to {self.ref} as they have the same polarity (and are not external)"
                )
        else:
            if sig.driver != self.driver:
                raise WrongPolarityConnection(
                    f"{sig.ref} cannot be connected to {self.ref} as they have different polarity (and ARE external)"
                )

    def connect(self, sig: Signal) -> None:
        """
        Connect this signal to sig
        """
        if not self.connection_exists(sig):
            self._check_polarity(sig)
            self._connections[sig.ref] = sig
            self.con_refs.append(sig.ref)
        #else: ## TODO: This needs to be added back in for buildtime stuff
        #    raise PortSignalAlreadyExists(
        #        f"{sig.ref} is already connected to {self.ref} .  full list of signals {self._connections.keys()}"
        #    )

    def _get_root(self) -> MetadataObject:
        """
        Returns the root module that this signal is a part of
        otherwise throw an error
        """
        port = self._parent
        if isinstance(port, MetadataObject):
            core = port.parent()
            if isinstance(core, MetadataObject):
                module = core.parent()
                if isinstance(module, MetadataObject):
                    if module.type.split("-")[0] == "module":
                        return module
        raise UnexpectedMetadataObjectType(f"Cannot find root from {self.ref}")

    def disconnect(self, sig: Signal, refresh: bool = True) -> None:
        """
        Disconnects sig from this signal

        refresh:bool
        --------------
        When true this will refresh the connectivity (bus level) for the
        entire module. We might not want to do this every time such as
        when removing a whole object up the hierarchy, so it is optional
        """
        if self.connection_exists(sig):
            if self._con_ref_exists(sig.ref):
                self._remove_con_ref(sig.ref)
            else:
                raise PortSignalNotFound(
                    f"Could not find {sig.ref} in {self.ref} reference list when removing"
                )

            if refresh:
                self._get_root().refresh()

        else:
            raise PortSignalNotFound(
                f"Could not disconnect {sig.ref} from {self.ref} as pre-existing connection could not be found"
            )

    def connections(self) -> Dict[str, Signal]:
        """
        Returns a list of destinations from this signal
        """
        return self._connections

    def exists(self, item: Signal) -> bool:
        """
        Return true if the destination is in the destination list
        """
        return self.connection_exists(item)

    def add(self, item: Signal) -> None:
        """
        Adds a destination signal to the object
        """
        self.connect(item)

    def remove(
        self, item: Optional[MetadataObject] = None, refresh: bool = True
    ) -> None:
        """Removes this signal from the wider design it is connected to"""
        if item is not None:
            raise FeatureNotYetImplemented(
                f"Item {item.ref} cannot be yet removed from {self.ref}. Objects can only remove themselves from a design"
            )
        else:
            root = self._get_root()
            for core in root.blocks.values():
                for port in core.ports.values():
                    for signal in port.signals.values():
                        if signal != self:
                            if signal.connection_exists(self):
                                signal.disconnect(self)

            # remove from external ports also
            for port in root.ports.values():
                for signal in port.signals.values():
                    if signal != self:
                        signal.disconnect(self)

        if isinstance(self._parent, MetadataObject):
            del self._parent.signals[self.name]
        else:
            raise UnexpectedMetadataObjectType(
                f"Trying to remove {self.ref} from it's parent, but it's parent was not type Port"
            )

        if refresh:
            root.refresh()
