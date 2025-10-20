#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ESP32 Arduino风格Python控制库 - 核心实现

提供Arduino风格的API来控制ESP32，让Python代码像Arduino代码一样简单直观。

作者: 王海涛
版本: 2.2.0
"""

import time
import threading
import random
from typing import Optional, Dict, Any, Union
from dataclasses import dataclass
from .device_manager import ESP32DeviceManager

# ==================== 常量定义 ====================

# Arduino风格常量
HIGH = 1
LOW = 0

# 引脚模式
INPUT = 0
OUTPUT = 1

# 扩展板通道映射 (GPIO引脚号)
CH0 = 32  # ADC输入 - 温度传感器
CH1 = 33  # ADC输入 - 湿度传感器
CH2 = 25  # 数字输出 - LED指示灯
CH3 = 26  # 数字输出 - 继电器控制
CH4 = 27  # 数字输入/输出 - 通用GPIO
CH5 = 21  # I2C SDA (预留)
CH6 = 22  # I2C SCL (预留)
CH7 = 18  # SPI SCK (预留)
CH8 = 19  # SPI MISO (预留)

# ==================== 数据类 ====================

@dataclass
class SensorReading:
    """传感器读数数据类"""
    value: float
    unit: str
    voltage: float = 0.0
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

# ==================== 全局变量 ====================

# ESP32实例
_esp32_instance = None
_connection_lock = threading.Lock()
_start_time = time.time()

# 硬件可用性检查
HARDWARE_AVAILABLE = False  # 默认为模拟模式

# ==================== 模拟ESP32通信类 ====================

class MockESP32Communicator:
    """模拟ESP32通信器，用于测试和开发"""
    
    def __init__(self, port: str, baudrate: int):
        self.port = port
        self.baudrate = baudrate
        self.connected = False
        self.led_state = False
        
    def connect(self) -> bool:
        """模拟连接"""
        self.connected = True
        return True
        
    def disconnect(self) -> None:
        """模拟断开连接"""
        self.connected = False
        
    def send_command(self, cmd_type: str, cmd_data: str) -> str:
        """模拟发送命令"""
        if not self.connected:
            return None
            
        if cmd_type == "GET":
            if "GPIO:" in cmd_data:
                return f"OK:{random.choice([0, 1])}"
            elif "ADC:" in cmd_data:
                return f"OK:{random.randint(0, 4095)}"
            elif "TEMP" in cmd_data:
                return f"OK:{random.uniform(18.0, 32.0):.1f}"
            elif "HUMID" in cmd_data:
                return f"OK:{random.uniform(35.0, 85.0):.1f}"
        elif cmd_type == "SET":
            return "OK:SET_SUCCESS"
            
        return "ERROR:UNKNOWN_COMMAND"
        
    def set_led(self, state: bool) -> bool:
        """模拟LED控制"""
        self.led_state = state
        return True
        
    def get_system_info(self) -> Dict[str, Any]:
        """模拟获取系统信息"""
        return {
            'firmware_version': '1.0.0',
            'chip_id': 'ESP32_MOCK',
            'flash_size': '4MB',
            'free_heap': 200000,
            'uptime': int(time.time() - _start_time)
        }

# ==================== 连接管理 ====================

def esp32_begin(port: str = "/dev/ttyUSB0", baudrate: int = 115200, auto_setup: bool = True) -> bool:
    """
    初始化ESP32连接

    Args:
        port: 串口端口
        baudrate: 波特率
        auto_setup: 是否自动检测和烧录固件

    Returns:
        bool: 连接是否成功
    """
    global _esp32_instance, HARDWARE_AVAILABLE

    with _connection_lock:
        if _esp32_instance is not None:
            print("ESP32已连接")
            return True

        try:
            # 如果启用自动设置，先进行设备检测和固件烧录
            if auto_setup:
                print("🔍 开始ESP32自动检测和设置...")
                device_manager = ESP32DeviceManager(port, baudrate)

                # 检测设备
                if not device_manager.detect_device():
                    print(f"❌ 未检测到ESP32设备: {port}")
                    # 使用模拟模块
                    _esp32_instance = MockESP32Communicator(port, baudrate)
                    HARDWARE_AVAILABLE = False
                    print("⚠️ 使用模拟ESP32通信模块")
                    return _esp32_instance.connect()

                # 检查固件
                has_firmware, firmware_info = device_manager.check_firmware()

                if not has_firmware:
                    print("⚠️ ESP32没有固件或固件不兼容，开始自动烧录...")

                    # 尝试烧录固件
                    if device_manager.flash_firmware():
                        print("✅ 固件烧录成功，等待设备重启...")
                        # 等待设备重启
                        if device_manager.wait_for_device_ready():
                            print("✅ ESP32设备已准备就绪")
                        else:
                            print("⚠️ 设备重启后验证失败，尝试连接...")
                    else:
                        print("❌ 固件烧录失败，使用模拟模式")
                        _esp32_instance = MockESP32Communicator(port, baudrate)
                        HARDWARE_AVAILABLE = False
                        return _esp32_instance.connect()
                else:
                    print(f"✅ ESP32固件正常: {firmware_info}")

            # 尝试导入真实的ESP32通信模块
            try:
                import sys
                import os

                # 添加ESP32通信模块路径
                esp32_comm_path = os.path.join(os.path.dirname(__file__), '..', 'esp32-rk3588-sensor-system', 'rk3588_controller')
                if esp32_comm_path not in sys.path:
                    sys.path.append(esp32_comm_path)

                from esp32_comm import ESP32Communicator
                _esp32_instance = ESP32Communicator(port, baudrate)
                HARDWARE_AVAILABLE = True
                print("使用真实ESP32通信模块")
            except ImportError:
                # 使用模拟模块
                _esp32_instance = MockESP32Communicator(port, baudrate)
                HARDWARE_AVAILABLE = False
                print("⚠️ 使用模拟ESP32通信模块")

            success = _esp32_instance.connect()

            if success:
                print(f"✅ ESP32连接成功: {port}")
            else:
                print(f"❌ ESP32连接失败: {port}")
                _esp32_instance = None

            return success
        except Exception as e:
            print(f"❌ ESP32连接异常: {e}")
            _esp32_instance = None
            return False

def esp32_close() -> None:
    """关闭ESP32连接"""
    global _esp32_instance
    
    with _connection_lock:
        if _esp32_instance:
            try:
                _esp32_instance.disconnect()
                print("ESP32连接已断开")
            except Exception as e:
                print(f"断开连接时发生异常: {e}")
            finally:
                _esp32_instance = None

def _ensure_connection() -> bool:
    """确保连接可用"""
    return _esp32_instance is not None

# ==================== Arduino风格API ====================

def digitalWrite(pin: int, value: int) -> bool:
    """
    数字输出
    
    Args:
        pin: 引脚号
        value: 输出值 (HIGH/LOW)
        
    Returns:
        bool: 操作是否成功
    """
    if not _ensure_connection():
        print(f"⚠️ 模拟模式: digitalWrite({pin}, {value})")
        return False
    
    try:
        if pin == CH2:  # LED控制
            return _esp32_instance.set_led(value == HIGH)
        else:
            response = _esp32_instance.send_command("SET", f"GPIO:{pin}:{value}")
            return response and response.startswith("OK:")
    except Exception as e:
        print(f"digitalWrite失败: {e}")
        return False

def digitalRead(pin: int) -> int:
    """
    数字输入
    
    Args:
        pin: 引脚号
        
    Returns:
        int: 输入值 (HIGH/LOW)
    """
    if not _ensure_connection():
        return random.choice([HIGH, LOW])
    
    try:
        response = _esp32_instance.send_command("GET", f"GPIO:{pin}")
        if response and response.startswith("OK:"):
            return int(response.split(":")[1])
        return LOW
    except Exception as e:
        print(f"digitalRead失败: {e}")
        return LOW

def pinMode(pin: int, mode: int) -> None:
    """
    设置引脚模式
    
    Args:
        pin: 引脚号
        mode: 引脚模式 (INPUT/OUTPUT)
    """
    if not _ensure_connection():
        print(f"⚠️ 模拟模式: pinMode({pin}, {mode})")
        return
    
    try:
        mode_str = "INPUT" if mode == INPUT else "OUTPUT"
        _esp32_instance.send_command("SET", f"MODE:{pin}:{mode_str}")
    except Exception as e:
        print(f"pinMode失败: {e}")

def analogRead(pin: int) -> int:
    """
    模拟输入
    
    Args:
        pin: 引脚号
        
    Returns:
        int: ADC值 (0-4095)
    """
    if not _ensure_connection():
        return random.randint(0, 4095)
    
    try:
        response = _esp32_instance.send_command("GET", f"ADC:{pin}")
        if response and response.startswith("OK:"):
            return int(response.split(":")[1])
        return 0
    except Exception as e:
        print(f"analogRead失败: {e}")
        return 0

# ==================== 时间函数 ====================

def delay(ms: int) -> None:
    """
    延时函数
    
    Args:
        ms: 延时毫秒数
    """
    time.sleep(ms / 1000.0)

def millis() -> int:
    """
    获取运行时间
    
    Returns:
        int: 从程序开始运行的毫秒数
    """
    return int((time.time() - _start_time) * 1000)

# ==================== 便捷函数 ====================

def ledOn() -> bool:
    """打开LED"""
    return digitalWrite(CH2, HIGH)

def ledOff() -> bool:
    """关闭LED"""
    return digitalWrite(CH2, LOW)

def readTemperature() -> float:
    """
    读取温度
    
    Returns:
        float: 温度值 (摄氏度)
    """
    if not _ensure_connection():
        return round(random.uniform(18.0, 32.0), 1)
    
    try:
        response = _esp32_instance.send_command("GET", "TEMP")
        if response and response.startswith("OK:"):
            return float(response.split(":")[1])
        return 0.0
    except Exception as e:
        print(f"读取温度失败: {e}")
        return 0.0

def readHumidity() -> float:
    """
    读取湿度
    
    Returns:
        float: 湿度值 (%)
    """
    if not _ensure_connection():
        return round(random.uniform(35.0, 85.0), 1)
    
    try:
        response = _esp32_instance.send_command("GET", "HUMID")
        if response and response.startswith("OK:"):
            return float(response.split(":")[1])
        return 0.0
    except Exception as e:
        print(f"读取湿度失败: {e}")
        return 0.0

def readAllSensors() -> Dict[str, float]:
    """
    读取所有传感器数据
    
    Returns:
        dict: 包含所有传感器数据的字典
    """
    return {
        'temperature': readTemperature(),
        'humidity': readHumidity()
    }

# ==================== 高级功能 ====================

def testAllChannels() -> Dict[str, Any]:
    """
    测试所有通道
    
    Returns:
        dict: 测试结果
    """
    results = {}
    
    # 测试数字输出通道
    for pin in [CH2, CH3, CH4]:
        try:
            digitalWrite(pin, HIGH)
            delay(100)
            digitalWrite(pin, LOW)
            results[f"CH{pin-32+2}_digital_out"] = "OK"
        except Exception as e:
            results[f"CH{pin-32+2}_digital_out"] = f"ERROR: {e}"
    
    # 测试模拟输入通道
    for pin in [CH0, CH1]:
        try:
            value = analogRead(pin)
            results[f"CH{pin-32}_analog_in"] = value
        except Exception as e:
            results[f"CH{pin-32}_analog_in"] = f"ERROR: {e}"
    
    # 测试传感器
    try:
        temp = readTemperature()
        humid = readHumidity()
        results["temperature"] = temp
        results["humidity"] = humid
    except Exception as e:
        results["sensors"] = f"ERROR: {e}"
    
    return results

def getSystemInfo() -> Dict[str, Any]:
    """
    获取系统信息
    
    Returns:
        dict: 系统信息
    """
    info = {
        'library_version': '2.2.0',
        'hardware_available': HARDWARE_AVAILABLE,
        'connection_status': 'connected' if _ensure_connection() else 'disconnected',
        'uptime_ms': millis(),
        'channels': {
            'CH0': {'pin': CH0, 'type': 'ADC', 'description': '温度传感器'},
            'CH1': {'pin': CH1, 'type': 'ADC', 'description': '湿度传感器'},
            'CH2': {'pin': CH2, 'type': 'GPIO', 'description': 'LED指示灯'},
            'CH3': {'pin': CH3, 'type': 'GPIO', 'description': '继电器控制'},
            'CH4': {'pin': CH4, 'type': 'GPIO', 'description': '通用GPIO'},
            'CH5': {'pin': CH5, 'type': 'I2C', 'description': 'I2C SDA'},
            'CH6': {'pin': CH6, 'type': 'I2C', 'description': 'I2C SCL'},
            'CH7': {'pin': CH7, 'type': 'SPI', 'description': 'SPI SCK'},
            'CH8': {'pin': CH8, 'type': 'SPI', 'description': 'SPI MISO'},
        }
    }
    
    # 如果连接可用，获取ESP32系统信息
    if _ensure_connection():
        try:
            esp32_info = _esp32_instance.get_system_info()
            info['esp32'] = esp32_info
        except Exception as e:
            info['esp32'] = f"获取失败: {e}"
    
    return info

# ==================== 模块清理 ====================

def _cleanup():
    """模块清理函数"""
    esp32_close()

import atexit
atexit.register(_cleanup)

# ==================== 调试和测试 ====================

if __name__ == "__main__":
    print("=" * 50)
    print("ESP32 Arduino风格Python控制库 v2.0.0")
    print("=" * 50)
    
    # 测试连接
    print("\n1. 测试连接...")
    if esp32_begin():
        print("✓ 连接成功")
    else:
        print("⚠️ 连接失败，使用模拟模式")
    
    # 测试基本功能
    print("\n2. 测试基本功能...")
    
    # LED测试
    print("LED测试...")
    ledOn()
    delay(500)
    ledOff()
    print("✓ LED测试完成")
    
    # 传感器测试
    print("传感器测试...")
    temp = readTemperature()
    humid = readHumidity()
    print(f"温度: {temp}°C, 湿度: {humid}%")
    
    # 数字IO测试
    print("数字IO测试...")
    digitalWrite(CH4, HIGH)
    value = digitalRead(CH4)
    print(f"CH4输出HIGH，读取值: {value}")
    
    # 模拟输入测试
    print("模拟输入测试...")
    adc_value = analogRead(CH0)
    print(f"CH0 ADC值: {adc_value}")
    
    # 系统信息
    print("\n3. 系统信息...")
    info = getSystemInfo()
    print(f"库版本: {info['library_version']}")
    print(f"硬件可用: {info['hardware_available']}")
    print(f"连接状态: {info['connection_status']}")
    print(f"运行时间: {info['uptime_ms']}ms")
    
    # 关闭连接
    print("\n4. 关闭连接...")
    esp32_close()
    print("✓ 测试完成")