#!/usr/bin/env python3
"""
示例6: 继电器控制 - 设备开关
控制继电器开关，可用于控制灯具、电机等设备
"""

from esp32_arduino import *

def setup():
    """初始化设置"""
    print("=== 继电器控制示例 - 设备开关 ===")
    
    # 初始化ESP32连接
    if not esp32_begin():
        print("❌ ESP32连接失败")
        return False
    
    print("✅ ESP32连接成功")
    print("CH3 (GPIO26): 继电器控制")
    print("CH2 (GPIO25): 状态指示LED")
    print("⚠️ 注意: 请确保继电器正确连接并注意安全!")
    return True

def relay_on():
    """打开继电器"""
    digitalWrite(CH3, HIGH)
    digitalWrite(CH2, HIGH)  # LED指示继电器状态
    print("🔌 继电器已打开")

def relay_off():
    """关闭继电器"""
    digitalWrite(CH3, LOW)
    digitalWrite(CH2, LOW)   # LED指示继电器状态
    print("🔌 继电器已关闭")

def relay_status():
    """检查继电器状态"""
    status = digitalRead(CH3)
    if status == HIGH:
        print("📊 继电器状态: 开启")
    else:
        print("📊 继电器状态: 关闭")
    return status

def basic_control_demo():
    """基础控制演示"""
    print("\n=== 基础控制演示 ===")
    
    # 开关循环
    for i in range(5):
        print(f"\n第 {i+1} 轮:")
        
        relay_on()
        delay(2000)  # 开启2秒
        
        relay_off()
        delay(2000)  # 关闭2秒

def timed_control_demo():
    """定时控制演示"""
    print("\n=== 定时控制演示 ===")
    
    # 模拟定时器控制
    intervals = [1, 3, 5, 2]  # 不同的时间间隔(秒)
    
    for i, interval in enumerate(intervals):
        print(f"\n定时控制 {i+1}/{len(intervals)}: 开启 {interval} 秒")
        
        relay_on()
        
        # 倒计时显示
        for countdown in range(interval, 0, -1):
            print(f"⏰ 剩余时间: {countdown} 秒")
            delay(1000)
        
        relay_off()
        print("⏰ 时间到，继电器关闭")
        delay(1000)

def interactive_control():
    """交互式控制"""
    print("\n=== 交互式控制 ===")
    print("命令:")
    print("  1 或 on  - 打开继电器")
    print("  0 或 off - 关闭继电器")
    print("  s 或 status - 查看状态")
    print("  q 或 quit - 退出")
    
    while True:
        try:
            cmd = input("\n请输入命令: ").strip().lower()
            
            if cmd in ['1', 'on']:
                relay_on()
            elif cmd in ['0', 'off']:
                relay_off()
            elif cmd in ['s', 'status']:
                relay_status()
            elif cmd in ['q', 'quit']:
                break
            else:
                print("❌ 无效命令")
                
        except KeyboardInterrupt:
            break

def safety_test():
    """安全测试 - 快速开关测试"""
    print("\n=== 安全测试 - 快速开关 ===")
    print("⚠️ 进行快速开关测试，请确保继电器能承受频繁操作")
    
    confirm = input("确认继续? (y/N): ").strip().lower()
    if confirm != 'y':
        print("测试取消")
        return
    
    print("开始快速开关测试...")
    
    for i in range(20):
        print(f"快速开关 {i+1}/20")
        relay_on()
        delay(100)  # 100ms
        relay_off()
        delay(100)  # 100ms
    
    print("✅ 快速开关测试完成")

def main():
    if not setup():
        return
    
    # 确保初始状态为关闭
    relay_off()
    
    try:
        print("\n选择演示模式:")
        print("1 - 基础控制演示")
        print("2 - 定时控制演示")
        print("3 - 交互式控制")
        print("4 - 安全测试")
        
        choice = input("请选择 (1-4): ").strip()
        
        if choice == '1':
            basic_control_demo()
        elif choice == '2':
            timed_control_demo()
        elif choice == '3':
            interactive_control()
        elif choice == '4':
            safety_test()
        else:
            print("❌ 无效选择，运行基础演示")
            basic_control_demo()
            
    except KeyboardInterrupt:
        print("\n⏹️ 程序停止")
    finally:
        # 安全关闭
        relay_off()
        print("🔒 继电器已安全关闭")
        esp32_close()
        print("👋 再见!")

if __name__ == "__main__":
    main()