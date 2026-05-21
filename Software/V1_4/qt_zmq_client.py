import sys
import zmq
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QFormLayout, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox, QGridLayout
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

ZMQ_ADDR_SEND = "tcp://localhost:5555"
ZMQ_ADDR_RECV = "tcp://*:5556"  # Change to match your PUB address in GNU Radio

TEMPLATES = {
    "enemy_pos": {
        "cmd_option": "enemy_pos",
        "hero_x": 100, "hero_y": 200, "engineer_x": 300, "engineer_y": 400,
        "infantry_3_x": 500, "infantry_3_y": 600, "infantry_4_x": 700, "infantry_4_y": 800,
        "aerial_x": 900, "aerial_y": 1000, "sentry_x": 1100, "sentry_y": 1200
    },
    "enemy_hp": {
        "cmd_option": "enemy_hp",
        "hero_hp": 100, "engineer_hp": 90, "infantry_3_hp": 80, "infantry_4_hp": 70,
        "reserved": 0, "sentry_hp": 60
    },
    "enemy_ammo": {
        "cmd_option": "enemy_ammo",
        "hero_ammo": 10, "infantry_3_ammo": 9, "infantry_4_ammo": 8, "aerial_ammo": 7, "sentry_ammo": 6
    },
    "buff_state": {
        "cmd_option": "buff_state",
        "remaining_gold": 123, "total_gold": 456, "macro_bits": 0xAABBCCDD
    },
    "gains": {
        "cmd_option": "gains",
        "hero_health_regen": 1, "hero_cooling_boost": 2, "hero_defense_boost": 3, "hero_defense_debuff": 4, "hero_attack_boost": 5,
        "engineer_health_regen": 6, "engineer_cooling_boost": 7, "engineer_defense_boost": 8, "engineer_defense_debuff": 9, "engineer_attack_boost": 10,
        "infantry_3_health_regen": 11, "infantry_3_cooling_boost": 12, "infantry_3_defense_boost": 13, "infantry_3_defense_debuff": 14, "infantry_3_attack_boost": 15,
        "infantry_4_health_regen": 16, "infantry_4_cooling_boost": 17, "infantry_4_defense_boost": 18, "infantry_4_defense_debuff": 19, "infantry_4_attack_boost": 20,
        "sentry_health_regen": 21, "sentry_cooling_boost": 22, "sentry_defense_boost": 23, "sentry_defense_debuff": 24, "sentry_attack_boost": 25, "sentry_posture": 26
    },
    "jamming": {
        "cmd_option": "jamming",
        "key": "RM2026"
    }
}

class ZMQClient:
    def __init__(self, addr):
        self.ctx = zmq.Context()
        self.sock = self.ctx.socket(zmq.PUSH)
        self.sock.setsockopt(zmq.IMMEDIATE, 1)
        self.sock.setsockopt(zmq.SNDTIMEO, 10)
        self.sock.setsockopt(zmq.LINGER, 0)
        self.sock.setsockopt(zmq.SNDHWM, 10)
        self.sock.connect(addr)
    def send(self, data):
        self.sock.send_json(data)

class ZMQReceiverThread(QThread):
    received = pyqtSignal(str)
    def __init__(self, addr):
        super().__init__()
        self.addr = addr
        self.running = True
    def run(self):
        ctx = zmq.Context()
        sock = ctx.socket(zmq.SUB)
        sock.setsockopt(zmq.IMMEDIATE, 1)
        sock.setsockopt(zmq.RCVTIMEO, 10)
        sock.setsockopt(zmq.LINGER, 0)
        sock.setsockopt(zmq.RCVHWM, 10)
        sock.connect(self.addr)
        sock.setsockopt_string(zmq.SUBSCRIBE, "")
        while self.running:
            try:
                msg = sock.recv_string(flags=zmq.NOBLOCK)
                self.received.emit(msg)
            except zmq.Again:
                self.msleep(50)
    def stop(self):
        self.running = False
        self.wait()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FSK Protocol Client")
        self.setStyleSheet("""
            QWidget {
                background: #181c20;
                color: #e0e6ed;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-size: 14px;
            }
            QGroupBox {
                border: 1.5px solid #23272e;
                border-radius: 8px;
                margin-top: 12px;
                background: #23272e;
                font-weight: bold;
                font-size: 15px;
                color: #6cfaff;
                padding: 8px 8px 8px 8px;
            }
            QGroupBox:title {
                subcontrol-origin: margin;
                left: 10px;
                top: 2px;
                padding: 0 4px 0 4px;
                background: transparent;
            }
            QLabel[sectionheader="true"] {
                color: #6cfaff;
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 8px;
            }
            QLineEdit, QComboBox {
                background: #23272e;
                color: #e0e6ed;
                border: 1px solid #353b45;
                border-radius: 4px;
                padding: 2px 6px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1e90ff, stop:1 #00e6e6);
                color: #fff;
                border: none;
                border-radius: 6px;
                padding: 6px 18px;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00e6e6, stop:1 #1e90ff);
            }
            QComboBox QAbstractItemView {
                background: #23272e;
                color: #e0e6ed;
                selection-background-color: #1e90ff;
            }
            QScrollBar:vertical, QScrollBar:horizontal {
                background: #23272e;
                width: 10px;
                margin: 2px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
                background: #1e90ff;
                border-radius: 5px;
            }
        """)
        self.zmq_client = ZMQClient(ZMQ_ADDR_SEND)
        self.init_ui()
        self.receiver = ZMQReceiverThread("tcp://localhost:5556")  # Change if needed
        self.receiver.received.connect(self.append_received)
        self.receiver.start()
        # self.recv_history = []
    def init_ui(self):
        main_layout = QHBoxLayout()
        # Sender panel (card style)
        sender_panel = QVBoxLayout()
        sender_card = QGroupBox("Send Data")
        sender_card_layout = QVBoxLayout()
        hbox = QHBoxLayout()
        cmd_label = QLabel("Command Type:")
        cmd_label.setProperty("sectionheader", True)
        hbox.addWidget(cmd_label)
        self.cmd_combo = QComboBox()
        self.cmd_combo.addItems(TEMPLATES.keys())
        self.cmd_combo.currentTextChanged.connect(self.update_form)
        hbox.addWidget(self.cmd_combo)
        sender_card_layout.addLayout(hbox)
        self.form = QFormLayout()
        self.param_edits = {}
        sender_card_layout.addLayout(self.form)
        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.send_data)
        sender_card_layout.addWidget(self.send_btn, alignment=Qt.AlignRight)
        sender_card.setLayout(sender_card_layout)
        sender_panel.addWidget(sender_card)
        # Receiver panel (card style)
        receiver_panel = QVBoxLayout()
        recv_card = QGroupBox("Receive Data")
        recv_card_layout = QVBoxLayout()
        self.recv_groupbox = QGroupBox("Latest Decoded Data")
        self.recv_grid = QGridLayout()
        self.recv_groupbox.setLayout(self.recv_grid)
        self.no_data_label = QLabel("No data received yet.")
        self.no_data_label.setAlignment(Qt.AlignCenter)
        recv_card_layout.addWidget(self.recv_groupbox)
        recv_card_layout.addWidget(self.no_data_label)
        recv_card.setLayout(recv_card_layout)
        receiver_panel.addWidget(recv_card)
        self.last_data = None
        receiver_panel.setSpacing(5)
        self.recv_grid.setVerticalSpacing(2)
        # No history dropdown, only show latest
        # Combine panels
        main_layout.addLayout(sender_panel, 1)
        main_layout.addLayout(receiver_panel, 1)
        self.setLayout(main_layout)
        self.update_form(self.cmd_combo.currentText())
    def update_form(self, cmd):
        for i in reversed(range(self.form.count())):
            self.form.removeRow(i)
        self.param_edits.clear()
        params = TEMPLATES[cmd]
        for k, v in params.items():
            if k == "cmd_option":
                continue
            edit = QLineEdit(str(v))
            self.form.addRow(QLabel(k), edit)
            self.param_edits[k] = edit
    def send_data(self):
        cmd = self.cmd_combo.currentText()
        params = TEMPLATES[cmd].copy()
        for k, edit in self.param_edits.items():
            v = edit.text()
            if k != "key":
                try:
                    params[k] = int(v, 0)
                except Exception:
                    params[k] = v
            else:
                params[k] = v
        try:
            self.zmq_client.send(params)
            QMessageBox.information(self, "Success", f"Sent: {params}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    def append_received(self, msg):
        import datetime
        # Try to parse as JSON, fallback to plain text
        try:
            data = json.loads(msg)
            if not isinstance(data, dict):
                data = {"data": str(data)}
        except Exception:
            data = {"data": msg}
        # Add timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = {"Timestamp": timestamp, **data}
        # Only update if data changed to avoid flicker
        if self.last_data == data:
            return
        self.last_data = data
        self.display_data_in_form(data)


    def display_data_in_form(self, data):
        # Hide 'no data' label if data present
        self.no_data_label.setVisible(False)
        if not data:
            self.no_data_label.setVisible(True)
            return
        # Clear old grid
        while self.recv_grid.count():
            item = self.recv_grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        # Layout: two columns, field and value
        row = 0
        for k, v in data.items():
            label = QLabel(str(k))
            label.setStyleSheet("font-weight:bold;padding:6px 8px;background:#23272e;border-radius:6px;min-width:110px;max-width:140px;")
            if k.lower() == "hex":
                from PyQt5.QtWidgets import QPlainTextEdit
                if isinstance(v, int):
                    hexstr = hex(v)[2:]
                else:
                    hexstr = v[2:] if isinstance(v, str) and v.startswith("0x") else str(v)
                if len(hexstr) % 2:
                    hexstr = "0" + hexstr
                grouped = ' '.join([hexstr[i:i+2] for i in range(0, len(hexstr), 2)])
                # Split into lines, 16 bytes (32 hex chars) per line
                lines = [grouped[i:i+47] for i in range(0, len(grouped), 48)]
                text = '\n'.join(lines)
                value = QPlainTextEdit()
                value.setPlainText(text)
                value.setReadOnly(True)
                value.setMaximumHeight(60)
                value.setStyleSheet("background:#181c20;color:#6cfaff;font-family:monospace;font-size:13px;border:none;padding:4px 8px;border-radius:6px;")
            else:
                value = QLabel(str(v))
                value.setStyleSheet("background:#181c20;padding:6px 10px;border-radius:6px;")
            value.setTextInteractionFlags(Qt.TextSelectableByMouse)
            self.recv_grid.addWidget(label, row, 0, Qt.AlignRight)
            self.recv_grid.addWidget(value, row, 1)
            self.recv_grid.setColumnStretch(0, 0)
            self.recv_grid.setColumnStretch(1, 1)
            row += 1
    def closeEvent(self, event):
        self.receiver.stop()
        event.accept()

def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
