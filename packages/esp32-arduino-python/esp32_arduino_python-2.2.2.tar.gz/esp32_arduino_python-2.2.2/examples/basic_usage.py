#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ESP32 Arduino风格Python控制库 - 基本使用示例

本示例展示了如何使用esp32-arduino-python库进行基本的硬件控制操作。

作者: 王海涛
版本: 1.0.0
"""

import sys
import os

# 添加库路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# 导入Arduino风格的ESP32控制库
from esp32_arduino import *

def basic_led_control():
    """
    基本LED控制示例
    """
    print("\n💡 LED控制示例")
    print("-" * 30)
    
    # 点亮LED
    print("🔆 点亮LED")
    ledOn()
    delay(1000)
    
    # 熄灭LED
    print("🔅 熄灭LED")
    ledOff()
    delay(1000)
    
    # LED闪烁
    print("✨ LED闪烁3次")
    for i in range(3):
        ledOn()
        delay(500)
        ledOff()
        delay(500)

def basic_sensor_reading():
    """
    基本传感器读取示例
    """
    print("\n📡 传感器读取示例")
    print("-" * 30)
    
    # 读取单个传感器
    temp = readTemperature()
    humid = readHumidity()
    
    print(f"🌡️ 温度: {temp}°C")
    print(f"💧 湿度: {humid}%")
    
    # 读取所有传感器
    all_sensors = readAllSensors()
    if all_sensors:
        print("\n📊 所有传感器数据:")
        for sensor, value in all_sensors.items():
            unit = '°C' if sensor == 'temperature' else '%' if sensor == 'humidity' else ''
            print(f"  {sensor}: {value}{unit}")

def basic_gpio_operations():
    """
    基本GPIO操作示例
    """
    print("\n🔧 GPIO操作示例")
    print("-" * 30)
    
    # 设置引脚模式
    pinMode(CH4, OUTPUT)
    print(f"⚙️ 设置CH4为输出模式")
    
    # 数字输出
    digitalWrite(CH4, HIGH)
    print(f"📤 CH4输出高电平")
    delay(1000)
    
    digitalWrite(CH4, LOW)
    print(f"📤 CH4输出低电平")
    delay(1000)
    
    # 设置为输入模式并读取
    pinMode(CH4, INPUT)
    print(f"⚙️ 设置CH4为输入模式")
    
    value = digitalRead(CH4)
    print(f"📥 CH4输入值: {value}")
    
    # 模拟输入读取
    print("\n📊 模拟输入读取:")
    for pin in [CH0, CH1]:
        adc_value = analogRead(pin)
        voltage = (adc_value / 4095.0) * 3.3
        print(f"  CH{pin-32} (GPIO{pin}): ADC={adc_value}, 电压={voltage:.2f}V")

def advanced_features():
    """
    高级功能示例
    """
    print("\n🚀 高级功能示例")
    print("-" * 30)
    
    # 获取系统信息
    info = getSystemInfo()
    print(f"📦 库版本: {info.get('library_version', 'Unknown')}")
    print(f"🔌 硬件支持: {'是' if info.get('hardware_available', False) else '否'}")
    print(f"📡 连接状态: {'已连接' if info.get('connection_status', False) else '未连接'}")
    
    # 硬件通道测试
    print("\n🔧 硬件通道测试:")
    test_results = testAllChannels()
    if test_results:
        for channel, result in test_results.items():
            status = "✅" if result.get('success', False) else "❌"
            device = result.get('device', f'CH{channel}')
            print(f"  {status} {device}")
    else:
        print("  ⚠️ 无测试结果（可能在模拟模式下运行）")
    
    # 运行时间
    uptime = millis()
    print(f"\n⏱️ 程序运行时间: {uptime}ms")

def main():
    """
    主函数
    """
    print("="*50)
    print("🎯 ESP32 Arduino风格Python控制库 - 基本使用示例")
    print("="*50)
    
    # 初始化ESP32连接
    print("\n🔌 初始化ESP32连接...")
    if esp32_begin():
        print("✅ ESP32连接成功")
    else:
        print("⚠️ ESP32连接失败，使用模拟模式")
    
    try:
        # 执行各种示例
        basic_led_control()
        basic_sensor_reading()
        basic_gpio_operations()
        advanced_features()
        
        print("\n🎉 所有示例执行完成！")
        
    except KeyboardInterrupt:
        print("\n\n👋 用户中断，程序退出")
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理资源
        print("\n🧹 清理资源...")
        esp32_close()
        print("✅ 程序结束")

if __name__ == "__main__":
    main()