#!/usr/bin/env python3
"""
示例5: 传感器读取 - 温湿度监控
读取模拟传感器数据并进行简单的数据处理
"""

from esp32_arduino import *
import time

def setup():
    """初始化设置"""
    print("=== 传感器读取示例 - 温湿度监控 ===")
    
    # 初始化ESP32连接
    if not esp32_begin():
        print("❌ ESP32连接失败")
        return False
    
    print("✅ ESP32连接成功")
    print("CH0 (GPIO32): 温度传感器")
    print("CH1 (GPIO33): 湿度传感器")
    print("CH2 (GPIO25): 状态指示LED")
    return True

def read_temperature():
    """读取温度传感器"""
    adc_value = analogRead(CH0)
    # 简单的ADC到温度转换 (根据实际传感器调整)
    voltage = (adc_value / 4095.0) * 3.3
    temperature = 20.0 + (voltage - 1.0) * 10.0  # 假设1V对应20°C
    return temperature, adc_value

def read_humidity():
    """读取湿度传感器"""
    adc_value = analogRead(CH1)
    # 简单的ADC到湿度转换 (根据实际传感器调整)
    voltage = (adc_value / 4095.0) * 3.3
    humidity = voltage * 30.0  # 假设线性关系
    return humidity, adc_value

def check_alerts(temp, humid):
    """检查报警条件"""
    alerts = []
    
    if temp > 30:
        alerts.append(f"⚠️ 温度过高: {temp:.1f}°C")
    elif temp < 10:
        alerts.append(f"⚠️ 温度过低: {temp:.1f}°C")
    
    if humid > 80:
        alerts.append(f"⚠️ 湿度过高: {humid:.1f}%")
    elif humid < 20:
        alerts.append(f"⚠️ 湿度过低: {humid:.1f}%")
    
    return alerts

def loop():
    """主循环"""
    # 读取传感器数据
    temp, temp_adc = read_temperature()
    humid, humid_adc = read_humidity()
    
    # 获取系统运行时间
    uptime = millis()
    
    # 显示数据
    print(f"[{uptime:8d}ms] 🌡️ 温度: {temp:5.1f}°C (ADC:{temp_adc:4d}) | "
          f"💧 湿度: {humid:5.1f}% (ADC:{humid_adc:4d})")
    
    # 检查报警
    alerts = check_alerts(temp, humid)
    if alerts:
        for alert in alerts:
            print(alert)
        # 有报警时闪烁LED
        digitalWrite(CH2, HIGH)
        delay(200)
        digitalWrite(CH2, LOW)
        delay(200)
        digitalWrite(CH2, HIGH)
        delay(200)
        digitalWrite(CH2, LOW)
    else:
        # 正常时LED常亮
        digitalWrite(CH2, HIGH)
    
    delay(1000)  # 每秒读取一次

def data_logging_demo():
    """数据记录演示"""
    print("\n=== 数据记录演示 (10秒) ===")
    
    data_points = []
    start_time = time.time()
    
    for i in range(10):
        temp, _ = read_temperature()
        humid, _ = read_humidity()
        timestamp = time.time() - start_time
        
        data_points.append({
            'time': timestamp,
            'temperature': temp,
            'humidity': humid
        })
        
        print(f"记录点 {i+1}/10: 时间={timestamp:.1f}s, 温度={temp:.1f}°C, 湿度={humid:.1f}%")
        delay(1000)
    
    # 计算统计信息
    temps = [d['temperature'] for d in data_points]
    humids = [d['humidity'] for d in data_points]
    
    print(f"\n📊 统计信息:")
    print(f"温度: 最小={min(temps):.1f}°C, 最大={max(temps):.1f}°C, 平均={sum(temps)/len(temps):.1f}°C")
    print(f"湿度: 最小={min(humids):.1f}%, 最大={max(humids):.1f}%, 平均={sum(humids)/len(humids):.1f}%")

def main():
    if not setup():
        return
    
    try:
        print("选择模式:")
        print("1 - 实时监控")
        print("2 - 数据记录演示")
        
        choice = input("请选择 (1/2): ").strip()
        
        if choice == '2':
            data_logging_demo()
        else:
            print("开始实时监控 (按Ctrl+C停止)...")
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