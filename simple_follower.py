#!/usr/bin/env python3
import cv2
import numpy as np
import serial
import time

# ========== 初始化串口 ==========
print("初始化串口...")
ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=1)
time.sleep(0.5)
ser.write(b'K')
ser.write(b'X')
time.sleep(0.1)

# 速度再降一点
speed_cmd = "{0:10}"  # 10% 更慢
ser.write(speed_cmd.encode())
print(f"设置速度: 10%")
time.sleep(0.1)

# ========== 初始化摄像头 ==========
print("初始化摄像头...")
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
time.sleep(0.5)
print("摄像头初始化完成")

# ========== 红色阈值 ==========
lower_red = np.array([0, 60, 150])
upper_red = np.array([12, 255, 255])

# ========== 比例控制参数（优化版）==========
DEAD_ZONE = 120        # 你试过效果好的死区
MAX_ERROR = 200       
MIN_TURN_TIME = 0.01  # 最小转向30ms
MAX_TURN_TIME = 0.015  # 最大转向100ms（原来是0.3，现在缩短到0.1）
STRAIGHT_TIME = 0.2  # 转向后直走时间加长

# ========== 控制状态 ==========
send_interval = 0.05
last_send_time = 0
send_count = 0

turning_mode = False
turn_start_time = 0
turn_direction = 'Z'
turn_duration = 0

print("\n" + "="*50)
print("🚗 比例控制（超短转向版）")
print("="*50)
print(f"死区: {DEAD_ZONE}像素")
print(f"转向时间: {MIN_TURN_TIME}s - {MAX_TURN_TIME}s")
print("按 Ctrl+C 停止\n")

try:
    while True:
        current_time = time.time()
        
        if current_time - last_send_time >= send_interval:
            
            # ===== 转向状态处理 =====
            if turning_mode:
                if current_time - turn_start_time < turn_duration:
                    current_command = turn_direction
                else:
                    # 转向结束，强制直走一段时间
                    turning_mode = False
                    current_command = 'A'
                    print(f"\n✓ 修正完成，直走{STRAIGHT_TIME}s")
            
            # ===== 正常视觉处理 =====
            if not turning_mode:
                ret, frame = cap.read()
                if not ret:
                    continue
                
                h, w = frame.shape[:2]
                roi = frame[h-240:h, :]
                
                hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
                mask = cv2.inRange(hsv, lower_red, upper_red)
                
                kernel = np.ones((3,3), np.uint8)
                mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
                mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
                
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                if contours:
                    max_contour = max(contours, key=cv2.contourArea)
                    area = cv2.contourArea(max_contour)
                    
                    if area > 500:
                        M = cv2.moments(max_contour)
                        if M["m00"] > 0:
                            cx = int(M["m10"] / M["m00"])
                            error = cx - roi.shape[1]//2
                            
                            if abs(error) < DEAD_ZONE:
                                current_command = 'A'
                                print(f"\r[{send_count:4d}] 直走 | 误差: {error:+4d}", end='', flush=True)
                            else:
                                # 计算转向时间（大大缩短）
                                error_abs = min(abs(error), MAX_ERROR)
                                turn_time = MIN_TURN_TIME + (MAX_TURN_TIME - MIN_TURN_TIME) * (error_abs / MAX_ERROR)
                                
                                if error > 0:
                                    turn_direction = 'C'
                                else:
                                    turn_direction = 'G'
                                
                                turning_mode = True
                                turn_start_time = current_time
                                turn_duration = turn_time
                                current_command = turn_direction
                                
                                direction_name = '右转' if turn_direction == 'C' else '左转'
                                print(f"\n[{send_count:4d}] 🔄 {direction_name} | 误差:{error:+4d} | 转向:{turn_time:.3f}s")
            
            # 发送指令
            ser.write(current_command.encode())
            send_count += 1
            last_send_time = current_time
        
        time.sleep(0.01)

except KeyboardInterrupt:
    print("\n\n🛑 正在停止...")
finally:
    for _ in range(10):
        ser.write(b'Z')
        time.sleep(0.05)
    ser.close()
    cap.release()
    print(f"\n✅ 总共发送 {send_count} 条指令")