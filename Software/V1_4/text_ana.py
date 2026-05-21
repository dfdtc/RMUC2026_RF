import crc
class Frame_decoder:
# ------------------ CRC 配置（保持不变） ------------------
    def __init__(self):
        rm_crc8 = crc.Configuration(8, 0x31, 0xff, 0, True, True)
        rm_crc16 = crc.Configuration(16, 0x1021, 0xffff, 0, True, True)
        self.header_crc_calc = crc.Calculator(rm_crc8, True)
        self.frame_crc_calc = crc.Calculator(rm_crc16, True)

    # ------------------ 头部暴力修复函数（逻辑保持不变） ------------------
    def bf_header_fixing(self,data_len, data, crc, fix_mode="key"):
        """
        通过暴力修改某些字节，使头部 CRC8 校验通过。
        参数:
            data_len: 原始数据长度
            data: 头部四字节列表 [len_low, len_high, seq, crc8]
            crc: 原始的 header_crc8
            fix_mode: 修复模式 ("key" 等)
        返回:
            修复后的 data 列表，或 None
        """
        data_temp = data[:]          # 先复制一份，避免修改外部列表
        DATA_LEN_RANGE = 64

        # 特殊长度 1030 的处理（原有逻辑）
        if data_len == 1030:
            data_temp.insert(2, 0)
            data_temp.pop()
            for i in range(255):
                data_temp[3] = i
                if self.header_crc_calc.checksum(bytes(data_temp)) == crc:
                    return data_temp
            return None

        # key 模式且长度为 6
        if fix_mode == "key" and data_len == 6:
            for i in range(255):
                data_temp[3] = i
                if self.header_crc_calc.checksum(bytes(data_temp)) == crc:
                    return data_temp
            return None

        # 普通模式
        if data_len > DATA_LEN_RANGE:
            for i in range(65):
                data_temp[1] = i
                if self.header_crc_calc.checksum(bytes(data_temp)) == crc:
                    return data_temp
            return None
        return None  # 其他情况无法修复

    def frame_decoder(self,input_data):
    # ------------------ 主解析逻辑 ------------------
        i = 0
        n = len(input_data)

        while i < n:
            # 寻找帧起始标志 0xA5
            if input_data[i] != 0xA5:
                i += 1
                continue

            start = i                     # 记录帧起始位置，用于失败回退

            # ---------- 1. 尝试读取头部（至少需要 5 字节：0xA5 + len(2) + seq + crc8）----------
            if start + 5 > n:            # 剩余数据不足以构成最小头部，安全退出
                break

            # 读取数据长度 (2 字节小端)
            len_bytes = input_data[start+1 : start+3]
            data_len = int.from_bytes(len_bytes, byteorder='little')
            seq = input_data[start+3]
            header_crc8 = input_data[start+4]

            # 构建头部四字节列表
            header_list = [0xA5,len_bytes[0], len_bytes[1], seq]

            # ---------- 2. 头部 CRC8 校验与修复 ----------
            if self.header_crc_calc.checksum(bytes(header_list)) != header_crc8:
                print("header crc error, trying to fix")
                # 暴力修复（传入副本）
                fixed = self.bf_header_fixing(data_len, list(header_list), header_crc8)
                if fixed is None:
                    print("no bf result, won't fix")
                    i = start + 1         # 失败时跳过 0xA5 继续搜索
                    continue
                else:
                    print("bf success, header fixed")
                    header_list = fixed   # 使用修复后的头部
                    # 从修复后的头部重新提取数据长度
                    data_len = int.from_bytes(header_list[1:3], byteorder='little')
                    if data_len > 64:     # 长度异常，视为修复失败
                        print("data len too long after fix, may be wrong")
                        i = start + 1
                        continue

            # 头部最终包含 5 字节：原 4 字节再追加一次 crc8（保持原有帧拼接方式）
            header_list.append(header_crc8)   # 现在 header_list 长度为 5

            # ---------- 3. 检查剩余数据是否足够容纳 cmd + data + crc16 ----------
            # 当前 i 指向 0xA5，头部已经读取了 5 字节 (包括0xA5)，接下来是 cmd(2字节) + data(data_len) + crc16(2)
            cmd_start = start + 5
            data_start = cmd_start + 2                # cmd 假定为 2 字节
            crc_start = data_start + data_len
            frame_end = crc_start + 2                 # 帧结束的下一位置

            if frame_end > n:
                print("frame truncated at file end, skip parsing")
                i = start + 1
                continue

            # ---------- 4. 读取 cmd、data、frame_crc16 ----------
            cmd = int.from_bytes(input_data[cmd_start:cmd_start+2], byteorder='little')
            data = input_data[data_start : data_start + data_len]
            frame_crc16 = int.from_bytes(input_data[crc_start : crc_start+2], byteorder='little')

            # 构建帧体（不含尾部 CRC16）
            frame_body = input_data[cmd_start : crc_start]   # cmd(2) + data(data_len)
            # 完整帧 = header_list（5字节） + frame_body
            full_frame = bytes(header_list + frame_body)

            # ---------- 5. 帧 CRC16 校验 ----------
            if self.frame_crc_calc.checksum(full_frame) != frame_crc16:
                print("frame crc error")
                i = start + 1           # 帧 CRC 错，跳过一个字节继续搜索
                continue

            # ---------- 6. 校验通过，输出数据 ----------
            try:
                text = ''.join(chr(b) for b in data)
                print(text)
            except Exception:
                print(data)             # 非文本数据直接打印字节

            # 成功解析，游标移到帧尾的下一个字节
            i = frame_end

if __name__ == "__main__":
    temp = []
    with open("./test_decode.txt", "rb") as doc:
        for line in doc.readlines():
            for b in line:
                temp.append(b)
    Frame_decoder().frame_decoder(temp)