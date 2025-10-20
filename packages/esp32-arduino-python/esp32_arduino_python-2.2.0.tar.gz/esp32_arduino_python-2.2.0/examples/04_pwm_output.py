#!/usr/bin/env python3
"""
示例4: PWM输出 - LED亮度控制
使用快速开关模拟PWM效果，控制LED亮度
"""

from esp32_arduino import *
import math

def setup():
    """初始化设置"""
    print("=== PWM输出示例 - LED亮度控制 ===")
    
    # 初始化ESP32连接
    if not esp32_begin():
        print("❌ ESP32连接失败")
        return False
    
    print("✅ ESP32连接成功")
    print("将在CH2 (GPIO25) 上模拟PWM控制LED亮度")
    print("通过快速开关实现亮度变化效果")
    return True

def pwm_write(pin, duty_cycle):
    """
    模拟PWM输出
    duty_cycle: 0-100 (百分比)
    """
    if duty_cycle <= 0:
        digitalWrite(pin, LOW)
        delay(20)
    elif duty_cycle >= 100:
        digitalWrite(pin, HIGH)
        delay(20)
    else:
        # 计算高电平和低电平时间
        period = 20  # 总周期20ms
        high_time = int(period * duty_cycle / 100)
        low_time = period - high_time
        
        if high_time > 0:
            digitalWrite(pin, HIGH)
            delay(high_time)
        if low_time > 0:
            digitalWrite(pin, LOW)
            delay(low_time)

def fade_in_out():
    """LED淡入淡出效果"""
    print("💡 LED淡入...")
    # 淡入 (0% -> 100%)
    for brightness in range(0, 101, 5):
        print(f"亮度: {brightness}%")
        for _ in range(5):  # 重复几次以看到效果
            pwm_write(CH2, brightness)
    
    print("💡 LED淡出...")
    # 淡出 (100% -> 0%)
    for brightness in range(100, -1, -5):
        print(f"亮度: {brightness}%")
        for _ in range(5):  # 重复几次以看到效果
            pwm_write(CH2, brightness)

def breathing_effect():
    """呼吸灯效果"""
    print("💡 呼吸灯效果...")
    for i in range(360):
        # 使用正弦波产生平滑的呼吸效果
        brightness = int((math.sin(math.radians(i)) + 1) * 50)
        pwm_write(CH2, brightness)
        if i % 30 == 0:  # 每30度打印一次
            print(f"呼吸灯亮度: {brightness}%")

def main():
    if not setup():
        return
    
    try:
        print("开始PWM演示...")
        
        while True:
            print("\n=== 淡入淡出效果 ===")
            fade_in_out()
            
            print("\n=== 呼吸灯效果 ===")
            breathing_effect()
            
            print("\n=== 闪烁效果 ===")
            for i in range(10):
                print(f"快速闪烁 {i+1}/10")
                digitalWrite(CH2, HIGH)
                delay(100)
                digitalWrite(CH2, LOW)
                delay(100)
            
            delay(2000)  # 暂停2秒后重复
            
    except KeyboardInterrupt:
        print("\n⏹️ 程序停止")
        digitalWrite(CH2, LOW)  # 确保LED关闭
    finally:
        esp32_close()
        print("👋 再见!")

if __name__ == "__main__":
    main()