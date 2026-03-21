#!/usr/bin/env python3
import cv2
import numpy as np
import os
import time

# 创建保存目录
save_dir = "tape_test"
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# 你的红色参数
lower_para = np.array([0, 60, 150])
upper_para = np.array([12, 255, 255])

# 打开摄像头
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("无法打开摄像头")
    exit()

print("="*60)
print("红色胶带测试 (无显示屏版)")
print("="*60)
print(f"保存目录: {save_dir}/")
print("按 Ctrl+C 退出")
print("\n正在拍照测试...")

try:
    for i in range(10):  # 拍10张测试图
        ret, frame = cap.read()
        if not ret:
            continue
        
        # 处理图像
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_para, upper_para)
        
        # 形态学去噪
        kernel = np.ones((3,3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # 找轮廓
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 在原图上画结果
        result = frame.copy()
        if contours:
            max_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(max_contour)
            cv2.drawContours(result, [max_contour], -1, (0,255,0), 2)
            
            # 计算中心
            M = cv2.moments(max_contour)
            if M["m00"] > 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                cv2.circle(result, (cx, cy), 5, (0,0,255), -1)
                
                # 添加文字
                text = f"Area: {area}, Center: ({cx},{cy})"
                cv2.putText(result, text, (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
        
        # 保存图片
        cv2.imwrite(f"{save_dir}/{i:02d}_original.jpg", frame)
        cv2.imwrite(f"{save_dir}/{i:02d}_mask.jpg", mask)
        cv2.imwrite(f"{save_dir}/{i:02d}_result.jpg", result)
        
        print(f"  已保存第 {i+1} 组图片")
        time.sleep(1)  # 间隔1秒拍一张

except KeyboardInterrupt:
    print("\n\n测试中断")

cap.release()
print(f"\n测试完成！共保存 {i+1} 组图片到 {save_dir}/")
print("\n用SCP下载到本地查看：")
print(f"  scp -r annon@你的树莓派IP:~/Car_Project/{save_dir} ./")
