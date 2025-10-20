#!/usr/bin/env python3
"""
示例7: 全通道测试 - 扩展板功能验证
测试扩展板所有通道的功能，用于硬件验证
"""

from esp32_arduino import *

def setup():
    """初始化设置"""
    print("=== 全通道测试 - 扩展板功能验证 ===")
    
    # 初始化ESP32连接
    if not esp32_begin():
        print("❌ ESP32连接失败")
        return False
    
    print("✅ ESP32连接成功")
    print("\n📋 扩展板通道配置:")
    print("CH0 (GPIO32): ADC输入 - 温度传感器")
    print("CH1 (GPIO33): ADC输入 - 湿度传感器")
    print("CH2 (GPIO25): 数字输出 - LED指示灯")
    print("CH3 (GPIO26): 数字输出 - 继电器控制")
    print("CH4 (GPIO27): 数字输入/输出 - 通用GPIO")
    print("CH5-CH8: I2C接口 (预留)")
    return True

def test_digital_outputs():
    """测试数字输出通道"""
    print("\n🔧 测试数字输出通道...")
    
    channels = [
        (CH2, "CH2 (LED)"),
        (CH3, "CH3 (继电器)"),
        (CH4, "CH4 (GPIO)")
    ]
    
    for pin, name in channels:
        print(f"测试 {name}:")
        
        # 输出高电平
        digitalWrite(pin, HIGH)
        print(f"  ✅ 输出HIGH: {digitalRead(pin)}")
        delay(500)
        
        # 输出低电平
        digitalWrite(pin, LOW)
        print(f"  ✅ 输出LOW: {digitalRead(pin)}")
        delay(500)

def test_digital_inputs():
    """测试数字输入通道"""
    print("\n🔧 测试数字输入通道...")
    
    channels = [CH2, CH3, CH4]
    
    for i, pin in enumerate(channels):
        # 先设置为输入模式 (通过读取操作)
        value = digitalRead(pin)
        print(f"CH{i+2} 输入状态: {value} ({'HIGH' if value else 'LOW'})")

def test_analog_inputs():
    """测试模拟输入通道"""
    print("\n🔧 测试模拟输入通道...")
    
    channels = [
        (CH0, "CH0 (温度传感器)"),
        (CH1, "CH1 (湿度传感器)")
    ]
    
    for pin, name in channels:
        adc_value = analogRead(pin)
        voltage = (adc_value / 4095.0) * 3.3
        print(f"{name}: ADC={adc_value:4d}, 电压={voltage:.2f}V")

def test_channel_isolation():
    """测试通道隔离性"""
    print("\n🔧 测试通道隔离性...")
    
    # 设置不同通道为不同状态
    digitalWrite(CH2, HIGH)
    digitalWrite(CH3, LOW)
    digitalWrite(CH4, HIGH)
    
    delay(100)
    
    # 读取状态验证
    states = [
        (CH2, HIGH, "CH2"),
        (CH3, LOW, "CH3"),
        (CH4, HIGH, "CH4")
    ]
    
    all_correct = True
    for pin, expected, name in states:
        actual = digitalRead(pin)
        if actual == expected:
            print(f"✅ {name}: 期望={expected}, 实际={actual}")
        else:
            print(f"❌ {name}: 期望={expected}, 实际={actual}")
            all_correct = False
    
    if all_correct:
        print("✅ 通道隔离测试通过")
    else:
        print("❌ 通道隔离测试失败")

def test_timing_accuracy():
    """测试时序精度"""
    print("\n🔧 测试时序精度...")
    
    # 测试delay函数精度
    test_delays = [100, 500, 1000]  # ms
    
    for delay_time in test_delays:
        print(f"测试 {delay_time}ms 延时...")
        
        start_time = millis()
        delay(delay_time)
        end_time = millis()
        
        actual_delay = end_time - start_time
        error = abs(actual_delay - delay_time)
        error_percent = (error / delay_time) * 100
        
        print(f"  期望: {delay_time}ms, 实际: {actual_delay}ms, "
              f"误差: {error}ms ({error_percent:.1f}%)")

def stress_test():
    """压力测试"""
    print("\n🔧 压力测试 - 快速IO操作...")
    
    print("进行1000次快速IO操作...")
    start_time = millis()
    
    for i in range(1000):
        # 快速切换所有数字输出
        digitalWrite(CH2, i % 2)
        digitalWrite(CH3, (i + 1) % 2)
        digitalWrite(CH4, i % 2)
        
        # 读取ADC
        analogRead(CH0)
        analogRead(CH1)
        
        if i % 100 == 0:
            print(f"  完成 {i}/1000 次操作")
    
    end_time = millis()
    total_time = end_time - start_time
    ops_per_second = 1000 / (total_time / 1000.0)
    
    print(f"✅ 压力测试完成: {total_time}ms, {ops_per_second:.1f} 操作/秒")

def comprehensive_test():
    """综合测试"""
    print("\n🔧 综合功能测试...")
    
    # 模拟实际应用场景
    for cycle in range(5):
        print(f"\n--- 测试周期 {cycle + 1}/5 ---")
        
        # 读取传感器
        temp_adc = analogRead(CH0)
        humid_adc = analogRead(CH1)
        temp = 20 + (temp_adc / 4095.0) * 20
        humid = (humid_adc / 4095.0) * 100
        
        print(f"传感器读数: 温度={temp:.1f}°C, 湿度={humid:.1f}%")
        
        # 根据传感器数据控制输出
        if temp > 25:
            digitalWrite(CH2, HIGH)  # 温度高时点亮LED
            print("温度较高，LED点亮")
        else:
            digitalWrite(CH2, LOW)
            print("温度正常，LED关闭")
        
        if humid > 60:
            digitalWrite(CH3, HIGH)  # 湿度高时启动继电器
            print("湿度较高，继电器启动")
        else:
            digitalWrite(CH3, LOW)
            print("湿度正常，继电器关闭")
        
        # 检查输入状态
        input_state = digitalRead(CH4)
        print(f"输入状态: {'HIGH' if input_state else 'LOW'}")
        
        delay(2000)

def main():
    if not setup():
        return
    
    try:
        print("\n选择测试模式:")
        print("1 - 数字输出测试")
        print("2 - 数字输入测试")
        print("3 - 模拟输入测试")
        print("4 - 通道隔离测试")
        print("5 - 时序精度测试")
        print("6 - 压力测试")
        print("7 - 综合测试")
        print("8 - 全部测试")
        
        choice = input("请选择 (1-8): ").strip()
        
        if choice == '1':
            test_digital_outputs()
        elif choice == '2':
            test_digital_inputs()
        elif choice == '3':
            test_analog_inputs()
        elif choice == '4':
            test_channel_isolation()
        elif choice == '5':
            test_timing_accuracy()
        elif choice == '6':
            stress_test()
        elif choice == '7':
            comprehensive_test()
        elif choice == '8':
            # 运行所有测试
            test_digital_outputs()
            test_digital_inputs()
            test_analog_inputs()
            test_channel_isolation()
            test_timing_accuracy()
            stress_test()
            comprehensive_test()
        else:
            print("❌ 无效选择")
            
    except KeyboardInterrupt:
        print("\n⏹️ 测试中断")
    finally:
        # 清理所有输出
        digitalWrite(CH2, LOW)
        digitalWrite(CH3, LOW)
        digitalWrite(CH4, LOW)
        print("🧹 所有输出已清理")
        esp32_close()
        print("👋 测试结束!")

if __name__ == "__main__":
    main()