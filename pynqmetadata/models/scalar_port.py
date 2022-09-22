# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

from dataclasses import dataclass

from ..errors import MergeConflict, TooManySignals
from .metadata_object import MetadataObject
from .port import Port
from .signal import Signal


@dataclass(repr=False)
class ScalarPort(Port):
    """
    A port object for a core that can
    only have a single signal
    """

    type: str = "port-scalar"
    width: int = 1
    driver: bool = False

    def add(self, item: MetadataObject) -> None:
        """
        adds a signal to the scalar port.
        Will throw an error if more that one
        signal is added
        """
        self._add_signal_or_parameter(item)

        if len(self.signals) > 1:
            raise TooManySignals(
                f"Cannot add {item.name} to {self.ref} as it is a scalar port and already has a signal associated with it"
            )

    def sig(self) -> Signal:
        """As this is a scalar port it should only have one signal, so return it"""
        return self.signals[list(self.signals.keys())[0]]

    def merge(
        self,
        a: Port,
        skip_external: bool = False,
        inherit_signal_width: bool = False,
        inherit_addr_info: bool = False,
        ignore_addr_info: bool = False,
    ) -> None:
        """Attempts to merge the stream port, errors if there is any conflict"""
        assert isinstance(a, ScalarPort)
        self._merge(
            a, skip_external=skip_external, inherit_signal_width=inherit_signal_width
        )

        if self.driver != a.driver:
            raise MergeConflict(f"{self.driver=} conflicts with {a.driver=}")

        if not inherit_signal_width:
            if self.width != a.width:
                raise MergeConflict(f"{self.width=} conflicts with {a.width=}")
        else:
            self.width = a.width
