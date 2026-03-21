#!/usr/bin/env python3
import cv2
import numpy as np
import os

# 创建保存目录
save_dir = "detection_results"
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# 打开摄像头
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("无法打开摄像头")
    exit()

print("="*60)
print("HSV阈值调试工具 - 颜色检测")
print("="*60)
print(f"程序会自动保存调试图片到 ./{save_dir}/ 目录")
print("按 Ctrl+C 退出\n")

# 先拍一张原始图
ret, frame = cap.read()
if ret:
    cv2.imwrite(f"{save_dir}/01_original.jpg", frame)
    print("✅ 已保存原始图像: 01_original.jpg")

# 颜色阈值组合（可以根据需要修改）
thresholds = [
    # 红色范围
    {"name": "red_wide_1", "lower": [0,50,50], "upper": [10,255,255]},
    {"name": "red_wide_2", "lower": [160,50,50], "upper": [180,255,255]},
    {"name": "red_medium_1", "lower": [0,60,150], "upper": [12,255,255]},
    {"name": "red_medium_2", "lower": [168,60,150], "upper": [180,255,255]},
    {"name": "red_strict_1", "lower": [0,70,180], "upper": [8,255,255]},
    {"name": "red_strict_2", "lower": [172,70,180], "upper": [180,255,255]},
    
    # 蓝色范围
    {"name": "blue_wide", "lower": [100,50,50], "upper": [130,255,255]},
    {"name": "blue_medium", "lower": [105,100,100], "upper": [125,255,255]},
    {"name": "blue_strict", "lower": [110,150,150], "upper": [120,255,255]},
    
    # 绿色范围
    {"name": "green_wide", "lower": [40,50,50], "upper": [80,255,255]},
    {"name": "green_medium", "lower": [45,100,100], "upper": [75,255,255]},
    {"name": "green_strict", "lower": [50,150,150], "upper": [70,255,255]},
    
    # 黄色范围
    {"name": "yellow_wide", "lower": [20,50,50], "upper": [35,255,255]},
    {"name": "yellow_medium", "lower": [25,100,100], "upper": [30,255,255]},
    
    # 组合两个红色范围
    {"name": "red_combined_1", "lower1": [0,60,150], "upper1": [12,255,255], 
                               "lower2": [168,60,150], "upper2": [180,255,255]},
    {"name": "red_combined_2", "lower1": [0,70,180], "upper1": [8,255,255], 
                               "lower2": [172,70,180], "upper2": [180,255,255]},
]

print("\n正在生成不同阈值的结果...")

for t in thresholds:
    # 重新读取同一帧（保证对比公平）
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    ret, frame = cap.read()
    if not ret:
        continue
    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # 处理颜色范围（可能需要两个范围）
    if "lower1" in t:  # 组合两个范围
        lower1 = np.array(t["lower1"])
        upper1 = np.array(t["upper1"])
        lower2 = np.array(t["lower2"])
        upper2 = np.array(t["upper2"])
        
        mask1 = cv2.inRange(hsv, lower1, upper1)
        mask2 = cv2.inRange(hsv, lower2, upper2)
        mask = cv2.bitwise_or(mask1, mask2)
    else:  # 单个范围
        lower = np.array(t["lower"])
        upper = np.array(t["upper"])
        mask = cv2.inRange(hsv, lower, upper)
    
    # 形态学处理
    kernel = np.ones((3,3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    # 在原图上画出轮廓
    result = frame.copy()
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 创建只显示检测区域的图像
    detected_only = np.zeros_like(frame)
    detected_only[mask > 0] = frame[mask > 0]
    
    # 计算总面积和最大轮廓
    total_area = 0
    valid_contours = 0
    
    if contours:
        # 找出最大的轮廓
        max_contour = max(contours, key=cv2.contourArea)
        max_area = cv2.contourArea(max_contour)
        
        # 绘制所有轮廓
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 100:  # 忽略太小的噪声
                valid_contours += 1
                total_area += area
                cv2.drawContours(result, [contour], -1, (0,255,0), 2)
        
        # 计算最大轮廓的中心
        M = cv2.moments(max_contour)
        if M["m00"] > 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            # 绘制中心颜色，可以调节：
            cv2.circle(result, (cx, cy), 5, (255,255,255), -1)
        
        # 添加文字说明
        color_name = t['name'].split('_')[0].upper()
        
        if "lower1" in t:
            hsv_text = f"{color_name}: R1=[{t['lower1']}-{t['upper1']}] R2=[{t['lower2']}-{t['upper2']}]"
        else:
            hsv_text = f"{color_name}: [{t['lower']} - {t['upper']}]"
        
        # 在图像上显示信息
        y_offset = 30
        for i, text in enumerate([hsv_text[:40], 
                                  f"Areas: {valid_contours} | Total: {int(total_area)} | Max: {int(max_area)}"]):
            if text:
                cv2.putText(result, text, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 
                           0.5, (0,0,0), 3)
                cv2.putText(result, text, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 
                           0.5, (0,255,255), 1)
                y_offset += 25
    
    # 保存结果
    cv2.imwrite(f"{save_dir}/{t['name']}_mask.jpg", mask)
    cv2.imwrite(f"{save_dir}/{t['name']}_result.jpg", result)
    cv2.imwrite(f"{save_dir}/{t['name']}_detected.jpg", detected_only)
    print(f"✅ 已保存: {t['name']}_mask.jpg, {t['name']}_result.jpg, {t['name']}_detected.jpg")

# 输出调试建议
print("\n" + "="*60)
print("HSV阈值调试建议：")
print("="*60)
print("\n常见颜色的HSV范围：")
print("红色 (Red):   H: 0-10 和 160-180, S: 50-255, V: 50-255")
print("蓝色 (Blue):  H: 100-130, S: 50-255, V: 50-255")
print("绿色 (Green): H: 40-80, S: 50-255, V: 50-255")
print("黄色 (Yellow):H: 20-35, S: 50-255, V: 50-255")
print("\n根据光照条件调整：")
print("- 强光下：提高V下限到150-200，提高S下限到70-100")
print("- 弱光下：降低V下限到30-50，保持S下限50左右")
print("- 颜色鲜艳：S下限可以提高到80-100")
print("- 颜色暗淡：S下限降低到30-40")

print("\n" + "="*60)
print("调试完成！")
print(f"所有图片保存在: {save_dir}/")
print("\n文件说明：")
print("  *_mask.jpg     - 二值化掩码图像")
print("  *_result.jpg   - 在原图上画出轮廓的结果")
print("  *_detected.jpg - 只显示检测到的颜色区域")
print("="*60)
print("\n查看结果：")
print(f"  scp -r annon@你的树莓派IP:~/Car_Project/{save_dir} ./")
print(f"  eog {save_dir}/red_combined_1_result.jpg")

cap.release()