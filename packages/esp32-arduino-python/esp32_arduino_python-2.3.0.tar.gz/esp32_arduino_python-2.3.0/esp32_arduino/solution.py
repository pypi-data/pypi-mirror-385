#!/usr/bin/env python3
"""
ESP32最终解决方案模块
集成到ESP32-Arduino-Python库中，提供完整的Arduino风格API
"""

import serial
import time
import subprocess
import sys
import random
import os
from pathlib import Path

class ESP32UniversalSolution:
    """ESP32通用解决方案类"""

    def __init__(self, port='/dev/ttyUSB0'):
        self.port = port
        self.baudrate = 115200
        self.connected = False
        self.using_simulation = False
        self.ser = None

        # 固件查找路径
        self.firmware_paths = [
            Path(__file__).parent / "firmware" / "firmware.bin",  # 包内固件
            Path(__file__).parent.parent.parent / "esp32-rk3588-sensor-system" / "esp32_firmware" / ".pio" / "build" / "esp32dev" / "firmware.bin",  # 本地编译固件
        ]

    def check_esp32_status(self):
        """检查ESP32状态"""
        try:
            ser = serial.Serial(self.port, self.baudrate, timeout=2)
            ser.flushInput()
            time.sleep(1)

            if ser.in_waiting > 0:
                output = ser.read(ser.in_waiting).decode('ascii', errors='ignore').strip()
                ser.close()

                # 检查重启循环
                if 'rst:0x10' in output or 'RTCWDT_RTC_RESET' in output:
                    return "reboot_loop"
                elif 'Ready>' in output or len(output) == 0:
                    return "ready"
                else:
                    return "unknown"
            else:
                return "ready"  # 无输出可能表示正常启动

        except Exception as e:
            return f"error: {e}"

    def find_firmware(self):
        """查找可用的固件文件"""
        for firmware_path in self.firmware_paths:
            if firmware_path.exists():
                print(f"📦 找到固件: {firmware_path}")
                return str(firmware_path)

        print("❌ 未找到可用固件文件")
        return None

    def flash_esp32_firmware(self):
        """烧录ESP32固件"""
        firmware_path = self.find_firmware()
        if not firmware_path:
            return False

        print(f"🔥 烧录固件: {firmware_path}")
        return self._flash_firmware_file(firmware_path)

    def _flash_firmware_file(self, firmware_path):
        """烧录指定固件文件"""
        try:
            print("🔥 擦除Flash...")
            erase_cmd = [sys.executable, '-m', 'esptool', '--port', self.port, 'erase-flash']
            result = subprocess.run(erase_cmd, capture_output=True, text=True, timeout=60)

            if result.returncode != 0:
                print(f"❌ 擦除失败: {result.stderr}")
                return False

            print("✅ Flash擦除成功")

            print("🔥 烧录固件...")
            flash_cmd = [
                sys.executable, '-m', 'esptool',
                '--port', self.port,
                '--baud', '460800',
                'write-flash',
                '0x1000',
                firmware_path
            ]

            result = subprocess.run(flash_cmd, capture_output=True, text=True, timeout=120)

            if result.returncode == 0:
                print("✅ 固件烧录成功!")
                return True
            else:
                print(f"❌ 烧录失败: {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ 烧录异常: {e}")
            return False

    def connect(self):
        """连接ESP32"""
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=3)
            self.ser.flushInput()
            time.sleep(2)
            self.connected = True
            return True
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return False

    def test_communication(self):
        """测试通信"""
        if not self.connected:
            return False

        commands = ['PING', 'AT', 'INFO', 'D']
        for cmd in commands:
            try:
                self.ser.write(f"{cmd}\n".encode())
                time.sleep(0.5)

                if self.ser.in_waiting > 0:
                    response = self.ser.read(self.ser.in_waiting).decode('ascii', errors='ignore').strip()

                    # 检查是否为有效响应
                    if any(keyword in response for keyword in ['PONG', 'OK', 'TEMP:', 'HUM:', 'Ready']):
                        return True

                time.sleep(0.5)
            except:
                continue

        return False

    def read_real_sensor_data(self):
        """读取真实传感器数据"""
        if not self.connected:
            return None, None

        commands = ['D', 'READ:DHT11', 'GET:TEMP', 'SENSOR:DHT11']

        for cmd in commands:
            try:
                self.ser.flushInput()
                self.ser.write(f"{cmd}\n".encode())
                time.sleep(2)  # DHT11需要时间

                if self.ser.in_waiting > 0:
                    data = self.ser.read(self.ser.in_waiting).decode('ascii', errors='ignore').strip()

                    # 解析多种数据格式
                    temp, hum = self._parse_sensor_data(data)
                    if temp and hum:
                        return temp, hum

            except Exception as e:
                continue

        return None, None

    def _parse_sensor_data(self, data):
        """解析传感器数据，支持多种格式"""
        temp = hum = None

        # 格式1: TEMP:25.5 HUM:60.2
        if 'TEMP:' in data and 'HUM:' in data:
            lines = data.split('\n')
            for line in lines:
                if 'TEMP:' in line:
                    try:
                        temp = float(line.split('TEMP:')[1].split()[0])
                    except:
                        pass
                elif 'HUM:' in line:
                    try:
                        hum = float(line.split('HUM:')[1].split()[0])
                    except:
                        pass

        # 格式2: 25.5,60.2
        elif ',' in data and data.count(',') == 1:
            try:
                parts = data.split(',')
                temp = float(parts[0])
                hum = float(parts[1])
            except:
                pass

        return temp, hum

    def get_simulation_data(self):
        """获取模拟传感器数据"""
        # 基于时间的真实变化
        base_temp = 25.0
        base_hum = 60.0

        # 添加时间变化
        time_factor = time.time() % 100
        temp = base_temp + 2 * (time_factor / 50 - 1)  # ±2°C
        hum = base_hum + 5 * (time_factor / 50 - 1)   # ±5%

        # 添加小幅随机变化
        temp += random.uniform(-0.5, 0.5)
        hum += random.uniform(-1, 1)

        return round(temp, 1), round(hum, 1)

    def read_sensors(self):
        """读取传感器数据（真实优先，模拟备份）"""
        if self.using_simulation:
            return self.get_simulation_data()

        # 尝试读取真实数据
        if self.connected:
            temp, hum = self.read_real_sensor_data()
            if temp and hum:
                return temp, hum

        # 如果真实数据读取失败，使用模拟数据
        print("⚠️ 使用模拟传感器数据")
        self.using_simulation = True
        return self.get_simulation_data()

    def setup(self):
        """完整的ESP32设置流程"""
        print("🔍 ESP32库自动设置开始...")

        # 1. 检查ESP32状态
        status = self.check_esp32_status()
        print(f"📊 ESP32状态: {status}")

        # 2. 处理重启循环
        if status == "reboot_loop":
            print("🔄 检测到重启循环，尝试烧录固件...")
            if self.flash_esp32_firmware():
                print("⏳ 等待ESP32重启...")
                time.sleep(5)
                status = self.check_esp32_status()
                print(f"🔄 烧录后状态: {status}")

        # 3. 连接和测试
        if self.connect():
            print("✅ 串口连接成功")

            if self.test_communication():
                print("✅ ESP32通信正常")
                return True
            else:
                print("⚠️ ESP32通信异常，将使用模拟数据")
                self.using_simulation = True
                return True
        else:
            print("❌ 串口连接失败，将使用模拟数据")
            self.using_simulation = True
            return False

    def close(self):
        """关闭连接"""
        if self.ser:
            self.ser.close()
            self.connected = False

# 全局实例
_global_solution = None

def get_solution(port='/dev/ttyUSB0'):
    """获取全局解决方案实例"""
    global _global_solution
    if _global_solution is None:
        _global_solution = ESP32UniversalSolution(port)
    return _global_solution