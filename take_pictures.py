#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
相机拍照脚本 - 纯手动版
按回车拍照，输入命令控制
"""

import cv2
import os
import sys
import tty
import termios
import select
import time
from datetime import datetime

# ==================== 配置 ====================
CAMERA_ID = 0
SAVE_DIR = "camera_calibration_pictures"
IMAGE_FORMAT = "jpg"  # 可选 jpg 或 png
# ==============================================

def get_key_nonblock():
    """非阻塞获取键盘输入"""
    if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
        return sys.stdin.read(1)
    return None

def get_next_filename():
    """获取下一个可用的文件名"""
    os.makedirs(SAVE_DIR, exist_ok=True)
    files = [f for f in os.listdir(SAVE_DIR) 
             if f.startswith("calib_") and f.endswith(f".{IMAGE_FORMAT}")]
    
    if not files:
        return "calib_001"
    
    numbers = []
    for f in files:
        try:
            # 提取 "calib_XXX" 中的数字
            num = int(f[6:9])
            numbers.append(num)
        except:
            continue
    
    next_num = max(numbers) + 1 if numbers else 1
    return f"calib_{next_num:03d}"

def main():
    print("="*60)
    print("相机标定图片采集工具 - 手动控制版")
    print("="*60)
    
    # 显示当前文件夹中的照片数量
    os.makedirs(SAVE_DIR, exist_ok=True)
    existing = [f for f in os.listdir(SAVE_DIR) 
                if f.startswith("calib_") and f.endswith(f".{IMAGE_FORMAT}")]
    print(f"\n当前文件夹: {os.path.abspath(SAVE_DIR)}")
    print(f"已有照片: {len(existing)} 张")
    if existing:
        print(f"最新照片: {sorted(existing)[-1]}")
    
    # 打开摄像头
    cap = cv2.VideoCapture(CAMERA_ID)
    if not cap.isOpened():
        print(f"\n错误：无法打开摄像头 {CAMERA_ID}")
        print("可能的原因：")
        print("  1. 摄像头编号不对 (试试改成 1)")
        print("  2. 摄像头被其他程序占用")
        print("  3. 没有摄像头驱动")
        return
    
    # 获取分辨率
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"\n摄像头信息:")
    print(f"  - 设备ID: {CAMERA_ID}")
    print(f"  - 分辨率: {w} x {h}")
    
    print("\n" + "-"*60)
    print("操作说明:")
    print("  【空格/回车】- 拍照")
    print("  【l】         - 列出当前文件夹所有照片")
    print("  【c】         - 显示当前数量")
    print("  【q】         - 退出程序")
    print("-"*60)
    
    # 设置终端为原始模式，这样可以直接读取按键
    old_settings = termios.tcgetattr(sys.stdin)
    tty.setraw(sys.stdin.fileno())
    
    photo_count = 0
    try:
        while True:
            # 读取一帧
            ret, frame = cap.read()
            if not ret:
                print("\n无法读取摄像头画面")
                break
            
            # 获取下一个文件名
            next_name = get_next_filename()
            next_num = int(next_name[6:9])
            
            # 清空行并显示状态（用回车符覆盖）
            status = f"\r准备拍照: {next_name}.{IMAGE_FORMAT} | 已拍: {photo_count} 张 | 文件夹: {len(existing)} 张 | 按空格拍照，q退出"
            print(status, end="", flush=True)
            
            # 检查按键
            key = get_key_nonblock()
            if key:
                if key == ' ' or key == '\r' or key == '\n':  # 空格或回车
                    # 拍照
                    filename = os.path.join(SAVE_DIR, f"{next_name}.{IMAGE_FORMAT}")
                    cv2.imwrite(filename, frame)
                    photo_count += 1
                    existing.append(f"{next_name}.{IMAGE_FORMAT}")
                    
                    # 显示成功消息（换行打印，避免覆盖状态行）
                    print(f"\n✅ [{datetime.now().strftime('%H:%M:%S')}] 已保存: {filename}")
                    
                elif key == 'l' or key == 'L':
                    # 列出所有照片
                    print("\n📸 文件夹中的照片:")
                    all_files = sorted([f for f in os.listdir(SAVE_DIR) 
                                       if f.startswith("calib_") and f.endswith(f".{IMAGE_FORMAT}")])
                    for i, f in enumerate(all_files):
                        print(f"   {i+1:2d}. {f}")
                    print(f"   共 {len(all_files)} 张")
                    
                elif key == 'c' or key == 'C':
                    # 显示数量
                    current = len([f for f in os.listdir(SAVE_DIR) 
                                  if f.startswith("calib_") and f.endswith(f".{IMAGE_FORMAT}")])
                    print(f"\n📊 当前文件夹: {current} 张照片")
                    print(f"   本此运行已拍: {photo_count} 张")
                    
                elif key == 'q' or key == 'Q':
                    # 退出
                    print("\n\n👋 正在退出...")
                    break
                    
    except KeyboardInterrupt:
        print("\n\n程序被中断")
    finally:
        # 恢复终端设置
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        cap.release()
        print(f"\n拍照结束！本次拍摄: {photo_count} 张")
        total = len([f for f in os.listdir(SAVE_DIR) 
                    if f.startswith("calib_") and f.endswith(f".{IMAGE_FORMAT}")])
        print(f"文件夹总照片: {total} 张")
        print(f"照片位置: {os.path.abspath(SAVE_DIR)}")

if __name__ == "__main__":
    main()
