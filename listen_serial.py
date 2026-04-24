#!/usr/bin/env python3


'''
用于测试是否能够接收到小车的数据包
'''


import serial
import time
import sys

# ========== 配置 ==========
SERIAL_PORT = '/dev/ttyAMA0'  # 如果不行试试 /dev/ttyUSB0
BAUDRATE = 9600  # 如果没数据试试 115200

print("="*60)
print("🔍 串口持续监听工具")
print("="*60)
print(f"端口: {SERIAL_PORT}")
print(f"波特率: {BAUDRATE}")
print("按 Ctrl+C 停止")
print("="*60)

try:
    # 打开串口
    ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=0.1)
    time.sleep(0.5)
    
    # 发送按键模式（确保小车在正确状态）
    ser.write(b'K')
    time.sleep(0.1)
    print("✅ 已发送 K (按键模式)")
    
    # 尝试开启数据上报
    ser.write(b'{A}')
    print("✅ 已发送 {A} (请求状态数据)")
    print("\n开始监听...\n")
    
    count = 0
    while True:
        if ser.in_waiting > 0:
            # 读取所有可用数据
            data = ser.read(ser.in_waiting).decode('ascii', errors='ignore')
            
            # 打印原始数据
            for char in data:
                if char == '{':
                    print(f"\n[{count+1}] ", end='')
                print(char, end='', flush=True)
                count += 1
        time.sleep(0.01)
        
except KeyboardInterrupt:
    print("\n\n👋 停止监听")
    print(f"总共收到 {count} 个字符")
    
except Exception as e:
    print(f"错误: {e}")
    
finally:
    if 'ser' in locals():
        ser.close()