import json
import zmq
import sys
import argparse
import time
import threading


RED_SOURCES = {"Boardcast":0,"Inter_LV1":1,"Inter_LV2":2,"Inter_LV3":3}
BLUE_SOURCES = {"Boardcast":4,"Inter_LV1":5,"Inter_LV2":6,"Inter_LV3":7}


class ParaDistro:
    def __init__(self, team, json_file = "./RF_para.json", endpoint = "tcp://127.0.0.1:5555", delay = 0.3):
        if team not in ["blue","red","BLUE","RED"]:
            raise ValueError("team must be 'blue' or 'red'")
        self.json_file = json_file
        self.endpoint = endpoint
        self.delay = delay

        if team.lower() == "red":
            self.source_mapping = RED_SOURCES
        else:
            self.source_mapping = BLUE_SOURCES

        # 1. 读取 JSON 文件
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"错误：文件 {self.json_file} 不存在。")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"错误：JSON 解析失败 - {e}")
            sys.exit(1)

        # 预期格式：{"sources": [...]}
        sources = data.get("sources")
        if not isinstance(sources, list):
            print("错误：JSON 顶层应包含 'sources' 列表")
            sys.exit(1)


        # 2. 初始化 ZMQ
        self.context = zmq.Context()
        self.pub_socket = self.context.socket(zmq.PUB)
        self.pub_socket.setsockopt(zmq.CONFLATE, 1)      # 只保留最新命令
        self.pub_socket.linger = 0 

        try:
            self.pub_socket.bind(self.endpoint)
            print(f"已绑定到 {self.endpoint}，准备发送 {len(sources)} 条消息...")
        except zmq.ZMQError as e:
            print(f"ZMQ 绑定失败：{e}")
            sys.exit(1)

    def send_parameters(self, inter_level = 1):
        pub_temp = {"boardcast":self.source_mapping["Boardcast"],"inter":self.source_mapping[f"Inter_LV{inter_level}"]}
        message = json.dumps(pub_temp, ensure_ascii=False)
        self.pub_socket.send_string(message)
        print(f"已发送")

    def close(self):
        self.push_socket.close()
        self.context.term()

    class Auto_Distributor:
        def __init__(self, parent, inter_level = 1):
            self.parent = parent
            self._lock = threading.Lock()
            self.inter_level = inter_level
            self.thread = threading.Thread(target=self.run)
            self.thread.daemon = True
        
        def start(self):
            self.thread.start()

        def update_inter_level(self, new_level):
            with self._lock:
                self.inter_level = new_level

        def run(self):
            while True:
                with self._lock:
                    self.parent.send_parameters(self.inter_level)
                time.sleep(self.parent.delay)
        
        def stop(self):
            self.thread.join()

if __name__ == "__main__":
    """parser = argparse.ArgumentParser(description="读取电磁波源 JSON 文件并通过 ZMQ PUSH 发送")
    parser.add_argument("json_file", help="输入的 JSON 文件路径")
    parser.add_argument("--endpoint", default="tcp://127.0.0.1:5555",
                        help="ZMQ PUSH 端点，例如 tcp://127.0.0.1:5555 (默认)")
    parser.add_argument("--delay", type=float, default=0.0,
                        help="每条消息发送间隔（秒），默认 0")
    args = parser.parse_args()"""
    paradistro = ParaDistro(team = "blue", json_file="./RF_para.json",endpoint="tcp://127.0.0.1:5555")
    autorunner = paradistro.Auto_Distributor(paradistro, inter_level=1)
    autorunner.start
    time.sleep(5)
    autorunner.update_inter_level(2)
    time.sleep(5)
    autorunner.update_inter_level(3)
    time.sleep(5)
    autorunner.stop()

    