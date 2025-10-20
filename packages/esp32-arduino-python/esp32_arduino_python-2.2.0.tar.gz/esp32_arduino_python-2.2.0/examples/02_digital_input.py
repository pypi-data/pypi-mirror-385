#!/usr/bin/env python3
"""
示例2: 数字输入 - 按钮读取
读取数字输入状态，模拟按钮检测
"""

from esp32_arduino import *

def setup():
    """初始化设置"""
    print("=== 数字输入示例 - 按钮读取 ===")
    
    # 初始化ESP32连接
    if not esp32_begin():
        print("❌ ESP32连接失败")
        return False
    
    print("✅ ESP32连接成功")
    print("将读取CH4 (GPIO27) 的数字输入状态")
    print("可以连接按钮或开关到CH4进行测试")
    return True

def loop():
    """主循环"""
    # 读取数字输入状态
    button_state = digitalRead(CH4)
    
    if button_state == HIGH:
        print("🔘 CH4: HIGH (按钮按下或信号为高)")
        digitalWrite(CH2, HIGH)  # 按钮按下时点亮LED
    else:
        print("⚪ CH4: LOW (按钮释放或信号为低)")
        digitalWrite(CH2, LOW)   # 按钮释放时关闭LED
    
    delay(500)  # 延时500ms

def main():
    if not setup():
        return
    
    try:
        print("开始读取数字输入 (按Ctrl+C停止)...")
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