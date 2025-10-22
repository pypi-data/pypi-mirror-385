#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ESP32 Arduino风格Python控制库

提供Arduino风格的API来控制ESP32，让Python代码像Arduino代码一样简单直观。

基本用法:
    from esp32_arduino import *
    
    # 初始化连接
    esp32_begin()
    
    # 控制LED
    ledOn()
    delay(1000)
    ledOff()
    
    # 读取传感器
    temp = readTemperature()
    humid = readHumidity()
    
    # 数字IO
    digitalWrite(CH2, HIGH)
    value = digitalRead(CH4)
    
    # 模拟输入
    adc_value = analogRead(CH0)
    
    # 关闭连接
    esp32_close()

作者: 王海涛
版本: 1.0.0
"""

# 导入核心功能
from .core import (
    # 连接管理
    esp32_begin,
    esp32_close,

    # 数字IO
    digitalWrite,
    digitalRead,
    pinMode,

    # 模拟输入
    analogRead,

    # 时间函数
    delay,
    millis,

    # 便捷函数
    ledOn,
    ledOff,
    readTemperature,
    readHumidity,
    readAllSensors,

    # 常量
    HIGH,
    LOW,
    INPUT,
    OUTPUT,

    # 扩展板通道
    CH0, CH1, CH2, CH3, CH4, CH5, CH6, CH7, CH8,

    # 高级功能
    testAllChannels,
    getSystemInfo,

    # 数据类
    SensorReading,

    # 内部变量（用于高级用户）
    _esp32_instance
)

# 导入设备管理功能
from .device_manager import (
    ESP32DeviceManager,
    auto_setup_esp32
)

# 版本信息
__version__ = "2.2.1"
__author__ = "王海涛"
__description__ = "ESP32 Arduino风格Python控制库"

# 导出所有公共API
__all__ = [
    # 连接管理
    'esp32_begin',
    'esp32_close',

    # 数字IO
    'digitalWrite',
    'digitalRead',
    'pinMode',

    # 模拟输入
    'analogRead',

    # 时间函数
    'delay',
    'millis',

    # 便捷函数
    'ledOn',
    'ledOff',
    'readTemperature',
    'readHumidity',
    'readAllSensors',

    # 常量
    'HIGH',
    'LOW',
    'INPUT',
    'OUTPUT',

    # 扩展板通道
    'CH0', 'CH1', 'CH2', 'CH3', 'CH4', 'CH5', 'CH6', 'CH7', 'CH8',

    # 高级功能
    'testAllChannels',
    'getSystemInfo',

    # 数据类
    'SensorReading',

    # 设备管理
    'ESP32DeviceManager',
    'auto_setup_esp32'
]

# 库初始化信息
print(f"📦 ESP32 Arduino库 v{__version__} 已加载")
print("💡 使用方法: from esp32_arduino import *")
print("📖 文档: https://github.com/your-repo/esp32-arduino-python")