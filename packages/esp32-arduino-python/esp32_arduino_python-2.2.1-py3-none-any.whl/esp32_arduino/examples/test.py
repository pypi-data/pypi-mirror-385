#!/usr/bin/env python3
"""
ESP32 Arduino库测试工具
"""

from esp32_arduino import *

def main():
    """主测试函数"""
    print("=== ESP32 Arduino库测试 ===")
    
    # 初始化连接
    if not esp32_begin():
        print("❌ ESP32连接失败")
        return 1
    
    print("✅ ESP32连接成功")
    
    try:
        # LED闪烁测试
        print("LED闪烁测试...")
        for i in range(3):
            print(f"第{i+1}次闪烁")
            ledOn()
            delay(500)
            ledOff()
            delay(500)
        
        # 传感器读取测试
        print("传感器读取测试...")
        temp = readTemperature()
        humid = readHumidity()
        print(f"温度: {temp}°C")
        print(f"湿度: {humid}%")
        
        print("✅ 测试完成!")
        return 0
        
    except KeyboardInterrupt:
        print("\n⏹️ 测试中断")
        return 1
    finally:
        esp32_close()

if __name__ == "__main__":
    exit(main())