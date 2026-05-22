"""
Embedded Python Block: ZMQ PULL + JSON 解析
- 内部创建 ZMQ PULL socket，接收 JSON 消息
- 解析出 center_freq_mhz, bandwidth_mhz, access_code
- 输出三个 message 端口: freq (int), bw (int), access_code (string)
"""

import json
import threading
import zmq
from gnuradio import gr
import pmt
import time

class blk(gr.sync_block):
    def __init__(self, endpoint="tcp://127.0.0.1:5555", bind=False,rx_type = "inter"):
        gr.sync_block.__init__(
            self,
            name='ZMQ JSON Pull Parser (int freq/bw + access_code)',
            in_sig=None,
            out_sig=None
        )
        if rx_type not in ["inter", "boardcast"]:
            raise Exception("rx_type must be 'inter' or 'boardcast'")
        else:
            self.rx_type = rx_type
        self.endpoint = endpoint
        self.bind = bind
        self.running = False
        self.thread = None

        # 注册三个输出端口
        self.message_port_register_out(pmt.intern('freq'))        # int
        self.message_port_register_out(pmt.intern('bw'))          # int
        self.message_port_register_out(pmt.intern('access_code')) # string

        # 启动接收线程
        self.start_receiver()

    def start_receiver(self):
        self.running = True
        self.thread = threading.Thread(target=self.receiver_loop)
        self.thread.daemon = True
        self.thread.start()

    def receiver_loop(self):
        context = zmq.Context()
        socket = context.socket(zmq.SUB)

        socket.setsockopt(zmq.CONFLATE, 1)      # 只保留最新命令
        socket.setsockopt(zmq.SUBSCRIBE, b"")    # 订阅所有主题
        socket.setsockopt(zmq.RCVTIMEO, 10000)   # 30秒接收超时，防止无限期阻塞
        if self.bind:
            socket.bind(self.endpoint)
            print(f"[ZMQ] Binding PULL to {self.endpoint}")
        else:
            socket.connect(self.endpoint)
            print(f"[ZMQ] Connecting PULL to {self.endpoint}")

        while self.running:
            try:
                msg_bytes = socket.recv()
                self.process_message(msg_bytes)
            except zmq.Again:
                print("[ZMQ] Receive timeout, no message received")
                continue    
            except zmq.ZMQError as e:
                print(f"[ZMQ] Error: {e}")
                break
            except Exception as e:
                print(f"[ZMQ] Unexpected error: {e}")
                break

        socket.close()
        context.term()
        print("[ZMQ] Receiver thread stopped")
        if self.delay > 0:
            time.sleep(self.delay)

    def process_message(self, msg_bytes):
        try:
            s = msg_bytes.decode('utf-8')
            data = json.loads(s)
        except Exception as e:
            print(f"[Parser] JSON decode error: {e}")
            return
        data = data[self.rx_type]
        # 提取字段，缺失时使用默认值并报警
        freq_val = data.get('center_freq')
        bw_val   = data.get('bandwidth')
        code_val = data.get('access_code')

        if freq_val is None or bw_val is None or code_val is None:
            missing = []
            if freq_val is None: missing.append('center_freq')
            if bw_val is None: missing.append('bandwidth')
            if code_val is None: missing.append('access_code')
            print(f"[Parser] Missing keys: {missing} in {data.keys()}")
            return

        # 转换为 int (截断小数)
        freq_int = int(freq_val)
        bw_int   = int(bw_val)

        # 发送消息
        self.message_port_pub(pmt.intern('freq'), 
                              pmt.cons(pmt.intern('freq'), pmt.from_long(freq_int)))
        self.message_port_pub(pmt.intern('bw'), 
                              pmt.cons(pmt.intern('bw'), pmt.from_long(bw_int)))
        self.message_port_pub(pmt.intern('access_code'), 
                              pmt.cons(pmt.intern('access_code'), pmt.intern(code_val)))

        print(f"[Parser] Sent: freq={freq_int/1e6} MHz, bw={bw_int/1e6} MHz, access_code={code_val}")

    def stop(self):
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.0)

    def __del__(self):
        self.stop()