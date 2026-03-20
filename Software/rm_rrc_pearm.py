import numpy as np
import matplotlib.pyplot as plt

def rrc_filter(alpha, sps, num_taps, normalize=True):
    """ 根升余弦滤波器抽头（支持奇/偶数） """
    if not (0 <= alpha <= 1):
        raise ValueError("alpha 必须在 [0, 1] 范围内")
    if num_taps % 2 == 1:
        n = np.arange(-(num_taps - 1) // 2, (num_taps - 1) // 2 + 1)
    else:
        half = num_taps // 2
        n = np.arange(-half + 0.5, half, 1.0)
    Ts = float(sps)
    taps = np.zeros(num_taps)
    for i, ti in enumerate(n):
        x = ti / Ts
        if abs(ti) < 1e-12:
            taps[i] = (1 - alpha + 4 * alpha / np.pi) / np.sqrt(Ts)
        else:
            denom = 1 - (4 * alpha * x) ** 2
            if np.abs(denom) < 1e-12:
                taps[i] = (alpha / np.sqrt(2 * Ts)) * (
                    (1 + 2 / np.pi) * np.sin(np.pi / (4 * alpha)) +
                    (1 - 2 / np.pi) * np.cos(np.pi / (4 * alpha))
                )
            else:
                term1 = np.sin(np.pi * x * (1 - alpha))
                term2 = 4 * alpha * x * np.cos(np.pi * x * (1 + alpha))
                numerator = term1 + term2
                denominator = np.pi * x * denom
                taps[i] = numerator / denominator / np.sqrt(Ts)
    if normalize:
        taps = taps / np.sqrt(np.sum(taps ** 2))
    return taps

# ------------------ 参数设置 ------------------
preamble_syms = np.array([1,1,-1,-1,-3,-3,-3,-3,-1,1,-3,-3,1,1,-1,-1,-3,-3,-3,-3,-1,1,-3,-3,1,1,-1,-1,-3,-3,-3,-3,-1,1,-3,-3], dtype=np.float32)
alpha = 0.25          # 滚降因子
sps = 4               # 每符号采样数
num_taps = 44         # 滤波器抽头数（奇数）
normalize = True      # 归一化滤波器能量

# 1. 生成 RRC 滤波器抽头
rrc_coeffs = rrc_filter(alpha, sps, num_taps, normalize=normalize)
print("RRC 抽头系数:\n", rrc_coeffs)

# 2. 对符号序列进行上采样（插入零）
upsampled = np.zeros(len(preamble_syms) * sps, dtype=np.float32)
upsampled[::sps] = preamble_syms  # 每 sps 个位置放一个符号

# 3. 通过成形滤波器（卷积）
tx_signal = np.convolve(upsampled, rrc_coeffs, mode='full') *2
tx_signal = tx_signal[68:115]

# 4. （可选）绘制结果
plt.figure(figsize=(12, 4))

plt.subplot(1, 2, 1)
plt.stem(rrc_coeffs, basefmt=" ")
plt.title("RRC 滤波器抽头 (α=0.25, sps=4, taps=44)")
plt.xlabel("Tap index")
plt.grid(True)

plt.subplot(1, 2, 2)
t = np.arange(len(tx_signal)) / sps  # 时间轴，以符号周期为单位
plt.plot(t, tx_signal)
plt.title("成形后的前导信号")
plt.xlabel("Time (symbol periods)")
plt.ylabel("Amplitude")
plt.grid(True)
plt.tight_layout()
plt.show()

# 输出成形信号（可选）
print("成形信号长度:", len(tx_signal))
#print(tx_signal)
print(*tx_signal, sep=', ')