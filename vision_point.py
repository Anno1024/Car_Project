#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import numpy as np
import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from std_msgs.msg import Float32, Float32MultiArray

class TapeDetector:
    def __init__(self):
        rospy.init_node('tape_detector', anonymous=True)
        
        # 参数配置（可调）
        self.hsv_lower = np.array([0, 0, 200])    # 白色色带示例，根据你的色带颜色改
        self.hsv_upper = np.array([180, 30, 255])
        
        # 图像处理参数
        self.roi_height = 240    # 只处理下半部分图像（近处视野）
        self.min_area = 500      # 最小轮廓面积
        
        # 发布数据
        self.pub_error = rospy.Publisher('/tape/error', Float32, queue_size=10)
        self.pub_theta = rospy.Publisher('/tape/theta', Float32, queue_size=10)
        self.pub_debug = rospy.Publisher('/tape/debug_image', Image, queue_size=10)
        
        # 订阅摄像头
        self.bridge = CvBridge()
        self.image_sub = rospy.Subscriber('/camera/image_raw', Image, self.image_callback)
        
        rospy.loginfo("Tape detector initialized")
    
    def image_callback(self, msg):
        try:
            # 1. ROS图像转OpenCV
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            
            # 2. 只处理下半部分（减少计算量，聚焦近处）
            h, w = cv_image.shape[:2]
            roi = cv_image[h-self.roi_height:h, :]
            
            # 3. 颜色空间转换 + 阈值分割
            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, self.hsv_lower, self.hsv_upper)
            
            # 4. 形态学去噪
            kernel = np.ones((5,5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            
            # 5. 找轮廓
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            error = 0.0
            theta = 0.0
            
            if contours:
                # 取最大轮廓（应该是色带）
                max_contour = max(contours, key=cv2.contourArea)
                area = cv2.contourArea(max_contour)
                
                if area > self.min_area:
                    # 方法1：重心法计算偏移
                    M = cv2.moments(max_contour)
                    if M["m00"] > 0:
                        cx = int(M["m10"] / M["m00"])
                        cy = int(M["m01"] / M["m00"])
                        
                        # 误差 = 中心点x坐标 - 图像中心
                        error = cx - roi.shape[1]//2
                        
                        # 方法2：拟合直线计算角度（可选）
                        rows, cols = roi.shape[:2]
                        [vx, vy, x, y] = cv2.fitLine(max_contour, cv2.DIST_L2, 0, 0.01, 0.01)
                        theta = np.arctan2(vy, vx) * 180 / np.pi  # 角度
                        
                        # 可视化
                        cv2.drawContours(roi, [max_contour], -1, (0,255,0), 2)
                        cv2.circle(roi, (cx, cy), 5, (0,0,255), -1)
                        cv2.line(roi, (roi.shape[1]//2, 0), (roi.shape[1]//2, roi.shape[0]), (255,0,0), 2)
                        
                        # 显示偏差值
                        cv2.putText(roi, f"Error: {error:.1f}", (10, 30), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
            
            # 发布数据
            self.pub_error.publish(error)
            self.pub_theta.publish(theta)
            
            # 发布调试图像（把处理结果拼回原图）
            cv_image[h-self.roi_height:h, :] = roi
            debug_msg = self.bridge.cv2_to_imgmsg(cv_image, "bgr8")
            self.pub_debug.publish(debug_msg)
            
        except Exception as e:
            rospy.logerr(f"Image processing error: {e}")
    
    def run(self):
        rospy.spin()

if __name__ == '__main__':
    try:
        detector = TapeDetector()
        detector.run()
    except rospy.ROSInterruptException:
        pass