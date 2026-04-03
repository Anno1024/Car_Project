#!/usr/bin/env python3
import serial
import time
import math
import re

# ========== 实验标定参数 ==========
WHEEL_BASE = 0.161  # 你测量的 161mm 轮距
MM_TO_M = 0.001

class Mapper:
    def __init__(self):
        self.ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=0.01)
        self.x, self.y, self.theta = 0.0, 0.0, 0.0
        self.last_time = time.time()
        self.map_data = [] # 存储地图点

    def update(self, vl, vr):
        now = time.time()
        dt = now - self.last_time
        self.last_time = now

        # 差分运动学公式
        v_l, v_r = float(vl) * MM_TO_M, float(vr) * MM_TO_M
        v_lin = (v_r + v_l) / 2.0
        v_ang = (v_r - v_l) / WHEEL_BASE

        self.x += v_lin * math.cos(self.theta) * dt
        self.y += v_lin * math.sin(self.theta) * dt
        self.theta += v_ang * dt

        # 记录点 (每 0.2 秒存一次，避免文件过大)
        self.map_data.append(f"{self.x:.4f},{self.y:.4f},{self.theta:.4f}")

    def save_map(self):
        with open("my_map.txt", "w") as f:
            f.write("x(m),y(m),theta(rad)\n")
            f.writelines("\n".join(self.map_data))
        print(f"\n✅ 地图已保存！共采集 {len(self.map_data)} 个位置点。")

    def run_build(self, duration=5):
        print("🚀 正在建图... 请确保小车前方无障碍")
        self.ser.write(b'K'); time.sleep(0.1)
        self.ser.write("{0:30}".encode()) # 30%动力保证建模特征明显
        
        start = time.time()
        try:
            while time.time() - start < duration:
                self.ser.write(b'A') # 冲击直行
                if self.ser.in_waiting > 0:
                    raw = self.ser.read(self.ser.in_waiting).decode('ascii', errors='ignore')
                    matches = re.findall(r'\{A(.*?)\}\$', raw)
                    if matches:
                        d = matches[-1].split(':')
                        self.update(d[0], d[1])
                        print(f"\r绘制中: ({self.x:.2f}, {self.y:.2f})", end='')
                time.sleep(0.05)
        finally:
            self.ser.write(b'Z')
            self.save_map()

if __name__ == "__main__":
    Mapper().run_build(5) # 跑 5 秒建图