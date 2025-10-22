#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ESP32自动设置演示
演示ESP32设备的自动检测、固件烧录和连接功能

使用方法:
    python auto_setup_demo.py
"""

import sys
import os
from pathlib import Path

# 添加库路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir.parent))

from esp32_arduino import *

def demo_auto_setup():
    """演示自动设置功能"""
    print("=" * 60)
    print("ESP32 Arduino库 - 自动设置演示")
    print("=" * 60)

    # 方法1: 使用esp32_begin的自动设置功能
    print("\n1. 使用esp32_begin的自动设置功能...")
    print("   这将自动检测设备、检查固件、烧录（如果需要）并连接")

    if esp32_begin(auto_setup=True):
        print("✅ ESP32自动设置成功！")

        # 测试基本功能
        print("\n2. 测试基本功能...")

        # LED测试
        print("   LED闪烁测试...")
        ledOn()
        delay(500)
        ledOff()
        delay(500)
        ledOn()
        delay(500)
        ledOff()
        print("   ✅ LED测试完成")

        # 传感器测试
        print("   传感器读取测试...")
        temp = readTemperature()
        humid = readHumidity()
        print(f"   温度: {temp}°C, 湿度: {humid}%")

        # 模拟输入测试
        print("   模拟输入测试...")
        adc_value = analogRead(CH0)
        print(f"   CH0 ADC值: {adc_value}")

        # 系统信息
        print("\n3. 系统信息...")
        info = getSystemInfo()
        print(f"   库版本: {info['library_version']}")
        print(f"   硬件可用: {info['hardware_available']}")
        print(f"   连接状态: {info['connection_status']}")
        print(f"   运行时间: {info['uptime_ms']}ms")

        # 关闭连接
        print("\n4. 关闭连接...")
        esp32_close()
        print("   ✅ 连接已关闭")

    else:
        print("❌ ESP32自动设置失败，可能处于模拟模式")

def demo_device_manager():
    """演示设备管理器功能"""
    print("\n" + "=" * 60)
    print("ESP32设备管理器演示")
    print("=" * 60)

    # 创建设备管理器实例
    manager = ESP32DeviceManager()

    print("\n1. 检测设备...")
    if manager.detect_device():
        print("   ✅ ESP32设备检测成功")
    else:
        print("   ❌ ESP32设备检测失败")

    print("\n2. 检查固件...")
    has_firmware, info = manager.check_firmware()
    if has_firmware:
        print(f"   ✅ 检测到固件: {info}")
    else:
        print(f"   ❌ 未检测到固件: {info}")

    print("\n3. 查找固件文件...")
    firmware_path = manager.find_firmware_file()
    if firmware_path:
        print(f"   ✅ 找到固件文件: {firmware_path}")
    else:
        print("   ❌ 未找到固件文件")

    # 使用便捷函数
    print("\n4. 使用便捷函数进行自动设置...")
    success, message = auto_setup_esp32()
    if success:
        print(f"   ✅ 自动设置成功: {message}")
    else:
        print(f"   ❌ 自动设置失败: {message}")

def demo_manual_mode():
    """演示手动模式（不进行自动设置）"""
    print("\n" + "=" * 60)
    print("手动模式演示")
    print("=" * 60)

    print("\n使用手动模式连接（不进行自动检测和烧录）...")

    if esp32_begin(auto_setup=False):
        print("✅ 手动连接成功")

        # 进行简单测试
        print("进行简单测试...")
        ledOn()
        delay(200)
        ledOff()
        print("✅ LED测试完成")

        esp32_close()
    else:
        print("❌ 手动连接失败")

def main():
    """主函数"""
    try:
        # 演示自动设置功能
        demo_auto_setup()

        # 演示设备管理器功能
        demo_device_manager()

        # 演示手动模式
        demo_manual_mode()

        print("\n" + "=" * 60)
        print("演示完成！")
        print("=" * 60)
        print("\n💡 使用说明:")
        print("1. 默认情况下，esp32_begin() 会进行自动设置")
        print("2. 如果不想自动设置，使用 esp32_begin(auto_setup=False)")
        print("3. 可以单独使用 ESP32DeviceManager 类进行设备管理")
        print("4. 可以使用 auto_setup_esp32() 便捷函数进行自动设置")

    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断演示")
    except Exception as e:
        print(f"\n\n❌ 演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()