#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import numpy as np
import serial
import time

# ========== 核心控制逻辑 ==========
def control_logic():
    # 初始化串口
    try:
        ser = serial.Serial(SERIAL_PORT, BAUTRATE, timeout=1)
        time.sleep(0.5)
        ser.write(b'K')  # 切换为按键模式
        # ser.write(b'Y')  #降速
        # ser.write(b'Y')  #降速
        # # 设置初始速度
        speed_cmd = "{0:10}" # 默认10%速度，可根据需要调整
        ser.write(speed_cmd.encode())
        print(f"串口 {SERIAL_PORT} 初始化成功")
    except Exception as e:
        print(f"串口连接失败: {e}")
        return

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    print("🚗 平滑控制系统启动... 按 Ctrl+C 退出")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                continue

            # 1. 预处理：裁剪下方视野，减少环境干扰
            h, w = frame.shape[:2]
            roi = frame[int(h*ROI_START):h, :] 
            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            
            # 2. 颜色识别
            mask = cv2.inRange(hsv, LOWER_RED, UPPER_RED)
            # 简单去噪
            mask = cv2.erode(mask, None, iterations=2)
            mask = cv2.dilate(mask, None, iterations=2)

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            current_cmd = 'Z' # 默认停止

            if contours:
                max_cnt = max(contours, key=cv2.contourArea)
                if cv2.contourArea(max_cnt) > 500:
                    M = cv2.moments(max_cnt)
                    if M["m00"] > 0:
                        cx = int(M["m10"] / M["m00"])
                        error = cx - (w // 2)

                        # 3. 分级控制逻辑 (平滑转向核心)
                        abs_error = abs(error)

                        if abs_error <= DEAD_ZONE:
                            current_cmd = 'A'  # 在中心范围内，直行
                            status = "直行"
                        elif abs_error <= SMOOTH_ZONE:
                            # 中等误差：使用左上(H)/右上(B)，实现边走边转
                            current_cmd = 'B' if error > 0 else 'H'
                            status = "微调(平滑)"
                        else:
                            # 大误差：使用左转(G)/右转(C)，原地快速修正
                            current_cmd = 'C' if error > 0 else 'G'
                            status = "大转(纠偏)"

                        ser.write(current_cmd.encode())
                        print(f"\r误差: {error:+4d} | 动作: {current_cmd} ({status})", end='', flush=True)
            else:
                # 没看到线，安全起见可以发停止指令或直行寻线
                ser.write(b'A') 

            # 调试窗口（可选，远程运行时请注释掉）
            # cv2.imshow("Mask", mask)
            # if cv2.waitKey(1) == ord('q'): break

    except KeyboardInterrupt:
        print("\n正在停止...")
    finally:
        ser.write(b'Z')
        ser.close()
        cap.release()
        cv2.destroyAllWindows()

# ============================================================
# ==========             调试参数区                ==========
# ============================================================

# 1. 串口配置
SERIAL_PORT = '/dev/ttyAMA0' 
BAUTRATE = 9600

# 2. 视觉配置
# 红色阈值 (根据实际光线调整)
LOWER_RED = np.array([0, 60, 150])
UPPER_RED = np.array([12, 255, 255])
# ROI裁剪比例 (0.5表示取图像下半部分)
ROI_START = 0.5 

# 3. 转向平滑度配置 (最重要的调试项)
# DEAD_ZONE: 在这个像素范围以内，小车会直接跑直线 'A'
DEAD_ZONE = 60   

# SMOOTH_ZONE: 
# 误差在 DEAD_ZONE 到 SMOOTH_ZONE 之间时，发送 'B'/'H' (平滑转向)
# 误差超过 SMOOTH_ZONE 时，发送 'C'/'G' (原地转向)
SMOOTH_ZONE = 180 

# =======================暂时最好的版本==========================

if __name__ == "__main__":
    control_logic()