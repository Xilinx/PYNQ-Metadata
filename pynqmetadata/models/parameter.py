# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from pynqmetadata.errors.construction_errors import MergeConflict

from .metadata_object import MetadataObject


@dataclass(repr=False)
class Parameter(MetadataObject):
    """
    A model for a Pmd parameter
    """

    name: str
    type: str = "parameter"
    generic_type: str = "parameter"
    value: Optional[str] = None

    def merge(self, a: Parameter) -> None:
        """Attempt to merge the two parameters, raise an error if there is a conflict"""
        self._mo_merge(a)
        if self.value is not None and a.value is not None:
            if self.value != a.value:
                raise MergeConflict(f"{self.value=} conflicts with {a.value=}")
        else:
            self.value = a.value
