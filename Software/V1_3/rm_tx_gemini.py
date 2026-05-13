import numpy as np
import adi
from scipy import signal

# --- 参数设置 ---
sample_rate = 2e6       # 采样率 2MHz
symbol_rate = 500e3     # 符号率 500k
sps = int(sample_rate / symbol_rate)  # 每个符号的采样点数 (Interpolation=4)
alpha = 0.25            # RRC 滚降系数
num_taps = 44           # 滤波器抽头数
gain = -4               # Pluto TX 增益 (注意：Pluto增益通常为负值，-4表示接近最大)
center_freq = 915e6     # 发射中心频率

# 4-FSK 频偏设置
# 为了占用带宽 BW 约 1.04MHz，我们需要计算频率间隔
# BW ≈ (1+alpha)*Rs + 2*df_max -> 1.04M ≈ 1.25*500k + 2*df_max
# 2*df_max ≈ 415k -> df_max ≈ 207k。取符号映射为 [-3, -1, 1, 3] * freq_step
freq_step = 70e3        # 频偏步长，最大偏移 3 * 70k = 210kHz

# --- 1. 生成 RRC 滤波器系数 ---
def rrc_design(taps, alpha, sps):
    t = np.arange(-taps//2, taps//2) / sps
    h = np.zeros(len(t))
    for i in range(len(t)):
        if t[i] == 0.0:
            h[i] = 1.0 - alpha + (4 * alpha / np.pi)
        elif alpha != 0 and abs(t[i]) == 1.0 / (4 * alpha):
            h[i] = (alpha / np.sqrt(2)) * (((1 + 2 / np.pi) * np.sin(np.pi / (4 * alpha))) +
                                            ((1 - 2 / np.pi) * np.cos(np.pi / (4 * alpha))))
        else:
            h[i] = (np.sin(np.pi * t[i] * (1 - alpha)) +
                    4 * alpha * t[i] * np.cos(np.pi * t[i] * (1 + alpha))) / \
                   (np.pi * t[i] * (1 - (4 * alpha * t[i])**2))
    return h / np.sum(h)

rrc = rrc_design(num_taps, alpha, sps)

# --- 2. 生成随机 4-FSK 符号 ---
num_symbols = 1000
# 随机生成 0, 1, 2, 3 -> 映射到 -3, -1, 1, 3
bits = np.random.randint(0, 4, num_symbols)
symbols = 2 * bits - 3

# --- 3. 符号上采样与 RRC 滤波 ---
# 这里的处理方式是将 RRC 作用于频率控制信号上
upsampled_symbols = np.zeros(num_symbols * sps)
upsampled_symbols[::sps] = symbols
# 应用成形滤波
shaped_freq_signal = np.convolve(upsampled_symbols, rrc, mode='full')

# --- 4. 调频处理 (CPFSK) ---
# 频率积分为相位：phase = 2 * pi * f * t
# 归一化频率偏移
sensitivity = 2 * np.pi * freq_step / sample_rate
phase = np.cumsum(shaped_freq_signal * sensitivity)
tx_signal = np.exp(1j * phase) * 0.5 # 0.5 为缩放防止幅度溢出

# --- 5. 配置 PlutoSDR 并发射 ---
try:
    sdr = adi.Pluto("ip:192.168.2.1") # 默认 Pluto IP
    sdr.sample_rate = int(sample_rate)
    sdr.tx_rf_bandwidth = int(sample_rate) # 设置模拟带宽
    sdr.tx_lo = int(center_freq)
    sdr.tx_hardwaregain_chan0 = gain

    # 循环发射数据
    print(f"正在发射 4-RRC-FSK 信号于 {center_freq/1e6} MHz...")
    print("按 Ctrl+C 停止发射")
    sdr.tx_cyclic_buffer = True # 循环发送缓冲区内容
    sdr.tx(tx_signal * (2**14)) # Pluto 期待 12-16 bit 整数或复数

except KeyboardInterrupt:
    print("\n停止发射")
finally:
    sdr.tx_destroy_buffer()
