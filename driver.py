#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
负责所有的串口通信、高频指令冲击和协议解析。
'''

import serial
import re
import time
import threading
from collections import deque

class CarDriver:
    def __init__(self, port='/dev/ttyAMA0', baud=9600):
        self.ser = serial.Serial(port, baud, timeout=0.01)
        
        # 数据缓存
        self.left_speed = 0
        self.right_speed = 0
        self.battery = 0
        self.angle = 0
        
        # 后台解析线程控制
        self.running = False
        self.parser_thread = None
        
        # 数据缓冲区
        self.buffer = ""
        
    def init_car(self):
        """初始化小车"""
        self.ser.write(b'K')
        self.ser.write("{0:20}".encode())
        
        # 启动后台解析线程
        self.start_parser()
        
    def start_parser(self):
        """启动后台数据解析线程"""
        self.running = True
        self.parser_thread = threading.Thread(target=self._parse_loop, daemon=True)
        self.parser_thread.start()
    
    def _parse_loop(self):
        """后台持续解析串口数据（不阻塞主程序）"""
        while self.running:
            if self.ser.in_waiting > 0:
                try:
                    raw = self.ser.read(self.ser.in_waiting).decode('ascii', errors='ignore')
                    self.buffer += raw
                    self._parse_buffer()
                except Exception as e:
                    print(f"解析错误: {e}")
            time.sleep(0.005)  # 5ms 检查一次，不占用CPU
    
    def _parse_buffer(self):
        """解析缓冲区中的所有完整数据包"""
        # 查找所有以 { 开头，以 }$ 结尾的数据包
        pattern = r'\{A(.*?)\}\$'
        matches = re.findall(pattern, self.buffer)
        
        for content in matches:
            parts = content.split(':')
            if len(parts) >= 2:
                self.left_speed = float(parts[0])
                self.right_speed = float(parts[1])
            if len(parts) >= 3:
                self.battery = float(parts[2])
            if len(parts) >= 4:
                self.angle = float(parts[3])
        
        # 清理已处理的数据（保留最后可能的不完整数据）
        last_match_end = self.buffer.rfind('}$')
        if last_match_end != -1:
            self.buffer = self.buffer[last_match_end + 2:]

    def send(self, cmd):
        """发送控制指令"""
        self.ser.write(cmd.encode())

    def get_velocity(self):
        """
        获取最新的左右轮速度（立即返回，不等待）
        返回: (左轮速度_mm_s, 右轮速度_mm_s)
        """
        return self.left_speed, self.right_speed
    
    def get_battery(self):
        """获取电池电量"""
        return self.battery
    
    def get_angle(self):
        """获取平衡角度"""
        return self.angle

    def stop(self):
        """停止小车并释放资源"""
        self.running = False
        self.ser.write(b'Z')
        if self.parser_thread and self.parser_thread.is_alive():
            self.parser_thread.join(timeout=1)
        self.ser.close()