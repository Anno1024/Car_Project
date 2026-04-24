#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 文件名: config.py

import numpy as np

class Config:
    """系统配置类"""
    
    def __init__(self):
        # ========== 1. 视觉参数 ==========
        # 摄像头设置
        self.CAMERA_ID = 0
        self.FRAME_WIDTH = 640
        self.FRAME_HEIGHT = 480
        
        # ROI (Region of Interest) 设置
        # roi_ratio: 裁剪比例，0.7 表示保留图像下 30% 区域（近点）
        # 范围: 0.0 ~ 1.0
        #   - 0.5: 保留下半部分 50%（中等距离）
        #   - 0.7: 保留下半部分 30%（很近，稳定）
        #   - 0.3: 保留下半部分 70%（较远，预判）
        self.ROI_RATIO = 0.7  # 推荐: 低速(0.3m/s)用0.7，高速(0.8m/s)用0.5
        
        # 红色HSV阈值（可调整）
        self.RED_LOWER = np.array([0, 60, 150])
        self.RED_UPPER = np.array([12, 255, 255])
        
        # 形态学核大小
        self.MORPH_KERNEL_SIZE = (5, 5)
        
        # 红色区域最小面积（过滤噪点）
        self.MIN_RED_AREA = 300
        
        # ========== 2. 控制参数 ==========
        # 速度档位（根据error范围）
        self.SPEED_ZONES = {
        'straight': {'max_error': 50, 'cmd': 'A'},           # 直行（偏移<50）
        'micro_turn': {'max_error': 100, 'cmd_right': 'B', 'cmd_left': 'H'},  # 小转/微调（50-100）
        'medium_turn': {'max_error': 200, 'cmd_right': 'C', 'cmd_left': 'G'}, # 中转（100-200）
        'large_turn': {'cmd_right': 'D', 'cmd_left': 'F'}    # 大转（>200）
        }
        
        # 丢线时的默认指令
        self.LOST_LINE_CMD = 'A'  # 直行
        
        # ========== 3. 里程计参数 ==========
        self.WHEEL_BASE = 0.161  # 轮距（米）
        self.VELOCITY_UNIT_CONV = 0.001  # mm/s -> m/s
        
        # ========== 4. 建图参数 ==========
        self.MAP_INTERVAL = 0.1  # 地图点记录间隔（秒）
        self.CONTROL_LOOP_DT = 0.04  # 控制循环间隔（秒）-> 25Hz
        
        # ========== 5. TF变换参数 ==========
        self.CAMERA_HEIGHT = 0.075  # 相机高度（米）
        self.PITCH_ANGLE_DEG = 50   # 俯角（度）
        self.DX_TO_BASE = 0.14      # 相机到小车中心距离（米）
        
        # 图像偏移（如果裁剪了ROI）
        self.V_OFFSET = int(self.FRAME_HEIGHT * self.ROI_RATIO)  # 自动计算
        
        # 标定文件路径
        self.CALIB_PATH = 'calibration_result/camera_calibration_result.npz'
        
        # ========== 6. 文件路径 ==========
        self.TRAJ_FILE = 'map_data.txt'
        self.MAP_FILE = 'my_map.txt'
        self.RESULT_DIR = 'map_results'
        
    def update_roi(self, roi_ratio):
        """动态更新ROI比例"""
        self.ROI_RATIO = roi_ratio
        self.V_OFFSET = int(self.FRAME_HEIGHT * self.ROI_RATIO)
        print(f"📷 ROI已更新: {roi_ratio:.2f} (保留图像下 {100*(1-roi_ratio):.0f}%)")
    
    def get_roi_slice(self):
        """获取ROI切片索引"""
        roi_start = int(self.FRAME_HEIGHT * self.ROI_RATIO)
        return slice(roi_start, self.FRAME_HEIGHT)
    
    def print_config(self):
        """打印当前配置"""
        print("="*50)
        print("系统配置")
        print("="*50)
        print(f"📷 摄像头: {self.FRAME_WIDTH}x{self.FRAME_HEIGHT}")
        print(f"🎯 ROI比例: {self.ROI_RATIO:.2f} (保留图像下 {100*(1-self.ROI_RATIO):.0f}%)")
        print(f"🔴 红色阈值: H[{self.RED_LOWER[0]}-{self.RED_UPPER[0]}] "
            f"S[{self.RED_LOWER[1]}-{self.RED_UPPER[1]}] "
            f"V[{self.RED_LOWER[2]}-{self.RED_UPPER[2]}]")
        print(f"🚗 轮距: {self.WHEEL_BASE*100:.1f}cm")
        
        # 修改这里：使用新的键名
        print(f"🎮 控制档位: 直行<{self.SPEED_ZONES['straight']['max_error']}px, "
            f"小转<{self.SPEED_ZONES['micro_turn']['max_error']}px, "
            f"中转<{self.SPEED_ZONES['medium_turn']['max_error']}px, "
            f"大转>={self.SPEED_ZONES['medium_turn']['max_error']}px")
        
        print(f"🗺️  建图间隔: {self.MAP_INTERVAL*1000:.0f}ms")
        print(f"🔄 控制频率: {int(1/self.CONTROL_LOOP_DT)}Hz")
        print("="*50)


# 创建全局配置实例
config = Config()