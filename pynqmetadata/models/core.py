# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

from dataclasses import dataclass

from pynqmetadata.errors.construction_errors import MergeConflict

from .block import Block
from .metadata_object import MetadataObject
from .vlnv import Vlnv


@dataclass(repr=False)
class Core(Block):
    """
    The base model class for a metadata core object
    """

    vlnv: Vlnv = None
    type: str = "core"

    def exists(self, item: MetadataObject) -> bool:
        """Returns true if item is a parameter or a port that is present in this core"""
        return self._exists(item)

    def add(self, item: MetadataObject) -> None:
        """Add a parameter or a port to the core"""
        self._add(item)

    def _merge(
        self,
        a: Core,
        skip_external: bool = False,
        inherit_signal_width: bool = False,
        inherit_addr_info: bool = False,
        ignore_addr_info: bool = False,
    ) -> None:
        """Base merge operation"""
        self._block_merge(
            a,
            skip_external=skip_external,
            inherit_signal_width=inherit_signal_width,
            inherit_addr_info=inherit_addr_info,
            ignore_addr_info=ignore_addr_info,
        )
        if self.vlnv.dict() != a.vlnv.dict():
            raise MergeConflict(f"{self.vlnv=} confilcts with {a.vlnv=}")

    def merge(
        self,
        a: Block,
        skip_external: bool = False,
        inherit_signal_width: bool = False,
        inherit_addr_info: bool = False,
        ignore_addr_info: bool = False,
    ) -> None:
        """Overloaded in the specialised class"""
        self._merge(
            a,
            skip_external=skip_external,
            inherit_signal_width=inherit_signal_width,
            inherit_addr_info=inherit_addr_info,
            ignore_addr_info=ignore_addr_info,
        )
