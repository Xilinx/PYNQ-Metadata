// Copyright (C) 2022 Xilinx, Inc
// SPDX-License-Identifier: BSD-3-Clause

// Creates a small tool tip for mousing over an item
// It is passed a list of text items, each item can be given a
// colour for keying items in the visualisation
// author: stf

class KeyToolTip {
	constructor(svg, x, y, textlist, colourlist) {
		this.svg = svg
		this.x = x
		this.y = y

		this.max_len = 0;
		for(var i in textlist){
			if (textlist[i].length > this.max_len) {
				this.max_len = textlist[i].length;
			}
		}

		this.svg.append("rect")
			.attr("id", "tooltip")
			.attr("x", this.x-10)
			.attr("y", this.y-17)
			.attr("width", this.max_len*8 + 30)
			.attr("height", 14*(textlist.length+1) + 5)
			.attr("stroke", "grey")
			.attr("stroke-width", 1)
			.attr("fill", "white");

		for(var i in textlist) {

			if (colourlist[i] != "none") {
				this.svg.append("rect")
					.attr("id", "tooltip")
					.attr("x", this.x + 4)
					.attr("y", this.y + 14*i - 5)
					.attr("width", 7)
					.attr("height", 7)
					.attr("fill", colourlist[i])
					.attr("stroke", "none");
			}

			this.svg.append("text")
				.attr("id", "tooltip") // We only ever want one
				.attr("x", this.x + 30)
				.attr("y", this.y + 14*i)
				.attr("text-anchor", "left")
				.text(textlist[i]);
		}
	}
}
