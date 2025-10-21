# ESP32自动设置指南

本指南介绍如何使用ESP32 Arduino风格Python库的自动检测和固件烧录功能。

## 🚀 快速开始

### 基本使用

```python
from esp32_arduino import *

# 自动检测设备、检查固件、烧录（如果需要）并连接
if esp32_begin():
    print("ESP32设置成功！")

    # 现在可以使用所有Arduino风格的函数
    ledOn()
    delay(1000)
    ledOff()

    # 读取传感器
    temp = readTemperature()
    print(f"温度: {temp}°C")

    esp32_close()
```

### 手动模式

```python
# 不进行自动检测和烧录
if esp32_begin(auto_setup=False):
    print("手动连接成功")
```

## 🔧 设备管理器

### ESP32DeviceManager类

```python
from esp32_arduino import ESP32DeviceManager

# 创建设备管理器
manager = ESP32DeviceManager(port="/dev/ttyUSB0", baudrate=115200)

# 检测设备
if manager.detect_device():
    print("设备检测成功")

    # 检查固件
    has_firmware, info = manager.check_firmware()
    if not has_firmware:
        print("需要烧录固件")
        manager.flash_firmware()
```

### 便捷函数

```python
from esp32_arduino import auto_setup_esp32

# 一键自动设置
success, message = auto_setup_esp32()
if success:
    print(f"设置成功: {message}")
else:
    print(f"设置失败: {message}")
```

## 📋 功能特性

### 1. 自动设备检测
- 检测指定串口上的ESP32设备
- 使用esptool进行设备识别
- 支持超时设置

### 2. 固件状态检查
- 尝试连接ESP32并检查响应
- 验证固件版本和兼容性
- 提供详细的固件信息

### 3. 自动固件烧录
- 自动查找可用的固件文件
- 支持PlatformIO编译输出
- 如果找不到固件，自动尝试编译
- 使用esptool进行安全烧录

### 4. 设备验证
- 烧录后等待设备重启
- 验证固件是否正常工作
- 提供详细的状态反馈

## 🛠️ 配置选项

### 端口配置
```python
# 自定义端口和波特率
esp32_begin(port="/dev/ttyUSB1", baudrate=460800)

# 或使用设备管理器
manager = ESP32DeviceManager(port="/dev/ttyUSB1", baudrate=460800)
```

### 固件路径
固件文件查找顺序：
1. `esp32-rk3588-sensor-system/esp32_firmware/.pio/build/esp32dev/firmware.bin`
2. 固件目录下包含"firmware"的.bin文件
3. 固件目录下第一个.bin文件

## 📝 命令行工具

设备管理器也提供命令行接口：

```bash
# 进入库目录
cd /home/mobox/jupyter-vue/esp32-arduino-python

# 仅检测设备
python -m esp32_arduino.device_manager --detect

# 检查固件状态
python -m esp32_arduino.device_manager --check-firmware

# 编译固件
python -m esp32_arduino.device_manager --compile

# 烧录固件
python -m esp32_arduino.device_manager --flash

# 完整自动设置
python -m esp32_arduino.device_manager --auto-setup
```

## 🔍 故障排除

### 常见问题

1. **设备检测失败**
   ```
   ❌ 未检测到ESP32设备: /dev/ttyUSB0
   ```
   - 检查USB连接
   - 确认串口权限：`sudo chmod 666 /dev/ttyUSB0`
   - 检查设备是否被其他程序占用

2. **固件烧录失败**
   ```
   ❌ 固件烧录失败
   ```
   - 确保esptool已安装：`pip install esptool`
   - 检查固件文件是否存在
   - 尝试手动擦除Flash：`esptool.py --port /dev/ttyUSB0 erase_flash`

3. **编译失败**
   ```
   ❌ 固件编译失败
   ```
   - 确保PlatformIO已安装：`pip install platformio`
   - 检查固件源码是否完整
   - 确保网络连接正常（PlatformIO需要下载依赖）

### 调试模式

启用详细日志：
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 然后正常使用库
esp32_begin()
```

## 🎯 最佳实践

### 1. 项目初始化
```python
from esp32_arduino import *

def setup():
    """项目初始化"""
    if esp32_begin():
        print("硬件初始化成功")
        return True
    else:
        print("硬件初始化失败，使用模拟模式")
        return False

def loop():
    """主循环"""
    # 你的代码
    pass

def main():
    if setup():
        try:
            while True:
                loop()
        except KeyboardInterrupt:
            print("程序中断")
        finally:
            esp32_close()

if __name__ == "__main__":
    main()
```

### 2. 错误处理
```python
from esp32_arduino import *

def safe_esp32_operation():
    try:
        if esp32_begin():
            # 执行硬件操作
            ledOn()
            temp = readTemperature()
            print(f"温度: {temp}°C")
            return True
        else:
            print("ESP32连接失败")
            return False
    except Exception as e:
        print(f"操作异常: {e}")
        return False
    finally:
        esp32_close()
```

### 3. 配置管理
```python
# config.py
ESP32_CONFIG = {
    'port': '/dev/ttyUSB0',
    'baudrate': 115200,
    'auto_setup': True,
    'timeout': 30
}

# main.py
from esp32_arduino import *
from config import ESP32_CONFIG

esp32_begin(**ESP32_CONFIG)
```

## 📚 示例代码

查看以下示例文件：
- `examples/auto_setup_demo.py` - 完整的自动设置演示
- `examples/basic_usage.py` - 基本使用方法
- `examples/07_all_channels_test.py` - 全通道测试

## 🤝 贡献

欢迎提交问题和改进建议！

## 📄 许可证

MIT License