import crc
import struct
import numpy as np

def reverse_bits_in_list(byte_list):
    """
    将输入列表中的每个字节元素进行位翻转 (MSB -> LSB)
    """
    reversed_list = []
    
    for b in byte_list:
        # 确保处理的是 0-255 之间的字节
        b &= 0xFF 
        
        # 位翻转逻辑
        res = 0
        for i in range(8):
            # 将 res 左移一位，并把 b 的最后一位挪到 res 的末尾
            res = (res << 1) | (b & 1)
            # b 右移一位，处理下一个 bit
            b >>= 1
            
        reversed_list.append(res)
        
    return reversed_list


# 预计算表
BIT_REVERSE_TABLE = [reverse_bits_in_list([i])[0] for i in range(256)]

def reverse_bits_fast(byte_list):
    return [BIT_REVERSE_TABLE[b & 0xFF] for b in byte_list]

def to_byte_list(data, byteorder='big', encoding='utf-8', int_size = 2):
    """
将多种类型的输入拆分为单字节列表。

参数:
    data: 输入数据，支持 int, float, str, bytes, bytearray, list, numpy.ndarray 等。
    byteorder: 字节序，'little'（小端）或 'big'（大端）。对数字和编码有影响。
    encoding: 字符串编码方式，如 'utf-8', 'ascii', 'gbk'。
    
返回:
    list: 由整数（0-255）构成的单字节列表。
    """
    byte_list = []

    if isinstance(data, (int, float)):
        # 处理数字：使用 struct 模块打包为字节
        # 注意：int 会被视为平台的默认长度（通常是4或8字节），明确指定长度更安全
        if isinstance(data, int):
        # 根据指定大小处理整数
            
            if int_size == 1:
                if not 0 <= data <= 0xFF:
                    raise ValueError(f"值 {data} 超出8位范围")
                return [data & 0xFF]
            elif int_size == 2:
                if not 0 <= data <= 0xFFFF:
                    raise ValueError(f"值 {data} 超出16位范围")
                bytes_obj = data.to_bytes(2, byteorder)
                return list(bytes_obj)
            elif int_size == 4:
                format_char = 'i' if data < 0 else 'I'
                packed = struct.pack(f'{byteorder}{format_char}', data)
                return list(packed)
            elif int_size == 8:
                format_char = 'q' if data < 0 else 'Q'
                packed = struct.pack(f'{byteorder}{format_char}', data)
                return list(packed)
        else: # isinstance(data, float)
            # 转换为4字节单精度浮点，'d' 表示双精度
            packed = struct.pack(f'{byteorder}f', data)
        byte_list = list(packed)
    
    elif isinstance(data, str):
        # 处理字符串：编码为字节
        byte_list = list(data.encode(encoding))
    
    elif isinstance(data, (bytes, bytearray)):
        # 处理字节/字节数组：直接转换
        byte_list = list(data)
    
    elif isinstance(data, (list, tuple, np.ndarray)):
        # 处理序列：递归处理每个元素
        for item in data:
            byte_list.extend(to_byte_list(item, byteorder, encoding))
    else:
        # 其他类型尝试使用其内存表示
        try:
            # 例如：numpy标量类型
            byte_list = list(data.tobytes())
        except AttributeError:
            raise TypeError(f"不支持的数据类型: {type(data)}")

    return byte_list

class RM_Trans_protocal:
    def __init__(self):

        self.SOF = 0xa5
        rm_crc8 = crc.Configuration(8,0x31,0xff)
        rm_crc16 = crc.Configuration(16,0x1021,0xffff)
        self.header_crc_calc = crc.Calculator(rm_crc8,True)
        self.frame_crc_calc = crc.Calculator(rm_crc16,True)

    def header_init(self, lenth, seq):
        if seq > 255 or lenth > 65535:
            raise Exception
        if lenth<=255:
            header = [self.SOF, 0x0, lenth, seq]
        else:
            header = [self.SOF, lenth, seq]
        
        header.append(self.header_crc_calc.checksum(bytes(header)))
        return header
    
    def frame_former(self, cmd, data, seq = 0):
        data_len = len(data)
        frame = []
        header = self.header_init(data_len, seq)
        frame = frame + header
        if cmd <= 255:
            frame.append(0)
        frame = frame + list(cmd.to_bytes(2))
        frame = frame + to_byte_list(data)
        frame = frame + list(self.frame_crc_calc.checksum(frame).to_bytes(2))
        
        return frame
        

protocal = RM_Trans_protocal()
print(protocal.frame_former(0x0a06,"AAAAAA"))
