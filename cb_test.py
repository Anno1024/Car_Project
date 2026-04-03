#!/usr/bin/env python3   直走+里程计读取一起
# -*- coding: utf-8 -*-

import serial
import time
import math
import re

# ========== 1. 参数配置 (与你的一致) ==========
SERIAL_PORT = '/dev/ttyAMA0'
BAUTRATE = 9600
WHEEL_BASE = 0.16  # 轮距(米)
MM_TO_M = 0.001

def run_perfect_modeling():
    # 初始化串口
    try:
        ser = serial.Serial(SERIAL_PORT, BAUTRATE, timeout=0.01) # 极短超时，防止阻塞
        time.sleep(0.5)
        ser.write(b'K') 
        ser.write(b'X') # 按照你的逻辑执行初始化
        ser.write("{0:10}".encode()) 
        print("✅ 串口初始化成功，开始 4 秒直行建模...")
    except Exception as e:
        print(f"❌ 失败: {e}"); return

    # 里程计变量
    x, y, theta = 0.0, 0.0, 0.0
    last_time = time.time()
    path_history = []

    start_time = time.time()
    
    try:
        while time.time() - start_time < 4.0:
            # --- 核心：模仿你最顺滑的冲击方式 ---
            ser.write(b'A') 
            
            # --- 顺便读取里程计反馈 (非阻塞) ---
            if ser.in_waiting > 0:
                # 只读当前缓冲区，不等待换行
                raw = ser.read(ser.in_waiting).decode('ascii', errors='ignore')
                # 快速查找最近的一个数据包
                matches = re.findall(r'\{A(.*?)\}\$', raw)
                if matches:
                    data = matches[-1].split(':')
                    if len(data) >= 2:
                        # --- 执行建模算法 ---
                        now = time.time()
                        dt = now - last_time
                        last_time = now
                        
                        v_l = float(data[0]) * MM_TO_M
                        v_r = float(data[1]) * MM_TO_M
                        
                        v_lin = (v_r + v_l) / 2.0
                        v_ang = (v_r - v_l) / WHEEL_BASE
                        
                        x += v_lin * math.cos(theta) * dt
                        y += v_lin * math.sin(theta) * dt
                        theta += v_ang * dt
                        
                        path_history.append((round(x, 4), round(y, 4)))
                        print(f"\r[实时] X:{x:.3f}m | Y:{y:.3f}m | 速度:{data[0]}:{data[1]}", end='')

            # 控制频率与你的代码节奏对齐 (约 20-50ms)
            time.sleep(0.04) 

    except KeyboardInterrupt:
        pass
    finally:
        ser.write(b'Z')
        ser.close()
        print(f"\n\n🏁 建模完成！总点数: {len(path_history)}")
        print(f"最终坐标: ({x:.3f}, {y:.3f})")
        print("前5个路径点:", path_history[:5])

if __name__ == "__main__":
    run_perfect_modeling()