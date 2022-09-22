# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

from ..metadata_vis import MetadataVis
from pynqmetadata import BusConnection
from pynqmetadata import Module, Core
from pynqmetadata import Hierarchy
import random
import string

def VisHierarchyFilter(md:Module, h:Hierarchy)->Module:
    """ when given a hierarchy return a metadata object where 
    for visualisation the hierarchy has been filtered out """
    ret = md.copy()
    for c in ret.busses.values():
        c.ext["vis"]={}
        
        if not isinstance(c._dst_port._parent, Core) or not isinstance(c._src_port._parent, Core):
            c.ext["vis"]["hidden"] = "no"
        else:
            if h.exists(c._src_port._parent) or h.exists(c._dst_port._parent):
                c.ext["vis"]["hidden"] = "no"
            else:
                c.ext["vis"]["hidden"] = "yes"
                
    for b in ret.blocks.values():
        b.ext["vis"] = {}
        if h.exists(b):
            b.ext["vis"]["hidden"] = "no"
        else:
            b.ext["vis"]["hidden"] = "yes"
        
    return ret    
        
class ConMatVis(MetadataVis):
    
    def _is_con_hidden(self,connection:BusConnection)->bool:
        """
        Returns true if the connection is hidden
        """
        hidden = False
        if 'vis' in connection.ext:
            if 'hidden' in connection.ext['vis']:
                hidden = (connection.ext['vis']['hidden'] == "yes")
        return hidden

    def _is_core_hidden(self, core:Core)->bool:
        """
        Returns True if this core is hidden and should not be rendered
        """
        hidden = False
        if 'vis' in core.ext:
            if 'hidden' in core.ext['vis']:
                hidden = (core.ext['vis']['hidden'] == "yes")
        return hidden

    def _gen_force_vis_json(self)->str:
        """ Returns a string that contains 
            the format that the force visualisation
            is expecting
        """
        s = "{ \"nodes\" : [ \n"
        #for block in self.md.blocks:
        #    s += "{ \"id\": \""+block.name+"\", \"group\": 1, \"configured\":\"no\""
        #    s += "},"
        for cname, core in self.md.blocks.items():
            if not self._is_core_hidden(core):
                s += "{ \"id\": \""+cname+"\", \"group\": 1, \"configured\":\"yes\""
                s += "},"
        s = s.rstrip(s[-1])
        s += "],\n \"links\" : [\n"
        for conname,con in self.md.busses.items():
            if not self._is_con_hidden(con):
                s += "{ \"source\" : \""+con._src_port._parent.name+"\",\n"
                s += "  \"target\" : \""+con._dst_port._parent.name+"\",\n"
                s += "  \"source_port\" : \""+con._src_port.name+"\",\n"
                s += "  \"target_port\" : \""+con._dst_port.name+"\",\n"
                s += "  \"source_porttype\" : \""+con._src_port.type+"\",\n"
                s += "  \"target_porttype\" : \""+con._dst_port.type+"\"}"
                if conname != list(self.md.busses.keys())[-1]:
                    s+= ",\n"
        s += "]\n"
        s += "}"
        return s

    def __init__(self, md:Module)->None:
        self.md = md

        letters = string.ascii_lowercase
        self.canvas = ''.join(random.choice(letters) for i in range(8))

        self.body = "var g = " + self._gen_force_vis_json() + ";\n\n" 
        self.body += """
            // Find the longest string so we know how far to offset the diagram
            var max_len = 0;
            for(var n in g.nodes) {
                if (g.nodes[n].id.length > max_len) {
                    max_len = g.nodes[n].id.length;
                }
            }

            var text_unit_space = 5;
            var matrix_offset = text_unit_space * max_len;
            var boxsize = 8; 
            var box_bound = 2;
        """
        self.body += "var width = (matrix_offset + (g.nodes.length + 1)*(boxsize + box_bound)) + 250;"
        self.body += "var height = (matrix_offset + (g.nodes.length + 1)*(boxsize + box_bound)) + 150;"
        self.body += "var svg = d3.select(\"#"+self.canvas+"\").append(\"svg\")."
        self.body += "attr(\"height\", height).attr(\"width\", width)\n"
        self.body += """

            var colour = d3.scaleOrdinal(d3.schemeCategory20);

            svg.append('defs')
               .append('pattern')
                 .attr('id', 'diagonalHatch')
                 .attr('patternUnits', 'userSpaceOnUse')
                 .attr('width', 4)
                 .attr('height', 4)
               .append('path')
                 .attr('d', 'M-1,1 l2,-2 M0,4 l4,-4 M3,5 l2,-2')
                 .attr('stroke', '#000000')
                 .attr('stroke-width', 1);

        // When given a graph, remove all the elements from it
        function remove(graph) {
            for(var x in graph.nodes){
                for(var y in graph.nodes) {
                    d3.select("#UNIQUE_CANVAS_NAME").select("#"+graph.nodes[x].id+"_"+graph.nodes[y].id).remove();
                    if ((graph.nodes[x].configured=="no") || (graph.nodes[y].configured=="no")) {
                        d3.select("#UNIQUE_CANVAS_NAME").select("#"+graph.nodes[x].id+"_"+graph.nodes[y].id+"_unconfig").remove();
                    }                   
                }
            }

            for(var n in graph.nodes){
                    d3.select("#UNIQUE_CANVAS_NAME").select("#"+graph.nodes[n].id+"_x").remove();
                    d3.select("#UNIQUE_CANVAS_NAME").select("#"+graph.nodes[n].id+"_y").remove();
            }

            for(var l in graph.links) {
                d3.select("#UNIQUE_CANVAS_NAME").select("#"+graph.links[l].source+"_"+graph.links[l].target).remove();
            }
        }


        // When given a graph draw all the elements for it
        function draw(graph) {
            for(var x in graph.nodes) {
               for(var y in graph.nodes) {
                var lb = svg.append("rect")
                   .attr("id", graph.nodes[x].id+"_"+graph.nodes[y].id)
                   .attr("source_id", graph.nodes[x].id)
                   .attr("destination_id", graph.nodes[y].id)
                   .attr("x", matrix_offset +box_bound + x*(boxsize + box_bound/2))
                   .attr("y", matrix_offset + box_bound + y*(boxsize + box_bound/2))
                   .attr("height", boxsize)
                   .attr("width", boxsize)
                   .attr("linked", "no")
                   .style("opacity", 0.4)
                   .on("mouseover", function() {
                        var linked = (d3.select(this).attr("linked") == "yes");
                        if(linked) {
                            var x = parseInt(d3.select(this).attr("x"));
                            var y = parseInt(d3.select(this).attr("y"));
                            d3.select(this).attr("height", 2*boxsize).attr("width", 2*boxsize);
                            d3.select(this).attr("x", x - boxsize/2);
                            d3.select(this).attr("y", y - boxsize/2);

                            var src = d3.select(this).attr("source_id");
                            var dst = d3.select(this).attr("destination_id");

                            var keylist = ["Source: "+src, "Dest: "+dst];
                            var colourlist = ["none", "none"];
                            for(var l in graph.links) {
                                if(graph.links[l].source == src) {
                                    if(graph.links[l].target == dst) {
                                       keylist.push("("+graph.links[l].source_porttype+") "+graph.links[l].source_port + " -> "+graph.links[l].target_port);
                                       colourlist.push(colour(graph.links[l].source_porttype));
                                    }
                                }
                            }

                            ttip = new KeyToolTip(svg, x+20, y+20, keylist, colourlist);

                            d3.select("#UNIQUE_CANVAS_NAME").select("#"+dst+"_y").attr("font-weight", 700);
                            d3.select("#UNIQUE_CANVAS_NAME").select("#"+src+"_x").attr("font-weight", 700);
                        }
                   })
                   .on("mouseout", function() {
                        var linked = (d3.select(this).attr("linked") == "yes");
                        if(linked) {
                            var x = parseInt(d3.select(this).attr("x"));
                            var y = parseInt(d3.select(this).attr("y"));
                            d3.select(this).attr("height", boxsize).attr("width", boxsize);
                            d3.select(this).attr("x", x + boxsize/2);
                            d3.select(this).attr("y", y + boxsize/2);
                            d3.selectAll("#tooltip").remove();

                            var src = d3.select(this).attr("source_id");
                            var dst = d3.select(this).attr("destination_id");
                            d3.select("#UNIQUE_CANVAS_NAME").select("#"+dst+"_y").attr("font-weight", 300);
                            d3.select("#UNIQUE_CANVAS_NAME").select("#"+src+"_x").attr("font-weight", 300);
                        }
                   })
                   .attr("fill", "#F0F0F0");

                   // If we are an unconfigured block, overlay a hatchedblock
                   if ((graph.nodes[x].configured=="no") || (graph.nodes[y].configured=="no")) {
                        svg.append("rect")
                           .attr("id", graph.nodes[x].id+"_"+graph.nodes[y].id+"_unconfig")
                           .attr("x", matrix_offset +box_bound + x*(boxsize + box_bound/2))
                           .attr("y", matrix_offset + box_bound + y*(boxsize + box_bound/2))
                           .attr("height", boxsize)
                           .attr("width", boxsize)
                           .style("opacity", 0.4)
                           .attr("fill", "url(#diagonalHatch)");
                   }
               }
            }

            // Y - direction core labels
            for(var n in graph.nodes) {
                svg.append("text")
                   .attr("id", graph.nodes[n].id+"_y")
                   .attr("orig_id", graph.nodes[n].id)
                   .attr("x", matrix_offset)
                   .attr("y", matrix_offset + n*(boxsize + box_bound/2) + (boxsize + box_bound/2))
                   .attr("text-anchor", "end")
                   .attr("font-family", "sans-serif")
                   .on("mouseover", function() {
                        d3.select(this).attr("font-weight", 700);
                        for(var x in graph.nodes){
                           var this_id = d3.select(this).attr("orig_id");
                           var lb_linked = d3.select("#UNIQUE_CANVAS_NAME").select("#"+graph.nodes[x].id+"_"+this_id).attr("linked");
                           if (lb_linked == "no") {
                                d3.select("#UNIQUE_CANVAS_NAME").select("#"+graph.nodes[x].id+"_"+this_id).style("opacity", 0.2).attr("fill", "red");
                           } else {
                               d3.select("#UNIQUE_CANVAS_NAME").select("#"+graph.nodes[x].id+"_x").attr("fill", "red"); 
                           }
                        }
                   })
                   .on("mouseout", function() {
                        d3.select(this).attr("font-weight", 300);
                        for(var x in graph.nodes){
                           var this_id = d3.select(this).attr("orig_id");
                           var lb_linked = d3.select("#UNIQUE_CANVAS_NAME").select("#"+graph.nodes[x].id+"_"+this_id).attr("linked");
                           if (lb_linked == "no") {
                                d3.select("#UNIQUE_CANVAS_NAME").select("#"+graph.nodes[x].id+"_"+this_id).style("opacity", "0.4").attr("fill", "#F0F0F0");
                           } else {
                               d3.select("#UNIQUE_CANVAS_NAME").select("#"+graph.nodes[x].id+"_x").attr("fill", "black"); 
                           }
                        }
                   })
                   .style("font-size", "10px")
                   .text(graph.nodes[n].id);
            }

            // X - direction core labels
            for(var n in graph.nodes) {
                var x_pos = box_bound/2 + matrix_offset + n*(boxsize + box_bound/2) + (boxsize + box_bound/2)/2;
                var y_pos = box_bound/2 + matrix_offset;
                svg.append("text")
                   .attr("id", graph.nodes[n].id+"_x")
                   .attr("orig_id", graph.nodes[n].id)
                   .attr("text-anchor", "start")
                   .attr("font-family", "sans-serif")
                   .attr("dy", ".35em")
                   .attr("transform", "translate("+x_pos+","+y_pos+") rotate(-65)")
                   .attr("font-weight", 300)
                   .on("mouseover", function() {
                        d3.select(this).attr("font-weight", 700);
                        for(var y in graph.nodes){
                           var this_id = d3.select(this).attr("orig_id");
                           var lb_linked = d3.select("#UNIQUE_CANVAS_NAME").select("#"+this_id+"_"+graph.nodes[y].id).attr("linked");
                           if (lb_linked == "no") {
                                d3.select("#UNIQUE_CANVAS_NAME").select("#"+this_id+"_"+graph.nodes[y].id).style("opacity", 0.2).attr("fill", "red");
                           } else {
                               d3.select("#UNIQUE_CANVAS_NAME").select("#"+graph.nodes[y].id+"_y").attr("fill", "red"); 
                           }
                        }
                   })
                   .on("mouseout", function() {
                        d3.select(this).attr("font-weight", 300);
                        for(var y in graph.nodes){
                           var this_id = d3.select(this).attr("orig_id");
                           var lb_linked = d3.select("#UNIQUE_CANVAS_NAME").select("#"+this_id+"_"+graph.nodes[y].id).attr("linked");
                           if (lb_linked == "no") {
                                d3.select("#UNIQUE_CANVAS_NAME").select("#"+this_id+"_"+graph.nodes[y].id).style("opacity", 0.2).attr("fill", "#F0F0F0");
                           } else {
                               d3.select("#UNIQUE_CANVAS_NAME").select("#"+graph.nodes[y].id+"_y").attr("fill", "black"); 
                           }
                        }
                   })
                   .style("font-size", "10px")
                   .text(graph.nodes[n].id);
                
            }



            for(var l in graph.links) {
                d3.select("#UNIQUE_CANVAS_NAME").select("#"+graph.links[l].source+"_"+graph.links[l].target)
                  .style("opacity", 1.0)
                  .attr("linked", "yes")
                  .attr("fill", colour(graph.links[l].source_porttype));	

            }
        }

        // when given a graph and a core create a new graph showing port-level connectivity
        //function subgraph(g, src, dst) {
        //    var ngraph = {}
        //    ngraph['nodes'] = {}
        //    for( var l in g.links) {
        //    }
        //}


        draw(g);

        """

        self.body = self.body.replace("UNIQUE_CANVAS_NAME", self.canvas)

        super().__init__(['lib/d3.v4.min.js', 'lib/keytooltip.js'],body=self.body, canvas_name=self.canvas)
        self.render()
            
        


        
