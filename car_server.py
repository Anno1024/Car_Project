#!/usr/bin/env python3
"""
小车服务端 - 最终版（支持超低速）
运行在树莓派上，接收UDP命令，通过串口控制小车
"""

import serial
import time
import socket
import threading
import queue
import os
import signal
import sys

class CarServer:
    def __init__(self, serial_port='/dev/ttyAMA0', baudrate=9600, udp_port=8888):
        """
        初始化服务器
        """
        print("\n" + "="*60)
        print("🚗 小车服务端 v3.1 (超低速版)")
        print("="*60)
        
        # 运行状态
        self.running = True
        self.current_speed = 20  # 默认速度改为20%（更慢）
        self.current_direction = None  # 当前方向
        
        # 速度映射表 - 将客户端速度%映射到实际PWM值
        self.speed_map = {
            0: 0,      # 停止
            10: 15,    # 超低速
            20: 25,    # 非常慢
            30: 35,    # 慢
            40: 45,    # 较慢
            50: 55,    # 中慢
            60: 65,    # 中等
            70: 75,    # 中快
            80: 85,    # 快
            90: 92,    # 很快
            100: 100,  # 最快
        }
        
        # 命令队列
        self.cmd_queue = queue.Queue()
        self.last_send_time = 0
        self.send_interval = 0.05  # 50ms
        
        # 初始化各模块
        self.init_serial(serial_port, baudrate)
        self.init_udp(udp_port)
        
        # 启动线程
        self.start_threads()
        
        print("\n✅ 服务端初始化完成")
        self.print_status()
    
    def init_serial(self, port, baudrate):
        """初始化串口"""
        print(f"\n🔌 初始化串口: {port}")
        try:
            # 确保串口权限
            os.system(f'sudo chmod 666 {port} 2>/dev/null')
            
            self.ser = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=0.01,
                write_timeout=0.01
            )
            time.sleep(0.5)
            
            # 清空缓冲区
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            
            # 切换到按键模式
            print("   切换到按键模式...")
            self.ser.write(b'K')
            self.ser.flush()
            time.sleep(0.1)
            
            print(f"   ✅ 串口初始化成功")
            
        except Exception as e:
            print(f"   ❌ 串口初始化失败: {e}")
            print("   程序退出")
            sys.exit(1)
    
    def init_udp(self, port):
        """初始化UDP服务器"""
        print(f"\n📡 初始化UDP服务器: 端口 {port}")
        try:
            self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.udp_socket.bind(('0.0.0.0', port))
            self.udp_socket.settimeout(0.1)
            print(f"   ✅ UDP服务器启动成功")
            
        except Exception as e:
            print(f"   ❌ UDP服务器初始化失败: {e}")
            print("   程序退出")
            sys.exit(1)
    
    def start_threads(self):
        """启动所有线程"""
        # 发送线程
        self.send_thread = threading.Thread(target=self.send_loop)
        self.send_thread.daemon = True
        self.send_thread.start()
        
        # 接收线程
        self.recv_thread = threading.Thread(target=self.recv_loop)
        self.recv_thread.daemon = True
        self.recv_thread.start()
        
        # 状态显示线程
        self.status_thread = threading.Thread(target=self.status_loop)
        self.status_thread.daemon = True
        self.status_thread.start()
    
    def send_loop(self):
        """
        发送线程 - 保证50ms精确间隔
        """
        while self.running:
            current_time = time.time()
            
            # 处理命令队列
            if not self.cmd_queue.empty() and current_time - self.last_send_time >= self.send_interval:
                try:
                    cmd = self.cmd_queue.get_nowait()
                    
                    # 如果是速度参数，应用速度映射
                    if isinstance(cmd, tuple) and cmd[0] == 'speed':
                        speed_percent = cmd[1]
                        actual_speed = self.speed_map.get(speed_percent, speed_percent)
                        speed_cmd = f"{{0:{actual_speed}}}"
                        self.ser.write(speed_cmd.encode('ascii'))
                        print(f"\n   [速度映射] {speed_percent}% → {actual_speed}")
                    else:
                        self.ser.write(cmd.encode('ascii'))
                    
                    self.ser.flush()
                    self.last_send_time = current_time
                except Exception as e:
                    print(f"发送错误: {e}")
            
            time.sleep(0.001)  # 1ms精度
    
    def recv_loop(self):
        """
        接收线程 - 处理UDP命令
        """
        while self.running:
            try:
                data, addr = self.udp_socket.recvfrom(1024)
                cmd = data.decode().strip().lower()
                self.handle_command(cmd, addr)
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"\n❌ 接收错误: {e}")
    
    def handle_command(self, cmd, addr):
        """
        处理接收到的命令
        """
        # 心跳包不显示
        if cmd == 'heartbeat':
            return
        
        # 方向控制
        if cmd in ['w', 's', 'a', 'd']:
            dir_map = {'w': 'A', 's': 'E', 'a': 'G', 'd': 'C'}
            serial_cmd = dir_map[cmd]
            
            # 加入队列
            self.cmd_queue.put(serial_cmd)
            self.current_direction = cmd
            
            # 显示
            dir_names = {'w': '前进', 's': '后退', 'a': '左转', 'd': '右转'}
            print(f"\n▶️ {dir_names[cmd]} [{serial_cmd}] | 速度: {self.current_speed}% | 客户端: {addr[0]}")
        
        # 停止
        elif cmd == 'stop':
            self.cmd_queue.put('Z')
            self.current_direction = None
            print(f"\n⏹️ 停止 | 客户端: {addr[0]}")
        
        # 加速
        elif cmd == 'x':
            self.current_speed = min(100, self.current_speed + 5)  # 每次加5%
            # 发送速度参数
            self.cmd_queue.put(('speed', self.current_speed))
            # 同时发送加速指令（如果需要）
            self.cmd_queue.put('X')
            
            # 显示速度条
            speed_bar = self.get_speed_bar()
            print(f"\n⚡ 加速: {self.current_speed}% {speed_bar}")
        
        # 减速
        elif cmd == 'y':
            self.current_speed = max(5, self.current_speed - 5)  # 每次减5%，最低5%
            # 发送速度参数
            self.cmd_queue.put(('speed', self.current_speed))
            # 同时发送减速指令（如果需要）
            self.cmd_queue.put('Y')
            
            # 显示速度条
            speed_bar = self.get_speed_bar()
            print(f"\n⚡ 减速: {self.current_speed}% {speed_bar}")
        
        # 预设速度 (0-9) - 支持更精细的控制
        elif cmd in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            speed_map = {
                '0': 0,    # 停止
                '1': 5,    # 极慢
                '2': 10,   # 非常慢
                '3': 15,   # 很慢
                '4': 20,   # 慢
                '5': 30,   # 较慢
                '6': 40,   # 中慢
                '7': 50,   # 中等
                '8': 60,   # 中快
                '9': 70,   # 快
            }
            speed = speed_map[cmd]
            self.current_speed = speed
            
            # 发送速度参数
            self.cmd_queue.put(('speed', speed))
            
            speed_bar = self.get_speed_bar()
            print(f"\n🎯 预设速度 {cmd}: {speed}% {speed_bar}")
        
        # 参数设置 (格式: p0=100)
        elif cmd.startswith('p') and '=' in cmd:
            try:
                param = cmd[1:].split('=')[0]
                value = int(cmd.split('=')[1])
                param_cmd = f"{{{param}:{value}}}"
                self.cmd_queue.put(param_cmd)
                print(f"\n📊 参数 {param} = {value}")
            except:
                pass
        
        # 获取状态
        elif cmd == 'status':
            self.send_status(addr)
        
        # 测试命令
        elif cmd == 'test':
            print(f"\n📡 收到测试信号 | 客户端: {addr[0]}")
        
        # 退出
        elif cmd == 'q':
            print(f"\n👋 收到退出命令 | 客户端: {addr[0]}")
        
        # 未知命令
        else:
            print(f"\n⚠️ 未知命令: {cmd} | 客户端: {addr[0]}")
    
    def get_speed_bar(self, length=20):
        """获取速度进度条"""
        filled = int(length * self.current_speed / 100)
        return '█' * filled + '░' * (length - filled)
    
    def send_status(self, addr):
        """发送状态给客户端"""
        status = f"速度:{self.current_speed}% 方向:{self.current_direction}"
        self.udp_socket.sendto(status.encode(), addr)
    
    def status_loop(self):
        """状态显示线程"""
        last_display = 0
        while self.running:
            current_time = time.time()
            if current_time - last_display > 2:  # 每2秒显示一次
                self.print_status()
                last_display = current_time
            time.sleep(1)
    
    def print_status(self):
        """显示状态"""
        dir_names = {'w': '前进', 's': '后退', 'a': '左转', 'd': '右转', None: '停止'}
        direction = dir_names.get(self.current_direction, '未知')
        queue_size = self.cmd_queue.qsize()
        speed_bar = self.get_speed_bar(30)
        
        print(f"\r📊 状态 | 速度: {self.current_speed:3d}% {speed_bar} | 方向: {direction} | 队列: {queue_size}", end='', flush=True)
    
    def run(self):
        """运行主程序"""
        print("\n" + "="*60)
        print("服务端运行中... 按 Ctrl+C 停止")
        print("速度范围: 0-100% (实际映射到0-100)")
        print("超低速: 5%, 10%, 15%, 20% 可用数字键 1-4 设置")
        print("="*60)
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n👋 正在停止服务端...")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """清理资源"""
        print("\n🧹 清理中...")
        self.running = False
        
        time.sleep(0.2)
        
        # 发送停止指令
        if hasattr(self, 'ser'):
            try:
                print("   发送停止指令...")
                for _ in range(3):
                    self.ser.write(b'Z')
                    self.ser.flush()
                    time.sleep(0.05)
                self.ser.close()
                print("   ✅ 串口已关闭")
            except:
                pass
        
        # 关闭UDP
        if hasattr(self, 'udp_socket'):
            try:
                self.udp_socket.close()
                print("   ✅ UDP已关闭")
            except:
                pass
        
        print("\n✨ 服务端已停止")
        print("="*60)

def main():
    # 设置信号处理
    def signal_handler(sig, frame):
        print("\n\n👋 收到中断信号")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # 创建并运行服务器
    server = CarServer()
    server.run()

if __name__ == "__main__":
    main()