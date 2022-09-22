# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

import copy
import json
from dataclasses import dataclass, field, fields
from datetime import datetime
from typing import Dict, List, Optional, Set

from pydantic import BaseModel

from ..errors import MergeConflict, MetadataObjectNotFound
from .metadata_extension import MetadataExtension
from .vlnv import Vlnv


@dataclass(repr=False)
class MetadataObject:
    """
    Base metadata object
    """

    name: str = ""
    type: str = ""
    generic_type: str = ""
    _parent: Optional[MetadataObject] = None
    _children: Dict[str, MetadataObject] = field(default_factory=lambda: ({}))
    ref: str = ""
    ext: Dict[str, MetadataExtension] = field(default_factory=lambda: ({}))
    _timestamp: float = 0.0

    def walk_up_tree_timestamp_update(self, timestamp: float) -> None:
        """Recursively walk up the tree until you can't anymore
        applying the new timestamp"""
        if self._parent == None:
            return
        else:
            self._parent._timestamp = timestamp
            self._parent.walk_up_tree_timestamp_update(timestamp=timestamp)

    def __post_init__(self) -> None:
        """
        Add to the pydantic model constructor to preassign a reference for the object
        """
        self.ref = self.name
        self._timestamp = datetime.timestamp(datetime.now())

    def _mo_merge(self, a: MetadataObject) -> None:
        """Merges the base metadata object attributes. Raises an error if there are any conflicts"""
        if self.name != a.name:
            raise MergeConflict(f"{self.name=} does not match {a.name=}")
        if self.type != a.type:
            raise MergeConflict(f"{self.type=} does not match {a.type=}")
        if self.generic_type != a.generic_type:
            raise MergeConflict(
                f"{self.generic_type=} does not match {a.generic_type=}"
            )

        for a_ext in a.ext.keys():
            if a_ext not in self.ext.keys():
                self.ext[a_ext] = a.ext[a_ext]
            else:
                if self.ext[a_ext].dict() != a.ext[a_ext].dict():
                    raise MergeConflict(
                        f"Extension space object {a_ext} is not equivalent for both objects"
                    )

    def merge(self, a) -> None:
        """Default case is just to call the _mo_merge method"""
        self._mo_merge(a)

    def _lookup(self, ref_levels: List[str]) -> Optional[MetadataObject]:
        """
        helper used for recursively looking down the object
        tree
        WARNING: lookups are case insensitive
        """
        if ref_levels[0] == self.name:
            ref_levels.pop(0)
        if len(ref_levels) == 1:
            if ref_levels[0] in self._children:
                return self._children[ref_levels[0]]
            elif ref_levels[0].upper() in self._children:
                return self._children[ref_levels[0].upper()]
            elif ref_levels[0].lower() in self._children:
                return self._children[ref_levels[0].lower()]
            else:
                return None
        else:
            current = ref_levels[0]
            del ref_levels[0]
            if current in self._children:
                return self._children[current]._lookup(ref_levels)
            elif current.upper() in self._children:
                return self._children[current.upper()]._lookup(ref_levels)
            elif current.lower() in self._children:
                return self._children[current.lower()]._lookup(ref_levels)
            else:
                return None

    def _obj_dict(self, obj: object) -> object:
        """Helper for building up the dict from an object"""
        ret = {}
        # Is it a dict?
        if isinstance(obj, MetadataObject) or isinstance(obj, Vlnv):
            ret = obj.dict()
        # is it a pydantic model?
        elif isinstance(obj, BaseModel):
            ret = obj.dict()
        # Is it a list?
        elif isinstance(obj, list):
            ret = []
            for item in obj:
                if isinstance(item, object):
                    ret.append(self._obj_dict(item))
                else:
                    ret.append(item)
        # is it a set?
        elif isinstance(obj, set):
            ret = obj
        elif isinstance(obj, dict):
            ret = {}
            for name_i, i in obj.items():
                ret[name_i] = self._obj_dict(i)
        else:
            ret = obj
        return ret

    def dict(self) -> Dict:
        """renders the object as a dictionary, ignoring any fields that start with _"""
        ret = {}
        for field in fields(self):
            if not field.name.startswith("_"):
                atr = getattr(self, field.name)
                if isinstance(atr, object):
                    ret[field.name] = self._obj_dict(obj=atr)
                else:
                    ret[field.name] = atr
        return ret

    def copy(self):
        """Returns a deepcopy of the object"""
        return copy.deepcopy(self)

    def __eq__(self, a: object) -> bool:
        """Returns true if the non-private member fields are equal, false otherwise"""
        if not isinstance(a, MetadataObject):
            return False

        for field in fields(self):
            if not field.name.startswith("_"):
                if field.name not in fields(a):
                    return False
                else:
                    if getattr(self, field.name) != getattr(a, field.name):
                        return False
        return True

    def __ne__(self, a: object) -> bool:
        """Returns true if the non-private member fields are not equal, false otherwise"""
        return not self == a

    def json(self) -> str:
        """returns a json object from the sysgraph object, skipping any fields mentioned in the excludes set"""
        return json.dumps(self.dict())

    def export(self, path: str) -> None:
        """Export the model to a json file"""
        with open(path, "w") as f:
            f.write(self.json())

    def lookup(self, ref: str) -> MetadataObject:
        """
        Looks up the children of this metadata object to see
        if there is anything matching the input ref
        WARNING: lookups are case insensitive
        """
        ref_levels = ref.split(":")
        obj = self._lookup(ref_levels)
        if isinstance(obj, MetadataObject):
            return obj
        else:
            raise MetadataObjectNotFound(
                f"{ref} cannot be found in {self.ref} children={self._children.keys()}"
            )

    def _child_exists(self, item: MetadataObject) -> bool:
        """
        returns True if a child exists False otherwise
        """
        return f"{item.name}[{item.type}]" in self._children

    def _add_child(self, item: MetadataObject) -> None:
        """
        Adds a child to this metadata object
        """
        self._children[f"{item.name}[{item.generic_type}]"] = item
        # if not self._child_exists(item):
        #    self._children[f"{item.name}[{item.generic_type}]"] = item
        # else:
        # raise AlreadyAChild(
        #    f"{item.ref}[{item.generic_type}] type={type(item)} is already a child of {self.ref} type={type(self)} children={self._children.keys()}"
        # )

    def parent(self) -> Optional[MetadataObject]:
        """
        Returns a reference to the parent of this object
        """
        return self._parent

    def _refresh_child_refs(self, parent_ref: str) -> None:
        """Whenever the parent changes we needs to walk down through all the children
        recursively and update the refs"""
        for _, child in self._children.items():
            child.ref = f"{parent_ref}:{child.name}[{child.generic_type}]"
            child._refresh_child_refs(child.ref)

    def set_parent(self, parent: MetadataObject) -> None:
        """
        Sets the parent of this object
        """
        self._parent = parent
        self.ref = f"{self._parent.ref}:{self.name}[{self.generic_type}]"
        self._refresh_child_refs(self.ref)
        self._parent._add_child(self)

    def _default_repr(self, obj: object):
        return repr(obj)

    def _repr_json_(self) -> str:
        """For pretty printing the objects to the jupyter repr"""
        return json.loads(json.dumps(self.dict(), default=self._default_repr))
