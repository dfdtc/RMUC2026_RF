#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: gfsk_tx
# Author: dfdtc
# Copyright: dfdtc
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio import blocks
from gnuradio import digital
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import iio
import gfsk_tx_epy_block_0 as epy_block_0  # embedded python block
import gfsk_tx_epy_block_0_0 as epy_block_0_0  # embedded python block
import threading



class gfsk_tx(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "gfsk_tx", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("gfsk_tx")
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

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "gfsk_tx")

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
        self.rmuc_inter_format_0 = rmuc_inter_format_0 = digital.header_format_default("0010111101101111010011000111010010111001000101000100100100101110",4, 1)
        self.rmuc_inter_format = rmuc_inter_format = digital.header_format_default("0001011011101000110100110111011100010101000111000111000100101101",4, 1)
        self.cent_freq = cent_freq = 433.2e6
        self.access_code = access_code = "0001011011101000110100110111011100010101000111000111000100101101"
        self.D = D = bw/2-samp_rate/sps

        ##################################################
        # Blocks
        ##################################################

        self.iio_pluto_sink_0 = iio.fmcomms2_sink_fc32('' if '' else iio.get_pluto_uri(), [True, True], 32768, False)
        self.iio_pluto_sink_0.set_len_tag_key('')
        self.iio_pluto_sink_0.set_bandwidth(int(bw))
        self.iio_pluto_sink_0.set_frequency(int(cent_freq))
        self.iio_pluto_sink_0.set_samplerate(int(samp_rate))
        self.iio_pluto_sink_0.set_attenuation(0, 10.0)
        self.iio_pluto_sink_0.set_filter_params('Auto', '', 0, 0)
        self.epy_block_0_0 = epy_block_0_0.blk(endpoint='tcp://127.0.0.1:5555', bind=False, rx_type='inter')
        self.epy_block_0 = epy_block_0.byte_vector_source(sample_rate=1e6, payload=None, cmd_option="jamming", seq=3, chunk_bits=1, pad_mode='pad', mode='local', rand_pad=True, push_freq=10)
        self.digital_protocol_formatter_bb_0 = digital.protocol_formatter_bb(rmuc_inter_format, "packet_len")
        self.digital_gfsk_mod_0 = digital.gfsk_mod(
            samples_per_symbol=sps,
            sensitivity=(2*3.14*D/samp_rate),
            bt=0.35,
            verbose=False,
            log=False,
            do_unpack=True)
        self.blocks_tagged_stream_mux_0 = blocks.tagged_stream_mux(gr.sizeof_char*1, "packet_len", 0)
        self.blocks_msgpair_to_var_1_0 = blocks.msg_pair_to_var(self.set_access_code)
        self.blocks_msgpair_to_var_1 = blocks.msg_pair_to_var(self.set_bw)
        self.blocks_msgpair_to_var_0 = blocks.msg_pair_to_var(self.set_cent_freq)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.epy_block_0_0, 'freq'), (self.blocks_msgpair_to_var_0, 'inpair'))
        self.msg_connect((self.epy_block_0_0, 'bw'), (self.blocks_msgpair_to_var_1, 'inpair'))
        self.msg_connect((self.epy_block_0_0, 'access_code'), (self.blocks_msgpair_to_var_1_0, 'inpair'))
        self.connect((self.blocks_tagged_stream_mux_0, 0), (self.digital_gfsk_mod_0, 0))
        self.connect((self.digital_gfsk_mod_0, 0), (self.iio_pluto_sink_0, 0))
        self.connect((self.digital_protocol_formatter_bb_0, 0), (self.blocks_tagged_stream_mux_0, 0))
        self.connect((self.epy_block_0, 0), (self.blocks_tagged_stream_mux_0, 1))
        self.connect((self.epy_block_0, 0), (self.digital_protocol_formatter_bb_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "gfsk_tx")
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

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_D(self.bw/2-self.samp_rate/self.sps)
        self.set_symb_rate(self.samp_rate/self.sps)
        self.iio_pluto_sink_0.set_samplerate(int(self.samp_rate))

    def get_bw(self):
        return self.bw

    def set_bw(self, bw):
        self.bw = bw
        self.set_D(self.bw/2-self.samp_rate/self.sps)
        self.iio_pluto_sink_0.set_bandwidth(int(self.bw))

    def get_symb_rate(self):
        return self.symb_rate

    def set_symb_rate(self, symb_rate):
        self.symb_rate = symb_rate

    def get_rmuc_inter_format_0(self):
        return self.rmuc_inter_format_0

    def set_rmuc_inter_format_0(self, rmuc_inter_format_0):
        self.rmuc_inter_format_0 = rmuc_inter_format_0

    def get_rmuc_inter_format(self):
        return self.rmuc_inter_format

    def set_rmuc_inter_format(self, rmuc_inter_format):
        self.rmuc_inter_format = rmuc_inter_format
        self.digital_protocol_formatter_bb_0.set_header_format(self.rmuc_inter_format)

    def get_cent_freq(self):
        return self.cent_freq

    def set_cent_freq(self, cent_freq):
        self.cent_freq = cent_freq
        self.iio_pluto_sink_0.set_frequency(int(self.cent_freq))

    def get_access_code(self):
        return self.access_code

    def set_access_code(self, access_code):
        self.access_code = access_code

    def get_D(self):
        return self.D

    def set_D(self, D):
        self.D = D




def main(top_block_cls=gfsk_tx, options=None):

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
