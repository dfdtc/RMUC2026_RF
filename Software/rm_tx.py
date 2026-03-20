#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: rm_tx
# Author: dfdtc
# GNU Radio version: 3.10.12.0

from gnuradio import blocks
from gnuradio import digital
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import iio
import math
import threading




class rm_tx(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "rm_tx", catch_exceptions=True)
        self.flowgraph_started = threading.Event()

        ##################################################
        # Variables RRC参数，采样率和符号率什么的在这里改
        ##################################################
        self.symb_rate = symb_rate = 500e3
        self.sps = sps = 4
        self.samp_rate = samp_rate = 2e6
        self.inter = inter = 4
        self.alpha = alpha = 0.25
        self.D = D = symb_rate/4

        ##################################################
        # Blocks
        ##################################################

        self.root_raised_cosine_filter_0_0_0 = filter.interp_fir_filter_fff(
            sps,
            firdes.root_raised_cosine(
                sps,
                samp_rate,
                symb_rate,
                alpha,
                (11*sps)))
        self.iio_pluto_sink_0 = iio.fmcomms2_sink_fc32("192.168.2.1" if "192.168.2.1" else iio.get_pluto_uri(), [True, True], 32768, False)
        self.iio_pluto_sink_0.set_len_tag_key('')
        self.iio_pluto_sink_0.set_bandwidth(2000000)
        self.iio_pluto_sink_0.set_frequency(433000000)
        self.iio_pluto_sink_0.set_samplerate(2000000)
        self.iio_pluto_sink_0.set_attenuation(0, 0)
        self.iio_pluto_sink_0.set_filter_params('Auto', '', 500000, 900000)
        self.digital_map_bb_0 = digital.map_bb([-3,-1,1,3])
        self.blocks_vector_source_x_0 = blocks.vector_source_b((165, 0, 6, 0, 153, 10, 6, 65, 65, 65, 65, 65, 65, 189, 45), True, 1, [])
        self.blocks_vco_c_0 = blocks.vco_c(samp_rate, ((2*math.pi)*D), 1)
        self.blocks_stream_to_tagged_stream_0 = blocks.stream_to_tagged_stream(gr.sizeof_char, 1, 15, "packet_len")
        self.blocks_repack_bits_bb_1 = blocks.repack_bits_bb(8, 2, "packet_len", False, gr.GR_LSB_FIRST)
        self.blocks_char_to_float_0 = blocks.char_to_float(1, 1)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_char_to_float_0, 0), (self.root_raised_cosine_filter_0_0_0, 0))
        self.connect((self.blocks_repack_bits_bb_1, 0), (self.digital_map_bb_0, 0))
        self.connect((self.blocks_stream_to_tagged_stream_0, 0), (self.blocks_repack_bits_bb_1, 0))
        self.connect((self.blocks_vco_c_0, 0), (self.iio_pluto_sink_0, 0))
        self.connect((self.blocks_vector_source_x_0, 0), (self.blocks_stream_to_tagged_stream_0, 0))
        self.connect((self.digital_map_bb_0, 0), (self.blocks_char_to_float_0, 0))
        self.connect((self.root_raised_cosine_filter_0_0_0, 0), (self.blocks_vco_c_0, 0))


    def get_symb_rate(self):
        return self.symb_rate

    def set_symb_rate(self, symb_rate):
        self.symb_rate = symb_rate
        self.set_D(self.symb_rate/4)
        self.root_raised_cosine_filter_0_0_0.set_taps(firdes.root_raised_cosine(self.sps, self.samp_rate, self.symb_rate, self.alpha, (11*self.sps)))

    def get_sps(self):
        return self.sps

    def set_sps(self, sps):
        self.sps = sps
        self.root_raised_cosine_filter_0_0_0.set_taps(firdes.root_raised_cosine(self.sps, self.samp_rate, self.symb_rate, self.alpha, (11*self.sps)))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.root_raised_cosine_filter_0_0_0.set_taps(firdes.root_raised_cosine(self.sps, self.samp_rate, self.symb_rate, self.alpha, (11*self.sps)))

    def get_inter(self):
        return self.inter

    def set_inter(self, inter):
        self.inter = inter

    def get_alpha(self):
        return self.alpha

    def set_alpha(self, alpha):
        self.alpha = alpha
        self.root_raised_cosine_filter_0_0_0.set_taps(firdes.root_raised_cosine(self.sps, self.samp_rate, self.symb_rate, self.alpha, (11*self.sps)))

    def get_D(self):
        return self.D

    def set_D(self, D):
        self.D = D




def main(top_block_cls=rm_tx, options=None):
    tb = top_block_cls()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()
    tb.flowgraph_started.set()

    try:
        input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
