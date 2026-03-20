#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: rm_test
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
from gnuradio import analog
import math
from gnuradio import blocks
import numpy
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
import sip
import threading



class rm_test(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "rm_test", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("rm_test")
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

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "rm_test")

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
        self.symb_rate = symb_rate = 500e3
        self.samp_rate = samp_rate = 2e6
        self.pam4 = pam4 = digital.constellation_calcdist([-3,-1,1,3], [0, 1, 2,3],
        1, 1, digital.constellation.POWER_NORMALIZATION).base()
        self.pam4.set_npwr(1.0)
        self.noise_level = noise_level = 0.1
        self.gain = gain = 0.6
        self.bw = bw = 0.01
        self.D = D = symb_rate/4

        ##################################################
        # Blocks
        ##################################################

        self._noise_level_range = qtgui.Range(0, 4, 0.01, 0.1, 200)
        self._noise_level_win = qtgui.RangeWidget(self._noise_level_range, self.set_noise_level, "noise_level", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._noise_level_win)
        self._gain_range = qtgui.Range(0, 1, 0.01, 0.6, 200)
        self._gain_win = qtgui.RangeWidget(self._gain_range, self.set_gain, "gain", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._gain_win)
        self._bw_range = qtgui.Range(0, 1, 0.01, 0.01, 200)
        self._bw_win = qtgui.RangeWidget(self._bw_range, self.set_bw, "bw", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._bw_win)
        self.root_raised_cosine_filter_0_0_0 = filter.interp_fir_filter_fff(
            4,
            firdes.root_raised_cosine(
                4,
                samp_rate,
                500e3,
                0.250,
                (11*4)))
        self.root_raised_cosine_filter_0 = filter.fir_filter_fff(
            1,
            firdes.root_raised_cosine(
                1,
                samp_rate,
                500e3,
                0.25,
                (11*4)))
        self.qtgui_time_sink_x_3 = qtgui.time_sink_f(
            256, #size
            samp_rate, #samp_rate
            "", #name
            2, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_3.set_update_time(0.10)
        self.qtgui_time_sink_x_3.set_y_axis(-5, 5)

        self.qtgui_time_sink_x_3.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_3.enable_tags(True)
        self.qtgui_time_sink_x_3.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_3.enable_autoscale(False)
        self.qtgui_time_sink_x_3.enable_grid(False)
        self.qtgui_time_sink_x_3.enable_axis_labels(True)
        self.qtgui_time_sink_x_3.enable_control_panel(False)
        self.qtgui_time_sink_x_3.enable_stem_plot(False)


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


        for i in range(2):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_3.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_3.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_3.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_3.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_3.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_3.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_3.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_3_win = sip.wrapinstance(self.qtgui_time_sink_x_3.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_3_win)
        self.qtgui_time_sink_x_2_1_1 = qtgui.time_sink_f(
            512, #size
            samp_rate, #samp_rate
            "out base", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_2_1_1.set_update_time(5)
        self.qtgui_time_sink_x_2_1_1.set_y_axis(-5, 5)

        self.qtgui_time_sink_x_2_1_1.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_2_1_1.enable_tags(True)
        self.qtgui_time_sink_x_2_1_1.set_trigger_mode(qtgui.TRIG_MODE_NORM, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_2_1_1.enable_autoscale(False)
        self.qtgui_time_sink_x_2_1_1.enable_grid(True)
        self.qtgui_time_sink_x_2_1_1.enable_axis_labels(True)
        self.qtgui_time_sink_x_2_1_1.enable_control_panel(False)
        self.qtgui_time_sink_x_2_1_1.enable_stem_plot(False)


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
                self.qtgui_time_sink_x_2_1_1.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_2_1_1.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_2_1_1.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_2_1_1.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_2_1_1.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_2_1_1.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_2_1_1.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_2_1_1_win = sip.wrapinstance(self.qtgui_time_sink_x_2_1_1.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_2_1_1_win)
        self.qtgui_time_sink_x_0 = qtgui.time_sink_f(
            384, #size
            samp_rate, #samp_rate
            "org", #name
            2, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_0.set_update_time(10)
        self.qtgui_time_sink_x_0.set_y_axis(-4, 4)

        self.qtgui_time_sink_x_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0.enable_tags(True)
        self.qtgui_time_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0.enable_autoscale(False)
        self.qtgui_time_sink_x_0.enable_grid(False)
        self.qtgui_time_sink_x_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0.enable_control_panel(False)
        self.qtgui_time_sink_x_0.enable_stem_plot(False)


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


        for i in range(2):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_0_win)
        self.digital_symbol_sync_xx_0 = digital.symbol_sync_ff(
            digital.TED_MUELLER_AND_MULLER,
            4,
            bw,
            1,
            gain,
            1.5,
            1,
            pam4,
            digital.IR_PFB_NO_MF,
            128,
            [])
        self.digital_map_bb_0 = digital.map_bb([-3,-1,1,3])
        self.blocks_vco_c_0 = blocks.vco_c(samp_rate, ((2*math.pi)*D), 1)
        self.blocks_throttle2_0 = blocks.throttle( gr.sizeof_gr_complex*1, samp_rate, True, 0 if "auto" == "auto" else max( int(float(0.1) * samp_rate) if "auto" == "time" else int(0.1), 1) )
        self.blocks_stream_to_tagged_stream_0 = blocks.stream_to_tagged_stream(gr.sizeof_char, 1, 15, "packet_len")
        self.blocks_repeat_0 = blocks.repeat(gr.sizeof_float*1, 4)
        self.blocks_repack_bits_bb_1 = blocks.repack_bits_bb(8, 2, "packet_len", False, gr.GR_MSB_FIRST)
        self.blocks_multiply_xx_2 = blocks.multiply_vcc(1)
        self.blocks_multiply_const_vxx_1 = blocks.multiply_const_ff(0.8)
        self.blocks_freqshift_cc_0_0 = blocks.rotator_cc(2.0*math.pi*(-433000000)/samp_rate)
        self.blocks_delay_1 = blocks.delay(gr.sizeof_float*1, 5)
        self.blocks_char_to_float_0 = blocks.char_to_float(1, 1)
        self.blocks_add_xx_0_0_0 = blocks.add_vcc(1)
        self.analog_simple_squelch_cc_0 = analog.simple_squelch_cc((-70), 1)
        self.analog_sig_source_x_1_0 = analog.sig_source_c(samp_rate, analog.GR_SIN_WAVE, 433000000, 5, 0, 0)
        self.analog_random_source_x_0 = blocks.vector_source_b(list(map(int, numpy.random.randint(0, 255, 1000))), True)
        self.analog_quadrature_demod_cf_0 = analog.quadrature_demod_cf((samp_rate/(2*math.pi*D)))
        self.analog_noise_source_x_0_0 = analog.noise_source_c(analog.GR_GAUSSIAN, noise_level, 0)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_noise_source_x_0_0, 0), (self.blocks_add_xx_0_0_0, 0))
        self.connect((self.analog_quadrature_demod_cf_0, 0), (self.blocks_multiply_const_vxx_1, 0))
        self.connect((self.analog_random_source_x_0, 0), (self.blocks_stream_to_tagged_stream_0, 0))
        self.connect((self.analog_sig_source_x_1_0, 0), (self.blocks_multiply_xx_2, 1))
        self.connect((self.analog_simple_squelch_cc_0, 0), (self.analog_quadrature_demod_cf_0, 0))
        self.connect((self.blocks_add_xx_0_0_0, 0), (self.blocks_freqshift_cc_0_0, 0))
        self.connect((self.blocks_char_to_float_0, 0), (self.blocks_delay_1, 0))
        self.connect((self.blocks_char_to_float_0, 0), (self.root_raised_cosine_filter_0_0_0, 0))
        self.connect((self.blocks_delay_1, 0), (self.blocks_repeat_0, 0))
        self.connect((self.blocks_freqshift_cc_0_0, 0), (self.analog_simple_squelch_cc_0, 0))
        self.connect((self.blocks_multiply_const_vxx_1, 0), (self.qtgui_time_sink_x_2_1_1, 0))
        self.connect((self.blocks_multiply_const_vxx_1, 0), (self.root_raised_cosine_filter_0, 0))
        self.connect((self.blocks_multiply_xx_2, 0), (self.blocks_add_xx_0_0_0, 1))
        self.connect((self.blocks_repack_bits_bb_1, 0), (self.digital_map_bb_0, 0))
        self.connect((self.blocks_repeat_0, 0), (self.qtgui_time_sink_x_0, 1))
        self.connect((self.blocks_stream_to_tagged_stream_0, 0), (self.blocks_repack_bits_bb_1, 0))
        self.connect((self.blocks_throttle2_0, 0), (self.blocks_multiply_xx_2, 0))
        self.connect((self.blocks_vco_c_0, 0), (self.blocks_throttle2_0, 0))
        self.connect((self.digital_map_bb_0, 0), (self.blocks_char_to_float_0, 0))
        self.connect((self.digital_symbol_sync_xx_0, 1), (self.qtgui_time_sink_x_3, 1))
        self.connect((self.digital_symbol_sync_xx_0, 0), (self.qtgui_time_sink_x_3, 0))
        self.connect((self.root_raised_cosine_filter_0, 0), (self.digital_symbol_sync_xx_0, 0))
        self.connect((self.root_raised_cosine_filter_0_0_0, 0), (self.blocks_vco_c_0, 0))
        self.connect((self.root_raised_cosine_filter_0_0_0, 0), (self.qtgui_time_sink_x_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "rm_test")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_symb_rate(self):
        return self.symb_rate

    def set_symb_rate(self, symb_rate):
        self.symb_rate = symb_rate
        self.set_D(self.symb_rate/4)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.analog_quadrature_demod_cf_0.set_gain((self.samp_rate/(2*math.pi*self.D)))
        self.analog_sig_source_x_1_0.set_sampling_freq(self.samp_rate)
        self.blocks_freqshift_cc_0_0.set_phase_inc(2.0*math.pi*(-433000000)/self.samp_rate)
        self.blocks_throttle2_0.set_sample_rate(self.samp_rate)
        self.qtgui_time_sink_x_0.set_samp_rate(self.samp_rate)
        self.qtgui_time_sink_x_2_1_1.set_samp_rate(self.samp_rate)
        self.qtgui_time_sink_x_3.set_samp_rate(self.samp_rate)
        self.root_raised_cosine_filter_0.set_taps(firdes.root_raised_cosine(1, self.samp_rate, 500e3, 0.25, (11*4)))
        self.root_raised_cosine_filter_0_0_0.set_taps(firdes.root_raised_cosine(4, self.samp_rate, 500e3, 0.250, (11*4)))

    def get_pam4(self):
        return self.pam4

    def set_pam4(self, pam4):
        self.pam4 = pam4

    def get_noise_level(self):
        return self.noise_level

    def set_noise_level(self, noise_level):
        self.noise_level = noise_level
        self.analog_noise_source_x_0_0.set_amplitude(self.noise_level)

    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain
        self.digital_symbol_sync_xx_0.set_ted_gain(self.gain)

    def get_bw(self):
        return self.bw

    def set_bw(self, bw):
        self.bw = bw
        self.digital_symbol_sync_xx_0.set_loop_bandwidth(self.bw)

    def get_D(self):
        return self.D

    def set_D(self, D):
        self.D = D
        self.analog_quadrature_demod_cf_0.set_gain((self.samp_rate/(2*math.pi*self.D)))




def main(top_block_cls=rm_test, options=None):

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
