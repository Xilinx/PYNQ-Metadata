# Copyright (C) 2022 Xilinx, Inc
# SPDX-License-Identifier: BSD-3-Clause

import os

from pynqmetadata import Module
from pynqmetadata.frontends import Metadata

TEST_DIR = os.path.dirname(__file__)


def test_bus_level_connectivity():
    """
    tests to make sure that at a module level we can see bus-level connections
    """
    md = Metadata(f"{TEST_DIR}/hwhs/resizer.hwh")
    md.refresh()
    assert "resizer:axi_dma_0[block]:S_AXI_LITE[port]->resizer:axi_interconnect_0[block]:M00_AXI[port]" in md.busses
    assert "resizer:axi_dma_0[block]:M_AXI_MM2S[port]->resizer:axi_interconnect_1[block]:S00_AXI[port]" in md.busses
    assert "resizer:axi_dma_0[block]:M_AXI_S2MM[port]->resizer:axi_interconnect_1[block]:S01_AXI[port]" in md.busses
    assert "resizer:axi_dma_0[block]:M_AXIS_MM2S[port]->resizer:axis_dwidth_converter_0[block]:S_AXIS[port]" in md.busses
    assert "resizer:axi_dma_0[block]:S_AXIS_S2MM[port]->resizer:axis_dwidth_converter_1[block]:M_AXIS[port]" in md.busses
    assert "resizer:axi_dma_0[block]:s_axi_lite_aclk[port]->resizer:processing_system7_0[block]:FCLK_CLK0[port]" in md.busses
    assert "resizer:axi_dma_0[block]:m_axi_mm2s_aclk[port]->resizer:processing_system7_0[block]:FCLK_CLK0[port]" in md.busses
    assert "resizer:axi_dma_0[block]:m_axi_s2mm_aclk[port]->resizer:processing_system7_0[block]:FCLK_CLK0[port]" in md.busses
    assert "resizer:axi_dma_0[block]:axi_resetn[port]->resizer:rst_ps7_0_100M[block]:peripheral_aresetn[port]" in md.busses
    assert "resizer:axi_interconnect_0[block]:S00_AXI[port]->resizer:processing_system7_0[block]:M_AXI_GP0[port]" in md.busses
    assert "resizer:axi_interconnect_0[block]:M00_AXI[port]->resizer:axi_dma_0[block]:S_AXI_LITE[port]" in md.busses
    assert "resizer:axi_interconnect_0[block]:M01_AXI[port]->resizer:resize_accel_0[block]:s_axi_AXILiteS[port]" in md.busses
    assert "resizer:axi_interconnect_0[block]:ACLK[port]->resizer:processing_system7_0[block]:FCLK_CLK0[port]" in md.busses
    assert "resizer:axi_interconnect_0[block]:ARESETN[port]->resizer:rst_ps7_0_100M[block]:interconnect_aresetn[port]" in md.busses
    assert "resizer:axi_interconnect_0[block]:S00_ACLK[port]->resizer:processing_system7_0[block]:FCLK_CLK0[port]" in md.busses
    assert "resizer:axi_interconnect_0[block]:S00_ARESETN[port]->resizer:rst_ps7_0_100M[block]:peripheral_aresetn[port]" in md.busses
    assert "resizer:axi_interconnect_0[block]:M00_ACLK[port]->resizer:processing_system7_0[block]:FCLK_CLK0[port]" in md.busses
    assert "resizer:axi_interconnect_0[block]:M00_ARESETN[port]->resizer:rst_ps7_0_100M[block]:peripheral_aresetn[port]" in md.busses
    assert "resizer:axi_interconnect_0[block]:M01_ACLK[port]->resizer:processing_system7_0[block]:FCLK_CLK0[port]" in md.busses
    assert "resizer:axi_interconnect_0[block]:M01_ARESETN[port]->resizer:rst_ps7_0_100M[block]:peripheral_aresetn[port]" in md.busses
    assert "resizer:axi_interconnect_1[block]:S00_AXI[port]->resizer:axi_dma_0[block]:M_AXI_MM2S[port]" in md.busses
    assert "resizer:axi_interconnect_1[block]:M00_AXI[port]->resizer:processing_system7_0[block]:S_AXI_HP0[port]" in md.busses
    assert "resizer:axi_interconnect_1[block]:S01_AXI[port]->resizer:axi_dma_0[block]:M_AXI_S2MM[port]" in md.busses
    assert "resizer:axi_interconnect_1[block]:ACLK[port]->resizer:processing_system7_0[block]:FCLK_CLK0[port]" in md.busses
    assert "resizer:axi_interconnect_1[block]:ARESETN[port]->resizer:rst_ps7_0_100M[block]:interconnect_aresetn[port]" in md.busses
    assert "resizer:axi_interconnect_1[block]:S00_ACLK[port]->resizer:processing_system7_0[block]:FCLK_CLK0[port]" in md.busses
    assert "resizer:axi_interconnect_1[block]:S00_ARESETN[port]->resizer:rst_ps7_0_100M[block]:peripheral_aresetn[port]" in md.busses
    assert "resizer:axi_interconnect_1[block]:M00_ACLK[port]->resizer:processing_system7_0[block]:FCLK_CLK0[port]" in md.busses
    assert "resizer:axi_interconnect_1[block]:M00_ARESETN[port]->resizer:rst_ps7_0_100M[block]:peripheral_aresetn[port]" in md.busses
    assert "resizer:axi_interconnect_1[block]:S01_ACLK[port]->resizer:processing_system7_0[block]:FCLK_CLK0[port]" in md.busses
    assert "resizer:axi_interconnect_1[block]:S01_ARESETN[port]->resizer:rst_ps7_0_100M[block]:peripheral_aresetn[port]" in md.busses
    assert "resizer:axis_dwidth_converter_0[block]:S_AXIS[port]->resizer:axi_dma_0[block]:M_AXIS_MM2S[port]" in md.busses
    assert "resizer:axis_dwidth_converter_0[block]:M_AXIS[port]->resizer:resize_accel_0[block]:src[port]" in md.busses
    assert "resizer:axis_dwidth_converter_0[block]:aclk[port]->resizer:processing_system7_0[block]:FCLK_CLK0[port]" in md.busses
    assert "resizer:axis_dwidth_converter_0[block]:aresetn[port]->resizer:rst_ps7_0_100M[block]:interconnect_aresetn[port]" in md.busses
    assert "resizer:axis_dwidth_converter_1[block]:S_AXIS[port]->resizer:resize_accel_0[block]:dst[port]" in md.busses
    assert "resizer:axis_dwidth_converter_1[block]:M_AXIS[port]->resizer:axi_dma_0[block]:S_AXIS_S2MM[port]" in md.busses
    assert "resizer:axis_dwidth_converter_1[block]:aclk[port]->resizer:processing_system7_0[block]:FCLK_CLK0[port]" in md.busses
    assert "resizer:axis_dwidth_converter_1[block]:aresetn[port]->resizer:rst_ps7_0_100M[block]:interconnect_aresetn[port]" in md.busses
    assert "resizer:processing_system7_0[block]:M_AXI_GP0[port]->resizer:axi_interconnect_0[block]:S00_AXI[port]" in md.busses
    assert "resizer:processing_system7_0[block]:S_AXI_HP0[port]->resizer:axi_interconnect_1[block]:M00_AXI[port]" in md.busses
    assert "resizer:processing_system7_0[block]:M_AXI_GP0_ACLK[port]->resizer:processing_system7_0[block]:FCLK_CLK0[port]" in md.busses
    assert "resizer:processing_system7_0[block]:S_AXI_HP0_ACLK[port]->resizer:processing_system7_0[block]:FCLK_CLK0[port]" in md.busses
    assert "resizer:processing_system7_0[block]:FCLK_CLK0[port]->resizer:axi_dma_0[block]:m_axi_mm2s_aclk[port]" in md.busses
    assert "resizer:processing_system7_0[block]:FCLK_CLK0[port]->resizer:axi_dma_0[block]:m_axi_s2mm_aclk[port]" in md.busses
    assert "resizer:processing_system7_0[block]:FCLK_CLK0[port]->resizer:axi_dma_0[block]:s_axi_lite_aclk[port]" in md.busses
    assert "resizer:processing_system7_0[block]:FCLK_CLK0[port]->resizer:axi_interconnect_0[block]:ACLK[port]" in md.busses
    assert "resizer:processing_system7_0[block]:FCLK_CLK0[port]->resizer:axi_interconnect_0[block]:M00_ACLK[port]" in md.busses
    assert "resizer:processing_system7_0[block]:FCLK_CLK0[port]->resizer:axi_interconnect_0[block]:M01_ACLK[port]" in md.busses
    assert "resizer:processing_system7_0[block]:FCLK_CLK0[port]->resizer:axi_interconnect_0[block]:S00_ACLK[port]" in md.busses
    assert "resizer:processing_system7_0[block]:FCLK_CLK0[port]->resizer:axi_interconnect_1[block]:S01_ACLK[port]" in md.busses
    assert "resizer:processing_system7_0[block]:FCLK_CLK0[port]->resizer:axis_dwidth_converter_0[block]:aclk[port]" in md.busses
    assert "resizer:processing_system7_0[block]:FCLK_CLK0[port]->resizer:processing_system7_0[block]:M_AXI_GP0_ACLK[port]" in md.busses
    assert "resizer:processing_system7_0[block]:FCLK_CLK0[port]->resizer:processing_system7_0[block]:S_AXI_HP0_ACLK[port]" in md.busses
    assert "resizer:processing_system7_0[block]:FCLK_CLK0[port]->resizer:resize_accel_0[block]:ap_clk[port]" in md.busses
    assert "resizer:processing_system7_0[block]:FCLK_CLK0[port]->resizer:rst_ps7_0_100M[block]:slowest_sync_clk[port]" in md.busses
    assert "resizer:processing_system7_0[block]:FCLK_RESET0_N[port]->resizer:rst_ps7_0_100M[block]:ext_reset_in[port]" in md.busses
    assert "resizer:resize_accel_0[block]:s_axi_AXILiteS[port]->resizer:axi_interconnect_0[block]:M01_AXI[port]" in md.busses
    assert "resizer:resize_accel_0[block]:src[port]->resizer:axis_dwidth_converter_0[block]:M_AXIS[port]" in md.busses
    assert "resizer:resize_accel_0[block]:dst[port]->resizer:axis_dwidth_converter_1[block]:S_AXIS[port]" in md.busses
    assert "resizer:resize_accel_0[block]:ap_clk[port]->resizer:processing_system7_0[block]:FCLK_CLK0[port]" in md.busses
    assert "resizer:resize_accel_0[block]:ap_rst_n[port]->resizer:rst_ps7_0_100M[block]:peripheral_aresetn[port]" in md.busses
    assert "resizer:rst_ps7_0_100M[block]:slowest_sync_clk[port]->resizer:processing_system7_0[block]:FCLK_CLK0[port]" in md.busses
    assert "resizer:rst_ps7_0_100M[block]:ext_reset_in[port]->resizer:processing_system7_0[block]:FCLK_RESET0_N[port]" in md.busses
    assert "resizer:rst_ps7_0_100M[block]:interconnect_aresetn[port]->resizer:axi_interconnect_0[block]:ARESETN[port]" in md.busses
    assert "resizer:rst_ps7_0_100M[block]:interconnect_aresetn[port]->resizer:axis_dwidth_converter_0[block]:aresetn[port]" in md.busses
    assert "resizer:rst_ps7_0_100M[block]:peripheral_aresetn[port]->resizer:axi_dma_0[block]:axi_resetn[port]" in md.busses
    assert "resizer:rst_ps7_0_100M[block]:peripheral_aresetn[port]->resizer:axi_interconnect_0[block]:M00_ARESETN[port]" in md.busses
    assert "resizer:rst_ps7_0_100M[block]:peripheral_aresetn[port]->resizer:axi_interconnect_0[block]:M01_ARESETN[port]" in md.busses
    assert "resizer:rst_ps7_0_100M[block]:peripheral_aresetn[port]->resizer:axi_interconnect_0[block]:S00_ARESETN[port]" in md.busses
    assert "resizer:rst_ps7_0_100M[block]:peripheral_aresetn[port]->resizer:axi_interconnect_1[block]:S01_ARESETN[port]" in md.busses
    assert "resizer:rst_ps7_0_100M[block]:peripheral_aresetn[port]->resizer:resize_accel_0[block]:ap_rst_n[port]" in md.busses
