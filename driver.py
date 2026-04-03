'''
负责所有的串口通信、高频指令冲击和协议解析。

'''


import serial
import re

class CarDriver:
    def __init__(self, port='/dev/ttyAMA0', baud=9600):
        self.ser = serial.Serial(port, baud, timeout=0.01)
    
    def init_car(self):
        # 激活与初始化速度档位
        self.ser.write(b'K')
        #self.ser.write(b'Y' * 3)
        #self.ser.write(b'Y')
        self.ser.write("{0:20}".encode()) 

    def send(self, cmd):
        self.ser.write(cmd.encode())

    def get_velocity(self):
        """解析最新的速度反馈数据"""
        if self.ser.in_waiting > 0:
            raw = self.ser.read(self.ser.in_waiting).decode('ascii', errors='ignore')
            matches = re.findall(r'\{A(.*?)\}\$', raw)
            if matches:
                parts = matches[-1].split(':')
                if len(parts) >= 2:
                    return float(parts[0]), float(parts[1])
        return None, None

    def stop(self):
        self.ser.write(b'Z')
        self.ser.close()