import numpy as np
from gnuradio import gr
import pmt

class pi_pdu_controller_v2(gr.sync_block):
    def __init__(self, kp=0.1, ki=0.01, setpoint=0.1, samp_rate=32000.0):
        gr.sync_block.__init__(
            self,
            name='PI PDU Controller (Setpoint 0.1)',
            in_sig=[np.float32],
            out_sig=None
        )
        self.kp = kp
        self.ki = ki
        self.setpoint = setpoint
        self.dt = 1.0 / samp_rate

        self.integrator = 0.0
        self.i_limit = 180.0  # 积分限幅，防止饱和

        # 注册 PDU 输出端口
        self.message_port_register_out(pmt.intern("pdu_out"))

    def work(self, input_items, output_items):
        control_out = 100
        in0 = input_items[0]

        # 为了防止 PDU 发送频率过高击垮调度器
        # 我们只取当前缓冲区最后一个样本的控制结果进行异步输出
        if len(in0) > 0:
            last_val = in0[-1]

            # 1. 计算误差：目标是 0.1
            error = self.setpoint - last_val

            # 2. 更新积分项（带限幅）
            self.integrator += error * self.dt

            #self.integrator = max(min(self.integrator, self.i_limit), -self.i_limit)

            # 3. 计算 PI 输出
            control_out = (self.kp * error) + (self.ki * self.integrator)
            # 构造 PDU: (dictionary, data_vector)
            p = pmt.from_double(control_out)

            self.message_port_pub(pmt.intern("pdu_out"),
                                  pmt.cons(pmt.intern("phase"),p))

        # 消耗掉所有输入采样点
        return len(in0)
