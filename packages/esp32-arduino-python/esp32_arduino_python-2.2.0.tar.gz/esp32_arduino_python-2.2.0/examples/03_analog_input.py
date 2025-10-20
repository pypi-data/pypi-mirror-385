#!/usr/bin/env python3
"""
示例3: 模拟输入 - ADC读取
读取模拟信号，如传感器、电位器等
"""

from esp32_arduino import *

def setup():
    """初始化设置"""
    print("=== 模拟输入示例 - ADC读取 ===")
    
    # 初始化ESP32连接
    if not esp32_begin():
        print("❌ ESP32连接失败")
        return False
    
    print("✅ ESP32连接成功")
    print("将读取CH0 (GPIO32) 和 CH1 (GPIO33) 的模拟输入")
    print("可以连接传感器、电位器或电压分压器进行测试")
    print("ADC范围: 0-4095 (对应0-3.3V)")
    return True

def loop():
    """主循环"""
    # 读取两个ADC通道
    adc_ch0 = analogRead(CH0)  # 读取CH0的ADC值
    adc_ch1 = analogRead(CH1)  # 读取CH1的ADC值
    
    # 转换为电压值 (ESP32 ADC: 0-4095 对应 0-3.3V)
    voltage_ch0 = (adc_ch0 / 4095.0) * 3.3
    voltage_ch1 = (adc_ch1 / 4095.0) * 3.3
    
    # 显示结果
    print(f"📊 CH0: ADC={adc_ch0:4d}, 电压={voltage_ch0:.2f}V")
    print(f"📊 CH1: ADC={adc_ch1:4d}, 电压={voltage_ch1:.2f}V")
    
    # 根据电压控制LED (简单的阈值检测)
    if voltage_ch0 > 1.5:  # 如果CH0电压大于1.5V
        digitalWrite(CH2, HIGH)  # 点亮LED
        print("💡 CH0电压较高，LED点亮")
    else:
        digitalWrite(CH2, LOW)   # 关闭LED
        print("💡 CH0电压较低，LED关闭")
    
    print("-" * 40)
    delay(1000)  # 延时1秒

def main():
    if not setup():
        return
    
    try:
        print("开始读取模拟输入 (按Ctrl+C停止)...")
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