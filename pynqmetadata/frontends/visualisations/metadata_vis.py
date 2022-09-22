# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

from IPython.display import display, Javascript, HTML
from typing import List
import random
import string

import os
PROJECT_DIR = os.path.dirname(__file__)

class MetadataVis:
    """
    Base class used to help with creating visualisations of the
    Metadata objects (and views onto Metadata objects) 
    """

    def __init__(self, js_files:List[str]=[], body:str="", canvas_name:str="")->None:
        """
        Creates a display for a canvas with a given name.
        * A canvas can be updated at a later date using the name
        (canvas_name) as a reference. If no name is given then a 
        unique canvas is created for the object.
        * A list of javascript files is provided js_files that get
        loaded before the rendering.
        * Some javascript is given in body that loads the visualisation 
        """
        self.js_files = js_files 
        self._load_js_files()
        if canvas_name == "":
            letters = string.ascii_lowercase
            self.canvas_name = ''.join(random.choice(letters) for i in range(8)) 
        else:
            self.canvas_name = canvas_name
        self.body = body 
        self.style = ""

    def _repr_html_(self)->None:
        html = "<div id=\""+self.canvas_name+"\"></div>\n"
        html += "<style>\n"
        html += self.style
        html += "</style>\n"
        html += "<script>\n"
        html += self.body
        html += "\n</script>\n"
        return html

    def _read_js_file(self, filepath:str)->None:
        """
        Returns the string for a file for renderings the visualisation
        """
        fp = open(PROJECT_DIR+"/"+filepath)
        fp_str = fp.read()
        fp.close()
        return fp_str

    def _load_js_files(self)->None:
        for js in self.js_files:
            display(HTML("<script> "+self._read_js_file(js) + "</script>"))

    def render(self)->None:
        """
        Renders the visualisation
        """
        display(self) 

