![pynq_logo](https://github.com/Xilinx/PYNQ/raw/master/logo.png)
### version 0.1.5

PYNQ-Metadata is an open-source project from Xilinx and is part of the PYNQ ecosystem. It's aims are to provide an abstract description of reconfigurable system designs. It is currently used internally within PYNQ to represent the hardware design currently configured in the Programmable Logic of Zynq-based devices. It is currently in pre-release.  

## Quick Start
PYNQ-Metadata can parse the design of a system in the following formats:
* A HWH file
* An XSA file
* A JSON PYNQ-Metadata description 

To install PYNQ-Metadata use the following command:
```
python3 -m pip install pynqmetadata 
```

To parse a design use the following python commands:
```python
from pynqmetadata.frontends import Metadata
md = Metadata('xsa_file.xsa')
md = Metadata('hwh_file.hwh')
md = Metadata('pynq_metadata_json_file.json')
```

Once a design has been parsed it can then be easily walked, searched, modified, extended, and much more. 

## Tutorials
__Coming soon:__ Documentation on how to use PYNQ-Metadata to manipulate and inspect designs.

## Python Source Code

All python code for the ``PYNQ-Metadata`` package can be found in the `/pynqmetadata` folder.

* `pynqmetadata/frontends` -- contains the frontend parsers for taking an XSA, HWH, or more into the PYNQMetadata format. 
* `pynqmetadata/models` -- contains the class hierarchy for the internal object model of a PYNQMetadata representation.
* `pynqmetadata/errors` -- contains the exception classes.


## Changelog
* v0.1.5 : Prevent parsing error when external AXI ports are present in the design. 
* v0.1.4 : Fixing runtime metadata views for when the PS is contained within a hierarchy. Relaxing the Python version constraint (for x86). 
* v0.1.3 : Fixing python version requirement 
* v0.1.2 : Fixed issue where custom IP was being interpreted as an empty hierarchy
* v0.1.1 : Fixed circular dependency issue with PYNQ-Utils
