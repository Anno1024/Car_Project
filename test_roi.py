#!/usr/bin/env python3
import cv2
import numpy as np
import os
import time
from datetime import datetime

# ========== 创建保存文件夹 ==========
save_dir = "roi_test_results"
if not os.path.exists(save_dir):
    os.makedirs(save_dir)
print(f"📁 图片将保存到: {save_dir}/")

# ========== 你的红色阈值 ==========
lower_red = np.array([0, 60, 150])
upper_red = np.array([12, 255, 255])

# ========== 初始化摄像头 ==========
print("📷 初始化摄像头...")
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
time.sleep(0.5)
print("✅ 摄像头初始化完成")

print("\n" + "="*60)
print("🚗 ROI验证程序 (只处理下半部分)")
print("="*60)
print("每2秒自动拍一张照片，共拍10张")
print("请移动色带或小车，拍下不同位置")
print("按 Ctrl+C 提前结束\n")

try:
    for i in range(5):
        # 读取一帧
        ret, frame = cap.read()
        if not ret:
            print("❌ 读取失败")
            continue
        
        # 获取图像尺寸
        h, w = frame.shape[:2]
        
        # ===== 只取下半部分 (ROI) =====
        roi_height = 240  # 处理底部240像素
        roi = frame[h-roi_height:h, :]  # 这就是你代码里用的
        
        # ===== 在ROI上做红色检测 =====
        hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv_roi, lower_red, upper_red)
        
        # 形态学去噪
        kernel = np.ones((3,3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # 找轮廓
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # ===== 创建结果图像 =====
        # 1. 原图（标记ROI区域）
        img_original = frame.copy()
        # 画一条红线标记ROI的上边界
        cv2.line(img_original, (0, h-roi_height), (w, h-roi_height), (0, 0, 255), 2)
        cv2.putText(img_original, "ROI (只看以下区域)", (10, h-roi_height-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        # 2. ROI放大图
        img_roi = roi.copy()
        
        # 3. 检测结果图
        img_result = roi.copy()
        if contours:
            max_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(max_contour)
            
            if area > 500:
                # 画轮廓
                cv2.drawContours(img_result, [max_contour], -1, (0, 255, 0), 2)
                
                # 计算中心
                M = cv2.moments(max_contour)
                if M["m00"] > 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    cv2.circle(img_result, (cx, cy), 5, (0, 0, 255), -1)
                    
                    # 计算误差
                    error = cx - roi.shape[1]//2
                    
                    # 画中心线
                    cv2.line(img_result, (roi.shape[1]//2, 0), (roi.shape[1]//2, roi.shape[0]), (255, 0, 0), 2)
                    
                    # 添加文字
                    cv2.putText(img_result, f"Error: {error}", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(img_result, f"Area: {area:.0f}", (10, 60), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # ===== 保存图片 =====
        timestamp = datetime.now().strftime("%H%M%S")
        
        cv2.imwrite(f"{save_dir}/{i:02d}_original.jpg", img_original)
        cv2.imwrite(f"{save_dir}/{i:02d}_roi.jpg", img_roi)
        cv2.imwrite(f"{save_dir}/{i:02d}_result.jpg", img_result)
        
        print(f"[{i+1}/10] ✅ 已保存第 {i+1} 组图片")
        print(f"    误差: {error if 'error' in locals() else 'N/A'}")
        
        # 等待2秒再拍下一张
        if i < 9:
            time.sleep(2)
        
except KeyboardInterrupt:
    print("\n\n👋 用户中断")

finally:
    cap.release()
    print(f"\n📁 所有图片保存在: {save_dir}/")
    print("文件说明:")
    print("  XX_original.jpg - 原图（红线以上不处理）")
    print("  XX_roi.jpg      - 只截取下半部分")
    print("  XX_result.jpg   - 检测结果（只在下半部分找线）")