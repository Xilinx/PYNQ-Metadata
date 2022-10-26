# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

from dataclasses import dataclass, field
from re import L
from typing import Dict, List, Optional

from pynqmetadata.errors.metadata_type_errors import UnexpectedMetadataObjectType

from ..errors import CoreAlreadyExists, UnexpectedPmdObject
from .block import Block
from .bus_connection import BusConnection
from .core import Core
from .hierarchy import Hierarchy
from .manager_port import ManagerPort
from .metadata_object import MetadataObject
from .parameter import Parameter
from .port import Port
from .proc_sys_core import ProcSysCore


@dataclass(repr=False)
class Module(Block):
    """
    A Metadata object that contains a hierarchy of
    cores and connections between the cores
    """

    type: str = "module"
    blocks: Dict[str, Block] = field(default_factory=lambda: ({}))
    modules: Dict[str, MetadataObject] = field(default_factory=lambda: ({}))
    busses: Dict[str, BusConnection] = field(default_factory=lambda: ({}))
    _hierarchies: Optional[Hierarchy] = None

    def merge(
        self,
        a: Block,
        skip_external: bool = False,
        inherit_signal_width: bool = False,
        inherit_addr_info: bool = False,
        ignore_addr_info: bool = False,
    ) -> None:
        assert isinstance(a, Module)
        self._block_merge(
            a,
            skip_external=skip_external,
            inherit_signal_width=inherit_signal_width,
            inherit_addr_info=inherit_addr_info,
            ignore_addr_info=ignore_addr_info,
        )

        for block in a.blocks:
            if block in self.blocks:
                self.blocks[block].merge(
                    a.blocks[block],
                    skip_external=skip_external,
                    inherit_signal_width=inherit_signal_width,
                    inherit_addr_info=inherit_addr_info,
                    ignore_addr_info=ignore_addr_info,
                )
            else:
                self.blocks[block] = a.blocks[block]

        for mod in a.modules:
            if mod in self.modules:
                self.modules[mod].merge(a.modules[mod])
            else:
                self.modules[mod] = a.modules[mod]

    def exists(self, item: MetadataObject) -> bool:
        """Returns true if the item is in this model"""
        if isinstance(item, Port) or isinstance(item, Parameter):
            return self._exists(item)
        elif isinstance(item, Block):
            return item.name in self.blocks
        else:
            return False

    def add(self, item: MetadataObject) -> None:
        """
        Adds either a core or an external port to this Pmd
        """
        if isinstance(item, Port) or isinstance(item, Parameter):
            self._add(item)
        elif isinstance(item, Block):
            if not self.exists(item):
                self.blocks[item.name] = item
                item.set_parent(self)
            else:
                raise CoreAlreadyExists(
                    f"{item.name} already exists in module {self.ref}"
                )
        else:
            raise UnexpectedPmdObject(
                f"unable to add {item} to {self.name} as it is not a external port or a core"
            )

    def refresh(self) -> None:
        """
        Refreshes the design:
            * populates all the connections
            * performs well-formdness checks on the design
            * populates the hierarchy mappings
        """
        if self.parent is None:
            self.ref = self.name
        else:
            if isinstance(self.parent, MetadataObject):
                self.ref = f"{self.parent.ref}:{self.name}[{self.generic_type}]"
            # else:
            #    raise UnexpectedMetadataObjectType(
            #        f"Parent of {self.name} is of type {type(self.parent)}"
            #    )

        self._update_parents()
        self._relink_objects()
        self._populate_connections()
        self._allocate_hierarchies()

    def _relink_objects(self) -> None:
        """Using the string references, relink the objects together in the model"""
        for block in self.blocks.values():
            for port in block.ports.values():
                if isinstance(port, ManagerPort):
                    for addr in port.addrmap:
                        port._addrmap_obj[addr] = self.lookup(
                            port.addrmap[addr]["subord_port"]
                        )

                for sig in port.signals.values():
                    for con in sig.con_refs:
                        sig._connections[con] = self.lookup(con)

    def _update_parents(self) -> None:
        """Walk down through the module and makes sure all the parent references are accurate
        This is usually performed when we do an update, merge, parse some json metadata
        """
        self._update_parents_base()
        for b in self.blocks.values():
            b.set_parent(self)
            b._update_parents()
        for b in self.busses.values():
            b.set_parent(self)

    def _populate_connections(self) -> None:
        """
        Populates bus-level connections in the design. Walks over the signal
        level wiring to determine this
        """
        for c in self.blocks.values():
            for p in c.ports.values():
                for d in p.destinations().values():
                    con_name = f"{p.ref}->{d.ref}"
                    conn = BusConnection(
                        name=con_name,
                        ref=con_name,
                        src_port=p.ref,
                        dst_port=d.ref,
                        _src_port=p,
                        _dst_port=d,
                    )
                    self.busses[conn.ref] = conn

        # External ports
        for p in self.ports.values():
            for d in p.destinations().values():
                con_name = f"{p.ref}->{d.ref}"
                conn = BusConnection(
                    name=con_name,
                    ref=con_name,
                    src_port=p.ref,
                    dst_port=d.ref,
                    _src_port=p,
                    _dst_port=d,
                )
                self.busses[conn.ref] = conn

    def _allocate_hierarchies(self) -> None:
        """
        Walks over all the cores and allocates them into the hierarchies.
        Uses the Xilinx hierarchy_name to determine what the hierarchy is.
        """
        self._hierarchies = Hierarchy(name=f"{self.name}_hier")
        for core in self.blocks.values():
            if isinstance(core, Core) or isinstance(core, Module):
                hiers = []
                if isinstance(core.hierarchy_name, str):
                    hiers = core.hierarchy_name.split("/")

                if len(hiers) > 1:
                    if hiers[0] not in self._hierarchies._hierarchies_obj:
                        self._hierarchies.add(Hierarchy(name=hiers[0], path=hiers[0]))
                    self._recurse_populate_hierarchy(
                        h=self._hierarchies._hierarchies_obj[hiers[0]],
                        h_strs=hiers[1:],
                        path=hiers[0],
                        core=core,
                    )
                else:
                    if not isinstance(core, Module):
                        self._hierarchies.add(core)
                    else:
                        self._hierarchies.add(
                            Hierarchy(name=core.name, path=core.name, pr_region=True)
                        )

    def _recurse_populate_hierarchy(
        self, h: Hierarchy, h_strs: List[str], core: Core, path: str
    ) -> None:
        """
        Recursively populate the hierarchy given:
            * the current hierarchy object
            * the current hierarchy string list
            * a reference to the block being added to the hierarchy
        """
        if len(h_strs) > 1:
            if h_strs[0] not in h._hierarchies_obj:
                h.add(Hierarchy(name=h_strs[0], path=f"{path}/{h_strs[0]}"))
            self._recurse_populate_hierarchy(
                h=h._hierarchies_obj[h_strs[0]],
                h_strs=h_strs[1:],
                core=core,
                path=f"{path}/{h_strs[0]}",
            )
        else:
            if isinstance(core, Module):
                h.add(Hierarchy(name=h_strs[0], path=f"{path}/{h_strs[0]}", pr_region=True))
            else:
                h.add(core)

    def _hierarchy_recurse_search(self, hier:Hierarchy, hier_name:List[str])->Hierarchy:
        """ Used by hierarchy() to recursively walk down the hierarchy tree 
        searching for the matching hierarchy"""
        if len(hier_name) == 1:
            return hier._hierarchies_obj[hier_name[0]] 
        else:
            return self._hierarchy_recurse_search(hier=hier._hierarchies_obj[hier_name[0]], hier_name=hier_name[1:])
        

    def hierarchy(self, hier_name:str)->Hierarchy:
        """ Given a hierarchy string, where levels are separated by a /, 
        return a hierarchy model from this module"""
        hn_split = hier_name.split("/")
        return self._hierarchy_recurse_search(hier_name=hn_split, hier=self._hierarchies)

    def get_processing_systems(self) -> Dict[str, ProcSysCore]:
        """Returns a list of processing system blocks that are in the design"""
        core_set: Dict[str, ProcSysCore] = {}
        for core in self.blocks.values():
            if isinstance(core, ProcSysCore):
                core_set[core.name] = core
        return core_set

    def get_dict_of_block_instances_with(self, name: str) -> Dict[str, MetadataObject]:
        """
        when given a string name get a list of the instances that match it and
        recursively walk down through the entire system structure
        """
        ret: Dict[str, MetadataObject] = {}
        for block in self.blocks.values():
            if name == block.name:
                ret[block.ref] = block
            if isinstance(block, Module):
                ret.update(block.get_dict_of_block_instances_with(name=name))
        return ret
