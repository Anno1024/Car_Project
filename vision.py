import cv2
import numpy as np
from config import config

class Vision:
    def __init__(self):
        # 从配置文件读取参数
        self.cap = cv2.VideoCapture(config.CAMERA_ID)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
        
        # 红色阈值
        self.lower_red = config.RED_LOWER
        self.upper_red = config.RED_UPPER
        
        # ROI比例（直接从配置读取）
        self.roi_ratio = config.ROI_RATIO
        
        # 形态学核
        self.kernel = np.ones(config.MORPH_KERNEL_SIZE, np.uint8)
        
        # 最小面积
        self.min_area = config.MIN_RED_AREA
        
        print(f"✅ Vision初始化完成")
        print(f"   - ROI比例: {self.roi_ratio:.2f}")
        print(f"   - 红色阈值: H[{self.lower_red[0]}-{self.upper_red[0]}]")

    def get_line_data(self):
        ret, frame = self.cap.read()
        if not ret:
            return None, None, None, None
        
        h, w = frame.shape[:2]
        
        # 使用配置的ROI比例
        roi_start_h = int(h * self.roi_ratio)
        roi = frame[roi_start_h:h, :]
        
        # 颜色识别
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower_red, self.upper_red)
        
        # 形态学操作
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, self.kernel)
        
        # 寻找轮廓
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            max_cnt = max(contours, key=cv2.contourArea)
            if cv2.contourArea(max_cnt) > self.min_area:
                M = cv2.moments(max_cnt)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    error = cx - (w // 2)
                    return error, cx, cy, frame
        
        return None, None, None, frame

    def release(self):
        self.cap.release()