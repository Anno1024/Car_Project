#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from driver import CarDriver
from odometry import Odometry
from vision import Vision
from tf_transformer import TFTransformer
from config import config  # 导入配置
import time
import math
import os

def run():
    # 打印当前配置
    config.print_config()
    
    # 1. 初始化所有硬件与算法模块
    car = CarDriver()
    # 使用配置文件中的轮距
    odom = Odometry(wheel_base=config.WHEEL_BASE)
    eye = Vision()
    tf = TFTransformer()
    
    # 2. 清理旧的地图数据文件（使用配置文件中的路径）
    for f in [config.TRAJ_FILE, config.MAP_FILE]:
        if os.path.exists(f):
            os.remove(f)
            print(f"📁 已清理旧文件: {f}")

    car.init_car()
    print("🚗 [系统已就绪] 正在执行巡线与实时建模...")
    print("提示: 按下 Ctrl+C 停止运行并保存地图数据。")

    # 定义一些统计变量
    last_map_time = 0
    map_interval = config.MAP_INTERVAL  # 使用配置的地图记录间隔
    loop_count = 0
    last_print_time = time.time()

    try:
        while True:
            # --- 步骤 1: 视觉感知 ---
            # error 用于控制, cx/cy 用于坐标转换
            error, cx, cy, frame = eye.get_line_data()
            
            # --- 步骤 2: 决策与执行控制 ---
            # 决策逻辑
            if error is not None:
                abs_err = abs(error)
                
                if abs_err <= config.SPEED_ZONES['straight']['max_error']:
                    cmd = config.SPEED_ZONES['straight']['cmd']
                    
                elif abs_err <= config.SPEED_ZONES['micro_turn']['max_error']:
                    cmd = config.SPEED_ZONES['micro_turn']['cmd_right'] if error > 0 \
                        else config.SPEED_ZONES['micro_turn']['cmd_left']
                        
                elif abs_err <= config.SPEED_ZONES['medium_turn']['max_error']:
                    cmd = config.SPEED_ZONES['medium_turn']['cmd_right'] if error > 0 \
                        else config.SPEED_ZONES['medium_turn']['cmd_left']
                        
                else:
                    cmd = config.SPEED_ZONES['large_turn']['cmd_right'] if error > 0 \
                        else config.SPEED_ZONES['large_turn']['cmd_left']
                
                status = "视觉引导"

            car.send(cmd)

            # --- 步骤 3: 运动学更新 (里程计) ---
            vl, vr = car.get_velocity()
            odom.update(vl, vr)

            # --- 步骤 4: 实时建模 (TF 坐标变换) ---
            current_time = time.time()
            if cx is not None and (current_time - last_map_time) > map_interval:
                # A. 像素坐标 -> 小车系物理坐标 (dx, dy)
                dx, dy = tf.pixel_to_base_frame(cx, cy)
                
                if dx is not None:
                    # B. 小车系 -> 全局地图坐标 (GX, GY)
                    gx, gy = odom.transform_to_global(dx, dy)
                    
                    # C. 记录红线位置到文件（使用配置文件中的路径）
                    with open(config.MAP_FILE, "a") as f_map:
                        f_map.write(f"{gx:.4f}, {gy:.4f}\n")
                    
                    last_map_time = current_time
                    loop_count += 1

            # --- 步骤 5: 实时反馈打印（降低打印频率，提高性能）---
            if current_time - last_print_time > 0.2:  # 每0.2秒打印一次
                print(f"\r[{status}] 车位姿:({odom.x:.2f}, {odom.y:.2f}) 角度:{math.degrees(odom.theta):.1f}° 地图点:{loop_count}", end='')
                last_print_time = current_time
            
            # 使用配置文件中的循环间隔
            time.sleep(config.CONTROL_LOOP_DT)

    except KeyboardInterrupt:
        print("\n🛑 收到停止指令，正在安全关闭...")
    except Exception as e:
        print(f"\n❌ 运行中发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 6. 资源释放与数据保存
        car.stop()
        eye.release()
        odom.save_data(config.TRAJ_FILE)  # 使用配置文件中的路径保存小车行驶轨迹
        print("✅ 数据已保存。")
        print(f"   - 轨迹数据: {config.TRAJ_FILE}")
        print(f"   - 红线地图: {config.MAP_FILE}")
        print(f"   - 总地图点数: {loop_count}")
        print("🚀 任务圆满完成！")

if __name__ == "__main__":
    run()