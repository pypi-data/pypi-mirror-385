#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ESP32 Arduino风格Python控制库 - 核心实现

提供Arduino风格的API来控制ESP32，遵循KISS原则，保持简单。

作者: 王海涛
版本: 2.2.1
"""

import time
from typing import Dict, Any
from dataclasses import dataclass

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
_start_time = time.time()

# 硬件连接状态
_is_connected = False

# ==================== 连接管理 ====================

def esp32_begin(port: str = "/dev/ttyUSB0", baudrate: int = 115200, auto_setup: bool = False) -> bool:
    """
    初始化ESP32连接

    Args:
        port: 串口端口
        baudrate: 波特率
        auto_setup: 是否自动检测和烧录固件

    Returns:
        bool: 连接是否成功
    """
    global _esp32_instance, _is_connected

    if _esp32_instance is not None:
        print("ESP32已连接")
        return True

    try:
        # 导入ESP32通信模块 - 使用内置模块
        from .esp32_comm import ESP32Communicator
        _esp32_instance = ESP32Communicator(port, baudrate)

        success = _esp32_instance.connect()
        _is_connected = success

        if success:
            print(f"✅ ESP32连接成功: {port}")
        else:
            print(f"❌ ESP32连接失败: {port}")
            _esp32_instance = None

        return success
    except Exception as e:
        print(f"❌ ESP32连接异常: {e}")
        _esp32_instance = None
        _is_connected = False
        return False

def esp32_close() -> None:
    """关闭ESP32连接"""
    global _esp32_instance, _is_connected

    if _esp32_instance:
        try:
            _esp32_instance.disconnect()
            print("ESP32连接已断开")
        except Exception as e:
            print(f"断开连接时发生异常: {e}")
        finally:
            _esp32_instance = None
            _is_connected = False

def _ensure_connection() -> bool:
    """确保连接可用"""
    return _is_connected

# ==================== Arduino风格API ====================

def digitalWrite(pin: int, value: int) -> bool:
    """数字输出"""
    if not _ensure_connection():
        return False

    try:
        if pin == CH2:  # LED控制
            return _esp32_instance.set_led(value == HIGH)
        else:
            response = _esp32_instance.send_command("", f"PINSET:{pin}:{value}")
            return response and ("OK:" in response or "SUCCESS" in response)
    except Exception:
        return False

def digitalRead(pin: int) -> int:
    """数字输入"""
    if not _ensure_connection():
        return LOW

    try:
        response = _esp32_instance.send_command("", f"PINREAD:{pin}")
        if response and ("OK:" in response or "VALUE:" in response):
            # 提取数值
            for token in response.split():
                try:
                    val = int(token)
                    return val
                except:
                    continue
        return LOW
    except Exception:
        return LOW

def pinMode(pin: int, mode: int) -> None:
    """设置引脚模式"""
    if not _ensure_connection():
        return

    try:
        mode_str = "INPUT" if mode == INPUT else "OUTPUT"
        _esp32_instance.send_command("SET", f"MODE:{pin}:{mode_str}")
    except Exception:
        pass

def analogRead(pin: int) -> int:
    """模拟输入"""
    if not _ensure_connection():
        return 0

    try:
        response = _esp32_instance.send_command("", f"ADCREAD:{pin}")
        if response and ("OK:" in response or "VALUE:" in response):
            # 提取数值
            for token in response.split():
                try:
                    val = int(token)
                    return val
                except:
                    continue
        return 0
    except Exception:
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
    """读取温度"""
    if not _ensure_connection():
        return 0.0

    try:
        # 使用通信模块的传感器读取方法
        temp, _ = _esp32_instance.read_sensor_data("DHT11")
        return temp if temp is not None else 0.0
    except Exception:
        return 0.0

def readHumidity() -> float:
    """读取湿度"""
    if not _ensure_connection():
        return 0.0

    try:
        # 使用通信模块的传感器读取方法
        _, humid = _esp32_instance.read_sensor_data("DHT11")
        return humid if humid is not None else 0.0
    except Exception:
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
        except Exception:
            results[f"CH{pin-32+2}_digital_out"] = "ERROR"

    # 测试模拟输入通道
    for pin in [CH0, CH1]:
        try:
            value = analogRead(pin)
            results[f"CH{pin-32}_analog_in"] = value
        except Exception:
            results[f"CH{pin-32}_analog_in"] = "ERROR"

    # 测试传感器
    try:
        temp = readTemperature()
        humid = readHumidity()
        results["temperature"] = temp
        results["humidity"] = humid
    except Exception:
        results["sensors"] = "ERROR"
    
    return results

def getSystemInfo() -> Dict[str, Any]:
    """
    获取系统信息
    
    Returns:
        dict: 系统信息
    """
    info = {
        'library_version': '2.2.1',
        'connection_status': 'connected' if _ensure_connection() else 'disconnected',
        'uptime_ms': millis()
    }

    # 如果连接可用，获取ESP32系统信息
    if _ensure_connection():
        try:
            esp32_info = _esp32_instance.get_system_info()
            info['esp32'] = esp32_info
        except Exception:
            info['esp32'] = "获取失败"
    
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