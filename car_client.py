#!/usr/bin/env python
"""
小车客户端 - 最终版（支持超低速）
运行在Windows上，通过UDP控制小车
"""

import socket
import msvcrt
import sys
import time
import threading
from datetime import datetime


class CarClient:
    def __init__(self, server_ip='10.85.124.171', server_port=8888):
        """
        初始化客户端
        """
        self.server_ip = server_ip
        self.server_port = server_port
        self.sock = None
        self.connected = False
        self.running = True

        # 状态信息
        self.current_direction = None
        self.current_speed = 15  # 默认速度改为15%（更慢）
        self.last_command_time = time.time()
        self.stop_sent = False

        # 统计信息
        self.stats = {
            'commands': 0,
            'stops': 0,
            'start_time': time.time()
        }

        # 命令映射
        self.dir_map = {
            'w': 'w',  # 前进
            's': 's',  # 后退
            'a': 'a',  # 左转
            'd': 'd',  # 右转
        }

        self.dir_names = {
            'w': '前进',
            's': '后退',
            'a': '左转',
            'd': '右转',
        }

        # 速度预设 - 支持超低速
        self.speed_presets = {
            '0': 0,  # 停止
            '1': 5,  # 极慢
            '2': 10,  # 非常慢
            '3': 15,  # 很慢
            '4': 20,  # 慢
            '5': 30,  # 较慢
            '6': 40,  # 中慢
            '7': 50,  # 中等
            '8': 60,  # 中快
            '9': 70,  # 快
        }

        # 连接服务器
        self.connect()

        if self.connected:
            self.print_welcome()
            self.start_monitor()

    def connect(self):
        """连接到服务器"""
        print(f"\n🔍 正在连接到 {self.server_ip}:{self.server_port}...")

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.settimeout(0.5)

            # 发送测试消息
            self.sock.sendto(b'test', (self.server_ip, self.server_port))

            self.connected = True
            print(f"✅ 连接成功！")

        except Exception as e:
            print(f"❌ 连接失败: {e}")
            print("\n请检查：")
            print("1. 树莓派是否开机")
            print("2. 服务器程序是否运行")
            print("3. IP地址是否正确")
            print("4. 网络连接是否正常")

    def start_monitor(self):
        """启动监控线程"""

        def monitor():
            while self.running and self.connected:
                current_time = time.time()

                # 1秒无操作自动停止
                if (self.current_direction and
                        not self.stop_sent and
                        current_time - self.last_command_time > 1.0):
                    self.send_stop()

                time.sleep(0.1)

        thread = threading.Thread(target=monitor)
        thread.daemon = True
        thread.start()

    def send_command(self, cmd):
        """发送命令到服务器"""
        if not self.connected or not self.sock:
            return False

        try:
            self.sock.sendto(cmd.encode(), (self.server_ip, self.server_port))
            self.stats['commands'] += 1
            return True
        except Exception as e:
            print(f"\n❌ 发送失败: {e}")
            self.connected = False
            return False

    def send_direction(self, key):
        """发送方向指令"""
        if not self.connected:
            return

        cmd = self.dir_map[key]
        if self.send_command(cmd):
            self.current_direction = key
            self.stop_sent = False
            self.last_command_time = time.time()

            name = self.dir_names[key]
            speed_bar = self.get_speed_bar()
            print(f"\r▶️ {name} {speed_bar} {self.current_speed}%  ", end='', flush=True)

    def send_stop(self):
        """发送停止指令"""
        if not self.connected or self.stop_sent:
            return

        if self.send_command('stop'):
            self.current_direction = None
            self.stop_sent = True
            self.stats['stops'] += 1
            print(f"\r⏹️ 停止 [已发送{self.stats['stops']}次]  ", end='', flush=True)

    def send_speed_up(self):
        """加速 - 每次加5%"""
        if self.send_command('x'):
            self.current_speed = min(70, self.current_speed + 5)  # 最高70%
            speed_bar = self.get_speed_bar()
            print(f"\r⚡ 加速 {speed_bar} {self.current_speed}%  ", end='', flush=True)

    def send_speed_down(self):
        """减速 - 每次减5%"""
        if self.send_command('y'):
            self.current_speed = max(5, self.current_speed - 5)  # 最低5%
            speed_bar = self.get_speed_bar()
            print(f"\r⚡ 减速 {speed_bar} {self.current_speed}%  ", end='', flush=True)

    def set_preset_speed(self, key):
        """设置预设速度（0-9）"""
        if key in self.speed_presets:
            speed = self.speed_presets[key]
            self.current_speed = speed
            if self.send_command(key):
                speed_bar = self.get_speed_bar()

                # 根据速度显示不同提示
                if speed == 0:
                    msg = "停止"
                elif speed <= 10:
                    msg = "极慢"
                elif speed <= 20:
                    msg = "很慢"
                elif speed <= 30:
                    msg = "较慢"
                elif speed <= 50:
                    msg = "中等"
                else:
                    msg = "快速"

                print(f"\r🎯 {msg} {speed}% {speed_bar}  ", end='', flush=True)

    def get_speed_bar(self, length=20):
        """获取速度进度条"""
        filled = int(length * self.current_speed / 100)
        return '█' * filled + '░' * (length - filled)

    def show_stats(self):
        """显示统计信息"""
        runtime = time.time() - self.stats['start_time']
        print(f"\n\n📊 统计信息:")
        print(f"   运行时间: {runtime:.1f} 秒")
        print(f"   发送命令: {self.stats['commands']} 次")
        print(f"   发送停止: {self.stats['stops']} 次")
        print(f"   停止频率: {self.stats['stops'] / runtime:.2f} 次/秒")
        print(f"   当前速度: {self.current_speed}%")

    def print_welcome(self):
        """显示欢迎信息"""
        print("\n" + "=" * 80)
        print("🚗 小车控制客户端 v3.1 (超低速版)")
        print("=" * 80)
        print(f"📡 服务器: {self.server_ip}:{self.server_port}")
        print(f"🕒 连接时间: {datetime.now().strftime('%H:%M:%S')}")
        print("\n🎮 控制说明：")
        print("┌─────────────┬─────────────────────────────────┐")
        print("│    方向控制  │    速度控制 (支持超低速)        │")
        print("├─────────────┼─────────────────────────────────┤")
        print("│  W: 前进    │  X: +5%    Y: -5%              │")
        print("│  S: 后退    │  0: 0% (停止)  1: 5% (极慢)    │")
        print("│  A: 左转    │  2: 10% (非常慢) 3: 15% (很慢) │")
        print("│  D: 右转    │  4: 20% (慢)    5: 30% (较慢)  │")
        print("│             │  6: 40% (中慢)  7: 50% (中等)  │")
        print("│             │  8: 60% (中快)  9: 70% (快)    │")
        print("└─────────────┴─────────────────────────────────┘")
        print("  空格: 立即停止   1秒无操作: 自动停止")
        print("  P: 显示统计      Q: 退出程序")
        print("=" * 80)
        print(f"\n当前速度: {self.current_speed}% (超低速模式)")
        print("开始控制...\n")

    def run(self):
        """主循环"""
        if not self.connected:
            input("\n按 Enter 键退出...")
            return

        print("等待输入...（按住按键连续运动）")
        print("-" * 50)

        try:
            while self.running:
                if msvcrt.kbhit():
                    key = msvcrt.getch().decode().lower()

                    if key == 'q':
                        print("\n\n👋 正在退出...")
                        self.send_stop()
                        break

                    elif key == 'p':
                        self.show_stats()

                    elif key == ' ':
                        self.send_stop()

                    elif key in self.dir_map:
                        self.send_direction(key)

                    elif key == 'x':
                        self.send_speed_up()

                    elif key == 'y':
                        self.send_speed_down()

                    elif key in self.speed_presets:
                        self.set_preset_speed(key)

                time.sleep(0.02)

        except KeyboardInterrupt:
            print("\n\n👋 用户中断")
        finally:
            self.cleanup()

    def cleanup(self):
        """清理资源"""
        print("\n🧹 清理中...")

        self.running = False
        if self.connected and self.sock:
            self.send_stop()
            time.sleep(0.1)
            self.sock.close()
            print("✅ 连接已关闭")

        self.show_stats()
        print("\n✨ 程序已退出")


def main():
    """主函数"""
    import os

    # 清屏
    os.system('cls' if os.name == 'nt' else 'clear')

    # 获取服务器IP
    if len(sys.argv) > 1:
        server_ip = sys.argv[1]
    else:
        server_ip = '10.85.124.171'
        print(f"使用默认IP: {server_ip}")
        print("如需指定IP: python car_client.py <IP地址>")

    # 创建并运行客户端
    client = CarClient(server_ip)
    client.run()


if __name__ == "__main__":
    main()