#!/usr/bin/env python3
import cv2
import numpy as np

def nothing(x):
    pass

# 创建窗口和滑动条
cv2.namedWindow('Tuning')
cv2.createTrackbar('H_min', 'Tuning', 0, 180, nothing)
cv2.createTrackbar('H_max', 'Tuning', 180, 180, nothing)
cv2.createTrackbar('S_min', 'Tuning', 0, 255, nothing)
cv2.createTrackbar('S_max', 'Tuning', 30, 255, nothing)
cv2.createTrackbar('V_min', 'Tuning', 200, 255, nothing)
cv2.createTrackbar('V_max', 'Tuning', 255, 255, nothing)

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # 获取当前阈值
    h_min = cv2.getTrackbarPos('H_min', 'Tuning')
    h_max = cv2.getTrackbarPos('H_max', 'Tuning')
    s_min = cv2.getTrackbarPos('S_min', 'Tuning')
    s_max = cv2.getTrackbarPos('S_max', 'Tuning')
    v_min = cv2.getTrackbarPos('V_min', 'Tuning')
    v_max = cv2.getTrackbarPos('V_max', 'Tuning')
    
    lower = np.array([h_min, s_min, v_min])
    upper = np.array([h_max, s_max, v_max])
    
    mask = cv2.inRange(hsv, lower, upper)
    
    # 显示结果
    cv2.imshow('Original', frame)
    cv2.imshow('Mask', mask)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()