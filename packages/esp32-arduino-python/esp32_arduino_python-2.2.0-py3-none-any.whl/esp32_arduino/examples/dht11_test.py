#!/usr/bin/env python3
"""
ESP32 DHT11传感器测试示例

这个示例展示了如何使用ESP32 Arduino库来测试DHT11传感器功能。

使用方法:
    python -m esp32_arduino.examples.dht11_test
"""

from .. import *
import time

def main():
    """DHT11传感器测试主函数"""
    print("🌡️  ESP32 DHT11传感器测试")
    print("="*40)

    # 初始化ESP32连接
    print("正在连接ESP32...")
    if not esp32_begin():
        print("❌ 连接失败，请检查ESP32连接")
        return

    print("✅ ESP32连接成功")

    # 测试基本通信
    print("\n📡 测试基本通信...")
    info = getSystemInfo()
    print(f"系统信息: {info}")

    # 连续读取温湿度数据
    print("\n🌡️  连续读取温湿度数据 (10次)")
    print("="*40)

    for i in range(10):
        # 读取温度和湿度
        temp = readTemperature()
        humid = readHumidity()

        if temp is not None and humid is not None:
            print(f"第{i+1:2d}次: 温度={temp:5.1f}°C, 湿度={humid:5.1f}%")
        else:
            print(f"第{i+1:2d}次: 读取失败")

        # DHT11需要至少2秒间隔
        delay(2000)

    # 测试所有传感器数据
    print("\n📊 测试所有传感器数据...")
    all_data = readAllSensors()
    if all_data:
        print("传感器数据:")
        for key, value in all_data.items():
            print(f"  {key}: {value}")
    else:
        print("读取所有传感器数据失败")

    # LED测试
    print("\n💡 LED测试...")
    print("LED开启")
    ledOn()
    delay(1000)

    print("LED关闭")
    ledOff()
    delay(500)

    print("LED闪烁 (3次)")
    for i in range(3):
        ledOn()
        delay(500)
        ledOff()
        delay(500)

    # 测试传感器模式切换
    print("\n🔄 传感器模式测试...")
    # 注意：这个功能需要ESP32固件支持传感器模式切换

    print("测试完成，断开连接...")
    esp32_close()
    print("👋 测试结束")

if __name__ == "__main__":
    main()