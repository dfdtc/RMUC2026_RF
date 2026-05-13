#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: anc
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
from gnuradio import analog
from gnuradio import blocks
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
from gnuradio import iio
import anc_epy_block_0 as epy_block_0  # embedded python block
import math
import sip
import threading



class anc(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "anc", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("anc")
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

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "anc")

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
        self.samp_rate = samp_rate = 2000000
        self.phase_shift = phase_shift = 0
        self.freq_tune = freq_tune = 0
        self.D = D = 125e3

        ##################################################
        # Blocks
        ##################################################

        self._phase_shift_range = qtgui.Range(-1000, 8000, 5, 0, 200)
        self._phase_shift_win = qtgui.RangeWidget(self._phase_shift_range, self.set_phase_shift, "phase_shift", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._phase_shift_win)
        self._freq_tune_range = qtgui.Range(-1000, 8000, 1, 0, 200)
        self._freq_tune_win = qtgui.RangeWidget(self._freq_tune_range, self.set_freq_tune, "freq_tune", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._freq_tune_win)
        self.root_raised_cosine_filter_0_0_0 = filter.interp_fir_filter_fff(
            4,
            firdes.root_raised_cosine(
                4,
                samp_rate,
                500e3,
                0.25,
                (11*4)))
        self.qtgui_time_sink_x_1 = qtgui.time_sink_f(
            1024, #size
            samp_rate, #samp_rate
            "add", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_1.set_update_time(0.10)
        self.qtgui_time_sink_x_1.set_y_axis(-2, 2)

        self.qtgui_time_sink_x_1.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_1.enable_tags(True)
        self.qtgui_time_sink_x_1.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_1.enable_autoscale(False)
        self.qtgui_time_sink_x_1.enable_grid(False)
        self.qtgui_time_sink_x_1.enable_axis_labels(True)
        self.qtgui_time_sink_x_1.enable_control_panel(False)
        self.qtgui_time_sink_x_1.enable_stem_plot(False)


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
                self.qtgui_time_sink_x_1.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_1.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_1.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_1.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_1.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_1.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_1.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_1_win = sip.wrapinstance(self.qtgui_time_sink_x_1.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_1_win)
        self.iio_pluto_source_0 = iio.fmcomms2_source_fc32("192.168.3.1" if "192.168.3.1" else iio.get_pluto_uri(), [True, True], 32768)
        self.iio_pluto_source_0.set_len_tag_key('packet_len')
        self.iio_pluto_source_0.set_frequency(333000000)
        self.iio_pluto_source_0.set_samplerate(int(samp_rate))
        self.iio_pluto_source_0.set_gain_mode(0, 'manual')
        self.iio_pluto_source_0.set_gain(0, 9)
        self.iio_pluto_source_0.set_quadrature(True)
        self.iio_pluto_source_0.set_rfdc(True)
        self.iio_pluto_source_0.set_bbdc(True)
        self.iio_pluto_source_0.set_filter_params('Auto', '', 0, 0)
        self.iio_pluto_sink_0 = iio.fmcomms2_sink_fc32("192.168.3.1" if "192.168.3.1" else iio.get_pluto_uri(), [True, True], 32768, False)
        self.iio_pluto_sink_0.set_len_tag_key('')
        self.iio_pluto_sink_0.set_bandwidth(2000000)
        self.iio_pluto_sink_0.set_frequency((333000000+freq_tune))
        self.iio_pluto_sink_0.set_samplerate(int(samp_rate))
        self.iio_pluto_sink_0.set_attenuation(0, 0)
        self.iio_pluto_sink_0.set_filter_params('Auto', '', 0, 0)
        self.epy_block_0 = epy_block_0.pi_pdu_controller_v2(kp=3.15, ki=38, setpoint=0.5, samp_rate=samp_rate)
        self.digital_map_bb_0 = digital.map_bb([-3,-1,1,3])
        self.blocks_vector_source_x_0 = blocks.vector_source_b((165, 0, 6, 0, 153, 10, 6, 65, 65, 65, 65, 65, 65, 189, 45), True, 1, [])
        self.blocks_vco_c_0 = blocks.vco_c(samp_rate, ((2*math.pi)*D), 1)
        self.blocks_stream_to_tagged_stream_0 = blocks.stream_to_tagged_stream(gr.sizeof_char, 1, 15, "packet_len")
        self.blocks_rms_xx_1 = blocks.rms_cf(0.0001)
        self.blocks_repack_bits_bb_1 = blocks.repack_bits_bb(8, 2, "packet_len", False, gr.GR_LSB_FIRST)
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.blocks_msgpair_to_var_0 = blocks.msg_pair_to_var(self.set_phase_shift)
        self.blocks_char_to_float_0 = blocks.char_to_float(1, 1)
        self.analog_sig_source_x_1 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, phase_shift, 1, 0, 0)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.epy_block_0, 'pdu_out'), (self.blocks_msgpair_to_var_0, 'inpair'))
        self.connect((self.analog_sig_source_x_1, 0), (self.blocks_multiply_xx_0, 0))
        self.connect((self.blocks_char_to_float_0, 0), (self.root_raised_cosine_filter_0_0_0, 0))
        self.connect((self.blocks_multiply_xx_0, 0), (self.iio_pluto_sink_0, 0))
        self.connect((self.blocks_repack_bits_bb_1, 0), (self.digital_map_bb_0, 0))
        self.connect((self.blocks_rms_xx_1, 0), (self.epy_block_0, 0))
        self.connect((self.blocks_rms_xx_1, 0), (self.qtgui_time_sink_x_1, 0))
        self.connect((self.blocks_stream_to_tagged_stream_0, 0), (self.blocks_repack_bits_bb_1, 0))
        self.connect((self.blocks_vco_c_0, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.blocks_vector_source_x_0, 0), (self.blocks_stream_to_tagged_stream_0, 0))
        self.connect((self.digital_map_bb_0, 0), (self.blocks_char_to_float_0, 0))
        self.connect((self.iio_pluto_source_0, 0), (self.blocks_rms_xx_1, 0))
        self.connect((self.root_raised_cosine_filter_0_0_0, 0), (self.blocks_vco_c_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "anc")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.analog_sig_source_x_1.set_sampling_freq(self.samp_rate)
        self.iio_pluto_sink_0.set_samplerate(int(self.samp_rate))
        self.iio_pluto_source_0.set_samplerate(int(self.samp_rate))
        self.qtgui_time_sink_x_1.set_samp_rate(self.samp_rate)
        self.root_raised_cosine_filter_0_0_0.set_taps(firdes.root_raised_cosine(4, self.samp_rate, 500e3, 0.25, (11*4)))

    def get_phase_shift(self):
        return self.phase_shift

    def set_phase_shift(self, phase_shift):
        self.phase_shift = phase_shift
        self.analog_sig_source_x_1.set_frequency(self.phase_shift)

    def get_freq_tune(self):
        return self.freq_tune

    def set_freq_tune(self, freq_tune):
        self.freq_tune = freq_tune
        self.iio_pluto_sink_0.set_frequency((333000000+self.freq_tune))

    def get_D(self):
        return self.D

    def set_D(self, D):
        self.D = D




def main(top_block_cls=anc, options=None):

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
