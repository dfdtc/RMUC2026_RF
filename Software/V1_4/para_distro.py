#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
读取包含电磁波源参数的JSON文件，格式化为GNU Radio PDU并通过ZMQ PUSH发送。

示例JSON结构见 README 或代码中的注释。
"""

import json
import argparse
import time
import zmq

def load_sources(json_file_path: str):
    """从JSON文件加载波源列表"""
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # 期望顶层 key 为 "sources"，值是一个列表
    sources = data.get("sources", [])
    if not sources:
        raise ValueError("JSON文件中未找到 'sources' 列表或列表为空")
    return sources

def build_pdu(source: dict):
    """
    将单个波源参数构建成GNU Radio PDU的格式。
    GNU Radio 中 PDU 通常是一个包含 'metadata' 和 'data' 的字典，
    我们将其序列化为 JSON 字符串以便通过 ZMQ 发送。
    这里 metadata 可以包含时间戳、类型等信息，data 保留原始参数。
    """
    pdu = {
        "metadata": {
            "type": "wave_source_params",
            "timestamp": time.time(),          # Unix 时间戳，可选
            "source_name": source.get("wave_source", "unknown")
        },
        "data": source                         # 整个波源参数作为数据载荷
    }
    # 返回 JSON 字符串（GNU Radio 端可以用 JSON Source 解析）
    return json.dumps(pdu, ensure_ascii=False)

def send_pdus(sources, zmq_address="tcp://127.0.0.1:5555", delay_sec=0.1):
    """
    通过 ZMQ PUSH 套接字发送每个波源构建的 PDU。
    :param sources: 波源列表
    :param zmq_address: ZMQ 绑定地址（PUSH 会 connect 到此地址）
    :param delay_sec: 每条消息之间的间隔（秒），避免瞬时洪泛
    """
    context = zmq.Context()
    socket = context.socket(zmq.PUSH)
    socket.connect(zmq_address)
    print(f"已连接到 ZMQ PUSH 地址：{zmq_address}")

    for idx, src in enumerate(sources, 1):
        pdu_str = build_pdu(src)
        socket.send_string(pdu_str)
        print(f"[{idx}/{len(sources)}] 已发送: {src.get('wave_source')}")
        if delay_sec > 0:
            time.sleep(delay_sec)

    socket.close()
    context.term()
    print("所有 PDU 发送完毕。")

def main():
    parser = argparse.ArgumentParser(description="将电磁波参数JSON转换为GNU Radio PDU并通过ZMQ发送。")
    parser.add_argument("json_file", help="包含波源参数的JSON文件路径")
    parser.add_argument("--zmq_addr", default="tcp://127.0.0.1:5555",
                        help="ZMQ PUSH 目标地址 (默认: tcp://127.0.0.1:5555)")
    parser.add_argument("--delay", type=float, default=0.1,
                        help="每条消息之间的发送间隔(秒)，默认0.1")
    args = parser.parse_args()

    try:
        sources = load_sources(args.json_file)
        print(f"成功加载 {len(sources)} 个波源")
        send_pdus(sources, zmq_address=args.zmq_addr, delay_sec=args.delay)
    except Exception as e:
        print(f"错误: {e}")
        return 1
    return 0

if __name__ == "__main__":
    exit(main())