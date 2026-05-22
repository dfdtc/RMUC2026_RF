# original author: SCNU-PIONEER 

import numpy as np
from gnuradio import gr
import crc


# --- Official CRC8 (poly=0x31) init & table ---
rm_crc8 = crc.Configuration(8,0x31,0xff,0,1,1)
rm_crc16 = crc.Configuration(16,0x1021,0xffff,0,1,1)
header_crc_calc = crc.Calculator(rm_crc8,True)
frame_crc_calc = crc.Calculator(rm_crc16,True)


# --- Official CRC16 table & init (little-endian output) ---
CRC16_INIT = 0xFFFF

def _crc8(data):

    return header_crc_calc.checksum(data) & 0xFF


def _crc16(data):

    return frame_crc_calc.checksum(data) & 0xFFFF


CMD_OPTIONS = {
    # name: (cmd_id, data_length)
    "enemy_pos": (0x0A01, 24),
    "enemy_hp": (0x0A02, 12),
    "enemy_ammo": (0x0A03, 10),
    "buff_state": (0x0A04, 8),
    "gains": (0x0A05, 36),
    "jamming": (0x0A06, 6),
}



# --- 协议字段结构定义（与 radar.yaml 保持同步） ---
_PROTO_FIELDS = {
    "enemy_pos": [
        ("hero_x", 2, "uint16"), ("hero_y", 2, "uint16"),
        ("engineer_x", 2, "uint16"), ("engineer_y", 2, "uint16"),
        ("infantry_3_x", 2, "uint16"), ("infantry_3_y", 2, "uint16"),
        ("infantry_4_x", 2, "uint16"), ("infantry_4_y", 2, "uint16"),
        ("aerial_x", 2, "uint16"), ("aerial_y", 2, "uint16"),
        ("sentry_x", 2, "uint16"), ("sentry_y", 2, "uint16"),
    ],
    "enemy_hp": [
        ("hero_hp", 2, "uint16"), ("engineer_hp", 2, "uint16"),
        ("infantry_3_hp", 2, "uint16"), ("infantry_4_hp", 2, "uint16"),
        ("reserved", 2, "uint16"), ("sentry_hp", 2, "uint16"),
    ],
    "enemy_ammo": [
        ("hero_ammo", 2, "uint16"), ("infantry_3_ammo", 2, "uint16"),
        ("infantry_4_ammo", 2, "uint16"), ("aerial_ammo", 2, "uint16"),
        ("sentry_ammo", 2, "uint16"),
    ],
    "buff_state": [
        ("remaining_gold", 2, "uint16"), ("total_gold", 2, "uint16"),
        ("macro_bits", 4, "uint32"),  # 4字节位域，建议用int传入
    ],
    "gains": [
        ("hero_health_regen", 1, "uint8"), ("hero_cooling_boost", 2, "uint16"),
        ("hero_defense_boost", 1, "uint8"), ("hero_defense_debuff", 1, "uint8"),
        ("hero_attack_boost", 2, "uint16"), ("engineer_health_regen", 1, "uint8"),
        ("engineer_cooling_boost", 2, "uint16"), ("engineer_defense_boost", 1, "uint8"),
        ("engineer_defense_debuff", 1, "uint8"), ("engineer_attack_boost", 2, "uint16"),
        ("infantry_3_health_regen", 1, "uint8"), ("infantry_3_cooling_boost", 2, "uint16"),
        ("infantry_3_defense_boost", 1, "uint8"), ("infantry_3_defense_debuff", 1, "uint8"),
        ("infantry_3_attack_boost", 2, "uint16"), ("infantry_4_health_regen", 1, "uint8"),
        ("infantry_4_cooling_boost", 2, "uint16"), ("infantry_4_defense_boost", 1, "uint8"),
        ("infantry_4_defense_debuff", 1, "uint8"), ("infantry_4_attack_boost", 2, "uint16"),
        ("sentry_health_regen", 1, "uint8"), ("sentry_cooling_boost", 2, "uint16"),
        ("sentry_defense_boost", 1, "uint8"), ("sentry_defense_debuff", 1, "uint8"),
        ("sentry_attack_boost", 2, "uint16"), ("sentry_posture", 1, "uint8"),
    ],
    "jamming": [
        ("key", 6, "ascii6"),
    ],
}

def _encode_payload(cmd_option, payload, pad_mode="pad"):
    fields = _PROTO_FIELDS.get(cmd_option)
    if not fields:
        # fallback: treat as ascii string
        if isinstance(payload, str):
            return [ord(c) for c in payload]
        else:
            raise ValueError(f"No field def for {cmd_option}, and payload not str")
    out = bytearray()
    if not isinstance(payload, dict):
        raise ValueError(f"For cmd_option {cmd_option}, payload must be dict")
    for name, size, typ in fields:
        v = payload.get(name, 0)
        if typ == "uint16":
            out += int(v).to_bytes(2, "little", signed=False)
        elif typ == "uint8":
            out += int(v).to_bytes(1, "little", signed=False)
        elif typ == "uint32":
            out += int(v).to_bytes(4, "little", signed=False)
        elif typ == "ascii6":
            s = str(v)[:6].ljust(6, '\0')
            out += bytes([ord(c) for c in s])
        else:
            raise ValueError(f"Unknown type {typ}")
    return list(out)


import threading
import zmq

class byte_vector_source(gr.sync_block):
    """
    将输入数据（dict或字符串）封装为 RoboMaster 协议帧并循环输出。
    支持本地参数（mode=local）或外部ZMQ客户端参数（mode=client）。
    帧结构: [SOF|len(2)|seq|CRC8][cmd_id(2)][data][CRC16(2)]
    """

    def __init__(self, payload=None, cmd_option="enemy_pos", seq=0, pad_mode="pad", mode="local"):
        gr.sync_block.__init__(
            self,
            name="Byte Vector Source",
            in_sig=None,
            out_sig=[np.uint8]
        )
        self._seq_manual = seq & 0xFF
        self.mode = mode
        self.cmd_option = cmd_option
        self.pad_mode = pad_mode
        self.chunk_bits = 2
        self.ptr = 0
        self.lock = threading.Lock()
        if self.mode == "client":
            self.vector = np.zeros(8, dtype=np.uint8)  # 初始空帧
            self.v_len = len(self.vector)
            self._start_zmq_thread()
            print("Byte Source in CLIENT mode, waiting for ZMQ payload...")
        else:
            if cmd_option not in CMD_OPTIONS:
                raise ValueError(f"cmd_option must be one of {list(CMD_OPTIONS.keys())}")
            self.vector = self._build_frame(payload)
            self.vector = self._bytes_to_chunks(self.vector, self.chunk_bits)
            self.v_len = len(self.vector)
            print(f"Byte Source Initialized (mode=chunks(2b), len={self.v_len}, cmd=0x{self._cmd_id:04X})")

    def _start_zmq_thread(self):
        def zmq_worker():
            ctx = zmq.Context()
            sock = ctx.socket(zmq.PULL)
            sock.bind("tcp://*:5555")
            while True:
                try:
                    msg = sock.recv_json()
                    # 期望msg为dict，包含cmd_option和payload字段
                    cmd_option = msg.get("cmd_option", "enemy_pos")
                    payload = {k: v for k, v in msg.items() if k != "cmd_option"}
                    if cmd_option not in CMD_OPTIONS:
                        continue
                    frame = self._build_frame(payload, cmd_option=cmd_option)
                    chunks = self._bytes_to_chunks(frame, self.chunk_bits)
                    with self.lock:
                        self.vector = chunks
                        self.v_len = len(chunks)
                        self.ptr = 0
                    print(f"[ZMQ] Received payload for {cmd_option}, frame updated.")
                except Exception as e:
                    print(f"[ZMQ] Error: {e}")
        t = threading.Thread(target=zmq_worker, daemon=True)
        t.start()

    def _build_frame(self, payload, cmd_option=None):
        if cmd_option is None:
            cmd_option = self.cmd_option
        self._cmd_id, data_len_expect = CMD_OPTIONS[cmd_option]
        # 编码payload
        if cmd_option == "jamming":
            if payload is None:
                payload = "RM2026"
            if isinstance(payload, str):
                data_bytes = [ord(c) for c in payload.strip().strip("'\"")]
                if len(data_bytes) < data_len_expect:
                    data_bytes += [0x00] * (data_len_expect - len(data_bytes))
                if len(data_bytes) > data_len_expect:
                    data_bytes = data_bytes[:data_len_expect]
            else:
                data_bytes = _encode_payload(cmd_option, payload, self.pad_mode)
        else:
            if payload is None:
                payload = {}
            data_bytes = _encode_payload(cmd_option, payload, self.pad_mode)
            if len(data_bytes) < data_len_expect:
                data_bytes += [0x00] * (data_len_expect - len(data_bytes))
            if len(data_bytes) > data_len_expect:
                data_bytes = data_bytes[:data_len_expect]
        data_len = len(data_bytes)
        sof = 0xA5
        len_l = data_len & 0xFF
        len_h = (data_len >> 8) & 0xFF
        seq_derived = self._cmd_id & 0xFF
        header_wo_crc8 = [sof, len_l, len_h, seq_derived]
        crc8 = _crc8(header_wo_crc8)
        frame_header = header_wo_crc8 + [crc8]
        cmd_l = self._cmd_id & 0xFF
        cmd_h = (self._cmd_id >> 8) & 0xFF
        body = [cmd_l, cmd_h] + data_bytes
        crc16 = _crc16(frame_header + body)
        crc16_l = crc16 & 0xFF
        crc16_h = (crc16 >> 8) & 0xFF
        frame = frame_header + body + [crc16_l, crc16_h]
        return np.array(frame, dtype=np.uint8)

    def _bytes_to_chunks(self, byte_arr, chunk_bits=2):
        """
        Convert an array of bytes (np.uint8) into an array of chunk values.
        - Interpret each byte MSB-first.
        - Group bits into chunks of `chunk_bits` (e.g. 2), producing values 0..(2^chunk_bits-1).
        - If total bits is not divisible by chunk_bits, pad with zeros at the end.
        Returns np.array(dtype=np.uint8) of chunk values.
        """
        if chunk_bits <= 0 or chunk_bits > 8:
            raise ValueError("chunk_bits must be in 1..8")
        arr = np.asarray(byte_arr, dtype=np.uint8)
        # Extract bits MSB-first per byte
        try:
            bits = np.unpackbits(arr, bitorder='big')
        except TypeError:
            # Older numpy versions may not support bitorder kw; fallback
            bits = np.empty(len(arr) * 8, dtype=np.uint8)
            for i, b in enumerate(arr):
                for j in range(8):
                    bits[i * 8 + j] = (int(b) >> (7 - j)) & 1

        total_bits = bits.size
        # Pad to multiple of chunk_bits
        rem = total_bits % chunk_bits
        if rem != 0:
            pad = chunk_bits - rem
            bits = np.concatenate((bits, np.zeros(pad, dtype=np.uint8)))

        # Reshape and convert to integer values
        bits2 = bits.reshape(-1, chunk_bits)
        # weights: most-significant bit has highest weight
        weights = (1 << np.arange(chunk_bits - 1, -1, -1)).astype(np.uint8)
        vals = bits2.dot(weights).astype(np.uint8)
        return vals

    def work(self, input_items, output_items):
        out = output_items[0]
        n = len(out)
        with self.lock:
            for i in range(n):
                out[i] = self.vector[self.ptr]
                self.ptr = (self.ptr + 1) % self.v_len
        return n
