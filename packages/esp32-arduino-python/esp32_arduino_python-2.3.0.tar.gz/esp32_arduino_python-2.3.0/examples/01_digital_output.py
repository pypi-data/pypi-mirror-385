#!/usr/bin/env python3
"""
示例1: 数字输出 - LED控制
最基础的数字输出示例，控制LED开关
"""

from esp32_arduino import *

def setup():
    """初始化设置"""
    print("=== 数字输出示例 - LED控制 ===")
    
    # 初始化ESP32连接
    if not esp32_begin():
        print("❌ ESP32连接失败")
        return False
    
    print("✅ ESP32连接成功")
    print("将控制CH2 (GPIO25) 上的LED")
    return True

def loop():
    """主循环"""
    print("\n💡 点亮LED")
    digitalWrite(CH2, HIGH)  # 点亮LED
    delay(1000)              # 延时1秒
    
    print("💡 关闭LED")
    digitalWrite(CH2, LOW)   # 关闭LED
    delay(1000)              # 延时1秒

def main():
    if not setup():
        return
    
    try:
        print("开始LED闪烁 (按Ctrl+C停止)...")
        while True:
            loop()
    except KeyboardInterrupt:
        print("\n⏹️ 程序停止")
        digitalWrite(CH2, LOW)  # 确保LED关闭
    finally:
        esp32_close()
        print("👋 再见!")

if __name__ == "__main__":
    main()