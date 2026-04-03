
'''负责 OpenCV 图像处理和误差识别'''

import cv2
import numpy as np

class Vision:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.lower_red = np.array([0, 60, 150])
        self.upper_red = np.array([12, 255, 255])

    def get_error(self):
        ret, frame = self.cap.read()
        if not ret: return None, None
        
        h, w = frame.shape[:2]
        roi = frame[int(h*0.5):h, :]
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower_red, self.upper_red)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            max_cnt = max(contours, key=cv2.contourArea)
            if cv2.contourArea(max_cnt) > 500:
                M = cv2.moments(max_cnt)
                cx = int(M["m10"] / M["m00"])
                return cx - (w // 2), frame
        return None, frame

    def release(self):
        self.cap.release()