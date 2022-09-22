# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

import json
import os
from typing import Dict

from pydantic import Field

from ..models.bit_field import BitField
from ..models.block import Block
from ..models.dfx_core import DFXCore
from ..models.ip_core import IPCore
from ..models.manager_port import ManagerPort
from ..models.metadata_object import MetadataObject
from ..models.module import Module
from ..models.parameter import Parameter
from ..models.port import Port
from ..models.register import Register
from ..models.scalar_port import ScalarPort
from ..models.signal import Signal
from ..models.stream_port import StreamPort
from ..models.subordinate_port import SubordinatePort
from ..models.ultrascale_proc_sys_core import UltrascaleProcSysCore
from ..models.vlnv import Vlnv
from ..models.zynq_proc_sys_core import ZynqProcSysCore
from ..models.clk_port import ClkPort
from ..models.rst_port import RstPort


class FileIOError(Exception):
    pass


def _get_json_str(path: str) -> str:
    try:
        file = open(path, "r")
        return file.read()
    except:
        raise FileIOError(f"Unable to open json file {path}")


def _block_factory(j: Dict) -> Block:
    """Create a block from a json description"""
    vlnv = None
    if "vlnv" in j:
        vlnv = Vlnv(
            vendor=j["vlnv"]["vendor"],
            library=j["vlnv"]["library"],
            name=j["vlnv"]["name"],
            version=(int(j["vlnv"]["version"][0]), int(j["vlnv"]["version"][1])),
        )

    core = None
    if j["type"] == "core-ip":
        core = IPCore(name=j["name"], vlnv=vlnv, hierarchy_name=j["hierarchy_name"])
    elif j["type"] == "core-zynq_arm":
        core = ZynqProcSysCore(
            name=j["name"], vlnv=vlnv, hierarchy_name=j["hierarchy_name"]
        )
    elif j["type"] == "core-zynq_aarch64":
        core = UltrascaleProcSysCore(
            name=j["name"], vlnv=vlnv, hierarchy_name=j["hierarchy_name"]
        )
    elif j["type"] == "core-dfx":
        core = DFXCore(name=j["name"], vlnv=vlnv, hierarchy_name=j["hierarchy_name"])
    elif j["type"] == "module":
        core = _module_factory(j)
    else:
        core = IPCore(name=j["name"], vlnv=vlnv, hierarchy_name=j["hierarchy_name"])

    for p in j["parameters"].values():
        if "value" in p:
            param = Parameter(name=p["name"], value=p["value"])
        else:
            param = Parameter(name=p["name"])
        core.add(param)

    for p in j["ports"].values():
        core.add(_port_factory(p))

    return core


def _port_factory(j: Dict) -> Port:
    """constructs a port from a JSON description of the port"""
    vlnv = None
    if j["vlnv"] is not None:
        vlnv = Vlnv(
            vendor=j["vlnv"]["vendor"],
            library=j["vlnv"]["library"],
            name=j["vlnv"]["name"],
            version=(int(j["vlnv"]["version"][0]), int(j["vlnv"]["version"][1])),
        )

    port = None
    t = j["type"]

    if t == "port-manager":
        port = ManagerPort(name=j["name"], vlnv=vlnv, external=j["external"])
        for a in j["addrmap"]:
            port.addrmap[a] = j["addrmap"][a]

    elif t == "port-subordinate":
        port = SubordinatePort(
            name=j["name"],
            vlnv=vlnv,
            external=j["external"],
            baseaddr=j["baseaddr"],
            range=j["range"],
        )
        for r in j["registers"].values():
            reg = Register(
                name=r["name"],
                description=r["description"],
                access=r["access"],
                offset=r["offset"],
                width=r["width"],
                enabled=r["enabled"],
            )
            for f in r["bitfields"].values():
                bit = BitField(
                    name=f["name"],
                    LSB=f["LSB"],
                    MSB=f["MSB"],
                    description=f["description"],
                    access=f["access"],
                )
                reg.add(bit)
            port.add(reg)

    elif t == "port-stream":
        port = StreamPort(
            name=j["name"], vlnv=vlnv, driver=j["driver"], external=j["external"]
        )

    elif t == "port-scalar":
        port = ScalarPort(name=j["name"], vlnv=vlnv, driver=j["driver"])
    elif t == "port-clk":
        port = ClkPort(name=j["name"], vlnv=vlnv, driver=j["driver"])
    elif t == "port-rst":
        port = RstPort(name=j["name"], vlnv=vlnv, driver=j["driver"])

    else:
        port = Port(name=j["name"], vlnv=vlnv, external=j["external"])

    for p in j["parameters"].values():
        if "value" in p:
            param = Parameter(name=p["name"], value=p["value"])
        else:
            param = Parameter(name=p["name"])
        port.add(param)

    for s in j["signals"].values():
        signal = Signal(
            name=s["name"],
            con_refs=s["con_refs"],
            width=s["width"],
            driver=s["driver"],
            external=s["external"],
        )
        port.add(signal)

    return port


def _relink_objects(md: Module) -> None:
    """Using the string references, relink the objects together in the model"""
    for block in md.blocks.values():
        for port in block.ports.values():
            if isinstance(port, ManagerPort):
                for addr in port.addrmap:
                    port._addrmap_obj[addr] = md.lookup(
                        port.addrmap[addr]["subord_port"]
                    )

            for sig in port.signals.values():
                for con in sig.con_refs:
                    sig._connections[con] = md.lookup(con)


def _module_factory(j: Dict) -> Module:
    """From the JSON object describing a module generate the pydantic object model"""
    md = Module(name=j["name"])

    for p in j["ports"].values():
        md.add(_port_factory(p))

    for b in j["blocks"].values():
        block = _block_factory(b)
        for p in b["ports"].values():
            port = _port_factory(p)
            block.add(port)
        md.add(block)

    md._relink_objects()
    md.refresh()
    return md


def JsonFrontend(input: str) -> MetadataObject:
    """Converts a Json file or string into a module"""
    if os.path.isfile(input):
        jstr = _get_json_str(input)
    else:
        jstr = input
    jdict = json.loads(jstr)

    jtype = jdict["type"]

    if jtype == "module":
        return _module_factory(jdict)
    if jtype.split("-")[0] == "core":
        return _block_factory(jdict)
    if jtype.split("-")[0] == "port":
        return _port_factory(jdict)

    raise RuntimeError("Unable to determine the type of the json object")
