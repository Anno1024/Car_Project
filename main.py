#!/usr/bin/env python3
from driver import CarDriver
from odometry import Odometry
from vision import Vision
import time
import math

def run():
    # 初始化三个模块
    car = CarDriver()
    odom = Odometry(wheel_base=0.161)
    eye = Vision()
    
    car.init_car()
    print("🚗 [系统已就绪] 正在执行巡线与实时建模...")

    try:
        while True:
            # 1. 视觉获取误差
            error, _ = eye.get_error()
            
            # 2. 决策逻辑
            if error is not None:
                if abs(error) <= 60:   cmd = 'A'
                elif abs(error) <= 180: cmd = 'B' if error > 0 else 'H'
                else:                  cmd = 'C' if error > 0 else 'G'
                status = "视觉引导"
            else:
                cmd = 'A' # 丢线补偿：惯性直行
                status = "惯性盲开"

            # 3. 执行控制（50ms冲击）
            car.send(cmd)

            # 4. 更新里程计
            vl, vr = car.get_velocity()
            odom.update(vl, vr)

            # 5. 打印状态
            print(f"\r[{status}] Pos:({odom.x:.2f}, {odom.y:.2f}) Angle:{math.degrees(odom.theta):.1f}°", end='')
            
            time.sleep(0.04)

    except KeyboardInterrupt:
        print("\n🛑 正在安全停止并保存地图...")
    finally:
        car.stop()
        eye.release()
        odom.save_data()
        print("✅ 任务完成！")

if __name__ == "__main__":
    run()


    