import zmq
import crc
from typing import Optional, Tuple, List

# ---------------------------- 原 Frame_decoder 类（仅用于 CRC 计算） ----------------------------
class Frame_decoder:
    def __init__(self):
        rm_crc8 = crc.Configuration(8, 0x31, 0xff, 0, True, True)
        rm_crc16 = crc.Configuration(16, 0x1021, 0xffff, 0, True, True)
        self.header_crc_calc = crc.Calculator(rm_crc8, True)
        self.frame_crc_calc = crc.Calculator(rm_crc16, True)

    def bf_header_fixing(self, data_len: int, data: List[int], crc_val: int, fix_mode: str = "key"):
        """暴力修复头部 CRC8（原逻辑保留）"""
        data_temp = data[:]
        DATA_LEN_RANGE = 64

        if data_len == 1030:
            data_temp.insert(2, 0)
            data_temp.pop()
            for i in range(255):
                data_temp[3] = i
                if self.header_crc_calc.checksum(bytes(data_temp)) == crc_val:
                    return data_temp
            return None

        if fix_mode == "key" and data_len == 6:
            for i in range(255):
                data_temp[3] = i
                if self.header_crc_calc.checksum(bytes(data_temp)) == crc_val:
                    return data_temp
            return None

        if data_len > DATA_LEN_RANGE:
            for i in range(65):
                data_temp[1] = i
                if self.header_crc_calc.checksum(bytes(data_temp)) == crc_val:
                    return data_temp
            return None

        return None


# ---------------------------- 输出包装函数（便于后续替换） ----------------------------
def output_result(cmd:int, data: bytes, invert: bool = False):
    """
    输出解析结果，目前仅打印。
    后续可扩展为存储、转发、显示等。
    """
    try:
        # 尝试作为文本打印
        text = ''.join(chr(b) for b in data)
        print(f"[OUT] {text}")
    except Exception:
        print(f"[OUT] {data.hex()}")
    
    if invert:             # 组委会疑似抽风，上传密钥时需要翻转字节顺序，因此这里提供一个选项来翻转输出数据的字节顺序以便对接（可根据需要启用）
        data = data[::-1]  # 反转字节顺序

    # Your code here to handle the output data (e.g., store, forward, display) can be added here.


# ---------------------------- 流式解析器（复用原 CRC 逻辑） ----------------------------
class StreamFrameDecoder:
    def __init__(self):
        self.crc_helper = Frame_decoder()       # 仅用于 CRC 计算与头部修复
        self.buffer = bytearray()               # 未处理的字节缓冲区

    def feed(self, data: bytes):
        """将接收到的原始字节追加到缓冲区，并尝试解析完整帧"""
        self.buffer.extend(data)
        self._parse_all()

    def _parse_all(self):
        """循环解析缓冲区中的所有完整帧，直到无法解析更多"""
        while True:
            result = self._try_parse_one()
            if result is None:
                break          # 无法解析更多帧（数据不足或帧错误）
            cmd, data, consumed = result
            output_result(cmd, data)            # 输出解析结果
            # 移除已解析的字节
            self.buffer = self.buffer[consumed:]

    def _try_parse_one(self) -> Optional[Tuple[int, bytes, int]]:
        """
        尝试从缓冲区起始位置解析一帧。
        返回 (解析出的data负载, 本帧总字节数) 或 None。
        """
        buf = self.buffer
        n = len(buf)
        pos = 0

        # 寻找第一个 0xA5 起始标志
        while pos < n:
            if buf[pos] != 0xA5:
                pos += 1
                continue

            # 检查是否足够读取最小头部 (5字节)
            if pos + 5 > n:
                return None   # 数据不足，等待更多数据

            # 读取长度字段（小端）
            len_low = buf[pos+1]
            len_high = buf[pos+2]
            data_len = len_low + (len_high << 8)
            seq = buf[pos+3]
            header_crc8 = buf[pos+4]

            # 构建头部列表（不含 CRC8 字段）
            header_list = [0xA5, len_low, len_high, seq]

            # 头部 CRC8 校验
            if self.crc_helper.header_crc_calc.checksum(bytes(header_list)) != header_crc8:
                # 尝试暴力修复
                fixed = self.crc_helper.bf_header_fixing(data_len, header_list, header_crc8)
                if fixed is None:
                    # 无法修复，跳过这个 0xA5
                    pos += 1
                    continue
                else:
                    # 修复成功，更新头部
                    header_list = fixed
                    # 重新提取数据长度（修复后可能改变）
                    data_len = header_list[1] + (header_list[2] << 8)
                    # 原代码中修复后若长度>64则视为失败，此处同理
                    if data_len > 64:
                        pos += 1
                        continue

            # 此时头部有效，头部总长 = 5字节（包含CRC8）
            header_list.append(header_crc8)
            # 计算帧其他部分位置
            cmd_start = pos + 5
            data_start = cmd_start + 2
            crc_start = data_start + data_len
            frame_end = crc_start + 2

            if frame_end > n:
                # 数据不完整，等待更多
                return None

            # 读取 cmd、data、帧 CRC16
            cmd = int.from_bytes(buf[cmd_start:cmd_start+2], byteorder='little')
            data = bytes(buf[data_start:data_start+data_len])
            frame_crc16 = int.from_bytes(buf[crc_start:crc_start+2], byteorder='little')

            # 构建完整帧（不含尾部CRC16）用于校验
            full_frame = bytes(header_list) + buf[cmd_start:crc_start]

            if self.crc_helper.frame_crc_calc.checksum(full_frame) != frame_crc16:
                # 帧 CRC 错误，跳过此起始标志
                pos += 1
                continue

            # 解析成功，返回负载数据和总消耗字节数
            consumed = frame_end - pos
            return cmd, data, consumed

        # 没有找到有效帧起始（可能缓冲区全是无效数据），清空缓冲区？这里保守处理，仅返回 None
        # 实际应用中可考虑丢弃一定量的无效数据，但为安全暂不清空。
        return None


# ---------------------------- 主程序：ZMQ SUB 接收并解析 ----------------------------
def main(zmq_subscribe_address="tcp://localhost:5559", zmq_topic=b""):
    """
    启动 ZMQ SUB 客户端，订阅指定主题（默认空字符串表示全部），
    将接收到的数据交给流式解析器处理。
    """
    ctx = zmq.Context()
    sock = ctx.socket(zmq.SUB)
    sock.setsockopt(zmq.SUBSCRIBE, zmq_topic)   # 订阅主题，空字节串表示接收所有
    sock.connect(zmq_subscribe_address)

    decoder = StreamFrameDecoder()
    print(f"Listening on {zmq_subscribe_address}, topic={zmq_topic}")

    try:
        while True:
            # 接收消息（ZMQ 保证消息完整性，直接作为一帧数据喂入即可）
            msg = sock.recv()
            decoder.feed(msg)
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        sock.close()
        ctx.term()


if __name__ == "__main__":
    # 可根据需要修改地址和主题
    main(zmq_subscribe_address="tcp://127.0.0.1:5559", zmq_topic=b"")