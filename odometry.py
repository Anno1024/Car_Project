'''运动学分析模块'''

import math
import time

class Odometry:
    def __init__(self, wheel_base=0.161):
        self.wheel_base = wheel_base
        self.x, self.y, self.theta = 0.0, 0.0, 0.0
        self.last_time = time.time()
        self.path = []

    def update(self, v_l_mm, v_r_mm):
        if v_l_mm is None or v_r_mm is None: return
        
        now = time.time()
        dt = now - self.last_time
        self.last_time = now

        # mm/s -> m/s
        v_l, v_r = v_l_mm * 0.001, v_r_mm * 0.001
        
        v_lin = (v_r + v_l) / 2.0
        v_ang = (v_r - v_l) / self.wheel_base

        # 航位推算公式
        self.x += v_lin * math.cos(self.theta) * dt
        self.y += v_lin * math.sin(self.theta) * dt
        self.theta += v_ang * dt
        
        self.path.append((round(self.x, 4), round(self.y, 4)))

    def save_data(self, filename="map_data.txt"):
        with open(filename, "w") as f:
            for p in self.path:
                f.write(f"{p[0]},{p[1]}\n")