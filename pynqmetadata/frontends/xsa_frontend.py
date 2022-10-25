# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

from .hwh_frontend import HwhFrontend
from .json_frontend import JsonFrontend
from ..models.metadata_object import MetadataObject
from ..models.module import Module
from typing import Optional
from pydantic import Field
from ..models.metadata_extension import MetadataExtension

class XsaObjectExtension(MetadataExtension):
    """Extends the metadata to include an XSA parser object"""
    xsa: Optional[object] = Field(default=None, exclude=True)

def XsaFrontend(input: str) -> MetadataObject:
    """ 
    Convert an XSA into a metadata object. The XSA may contain
    multiple hwh files / BDC descriptions / or Metadata json files.
    """
    from pynqutils.build_utils import XsaParser
    xsa = XsaParser(input)
    xsa.load_bdc_metadata()
    md = HwhFrontend(_hwhfile=xsa.defaultHwhPaths[0])
    md.ext["xsa"] = XsaObjectExtension(xsa=xsa)
    for b in md.blocks.values():
        if isinstance(b, Module):
            if "bdc" in b.ext:
                bd = b.ext["bdc"]
                bdc_filename = f"{bd.bd_name}.hwh"
                for hwh_fp in xsa.referenceHwhPaths:
                    if hwh_fp.endswith(bdc_filename):
                        bdc_md = HwhFrontend(_hwhfile=hwh_fp)
                        bdc_md_json = bdc_md.json().replace(bdc_md.name, b.name)
                        mod_bdc_md = JsonFrontend(bdc_md_json)
                        mod_bdc_md.hierarchy_name = b.hierarchy_name
                        b.merge(
                            mod_bdc_md,
                            skip_external=True,
                            inherit_signal_width=True,
                            inherit_addr_info=True,
                        )
                for merge_obj_file in xsa.mergeableMetadataObjects:
                    if merge_obj_file.endswith(".hwh"):
                        merge_obj = HwhFrontend(_hwhfile=merge_obj_file)
                    elif merge_obj_file.endswith(".json"):
                        merge_obj = JsonFrontend(input=merge_obj_file)
                    else:
                        raise RuntimeError(f"{merge_obj_file} is an unknown file format that cannot be parsed")
                    name_matches = md.get_dict_of_block_instances_with(
                        merge_obj.name
                    )
                    if len(name_matches) == 1:
                        orig_obj = name_matches[list(name_matches.keys())[0]]
                        orig_obj.merge(merge_obj, ignore_addr_info=True)
                    else:
                        raise RuntimeError(
                            f"Aborting more than one object matches name {merge_obj.name} = {name_matches}"
                        )
                b.refresh()
    return md