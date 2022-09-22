# pynq-metadata
## version=0.2.3

``pynq-metadata`` is an abstract representation of a reconfigurable system. The design of the core metadata is to be simple and extensible. It adopts a modular approach, where analysis and transformation passes can be applied to the metadata to extend it as required. Transformation and analysis passes can occur statically, say optimising the design of a system, or dynamically on-target, such as for system discovery during operation.

This repository contains the core metadata definition; it also includes classes for constructing an abstract representation of the metadata in Python and C++ and validators to check correctness against a schema.
The file format for the metadata is ``.pmd``; however, the metadata is all constructed around JSON objects to make cross-platform parsing and facilitate community-driven extensions.

```diff
@@ At this stage this document should be considered a living document used to explore the initial pynq-metadata. In places it will also mention ideas/questions that need to be addressed as the metadata is being developed. @@
```
## Example schema structure
This section will briefly walk through an example pmd object structure. However, the formal specification for the pmd json can be found in ```pynqmetadata/schema```.

### Pmd : Pynq Metadata Object
![](pynqmetadata/docs/diagrams/pmd_object.png)

The root of the metadata is a pmd object that contains a list of core objects in the design, a list of blocks (which are object pmd objects) and a list of connections. The blocks represent block design containers, such as DFX regions, that can be considered as standalone metadata outright. The list of connections is a flat hierarchy of all the bus-level connections within the design. The ext region is a metadata extension space where additional metadata can be added. The ext region is not checked by the json schema, however, it is possible for the schema to be extended to include these regions. 

All the fields highlighted are mandatory, optional fields do not have to exsist, but if they do exist have a strict schema that they must follow. For example, if there are cores in the core list then each core must follow the core schema, see the next section for an example of the core schema. 

### Core : Describes IP cores and Processing system blocks
![](pynqmetadata/docs/diagrams/core_object.png)

Cores describe an IP block or processing system within the design. They must have a unique name, a coretype, and a vlnv type (internal xilinx IP identifier). Optionally they may have a list of ports, that enable them to connect to other IP; and a list of parameters and the parameter's configuration. If they do have a list of ports or parameters then they must obey the schema for those fields. There is also an optional metadata extension space where the metadata for the core can be extended. 

## Ports
Cores can have ports associated with them that can be used to connect them to other cores. Every port must have a unique name specified and a port type. Depending on the port type other fields are required, for instance, a subordinate port must contain the memory mapped register information, whereas a manager port type must contain a list of the subordinate ports that it manages. Below is a description of the different mandatory fields for each porttype in the metadata.

Ports also contain a list of portsignals. These are the individual nets of the bus that connect to other port connections. This information provides the low-level connectivity of the Port.

### Ports: Subordinate port type
![](pynqmetadata/docs/diagrams/subordinate_port.png)

A subordinate port type is a memory-mapped register endpoint. It must contain a register field where the base address and address range is specified. In this register field there may also be a list of register objects describing the memory layout of the endpoint.
the list of registers is optional, but if present, must follow the register schema.

### Registers and bitfields
![](pynqmetadata/docs/diagrams/registers_and_bitfields.png)

Each individual register must contain a byte-aligned offset and a width in bytes. They may optionally have a name, a description, and a list of the functions of individual bits. For each individual specified bit field, the LSB and MSB of the bits must be specified and an optional name and description may be given.  

### Ports: Manager port type
![](pynqmetadata/docs/diagrams/manager_port.png)

Manager port types must contain an addrmap field which is a list of subordinate ports that they are managing. Each addrmap item must contain a reference to the subordinate port of the form ```<core>:<port>```  and a block name which the tools something use to refer to it.

### Ports: Clk, Rst, and Stream port types
![](pynqmetadata/docs/diagrams/clk_rst_port.png)
The clk, rst, and stream ports contain an extra field to indicate if they are driving the signal or not.

### PortSignal : Describing the nets associated with a port and their connections
![](pynqmetadata/docs/diagrams/portsignal.png)

### Python metadata object
Along with a schema JSON representation for the metadata, there is also an internal Python data structure for walking and manipulating the metadata. A diagram of the class hierarchy is displayed below:
![](pynqmetadata/docs/diagrams/pmd_uml.svg)

## Creating alternative views onto the metadata

## Creating metadata passes

## Validation 

Along with the metadata classes and structural definitions, this repository also contains tools for validating the metadata. Validation has a few stages:

* __[1: Schema check]__ The metadata is checked against a schema to ensure that the base structure and syntax of the metadata are correct. 
* __[2. Well-formedness check]__ After a valid schema check, we create an internal metadata object and perform checks to ensure that the metadata describes a well-formed design. This stage performs tasks like type checking on connections between cores and various design rule checks.

### Schema check

In the ``pynqmetadata/schema`` directory, you can find the metadata schema. The schema is a hierarchical structure consisting of nested files referenced with a ``$ref`` jsonschema reference. The intention is that developers who wish to extend the metadata will append their schemas to provide additional checks specific to their metadata transformation pass.

There is also a tool ``pmdcheck`` included in the package for checking if a ``.pmd`` metadata file matches the schema. Usage:
```
	cat metadata_file.pmd | pmdcheck
```

or

```
	pmdcheck --input metadata_file.pmd
```

## Requirements

```
	python3.8
	pip install jsonschema
```

# Testing
The abstract representation of the metadata exists in both Python and C++ and tests are supplied for both. However, the validator is only written in python, so testing the validator is included in the python section.
## Running python tests
To run python tests we use the ``pytest`` package. In the project root directory run:
```
	python3 -m pytest
```
To test just the metadata validation with the schema run the following tests
```
	python3 -m pytest pynqmetadata/tests/validation
```

To test just the python metadata object classes run 
```
	python3 -m pytest pynqmetadata/tests/python
```

