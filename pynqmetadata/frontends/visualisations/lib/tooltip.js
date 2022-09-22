# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

// Creates a small tool tip for mousing over an item

class ToolTip {
	constructor(svg, x, y, text) {
		this.svg = svg
		this.x = x
		this.y = y

		this.svg.append("rect")
			.attr("id", "tooltip")
			.attr("x", this.x-10)
			.attr("y", this.y-17)
			.attr("width", text.length*8)
			.attr("height", 25)
			.attr("stroke", "grey")
			.attr("stroke-width", 1)
			.attr("fill", "white");

		this.svg.append("text")
			.attr("id", "tooltip") // We only ever want one
			.attr("x", this.x)
			.attr("y", this.y)
			.attr("text-anchor", "left")
			.text(text);
	}
}
