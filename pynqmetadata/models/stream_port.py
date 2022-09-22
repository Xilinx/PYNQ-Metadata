# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

from dataclasses import dataclass

from ..errors import MergeConflict
from .port import Port


@dataclass(repr=False)
class StreamPort(Port):
    """
    A model for an AXI stream port.
    """

    type: str = "port-stream"
    driver: bool = True

    def merge(
        self,
        a: Port,
        skip_external: bool = False,
        inherit_signal_width: bool = False,
        inherit_addr_info: bool = False,
        ignore_addr_info: bool = False,
    ) -> None:
        """Attempts to merge the stream port, errors if there is any conflict"""
        assert isinstance(a, StreamPort)
        self._merge(
            a, skip_external=skip_external, inherit_signal_width=inherit_signal_width
        )

        if self.driver != a.driver:
            raise MergeConflict(f"{self.driver=} conflicts with {a.driver=}")
