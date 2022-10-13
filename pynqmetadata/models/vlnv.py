# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Tuple, Dict


@dataclass(repr=False)
class Vlnv:
    """
    Class that describes the model for a vendor:library:name:version
    type
    """

    vendor: str
    library: str
    name: str
    version: Tuple[int, int] = field(default_factory=tuple)

    def dict(self) -> Dict:
        """Returns a dict of the Vlnv"""
        return asdict(self)

    def json(self) -> str:
        """Returns the VLNV as a json object"""
        return json.dumps(self.dict())

    def copy(self) -> Vlnv:
        return Vlnv(
            vendor=self.vendor,
            library=self.library,
            name=self.name,
            version=self.version,
        )

    @property
    def str(self) -> str:
        """Returns a stringified version of the VLNV"""
        return f"{self.vendor}:{self.library}:{self.name}:{self.version[0]}.{self.version[1]}"
