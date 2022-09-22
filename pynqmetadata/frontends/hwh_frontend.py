# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

import os
from dataclasses import dataclass, field
from typing import Optional
from xml.etree import ElementTree
import warnings

from pydantic import Field

from ..errors import ExpectedSignalType, PortNotFound, UnexpectedPortTypeError
from ..models.bit_field import BitField
from ..models.block import Block
from ..models.core import Core
from ..models.dfx_core import DFXCore
from ..models.ip_core import IPCore
from ..models.manager_port import ManagerPort
from ..models.metadata_extension import MetadataExtension
from ..models.module import Module
from ..models.parameter import Parameter
from ..models.port import Port
from ..models.proc_sys_core import ProcSysCore
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


def string2int(a: str) -> int:
    """Convert a hex or decimal string into an int."""
    return int(a, 16 if a.startswith("0x") else 10)


def vlnv_creator(vlnv_str: str) -> Vlnv:
    """
    When given a VLNV string, return a VLNV model
    """
    split_str = vlnv_str.split(":")
    version_str = split_str[3].split(".")
    version = (int(version_str[0]), int(version_str[1]))
    return Vlnv(
        vendor=split_str[0], library=split_str[1], name=split_str[2], version=version
    )


class BDNameExtension(MetadataExtension):
    bd_name: str = Field(
        ...,
        description="The BD name when adding a BDC to a design, used to check for partial HWH files in the XSA",
    )


def core_factory(module: ElementTree) -> Block:
    """
    Based on the elementTree module tags generate
    the appropriate specialised core model
    """
    name = module.get("INSTANCE")

    if module.get("BDTYPE") == "BLOCK_CONTAINER":
        vlnv = Vlnv(vendor="xilinx", library="bdc", name="bdc", version=(1, 0))
    else:
        vlnv = vlnv_creator(module.get("VLNV"))

    fullname = module.get("FULLNAME", None)
    if fullname is not None:
        fullname = fullname.lstrip("/")

    # Processing System
    if (module.get("IS_PL") is not None) and module.get("IS_PL") == "FALSE":
        if module.get("MODTYPE") == "zynq_ultra_ps_e":
            core = UltrascaleProcSysCore(name=name, vlnv=vlnv, hierarchy_name=fullname)
        elif module.get("MODTYPE") == "processing_system7":
            core = ZynqProcSysCore(name=name, vlnv=vlnv, hierarchy_name=fullname)
        else:
            core = ProcSysCore(name=name, vlnv=vlnv, hierarchy_name=fullname)

    # BDC
    elif module.get("BDTYPE") == "BLOCK_CONTAINER":
        bdc_name = BDNameExtension(bd_name=module.get("BD"))
        core = Module(name=name, hierarchy_name=fullname)
        core.ext["bdc"] = bdc_name

    # Everything else is an IPCore
    else:
        core = IPCore(name=name, vlnv=vlnv, hierarchy_name=fullname)

    # Populate the parameters
    for param in module.iter("PARAMETER"):
        core.add(
            Parameter(
                name=param.get("NAME"),
                value=param.get("VALUE"),
                # hierarchy_name=fullname,
            )
        )

    return core


def determine_if_bus_driver(btype: str) -> bool:
    """
    Given the XML bus type determine if it
    drives the bus or not
    """
    if btype == "MASTER" or btype == "INITIATOR":
        return True
    elif btype == "SLAVE" or btype == "TARGET" or btype=="MONITOR":
        return False
    else:
        warnings.warn( 
            f"{btype} was not expected, expected (MASTER|INITIATOR|TARGET|SLAVE)"
        )


def port_factory(bus_itf: ElementTree) -> Port:
    """
    Given the XML bus interface, construct a port
    """
    name: str = bus_itf.get("NAME")
    btype: str = bus_itf.get("TYPE")
    vlnv = vlnv_creator(bus_itf.get("VLNV"))

    # Memory mapped port
    if vlnv.name == "aximm":
        if determine_if_bus_driver(btype):
            port = ManagerPort(name=name, vlnv=vlnv)
        else:
            port = SubordinatePort(name=name, vlnv=vlnv)

    # Microblaze LMB
    elif vlnv.name == "lmb":
        if determine_if_bus_driver(btype):
            port = ManagerPort(name=name, vlnv=vlnv)
        else:
            port = SubordinatePort(name=name, vlnv=vlnv)

    elif vlnv.name == "axis":
        port = StreamPort(name=name, vlnv=vlnv, driver=determine_if_bus_driver(btype))

    else:
        port = Port(name=name, vlnv=vlnv)

    # Populate the parameters
    for param in bus_itf.iter("PARAMETER"):
        port.add(Parameter(name=param.get("NAME"), value=param.get("VALUE")))

    return port


def external_port_factory(b_itf: ElementTree) -> Port:
    """From an external port XML description create an appropriate port model"""
    bname = b_itf.get("NAME")
    porttype = ""
    for param in b_itf.iter("PARAMETER"):
        if param.get("NAME") == "HAS_QOS":
            porttype = "aximm"
        if param.get("NAME") == "HAS_TLAST":
            porttype = "axis"

    driver = b_itf.get("TYPE") == "INITIATOR" or b_itf.get("TYPE") == "MASTER"
    vlnv = Vlnv(vendor="extern", library="extern", name=porttype, version=(1, 0))
    if vlnv.name == "aximm":
        if driver:
            port = ManagerPort(name=bname, vlnv=vlnv, external=True)
        else:
            port = SubordinatePort(name=bname, vlnv=vlnv, external=True)

    elif vlnv.name == "axis":
        port = StreamPort(name=bname, vlnv=vlnv, driver=driver, external=True)

    else:
        port = Port(name=bname, vlnv=vlnv, external=True)

    # populate the parameters
    for param in b_itf.iter("PARAMETER"):
        port.add(Parameter(name=param.get("NAME"), value=param.get("Value")))

    return port


@dataclass
class HwhFrontend(Module):
    """
    Class used for parsing a HWH file into
    a Metadata model
    """

    name: str = "unknown"
    _hwhfile: str = ""
    _element_tree: object = None
    _root: object = None

    _logical2physical_portmap: dict = field(default_factory=lambda: ({}))
    _physical2logical_portmap: dict = field(default_factory=lambda: ({}))
    _logical2physical_extern_pm: dict = field(default_factory=lambda: ({}))
    _physical2logical_extern_pm: dict = field(default_factory=lambda: ({}))

    def __post_init__(self) -> None:
        """
        Performs the parsing of the hwh into the metadata model
        * checks to see if the hwhfile is an XML string or a
          file containing xml.

        * walks over all the IP cores
            * adds each port to the IP core
                * adds the signals to each port

        * Performs a connectivity pass
        """
        if self._hwhfile != "":
            self.parse()

    def parse(self) -> None:
        if os.path.isfile(self._hwhfile):
            self._element_tree = ElementTree.parse(self._hwhfile)
        else:
            self._element_tree = ElementTree.ElementTree(
                ElementTree.fromstring(self._hwhfile)
            )

        self._root = self._element_tree.getroot()
        self.name: str = self.get_name()
        self.ref = self.name

        self._construct_logical2physical_portmap()
        self._construct_physical2logical_portmap()
        self.populate_cores()

        self._construct_logical2physical_extern_pm()
        self._create_external_ports()

        self.resolve_addressing()
        self.connect_signals()

        self.refresh()

    def get_name(self) -> str:
        """
        Returns the name of the system this HWH is describing.
        This is used for the root module name.
        """
        for i in self._root.iter("SYSTEMINFO"):
            name: str = i.get("NAME")
            return name
        return ""

    def _construct_logical2physical_extern_pm(self) -> None:
        """
        Constructs the logical2physical portmap for the external ports
        [busname:str][logical:str] -> physical:str
        """
        self._construct_physical2logical_extern_pm()
        for pname in self._physical2logical_extern_pm:
            lname = self._physical2logical_extern_pm[pname]["logical_name"]
            bus = self._physical2logical_extern_pm[pname]["busname"]
            porttype = self._physical2logical_extern_pm[pname]["porttype"]
            self._logical2physical_extern_pm[bus] = {}
            self._logical2physical_extern_pm[bus][lname] = pname

    def _construct_physical2logical_extern_pm(self) -> None:
        """
        Constructs the physical2logical portmap for the external ports
        [physical_signal:str] -> { busname: str, porttype: str,  logical_name:str, width:int,  }
        """
        for ext_i in self._root.iter("EXTERNALINTERFACES"):
            for b_itf in ext_i.iter("BUSINTERFACE"):
                busname = b_itf.get("NAME")
                # infer the port type from the parameters
                porttype = ""
                for param in b_itf.iter("PARAMETER"):
                    if param.get("NAME") == "HAS_QOS":
                        porttype = "aximm"
                    if param.get("NAME") == "HAS_TLAST":
                        porttype = "axis"
                for pm in b_itf.iter("PORTMAP"):
                    pname = pm.get("PHYSICAL")
                    lname = pm.get("LOGICAL")
                    self._physical2logical_extern_pm[pname] = {}
                    self._physical2logical_extern_pm[pname]["busname"] = busname
                    self._physical2logical_extern_pm[pname]["porttype"] = porttype
                    self._physical2logical_extern_pm[pname]["logical_name"] = lname
                    self._physical2logical_extern_pm[pname]["width"] = 999
                    self._physical2logical_extern_pm[pname]["driver"] = False
                    for ext_prts in self._root.iter("EXTERNALPORTS"):
                        for ext_p in ext_prts.iter("PORT"):
                            if ext_p.get("NAME") == pname:
                                driver = ext_p.get("DIR") == "O"
                                width = 1
                                if ext_p.get("LEFT") is not None:
                                    width = (
                                        int(ext_p.get("LEFT"))
                                        - int(ext_p.get("RIGHT"))
                                        + 1
                                    )
                                self._physical2logical_extern_pm[pname]["width"] = width
                                self._physical2logical_extern_pm[pname][
                                    "driver"
                                ] = driver

    def _create_external_ports(self) -> None:
        """Creates the external ports for the metadata object, both bus based and scalar"""
        for ext_i in self._root.iter("EXTERNALINTERFACES"):
            for ext_b in ext_i.iter("BUSINTERFACE"):
                port = external_port_factory(ext_b)

                for pm in ext_b.iter("PORTMAP"):
                    sigp = self._physical2logical_extern_pm[pm.get("PHYSICAL")]
                    port.add(
                        Signal(
                            name=sigp["logical_name"],
                            width=sigp["width"],
                            driver=sigp["driver"],
                            external=True,
                        )
                    )
                self.add(port)

        # For all the scalar external ports
        ext_prts = self._root.find("EXTERNALPORTS")
        for ext_p in ext_prts.iter("PORT"):
            if ext_p.get("NAME") not in self._physical2logical_extern_pm:
                driver = ext_p.get("DIR") == "O"
                width = 1
                if ext_p.get("LEFT") is not None:
                    width = int(ext_p.get("LEFT")) - int(ext_p.get("RIGHT")) + 1

                # Determine the type of the external scalar port
                if ext_p.get("SIGIS") == "clk":
                    scalar_port = ClkPort(name=ext_p.get("NAME"), driver=driver, width=width)
                elif ext_p.get("SIGIS") == "rst":
                    scalar_port = RstPort(name=ext_p.get("NAME"), driver=driver, width=width)
                else:
                    scalar_port = ScalarPort(name=ext_p.get("NAME"), driver=driver, width=width)

                scalar_port.add(
                    Signal(
                        name=ext_p.get("NAME"),
                        width=width,
                        driver=driver,
                        external=True,
                    )
                )
                self.add(scalar_port)

    def _construct_logical2physical_portmap(self) -> None:
        """
        Creates a mapping from the logical ports [instance][bus][logical]->physical:elementTree
        useful for looking up specific attibutes of a port from it's logical name
        """
        self._logical2physical_portmap = {}
        for i in self._root.iter("MODULE"):
            name = i.get("INSTANCE")
            self._logical2physical_portmap[name] = {}
            for b_itf in i.iter("BUSINTERFACE"):
                bname = b_itf.get("NAME")
                self._logical2physical_portmap[name][bname] = {}
                for pm in b_itf.iter("PORTMAP"):
                    logical_portname = pm.get("LOGICAL")
                    self._logical2physical_portmap[name][bname][logical_portname] = None
                    phys_portname = pm.get("PHYSICAL")
                    found = False
                    for prt in i.iter("PORT"):
                        if prt.get("NAME") == phys_portname:
                            self._logical2physical_portmap[name][bname][
                                logical_portname
                            ] = prt
                            found = True
                            break
                    if not found:
                        raise PortNotFound(
                            f"Could not find physical port {phys_portname} for logical one {logical_portname}"
                        )

    def _construct_physical2logical_portmap(self) -> None:
        """
        Create the physical to logical portmapping for the hwh
        bus interfaces
        """
        self._physical2logical_portmap = {}
        for i in self._root.iter("MODULE"):
            name = i.get("INSTANCE")
            self._physical2logical_portmap[name] = {}
            for b_itf in i.iter("BUSINTERFACE"):
                bname = b_itf.get("NAME")
                for pm in b_itf.iter("PORTMAP"):
                    self._physical2logical_portmap[name][pm.get("PHYSICAL")] = [
                        bname,
                        pm.get("LOGICAL"),
                    ]

    def populate_cores(self) -> None:
        """
        Gets all the cores and populates the metadata.
        This pass does not worry about connecting the signals up.
        """
        for i in self._root.iter("MODULE"):
            core = core_factory(i)
            for b in i.iter("BUSINTERFACE"):
                port = port_factory(b)

                # Add the signals to the port
                for pm in b.iter("PORTMAP"):
                    phys_et_port = self._logical2physical_portmap[core.name][port.name][
                        pm.get("LOGICAL")
                    ]
                    driver = phys_et_port.get("DIR") == "O"
                    width = 1
                    if pm.get("LEFT") is not None:
                        width = int(pm.get("LEFT")) - int(pm.get("RIGHT")) + 1
                    sig = Signal(name=pm.get("LOGICAL"), width=width, driver=driver)
                    port.add(sig)

                core.add(port)

            # Add all the scalar ports
            for p in i.iter("PORT"):
                if p.get("NAME") not in self._physical2logical_portmap[core.name]:
                    driver = p.get("DIR") == "O"
                    width = 1
                    if p.get("LEFT") is not None:
                        width = int(p.get("LEFT")) - int(p.get("RIGHT")) + 1

                    # Determine the type of the scalar port
                    if p.get("SIGIS") == "clk":
                        scalar_port = ClkPort(name=p.get("NAME"), driver=driver, width=width)
                    elif p.get("SIGIS") == "rst":
                        scalar_port = RstPort(name=p.get("NAME"), driver=driver, width=width)
                    else:
                        scalar_port = ScalarPort(name=p.get("NAME"), driver=driver, width=width)

                    scalar_port.add(Signal(name=p.get("NAME"), width=width, driver=driver))
                    core.add(scalar_port)

            self.add(core)

    def _resolve_subordinate_addressing(self) -> None:
        """
        For all subordinate ports populate their base address and range
        WARNING: This should only be called after all the cores and ports
        have been populated.
        """
        for i in self._root.iter("MEMRANGE"):
            if i.get("MEMTYPE") == "REGISTER" or i.get("MEMTYPE") == "MEMORY":
                core = self.blocks[i.get("INSTANCE")]
                port = core.ports[i.get("SLAVEBUSINTERFACE")]
                if isinstance(port, SubordinatePort):
                    port.baseaddr = int(i.get("BASEVALUE"), 16)
                    port.range = (int(i.get("HIGHVALUE"), 16) - port.baseaddr) + 1
                else:
                    raise UnexpectedPortTypeError(
                        f"Expected {port.ref} to be SubordinatePort when assigning base address"
                    )

    def _populate_subordinate_regmap(self) -> None:
        """
        For all subordinate ports populate the register maps
        WARNING: This should only be called after all the cores and ports
        have been populated.
        """
        for i in self._root.iter("MODULE"):
            core = self.lookup(f"{i.get('INSTANCE')}[block]")
            for addrblock in i.iter("ADDRESSBLOCK"):
                if (
                    addrblock.get("USAGE") == "register"
                    or addrblock.get("USAGE") == "memory"
                ):

                    _port_available = False
                    _portname = ""
                    if addrblock.get("INTERFACE").lower() in core.ports:
                        _port_available = True
                        _portname = addrblock.get("INTERFACE").lower()
                    elif addrblock.get("INTERFACE").upper() in core.ports:
                        _port_available = True
                        _portname = addrblock.get("INTERFACE").upper()
                    elif addrblock.get("INTERFACE") in core.ports:
                        _port_available = True
                        _portname = addrblock.get("INTERFACE")

                    if _port_available:
                        port = core.ports[_portname]
                        if isinstance(port, SubordinatePort):
                            for reg in addrblock.iter("REGISTER"):
                                rname: str = reg.get("NAME")
                                description: str = ""
                                offset: int = 0
                                width: int = 4
                                access: str = "read-write"
                                enabled: bool = False
                                for prop in reg.findall("PROPERTY"):
                                    if prop.get("NAME") == "DESCRIPTION":
                                        description = prop.get("VALUE")
                                    if prop.get("NAME") == "ADDRESS_OFFSET":
                                        offset = string2int(prop.get("VALUE"))
                                    if prop.get("NAME") == "SIZE":
                                        width = int(prop.get("VALUE"))
                                    if prop.get("NAME") == "IS_ENABLED":
                                        if addrblock.get("USAGE") == "register":
                                            enabled = prop.get("VALUE") == "true"
                                        else:
                                            enabled = True

                                    if prop.get("NAME") == "ACCESS":
                                        access = prop.get("VALUE")

                                rego = Register(
                                    name=rname,
                                    description=description,
                                    offset=offset,
                                    width=width,
                                    enabled=enabled,
                                    access=access,
                                )

                                for field in reg.iter("FIELD"):
                                    fname: str = field.get("NAME")
                                    fdisc: str = ""
                                    LSB: int = 0
                                    MSB: int = 0
                                    faccess: str = "read-write"
                                    for prop in field.iter("PROPERTY"):
                                        if prop.get("NAME") == "DESCRIPTION":
                                            fdisc = prop.get("VALUE")
                                        if prop.get("NAME") == "BIT_OFFSET":
                                            LSB = int(prop.get("VALUE"))
                                        if prop.get("NAME") == "BIT_WIDTH":
                                            MSB = LSB + int(prop.get("VALUE")) - 1
                                        if prop.get("NAME") == "ACCESS":
                                            faccess = prop.get("VALUE")
                                    rego.add(
                                        BitField(
                                            name=fname,
                                            description=fdisc,
                                            LSB=LSB,
                                            MSB=MSB,
                                            access=faccess,
                                        )
                                    )

                                port.add(rego)
                        else:
                            raise UnexpectedPortTypeError(
                                f"{port.name} is not a SubordinatePort but we are trying to assign it a regmap"
                            )

    def _resolve_manager_address_maps(self) -> None:
        """
        For all the manager ports resolve their address spaces
        """
        for i in self._root.iter("MODULE"):
            core = self.blocks[i.get("INSTANCE")]
            for mem in i.iter("MEMRANGE"):
                try:  # Port might not exist if there is a hole into a BDC/RPD
                    master_port = core.ports[mem.get("MASTERBUSINTERFACE")]
                    subord_port = self.blocks[mem.get("INSTANCE")].ports[
                        mem.get("SLAVEBUSINTERFACE")
                    ]
                    memtype = mem.get("MEMTYPE").lower()
                    if isinstance(master_port, ManagerPort) and isinstance(
                        subord_port, SubordinatePort
                    ):

                        master_port.addrmap_add(
                            mem.get("ADDRESSBLOCK"), memtype, subord_port
                        )
                        # addrmap = AddressMap(
                        #    name=f"{master_port.ref}_{subord_port.ref}",
                        #    block=mem.get("ADDRESSBLOCK"),
                        #    subord_port_obj=subord_port,
                        #    subord_port=subord_port.ref,
                        #    memtype=memtype,
                        # )
                        # master_port.addrmap_add(addrmap)
                    else:
                        raise RuntimeError(
                            f"Expected {master_port.ref} to be a manger and {subord_port.ref} to be a subordinate port"
                        )
                except:
                    pass

    def resolve_addressing(self) -> None:
        """
        For all the subordinate ports in the design and manager ports
        grab all the addressing information
        WARNING: This should only be called after all the cores and ports
        have been populated.
        """
        self._resolve_subordinate_addressing()
        self._populate_subordinate_regmap()
        self._resolve_manager_address_maps()

    def connect_signals(self) -> None:
        """
        Walk over the HWH and connect all the signals together
        WARNING: This needs to be run after all the cores/ports/signals
        have been populated
        """

        for i in self._root.iter("MODULE"):
            core = self.lookup(f"{i.get('INSTANCE')}[block]")
            for p in i.iter("PORT"):
                if p.get("NAME") in self._physical2logical_portmap[core.name]:
                    portname = self._physical2logical_portmap[core.name][p.get("NAME")][
                        0
                    ]
                    signame = self._physical2logical_portmap[core.name][p.get("NAME")][
                        1
                    ]
                    signal = core.lookup(f"{portname}[port]:{signame}[signal]")
                else:
                    signal = core.lookup(
                        f"{p.get('NAME')}[port]:{p.get('NAME')}[signal]"
                    )

                for con in p.iter("CONNECTION"):
                    if (con.get("INSTANCE") == f"{self.name}_imp") or (
                        con.get("INSTANCE") == "External_Ports"
                    ):
                        c_dst = con.get("PORT")
                        if c_dst in self._physical2logical_extern_pm:
                            dst_portname = self._physical2logical_extern_pm[c_dst][
                                "busname"
                            ]
                            dst_signame = self._physical2logical_extern_pm[c_dst][
                                "logical_name"
                            ]
                            dst_signal = self.ports[dst_portname].signals[dst_signame]
                        else:
                            dst_signal = self.ports[c_dst].signals[c_dst]

                        # Infect the external ports VLNV with the internal ports VLNV
                        if signal._parent.vlnv is not None:
                            dst_signal._parent.vlnv = signal._parent.vlnv.copy()

                    else:
                        dst_core = self.lookup(f"{con.get('INSTANCE')}[block]")
                        c_dst = con.get("PORT")
                        if c_dst in self._physical2logical_portmap[dst_core.name]:
                            dst_portname = self._physical2logical_portmap[
                                dst_core.name
                            ][c_dst][0]
                            dst_signame = self._physical2logical_portmap[dst_core.name][
                                c_dst
                            ][1]
                            dst_signal = dst_core.lookup(
                                f"{dst_portname}[port]:{dst_signame}[signal]"
                            )
                        else:
                            dst_signal = dst_core.lookup(
                                f"{c_dst}[port]:{c_dst}[signal]"
                            )

                    if isinstance(signal, Signal) and isinstance(dst_signal, Signal):
                        signal.connect(dst_signal)
                    else:
                        raise ExpectedSignalType(
                            f"{signal} and {dst_signal} were both expected to be of type Signal so that they could be connected"
                        )
