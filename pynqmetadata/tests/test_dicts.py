import os
import json
import re
from deepdiff import DeepDiff
from typing import Dict

from pynqmetadata.frontends import Metadata
from pynqmetadata.views.runtime import RuntimeMetadataParser

TEST_DIR = os.path.dirname(__file__)

md = Metadata(f"{TEST_DIR}/hwhs/resizer.hwh")
rt_md = RuntimeMetadataParser(md) 

class NonIdenticalDicts(Exception):
    """Error that is thrown when identical Dicts are expected, but they are not identical"""
    pass

def _dict_comparer(dut:Dict, golden_dict_name:str)->None:
    """tests to see if a dict matches a golden file"""
    golden_f =open(os.path.join(TEST_DIR, 'golden_dicts', golden_dict_name), "r")
    golden_json = golden_f.read()
    golden = json.loads(golden_json)

    # dut - dict under test
    dut = json.dumps(dut, default=lambda o: '<not serializable>')
    dut_dict = json.loads(dut)

    diff = DeepDiff(golden, dut_dict, ignore_order=True) 

    filtered_diff = {}
    for item_name, item in diff.items():
        if item_name == "dictionary_item_removed":
            filtered_diff[item_name] = item
        elif item_name == "value_changed":
            for val_name, val in diff["value_changed"].items():
                pattern = re.compile("*.['(description|addr_range|size)']")
                if not pattern.match(val_name):
                    filtered_diff[val_name] = val

    if len(filtered_diff) > 0:
        raise NonIdenticalDicts(f"Dicts are not the same, diff={filtered_diff}")


def test_resizer_ip_dict_correct():
    _dict_comparer(rt_md.ip_dict, os.path.join('resizer','ip_dict_golden.json'))

#def test_resizer_mem_dict_correct():
#    _dict_comparer(rt_md.mem_dict, os.path.join('resizer','mem_dict_golden.json'))

def test_resizer_gpio_dict_correct():
    _dict_comparer(rt_md.gpio_dict, os.path.join('resizer','gpio_dict_golden.json'))

def test_resizer_clock_dict_correct():
    _dict_comparer(rt_md.clock_dict, os.path.join('resizer','clock_dict_golden.json'))

def test_resizer_hierarchy_dict_correct():
    _dict_comparer(rt_md.hierarchy_dict, os.path.join('resizer','hierarchy_dict_golden.json'))

def test_resizer_interrupt_controllers_correct():
    _dict_comparer(rt_md.interrupt_controllers, os.path.join('resizer','interrupt_controllers_golden.json'))

def test_resizer_interrupt_pins_correct():
    _dict_comparer(rt_md.interrupt_pins, os.path.join('resizer','interrupt_pins_golden.json'))
