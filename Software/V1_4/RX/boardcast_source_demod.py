#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: boardcast_source_demod
# Author: dfdtc
# Copyright: dfdtc
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio import analog
import math
from gnuradio import blocks
import pmt
from gnuradio import digital
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import zeromq
import boardcast_source_demod_epy_block_0 as epy_block_0  # embedded python block
import sip
import threading



class boardcast_source_demod(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "boardcast_source_demod", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("boardcast_source_demod")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "boardcast_source_demod")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)
        self.flowgraph_started = threading.Event()

        ##################################################
        # Variables
        ##################################################
        self.sps = sps = 52
        self.samp_rate = samp_rate = 1e6
        self.bw = bw = 0.820e6
        self.symb_rate = symb_rate = samp_rate/sps
        self.cent_freq = cent_freq = 433.2e6
        self.bfsk = bfsk = digital.constellation_calcdist([-1,1], [0, 1],
        1, 1, digital.constellation.AMPLITUDE_NORMALIZATION).base()
        self.bfsk.set_npwr(1.0)
        self.access_code = access_code = "0001011011101000110100110111011100010101000111000111000100101101"
        self.D = D = bw/2-samp_rate/sps

        ##################################################
        # Blocks
        ##################################################

        self.zeromq_pub_sink_0 = zeromq.pub_sink(gr.sizeof_char, 1, "tcp://127.0.0.1:5559", 100, False, 4096, '', True, True)
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
                interpolation=1,
                decimation=2,
                taps=[],
                fractional_bw=0)
        self.qtgui_time_sink_x_2_0_1 = qtgui.time_sink_f(
            2048, #size
            samp_rate, #samp_rate
            "Baseband", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_2_0_1.set_update_time(2)
        self.qtgui_time_sink_x_2_0_1.set_y_axis(-2, 2)

        self.qtgui_time_sink_x_2_0_1.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_2_0_1.enable_tags(True)
        self.qtgui_time_sink_x_2_0_1.set_trigger_mode(qtgui.TRIG_MODE_AUTO, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_2_0_1.enable_autoscale(False)
        self.qtgui_time_sink_x_2_0_1.enable_grid(True)
        self.qtgui_time_sink_x_2_0_1.enable_axis_labels(True)
        self.qtgui_time_sink_x_2_0_1.enable_control_panel(False)
        self.qtgui_time_sink_x_2_0_1.enable_stem_plot(False)


        labels = ['Signal 1', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_2_0_1.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_2_0_1.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_2_0_1.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_2_0_1.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_2_0_1.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_2_0_1.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_2_0_1.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_2_0_1_win = sip.wrapinstance(self.qtgui_time_sink_x_2_0_1.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_2_0_1_win)
        self.fir_filter_xxx_0_0 = filter.fir_filter_fff(1, firdes.gaussian(1.2, sps, 0.35, 60))
        self.fir_filter_xxx_0_0.declare_sample_delay(0)
        self.epy_block_0 = epy_block_0.blk(endpoint='tcp://127.0.0.1:5555', bind=False, rx_type='boardcast')
        self.digital_symbol_sync_xx_0 = digital.symbol_sync_ff(
            digital.TED_MOD_MUELLER_AND_MULLER,
            sps,
            0.046,
            1.0,
            0.85,
            1.5,
            1,
            bfsk,
            digital.IR_PFB_NO_MF,
            32,
            [])
        self.digital_correlate_access_code_xx_ts_0 = digital.correlate_access_code_bb_ts(access_code,
          3, 'pack_len')
        self.digital_binary_slicer_fb_0 = digital.binary_slicer_fb()
        self.blocks_throttle2_0 = blocks.throttle( gr.sizeof_gr_complex*1, (samp_rate*2), True, 0 if "auto" == "auto" else max( int(float(0.1) * (samp_rate*2)) if "auto" == "time" else int(0.1), 1) )
        self.blocks_pack_k_bits_bb_0 = blocks.pack_k_bits_bb(8)
        self.blocks_msgpair_to_var_1_0 = blocks.msg_pair_to_var(self.set_access_code)
        self.blocks_msgpair_to_var_1 = blocks.msg_pair_to_var(self.set_bw)
        self.blocks_msgpair_to_var_0 = blocks.msg_pair_to_var(self.set_cent_freq)
        self.blocks_file_source_0 = blocks.file_source(gr.sizeof_gr_complex*1, '/home/shuyusihan/下载/RX_BLUE_ganrao_1', False, 0, 0)
        self.blocks_file_source_0.set_begin_tag(pmt.PMT_NIL)
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_char*1, './test_decode.txt', False)
        self.blocks_file_sink_0.set_unbuffered(False)
        self.analog_quadrature_demod_cf_0_0_0 = analog.quadrature_demod_cf((samp_rate/(2*math.pi*D)))
        self.analog_agc_xx_1 = analog.agc_ff((1e-4), 1.0, 1.0, 65536)
        self.analog_agc_xx_0 = analog.agc_cc((1e-4), 1.0, 1.0, 4)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.epy_block_0, 'freq'), (self.blocks_msgpair_to_var_0, 'inpair'))
        self.msg_connect((self.epy_block_0, 'bw'), (self.blocks_msgpair_to_var_1, 'inpair'))
        self.msg_connect((self.epy_block_0, 'access_code'), (self.blocks_msgpair_to_var_1_0, 'inpair'))
        self.connect((self.analog_agc_xx_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.analog_agc_xx_1, 0), (self.digital_symbol_sync_xx_0, 0))
        self.connect((self.analog_quadrature_demod_cf_0_0_0, 0), (self.fir_filter_xxx_0_0, 0))
        self.connect((self.blocks_file_source_0, 0), (self.blocks_throttle2_0, 0))
        self.connect((self.blocks_pack_k_bits_bb_0, 0), (self.blocks_file_sink_0, 0))
        self.connect((self.blocks_pack_k_bits_bb_0, 0), (self.zeromq_pub_sink_0, 0))
        self.connect((self.blocks_throttle2_0, 0), (self.analog_agc_xx_0, 0))
        self.connect((self.digital_binary_slicer_fb_0, 0), (self.digital_correlate_access_code_xx_ts_0, 0))
        self.connect((self.digital_correlate_access_code_xx_ts_0, 0), (self.blocks_pack_k_bits_bb_0, 0))
        self.connect((self.digital_symbol_sync_xx_0, 0), (self.digital_binary_slicer_fb_0, 0))
        self.connect((self.fir_filter_xxx_0_0, 0), (self.analog_agc_xx_1, 0))
        self.connect((self.fir_filter_xxx_0_0, 0), (self.qtgui_time_sink_x_2_0_1, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.analog_quadrature_demod_cf_0_0_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "boardcast_source_demod")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_sps(self):
        return self.sps

    def set_sps(self, sps):
        self.sps = sps
        self.set_D(self.bw/2-self.samp_rate/self.sps)
        self.set_symb_rate(self.samp_rate/self.sps)
        self.digital_symbol_sync_xx_0.set_sps(self.sps)
        self.fir_filter_xxx_0_0.set_taps(firdes.gaussian(1.2, self.sps, 0.35, 60))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_D(self.bw/2-self.samp_rate/self.sps)
        self.set_symb_rate(self.samp_rate/self.sps)
        self.analog_quadrature_demod_cf_0_0_0.set_gain((self.samp_rate/(2*math.pi*self.D)))
        self.blocks_throttle2_0.set_sample_rate((self.samp_rate*2))
        self.qtgui_time_sink_x_2_0_1.set_samp_rate(self.samp_rate)

    def get_bw(self):
        return self.bw

    def set_bw(self, bw):
        self.bw = bw
        self.set_D(self.bw/2-self.samp_rate/self.sps)

    def get_symb_rate(self):
        return self.symb_rate

    def set_symb_rate(self, symb_rate):
        self.symb_rate = symb_rate

    def get_cent_freq(self):
        return self.cent_freq

    def set_cent_freq(self, cent_freq):
        self.cent_freq = cent_freq

    def get_bfsk(self):
        return self.bfsk

    def set_bfsk(self, bfsk):
        self.bfsk = bfsk

    def get_access_code(self):
        return self.access_code

    def set_access_code(self, access_code):
        self.access_code = access_code

    def get_D(self):
        return self.D

    def set_D(self, D):
        self.D = D
        self.analog_quadrature_demod_cf_0_0_0.set_gain((self.samp_rate/(2*math.pi*self.D)))




def main(top_block_cls=boardcast_source_demod, options=None):

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()
    tb.flowgraph_started.set()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
