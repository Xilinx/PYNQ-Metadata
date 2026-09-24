# Copyright (C) 2022 Xilinx, Inc
# Copyright (C) 2022 - 2026 Advanced Micro Devices, Inc.
# SPDX-License-Identifier: BSD-3-Clause

import json
from typing import Dict

from pynqmetadata import Core, ManagerPort, Module, ProcSysCore
from pynqmetadata.errors import MetadataObjectNotFound

from .metadata_view import MetadataView


# Interfaces that name the memory technology a controller fronts.
MEMORY_INTERFACES = ("ddr4", "ddr5", "lpddr4", "lpddr5", "hbm", "bram")


def _memory_type(core: Core) -> str:
    """The memory technology, taken from the interface facing the memory."""
    for port in core.ports.values():
        vlnv = getattr(port, "vlnv", None)
        if vlnv is not None and vlnv.name in MEMORY_INTERFACES:
            return vlnv.name.upper()
    return core.vlnv.name.upper() if core.vlnv is not None else "UNKNOWN"


class DummyHwhParser:
    def __init__(self, mem_dict):
        self.mem_dict = mem_dict


class MemDictView(MetadataView):
    """
    Provides a view onto the Metadata object that displays all 
    memory accessible from the Processing System. Models a dictionary,
    where the key is the memory name, and each entry contains, details
    such as the XRT allocation information for each memory.
    """

    def __init__(self, module: Module) -> None:
        super().__init__(module=module)
        self._first_run = True
        self._created_xclbin = {}
        self._psddr_cache = {}

    @property
    def view(self) -> Dict:
        repr_dict = {}

        ps_core = None
        for core in self._md.blocks.values():
            if isinstance(core, ProcSysCore):
                ps_core = core

        if ps_core is None:
            raise MetadataObjectNotFound(f"Unable to find a PS in {self._md.ref}")

        # Gather first: naming depends on how many regions a core turns out
        # to have.
        found = []
        for port in ps_core.ports.values():
            if not isinstance(port, ManagerPort):
                continue
            for key, addr in port.addrmap.items():
                if addr["memtype"] != "memory":
                    continue
                subord_port = port._addrmap_obj[key]
                dst_core = subord_port.parent()
                if not isinstance(dst_core, Core):
                    continue
                baseaddr = addr.get("baseaddr")
                addr_range = addr.get("addr_range")
                if baseaddr is None:
                    baseaddr = subord_port.baseaddr
                if addr_range is None:
                    addr_range = subord_port.range
                found.append((dst_core, subord_port, addr, baseaddr, addr_range))

        # Several routes and several controllers can describe one window, so
        # group by address.
        regions = {}
        for entry in found:
            dst_core, _, addr, baseaddr, addr_range = entry
            key = (dst_core.hierarchy_name, baseaddr, addr_range)
            if key not in regions or addr["block"] < regions[key][2]["block"]:
                regions[key] = entry

        per_core = {}
        for core_name, _, _ in regions:
            per_core[core_name] = per_core.get(core_name, 0) + 1

        for dst_core, subord_port, addr, baseaddr, addr_range in regions.values():
            # Only qualify the name when the core has more than one region.
            name = dst_core.hierarchy_name
            if per_core[name] > 1:
                name = f"{name}/{addr['block']}"

            repr_dict[name] = {}
            repr_dict[name]["fullpath"] = dst_core.hierarchy_name
            repr_dict[name]["type"] = _memory_type(dst_core)
            repr_dict[name]["bdtype"] = None
            repr_dict[name]["state"] = None
            repr_dict[name]["addr_range"] = addr_range
            repr_dict[name]["phys_addr"] = baseaddr
            repr_dict[name]["mem_id"] = subord_port.name
            repr_dict[name]["memtype"] = "MEMORY"
            repr_dict[name]["gpio"] = {}
            repr_dict[name]["interrupts"] = {}
            repr_dict[name]["parameters"] = {}
            for param in dst_core.parameters.values():
                repr_dict[name]["parameters"][param.name] = param.value
            repr_dict[name]["registers"] = {}
            for reg in subord_port.registers.values():
                repr_dict[name]["registers"][reg.name] = {}
                repr_dict[name]["registers"][reg.name]["address_offset"] = reg.offset
                repr_dict[name]["registers"][reg.name]["size"] = reg.width
                repr_dict[name]["registers"][reg.name]["access"] = reg.access
                repr_dict[name]["registers"][reg.name][
                    "description"
                ] = reg.description
                repr_dict[name]["registers"][reg.name]["fields"] = {}
                for field in reg.bitfields.values():
                    repr_dict[name]["registers"][reg.name]["fields"][field.name] = {}
                    repr_dict[name]["registers"][reg.name]["fields"][field.name][
                        "bit_offset"
                    ] = field.LSB
                    repr_dict[name]["registers"][reg.name]["fields"][field.name][
                        "bit_width"
                    ] = (field.MSB - field.LSB) + 1
                    repr_dict[name]["registers"][reg.name]["fields"][field.name][
                        "description"
                    ] = field.description
                    repr_dict[name]["registers"][reg.name]["fields"][field.name][
                        "access"
                    ] = field.access

            repr_dict[name]["used"] = 1

        if self._first_run:
            self._first_run = False
        else:
            for ( name, mem ) in repr_dict.items():  
                if name != "PSDDR":
                    mem["xrt_mem_idx"] = self._created_xclbin[name]["xrt_mem_idx"]
                    mem["raw_type"] = self._created_xclbin[name]["raw_type"]
                    mem["base_address"] = self._created_xclbin[name]["base_address"]
                    mem["size"] = self._created_xclbin[name]["size"]
                    mem["streaming"] = self._created_xclbin[name]["streaming"]
                    mem["idx"] = self._created_xclbin[name]["idx"]
                    mem["tag"] = self._created_xclbin[name]["tag"]
            repr_dict["PSDDR"] = self._psddr_cache
        return repr_dict
