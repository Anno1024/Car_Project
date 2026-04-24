import numpy as np
import cv2
from config import config  # 导入配置

class TFTransformer:
    def __init__(self, calib_path=None):
        if calib_path is None:
            calib_path = config.CALIB_PATH
        
        # 加载相机内参
        try:
            data = np.load(calib_path)
            self.mtx = data['camera_matrix']
            self.dist = data['dist_coeffs']
            self.fx = self.mtx[0, 0]
            self.fy = self.mtx[1, 1]
            self.cx = self.mtx[0, 2]
            self.cy = self.mtx[1, 2]
            print(f"✅ 加载标定文件: {calib_path}")
        except Exception as e:
            print(f"❌ 加载标定文件失败: {e}")
            # 使用配置的默认值
            self.fx, self.fy, self.cx, self.cy = 600, 600, 320, 240
        
        # 从配置读取物理参数
        self.camera_height = config.CAMERA_HEIGHT
        self.pitch_angle = np.radians(config.PITCH_ANGLE_DEG)
        self.dx_to_base = config.DX_TO_BASE
        self.v_offset = config.V_OFFSET  # 使用配置的偏移量

    def pixel_to_base_frame(self, u, v):
        v_full = v + self.v_offset
        
        alpha = np.arctan((v_full - self.cy) / self.fy)
        angle_total = self.pitch_angle + alpha
        
        if angle_total <= 0:
            return None, None
        
        dist_horizontal = self.camera_height / np.tan(angle_total)
        dist_lateral = (u - self.cx) * dist_horizontal / self.fx
        
        real_x = dist_horizontal + self.dx_to_base
        real_y = -dist_lateral
        
        return round(real_x, 4), round(real_y, 4)