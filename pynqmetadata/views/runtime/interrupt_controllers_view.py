# Copyright (C) 2022 Xilinx, Inc
# Copyright (C) 2022-2026 Advanced Micro Devices, Inc.
# SPDX-License-Identifier: BSD-3-Clause

import re

from pydantic import Field
from pynqmetadata import Core, MetadataExtension

from .metadata_view import MetadataView


class InterruptControllerIndex(MetadataExtension):
    index: int = Field(..., description="The interrupt controller's parent input index")


def _interrupt_metadata(module):
    controllers, pins, signals = {}, {}, {}
    systems = module.get_processing_systems()
    if not systems:
        return controllers, pins, signals
    if len(systems) != 1:
        raise RuntimeError("Interrupt metadata requires one processing system")
    ps = next(iter(systems.values()))
    expanded = set()

    def walk(signal, bit, parent, index, raw_irq, visited):
        if bit >= signal.width:
            return
        position = (signal.ref, bit)
        if position in visited:
            return
        visited = visited | {position}
        core = signal.parent().parent()
        if isinstance(core, Core) and core is not ps:
            name = core.vlnv.name if core.vlnv is not None else ""
            port = signal.parent().name
            if name == "xlconcat" and port == "dout":
                offset = 0
                inputs = sorted(
                    (p for p in core.ports.values() if re.fullmatch(r"In\d+", p.name)),
                    key=lambda p: int(p.name[2:]),
                )
                for input_port in inputs:
                    source = input_port.sig()
                    if offset <= bit < offset + source.width:
                        walk(source, bit - offset, parent, index, raw_irq, visited)
                        break
                    offset += source.width
                return
            if name == "axi_intc" and port in ("irq", "interrupt"):
                entry = {"parent": parent, "index": index}
                if not parent:
                    entry["raw_irq"] = raw_irq
                previous = controllers.get(core.hierarchy_name)
                if previous is not None and previous != entry:
                    raise ValueError(f"Conflicting interrupt routes for {core.hierarchy_name}")
                controllers[core.hierarchy_name] = entry
                core.ext["interrupt_controller_index"] = InterruptControllerIndex(index=index)
                if core.hierarchy_name not in expanded:
                    expanded.add(core.hierarchy_name)
                    source = core.ports["intr"].sig()
                    for child in range(source.width):
                        walk(source, child, core.hierarchy_name, child, None, set())
                return
            if signal.width == 1:
                path = f"{core.hierarchy_name}/{signal.name}"
                entry = {"controller": parent, "index": index, "fullpath": path}
                if not parent:
                    entry["raw_irq"] = raw_irq
                previous = pins.get(path)
                if previous is not None and previous != entry:
                    raise ValueError(f"Conflicting interrupt routes for {path}")
                pins[path] = entry
                signals[path] = signal
        for connection in signal._connections.values():
            walk(connection, bit, parent, index, raw_irq, visited)

    offset = 0
    for port_name, ranges in ps.irq.items():
        raw_irqs = [base + i for base, count in ranges for i in range(count)]
        if port_name in ps.ports:
            signal = ps.ports[port_name].sig()
            for bit, raw_irq in enumerate(raw_irqs):
                walk(signal, bit, "", offset + bit, raw_irq, set())
        offset += len(raw_irqs)
    return controllers, pins, signals


class InterruptControllersView(MetadataView):
    """AXI interrupt controllers indexed by their full hierarchical names."""

    def __init__(self, module):
        super().__init__(module=module)
        self._state = {}

    @property
    def view(self):
        return _interrupt_metadata(self._md)[0]

    def __setitem__(self, key, value):
        self._state[key] = value
