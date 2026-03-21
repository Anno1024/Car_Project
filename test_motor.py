#!/usr/bin/env python3
import serial
import time

ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=1)
time.sleep(0.5)

print("切换到按键模式...")
ser.write(b'K')
time.sleep(0.1)

print("设置速度20%...")
ser.write(b'{0:20}')
time.sleep(0.1)

print("开始持续发送前进指令 (A)...")
print("按 Ctrl+C 停止")

try:
    count = 0
    while True:
        ser.write(b'A')
        count += 1
        if count % 20 == 0:  # 每秒显示一次（20*50ms=1秒）
            print(f"已发送 {count} 次前进指令")
        time.sleep(0.05)  # 50ms一次
except KeyboardInterrupt:
    print(f"\n停止，共发送 {count} 次")
finally:
    ser.write(b'Z')
    ser.close()