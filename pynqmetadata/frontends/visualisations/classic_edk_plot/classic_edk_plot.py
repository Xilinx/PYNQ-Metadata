# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

from ..metadata_vis import MetadataVis
from pynqmetadata import Module, Port
from pynqmetadata import ManagerPort, StreamPort, ClkPort, RstPort
from pynqmetadata import SubordinatePort, BusConnection
import random
import string
import json

class ClassicEdkPlot(MetadataVis):
    
    def _is_con_hidden(self,connection:BusConnection)->bool:
        """
        Returns true if the connection is hidden
        """
        hidden = False
        if 'vis' in connection._src_port.ext:
            if 'hidden' in connection._src_port.ext['vis']:
                hidden = (connection._src_port.ext['vis']['hidden'] == "yes")
        return hidden

    def _bus_type_from_port(self, port:Port)->str:
        """
        Returns the associated bustype with a port
        """
        if isinstance(port, SubordinatePort) or isinstance(port, ManagerPort):
            return "MemoryMapped"
        if isinstance(port, StreamPort):
            return "Stream"
        if isinstance(port, ClkPort):
            return "clk/rst"
        if isinstance(port, RstPort):
            return "clk/rst"
        return "scalar"

    def _gen_patch_panel_json(self)->str:
        """ Returns a string that contains 
            the format the visualisation is
            expecting
        """
        ppan = {}
        ppan["nodes"] = []
        for cname, core in self.md.blocks.items():
            ppan["nodes"].append(cname)
        ppan["busses"] = []
        for cname, core in self.md.blocks.items():
            for pname, port in core.ports.items():
                bus={}
                bus["busmastername"] = port.ref
                bus["origin"] = port._parent.name 
                bus["type"] = self._bus_type_from_port(port)
                if hasattr(port, "driver") and not (isinstance(port, ClkPort) or isinstance(port, RstPort)):
                    if port.driver == "yes":
                        ppan["busses"].append(bus)
                if isinstance(port, ManagerPort):
                    ppan["busses"].append(bus)

        ppan["subordinates"] = []
        for constr, con in self.md.busses.items():
            sbord_con = {}
            sbord_con["bus"] = con._dst_port.ref
            sbord_con["dst"] = con._src_port._parent.name
            sbord_con["type"] = self._bus_type_from_port(con._dst_port)

            if hasattr(con._src_port, "driver") and not (isinstance(con._src_port, ClkPort) or isinstance(con._dst_port, RstPort)):
                if not con._src_port.driver:
                    ppan["subordinates"].append(sbord_con)
            if isinstance(con._src_port, SubordinatePort):
                ppan["subordinates"].append(sbord_con)

        return json.dumps(ppan)

    def __init__(self, md:Module)->None:
        self.md = md

        letters = string.ascii_lowercase
        self.canvas = ''.join(random.choice(letters) for i in range(8))

        self.body = "var graph = " + self._gen_patch_panel_json() + ";\n\n" 
        self.body += "var colour = d3.scaleOrdinal(d3.schemeCategory10);\n"
        self.body += f"var bus_width = 15;\n"
        self.body += f"var ip_height = 17;\n"
        self.body += f"var x_pos = 5;\n"
        self.body += f"var y_pos = 5;\n"
        self.body += f"var text_y_offset = 100;\n"
        self.body += "var width = x_pos + graph.busses.length*bus_width+25+350;\n"
        self.body += "var height = y_pos + text_y_offset + graph.nodes.length*ip_height+50;\n"
        self.body += "console.log(graph);\n"
        self.body += "var svg = d3.select(\"#"+self.canvas+"\").append(\"svg\")."
        self.body += "attr(\"height\", height).attr(\"width\", width);\n"

        self.body += " for(var bus in graph.busses){\n"
        self.body += "   var label_x_pos = x_pos + bus*bus_width; \n"
        self.body += "   var label_y_pos = y_pos + text_y_offset; \n"
        self.body += "      svg.append(\"text\")\n"
        self.body += "        .attr(\"id\", \""+self.canvas+"\"+\"_\"+graph.busses[bus].busmastername.replace(\":\", \"_\"))\n"
        self.body += "        .attr(\"idx\", bus)\n"
        self.body += """      .attr("text-anchor", "start")
                              .attr("font-family", "sans-serif")
                              .attr("dy", ".35em")
                              .attr("transform", "translate("+label_x_pos+","+label_y_pos+") rotate(-90)")
                              .attr("font-weight", 300)
                              .style("fill", colour(graph.busses[bus].type))
                              .text(graph.busses[bus].type)
                     }\n"""

        self.body += f"var text_x_offset = graph.busses.length*bus_width + x_pos + 25;\n"
        self.body += "for(var n in graph.nodes) {\n"
        self.body += "   var node_label_y_pos = text_y_offset + y_pos + n*ip_height + 25;\n"
        self.body += "      svg.append(\"text\")\n"
        self.body += "        .attr(\"id\", \""+self.canvas+"\"+\"_\"+graph.nodes[n])\n"
        self.body += "        .attr(\"idx\", n)\n"
        self.body += """      .attr("text-anchor", "start")
                              .attr("font-family", "sans-serif")
                              .attr("dy", ".35em")
                              .attr("transform", "translate("+text_x_offset+","+node_label_y_pos+") rotate(0)")
                              .attr("font-weight", 300)
                              .text(graph.nodes[n])
                     }\n"""

        # Place the master rectangles
        self.body += "for(var b in graph.busses) {\n"
        self.body += "    ip_idx = d3.select(\"#"+self.canvas+"_\"+graph.busses[b].origin).attr(\"idx\")\n"
        self.body += "    bus_idx = d3.select(\"#"+self.canvas+"_\"+graph.busses[b].busmastername.replace(\":\", \"_\")).attr(\"idx\")\n"
        self.body += "    mdot_x = x_pos + bus_idx*bus_width;\n"
        self.body += "    mdot_y = text_y_offset + y_pos + ip_idx*ip_height + 25;\n"

        self.body += "    svg.append(\"rect\")\n"
        self.body += "       .attr(\"id\", \""+self.canvas+"_dot_\"+graph.busses[b].busmastername.replace(\":\", \"_\"))\n"
        self.body += "       .attr(\"width\", 10)\n"
        self.body += "       .attr(\"height\", 10)\n"
        self.body += "       .attr(\"x\", mdot_x-5)\n"
        self.body += "       .attr(\"y\", mdot_y-5)\n"
        self.body += "       .style(\"fill\", colour(graph.busses[b].type));\n"

        self.body += "    svg.append(\"line\")\n"
        self.body += "       .attr(\"x1\", mdot_x)\n"
        self.body += "       .attr(\"y1\", mdot_y)\n"
        self.body += "       .attr(\"x2\", text_x_offset - 10)\n"
        self.body += "       .attr(\"y2\", mdot_y)\n"
        self.body += "       .style(\"stroke\", colour(graph.busses[b].type))\n"
        self.body += "       .style(\"stroke-width\", \"0.5\");\n"

        self.body += "}"
                                    

        # Place the slave dots 
        self.body += "for(var s in graph.subordinates) {\n"
        self.body += "    ip_idx = d3.select(\"#"+self.canvas+"_\"+graph.subordinates[s].dst).attr(\"idx\")\n"
        self.body += "    bus_idx = d3.select(\"#"+self.canvas+"_\"+graph.subordinates[s].bus.replace(\":\", \"_\")).attr(\"idx\")\n"
        self.body += "    mdot_x = x_pos + bus_idx*bus_width;\n"
        self.body += "    mdot_y = text_y_offset + y_pos + ip_idx*ip_height + 25;\n"
        self.body += "    svg.append(\"circle\")\n"
        self.body += "       .attr(\"r\", 5)\n"
        self.body += "       .attr(\"cx\", mdot_x)\n"
        self.body += "       .attr(\"cy\", mdot_y)\n"
        self.body += "       .style(\"fill\", colour(graph.subordinates[s].type))\n"

        self.body += "    var master_y = d3.select(\"#"+self.canvas+"_dot_\"+graph.subordinates[s].bus.replace(\":\", \"_\")).attr(\"y\");\n"
        self.body += "    console.log(graph.subordinates[s].bus +\"  \"+ master_y);\n"
        self.body += "    svg.append(\"line\")\n"
        self.body += "       .attr(\"x1\", mdot_x)\n"
        self.body += "       .attr(\"y1\", mdot_y)\n"
        self.body += "       .attr(\"x2\", mdot_x)\n"
        self.body += "       .attr(\"y2\", master_y)\n"
        self.body += "       .style(\"stroke\", colour(graph.subordinates[s].type))\n"
        self.body += "       .style(\"stroke-width\", \"0.5\");\n"

        self.body += "    svg.append(\"line\")\n"
        self.body += "       .attr(\"x1\", mdot_x)\n"
        self.body += "       .attr(\"y1\", mdot_y)\n"
        self.body += "       .attr(\"x2\", text_x_offset - 10)\n"
        self.body += "       .attr(\"y2\", mdot_y)\n"
        self.body += "       .style(\"stroke\", colour(graph.subordinates[s].type))\n"
        self.body += "       .style(\"stroke-width\", \"0.5\");\n"
    

        self.body += "}"



        super().__init__(['lib/d3.v4.min.js'],body=self.body, canvas_name=self.canvas)
        self.render()
            
        


        
