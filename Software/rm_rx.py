#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: rm_rx
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio import analog
import math
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
import rm_rx_epy_block_1_0 as epy_block_1_0  # embedded python block
import rm_rx_epy_block_1_0_0 as epy_block_1_0_0  # embedded python block
import sip
import threading



class rm_rx(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "rm_rx", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("rm_rx")
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

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "rm_rx")

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
        self.sps = sps = 4
        self.samp_rate = samp_rate = 2e6
        self.pam4 = pam4 = digital.constellation_calcdist([-3,-1,1,3], [0, 1, 2, 3],
        1, 1, digital.constellation.AMPLITUDE_NORMALIZATION).base()
        self.pam4.set_npwr(1.0)
        self.alpha = alpha = 0.25
        self.D = D = symb_rate/4

        ##################################################
        # Blocks
        ##################################################

        self.root_raised_cosine_filter_0_0 = filter.fir_filter_fff(
            1,
            firdes.root_raised_cosine(
                1,
                samp_rate,
                symb_rate,
                alpha,
                (11*sps)))
        self.qtgui_time_sink_x_2_0_2 = qtgui.time_sink_f(
            512, #size
            samp_rate, #samp_rate
            "CR_out", #name
            2, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_2_0_2.set_update_time(2)
        self.qtgui_time_sink_x_2_0_2.set_y_axis(-5, 5)

        self.qtgui_time_sink_x_2_0_2.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_2_0_2.enable_tags(True)
        self.qtgui_time_sink_x_2_0_2.set_trigger_mode(qtgui.TRIG_MODE_NORM, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_2_0_2.enable_autoscale(False)
        self.qtgui_time_sink_x_2_0_2.enable_grid(True)
        self.qtgui_time_sink_x_2_0_2.enable_axis_labels(True)
        self.qtgui_time_sink_x_2_0_2.enable_control_panel(False)
        self.qtgui_time_sink_x_2_0_2.enable_stem_plot(False)


        labels = ['Symb', 'error', 'Signal 3', 'Signal 4', 'Signal 5',
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
                self.qtgui_time_sink_x_2_0_2.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_2_0_2.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_2_0_2.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_2_0_2.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_2_0_2.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_2_0_2.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_2_0_2.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_2_0_2_win = sip.wrapinstance(self.qtgui_time_sink_x_2_0_2.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_2_0_2_win)
        self.qtgui_time_sink_x_2_0_1 = qtgui.time_sink_f(
            512, #size
            samp_rate, #samp_rate
            "Baseband", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_2_0_1.set_update_time(2)
        self.qtgui_time_sink_x_2_0_1.set_y_axis(-5, 5)

        self.qtgui_time_sink_x_2_0_1.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_2_0_1.enable_tags(True)
        self.qtgui_time_sink_x_2_0_1.set_trigger_mode(qtgui.TRIG_MODE_NORM, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
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
        self.qtgui_time_sink_x_2_0 = qtgui.time_sink_f(
            512, #size
            samp_rate, #samp_rate
            "Corr_tag", #name
            2, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_2_0.set_update_time(2)
        self.qtgui_time_sink_x_2_0.set_y_axis(-5, 5)

        self.qtgui_time_sink_x_2_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_2_0.enable_tags(True)
        self.qtgui_time_sink_x_2_0.set_trigger_mode(qtgui.TRIG_MODE_NORM, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_2_0.enable_autoscale(False)
        self.qtgui_time_sink_x_2_0.enable_grid(True)
        self.qtgui_time_sink_x_2_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_2_0.enable_control_panel(False)
        self.qtgui_time_sink_x_2_0.enable_stem_plot(False)


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
                self.qtgui_time_sink_x_2_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_2_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_2_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_2_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_2_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_2_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_2_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_2_0_win = sip.wrapinstance(self.qtgui_time_sink_x_2_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_2_0_win)
        self.qtgui_freq_sink_x_0 = qtgui.freq_sink_c(
            1024, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate, #bw
            "RF", #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_x_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_0.set_y_axis((-140), 10)
        self.qtgui_freq_sink_x_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_0.enable_grid(False)
        self.qtgui_freq_sink_x_0.set_fft_average(1.0)
        self.qtgui_freq_sink_x_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0.enable_control_panel(False)
        self.qtgui_freq_sink_x_0.set_fft_window_normalized(False)



        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_freq_sink_x_0_win)
        self.iio_pluto_source_0 = iio.fmcomms2_source_fc32("192.168.3.1" if "192.168.3.1" else iio.get_pluto_uri(), [True, True], 32768)
        self.iio_pluto_source_0.set_len_tag_key('packet_len')
        self.iio_pluto_source_0.set_frequency(433000000)
        self.iio_pluto_source_0.set_samplerate(2000000)
        self.iio_pluto_source_0.set_gain_mode(0, 'manual')
        self.iio_pluto_source_0.set_gain(0, 0)
        self.iio_pluto_source_0.set_quadrature(True)
        self.iio_pluto_source_0.set_rfdc(True)
        self.iio_pluto_source_0.set_bbdc(True)
        self.iio_pluto_source_0.set_filter_params('Auto', '', 0, 0)
        self.epy_block_1_0_0 = epy_block_1_0_0.fsk_burst_tagger(threshold=175)
        self.epy_block_1_0 = epy_block_1_0.fsk_corr_scorer()
        self.digital_symbol_sync_xx_0 = digital.symbol_sync_ff(
            digital.TED_MUELLER_AND_MULLER,
            sps,
            0.1,
            1.0,
            0.8,
            1.5,
            1,
            pam4,
            digital.IR_MMSE_8TAP,
            128,
            [])
        self.blocks_multiply_const_vxx_1 = blocks.multiply_const_ff(0.78)
        self.analog_simple_squelch_cc_0 = analog.simple_squelch_cc((-70), 1)
        self.analog_quadrature_demod_cf_0 = analog.quadrature_demod_cf((samp_rate/(2*math.pi*D)))


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_quadrature_demod_cf_0, 0), (self.root_raised_cosine_filter_0_0, 0))
        self.connect((self.analog_simple_squelch_cc_0, 0), (self.analog_quadrature_demod_cf_0, 0))
        self.connect((self.blocks_multiply_const_vxx_1, 0), (self.digital_symbol_sync_xx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_1, 0), (self.epy_block_1_0, 0))
        self.connect((self.blocks_multiply_const_vxx_1, 0), (self.epy_block_1_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_1, 0), (self.qtgui_time_sink_x_2_0_1, 0))
        self.connect((self.digital_symbol_sync_xx_0, 1), (self.qtgui_time_sink_x_2_0_2, 1))
        self.connect((self.digital_symbol_sync_xx_0, 0), (self.qtgui_time_sink_x_2_0_2, 0))
        self.connect((self.epy_block_1_0, 0), (self.qtgui_time_sink_x_2_0, 1))
        self.connect((self.epy_block_1_0_0, 0), (self.qtgui_time_sink_x_2_0, 0))
        self.connect((self.iio_pluto_source_0, 0), (self.analog_simple_squelch_cc_0, 0))
        self.connect((self.iio_pluto_source_0, 0), (self.qtgui_freq_sink_x_0, 0))
        self.connect((self.root_raised_cosine_filter_0_0, 0), (self.blocks_multiply_const_vxx_1, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "rm_rx")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_symb_rate(self):
        return self.symb_rate

    def set_symb_rate(self, symb_rate):
        self.symb_rate = symb_rate
        self.set_D(self.symb_rate/4)
        self.root_raised_cosine_filter_0_0.set_taps(firdes.root_raised_cosine(1, self.samp_rate, self.symb_rate, self.alpha, (11*self.sps)))

    def get_sps(self):
        return self.sps

    def set_sps(self, sps):
        self.sps = sps
        self.digital_symbol_sync_xx_0.set_sps(self.sps)
        self.root_raised_cosine_filter_0_0.set_taps(firdes.root_raised_cosine(1, self.samp_rate, self.symb_rate, self.alpha, (11*self.sps)))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.analog_quadrature_demod_cf_0.set_gain((self.samp_rate/(2*math.pi*self.D)))
        self.qtgui_freq_sink_x_0.set_frequency_range(0, self.samp_rate)
        self.qtgui_time_sink_x_2_0.set_samp_rate(self.samp_rate)
        self.qtgui_time_sink_x_2_0_1.set_samp_rate(self.samp_rate)
        self.qtgui_time_sink_x_2_0_2.set_samp_rate(self.samp_rate)
        self.root_raised_cosine_filter_0_0.set_taps(firdes.root_raised_cosine(1, self.samp_rate, self.symb_rate, self.alpha, (11*self.sps)))

    def get_pam4(self):
        return self.pam4

    def set_pam4(self, pam4):
        self.pam4 = pam4

    def get_alpha(self):
        return self.alpha

    def set_alpha(self, alpha):
        self.alpha = alpha
        self.root_raised_cosine_filter_0_0.set_taps(firdes.root_raised_cosine(1, self.samp_rate, self.symb_rate, self.alpha, (11*self.sps)))

    def get_D(self):
        return self.D

    def set_D(self, D):
        self.D = D
        self.analog_quadrature_demod_cf_0.set_gain((self.samp_rate/(2*math.pi*self.D)))




def main(top_block_cls=rm_rx, options=None):

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
