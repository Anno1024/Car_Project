# test_speed.py
import serial
import time

# 初始化串口
ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=0.01)

# 初始化小车
ser.write(b'K')
time.sleep(0.5)

print("="*50)
print("速度测试：前进 5 秒")
print("="*50)
print("请用尺子测量小车实际前进距离")
print("按 Enter 开始测试...")
input()

# 开始计时
start_time = time.time()
count = 0

# 高频发送 A 指令（前进）
while time.time() - start_time < 5:
    ser.write(b'A')
    
    count += 1
    time.sleep(0.02)  # 50Hz

# 停止
ser.write(b'Z')
ser.close()

print("\n" + "="*50)
print(f"已发送 {count} 次 'A' 指令")
print("请测量小车从起点到终点的距离（厘米）")
print("="*50)