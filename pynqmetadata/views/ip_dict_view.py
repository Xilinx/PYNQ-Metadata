# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

from typing import Dict

from ..errors import FeatureNotYetImplemented
from ..models.module import Module
from ..models.subordinate_port import SubordinatePort


class IpDictView:
    """
    Provides a view over the IP register map space, similar to the
    classic pynq metadata ip_dict view
    """

    def __init__(self, module: Module) -> None:
        self._md = module

    @property
    def ip_dict(self) -> Dict:
        repr_dict = {}
        for core in self._md.cores.values():
            for port in core.ports.values():
                if isinstance(port, SubordinatePort):
                    repr_dict[core.name] = {}
                    repr_dict[core.name]["fullpath"] = core.name
                    repr_dict[core.name]["bdtype"] = None
                    repr_dict[core.name]["state"] = None
                    repr_dict[core.name]["type"] = core.vlnv.str
                    repr_dict[core.name]["gpio"] = {}
                    repr_dict[core.name]["interrupts"] = {}
                    repr_dict[core.name]["phys_addr"] = port.baseaddr
                    repr_dict[core.name]["addr_range"] = port.range
                    repr_dict[core.name]["parameters"] = {}
                    for param in core.parameters.values():
                        repr_dict[core.name]["parameters"][param.name] = param.value
                    repr_dict[core.name]["registers"] = {}
                    for reg in port.registers.values():
                        repr_dict[core.name]["registers"][reg.name] = {}
                        repr_dict[core.name]["registers"][reg.name][
                            "address_offset"
                        ] = reg.offset
                        repr_dict[core.name]["registers"][reg.name]["width"] = reg.width
                        repr_dict[core.name]["registers"][reg.name][
                            "description"
                        ] = reg.description
                        repr_dict[core.name]["registers"][reg.name]["fields"] = {}
                        for f in reg.bitfields.values():
                            repr_dict[core.name]["registers"][reg.name]["fields"][
                                f.name
                            ] = {}
                            repr_dict[core.name]["registers"][reg.name]["fields"][
                                f.name
                            ]["bit_offset"] = f.LSB
                            repr_dict[core.name]["registers"][reg.name]["fields"][
                                f.name
                            ]["bit_width"] = (f.MSB - f.LSB)
                            repr_dict[core.name]["registers"][reg.name]["fields"][
                                f.name
                            ]["description"] = f.description
        return repr_dict

    def __len__(self) -> int:
        return len(self.ip_dict)

    def __iter__(self):
        for ip in self.ip_dict:
            yield ip

    def __getitem__(self, key: str) -> None:
        return self.ip_dict[key]

    def __setitem__(self, key: str, value: object) -> None:
        """TODO: needs to send value into the model bypassing ip_dict
        this will require view tranlation in the other direction"""
        raise FeatureNotYetImplemented("IPDictView is currently only read only")
