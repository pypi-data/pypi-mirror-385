# ESP32 Arduino风格Python控制库

## 📖 简介

这是一个为ESP32设计的Arduino风格Python控制库，旨在让Python代码像Arduino代码一样简单直观。该库提供了统一的硬件抽象层，支持数字IO、模拟输入、传感器读取等功能。

## 🎯 项目特色

- **Arduino风格API**: Python代码写起来就像Arduino代码
- **扩展板支持**: 完整支持ESP32扩展板的所有通道
- **即插即用**: 简单的硬件连接，快速上手
- **丰富示例**: 从基础到进阶的完整示例库
- **模块化设计**: 清晰的代码结构，易于扩展

## 📋 硬件配置

### 主要组件
- **主控制器**: RK3588 (Rock 5B Plus)
- **微控制器**: ESP32-D0WDR2-V3 (16MB Flash)
- **连接方式**: USB串口 (/dev/ttyUSB0)
- **波特率**: 115200

### 扩展板通道配置

| 通道 | GPIO | 类型 | 功能描述 | 示例用途 |
|------|------|------|----------|----------|
| CH0  | 32   | ADC  | 模拟输入 | 温度传感器 |
| CH1  | 33   | ADC  | 模拟输入 | 湿度传感器 |
| CH2  | 25   | GPIO | 数字输出 | LED指示灯 |
| CH3  | 26   | GPIO | 数字输出 | 继电器控制 |
| CH4  | 27   | GPIO | 数字IO   | 按钮/开关 |
| CH5  | 13   | I2C  | I2C SDA  | I2C设备 (预留) |
| CH6  | 14   | I2C  | I2C SCL  | I2C设备 (预留) |
| CH7  | 22   | I2C  | I2C SCL  | I2C设备 (预留) |
| CH8  | 21   | I2C  | I2C SDA  | I2C设备 (预留) |

## 🚀 快速开始

### 1. 环境准备

```bash
# 激活虚拟环境
source /home/mobox/hardware/esp_venv/bin/activate

# 检查ESP32连接
ls -la /dev/ttyUSB*

# 如果需要权限
sudo chmod 666 /dev/ttyUSB0
```

### 2. 编译和上传固件

```bash
# 进入固件目录
cd esp32-rk3588-sensor-system/esp32_firmware

# 编译固件
pio run

# 上传固件
pio run --target upload
```

### 3. 运行第一个示例

```python
#!/usr/bin/env python3
from esp32_arduino import *

# 自动初始化ESP32（包括设备检测、固件烧录和连接）
if esp32_begin():
    print("ESP32设置成功！")

    # Arduino风格的代码
    digitalWrite(CH2, HIGH)  # 点亮LED
    delay(1000)              # 延时1秒
    digitalWrite(CH2, LOW)   # 关闭LED

    # 读取传感器
    temp = readTemperature()
    print(f"温度: {temp}°C")

    # 关闭连接
    esp32_close()
else:
    print("使用模拟模式")
```

### 🚀 新功能：自动检测和烧录

库现在支持自动检测ESP32设备并在需要时自动烧录固件：

```python
from esp32_arduino import *

# 方法1：使用默认自动设置
esp32_begin()  # 自动检测、烧录、连接

# 方法2：手动控制
esp32_begin(auto_setup=False)  # 不进行自动设置

# 方法3：使用设备管理器
manager = ESP32DeviceManager()
success, info = manager.auto_setup()

# 方法4：使用便捷函数
success, info = auto_setup_esp32()
```

## 📚 示例库

我们提供了从基础到进阶的完整示例：

### 基础示例 (⭐)
- **[01_digital_output.py](examples/01_digital_output.py)** - LED控制
- **[02_digital_input.py](examples/02_digital_input.py)** - 按钮读取
- **[03_analog_input.py](examples/03_analog_input.py)** - ADC读取

### 进阶示例 (⭐⭐⭐)
- **[04_pwm_output.py](examples/04_pwm_output.py)** - PWM亮度控制
- **[05_sensor_reading.py](examples/05_sensor_reading.py)** - 传感器监控
- **[06_relay_control.py](examples/06_relay_control.py)** - 继电器控制

### 综合示例 (⭐⭐⭐⭐)
- **[07_all_channels_test.py](examples/07_all_channels_test.py)** - 全通道测试
- **[auto_setup_demo.py](examples/auto_setup_demo.py)** - 自动设置功能演示

详细说明请查看 [examples/README.md](examples/README.md)

## 🔧 Arduino风格API

### 基础函数

```python
# 连接管理
esp32_begin()                    # 初始化连接
esp32_close()                    # 关闭连接

# 数字IO
digitalWrite(pin, HIGH/LOW)      # 数字输出
value = digitalRead(pin)         # 数字输入

# 模拟输入
adc_value = analogRead(pin)      # ADC读取 (0-4095)

# 时间函数
delay(1000)                      # 延时1秒
uptime = millis()                # 获取运行时间
```

### 便捷函数

```python
# LED控制
ledOn()                          # 点亮CH2的LED
ledOff()                         # 关闭CH2的LED

# 传感器读取
temp = readTemperature()         # 读取CH0温度
humid = readHumidity()           # 读取CH1湿度
```

### 通道常量

```python
CH0 = 32  # ADC - 温度传感器
CH1 = 33  # ADC - 湿度传感器
CH2 = 25  # GPIO - LED指示灯
CH3 = 26  # GPIO - 继电器控制
CH4 = 27  # GPIO - 通用IO
```

## 📁 项目结构

```
esp32-rk3588-sensor-system/
├── esp32_firmware/              # ESP32固件 (PlatformIO项目)
│   ├── src/
│   │   ├── main.cpp            # 主程序
│   │   ├── pin_config.h        # 引脚配置
│   │   ├── command_handler.*   # 命令处理
│   │   ├── hardware_control.*  # 硬件控制
│   │   └── sensor_manager.*    # 传感器管理
│   └── platformio.ini          # PlatformIO配置
├── rk3588_controller/          # RK3588控制程序
├── docs/                       # 文档
├── tools/                      # 工具脚本
└── examples/                   # 示例代码
    ├── 01_digital_output.py    # 数字输出示例
    ├── 02_digital_input.py     # 数字输入示例
    ├── 03_analog_input.py      # 模拟输入示例
    ├── 04_pwm_output.py        # PWM输出示例
    ├── 05_sensor_reading.py    # 传感器读取示例
    ├── 06_relay_control.py     # 继电器控制示例
    ├── 07_all_channels_test.py # 全通道测试
    └── README.md               # 示例说明

arduino_esp32.py                # Arduino风格Python库
arduino_example.py              # 综合示例
debug_serial.py                 # 串口调试工具
```

## 🛠️ 开发工具

### 调试工具
```bash
# 串口调试
python3 debug_serial.py

# LED测试
python3 test_led.py

# Arduino库测试
python3 arduino_esp32.py
```

### 固件开发
```bash
# 编译
cd esp32-rk3588-sensor-system/esp32_firmware
pio run

# 上传
pio run --target upload

# 监控串口
pio device monitor
```

## 📖 支持的命令协议

ESP32固件支持以下串口命令：

### Arduino风格命令
- `PINREAD:pin` - 数字读取 (类似digitalRead)
- `PINSET:pin:value` - 数字写入 (类似digitalWrite)
- `ADCREAD:pin` - 模拟读取 (类似analogRead)

### 系统命令
- `PING` - 连接测试
- `INFO` - 获取系统信息
- `RESET` - 重启ESP32

### 传统命令 (兼容)
- `READ:TEMP` - 读取温度
- `READ:HUMID` - 读取湿度
- `SET:LED:ON/OFF` - 控制LED
- `SET:RELAY:ON/OFF` - 控制继电器

## 🔍 故障排除

### 常见问题

1. **ESP32连接失败**
   ```bash
   # 检查设备
   ls -la /dev/ttyUSB*
   
   # 检查权限
   sudo chmod 666 /dev/ttyUSB0
   
   # 测试连接
   echo "PING" > /dev/ttyUSB0 && timeout 2 cat /dev/ttyUSB0
   ```

2. **编译错误**
   ```bash
   # 清理重新编译
   cd esp32-rk3588-sensor-system/esp32_firmware
   pio run --target clean
   pio run
   ```

3. **Python库连接问题**
   ```python
   # 调试连接
   from arduino_esp32 import *
   if not esp32_begin():
       print("连接失败，请检查硬件")
   ```

### 硬件检查

```bash
# 运行全通道测试
python3 examples/07_all_channels_test.py

# 选择 "8 - 全部测试" 进行完整硬件验证
```

## 📊 性能特性

- **传感器更新频率**: 1Hz (可配置)
- **串口通信**: 115200 bps
- **命令响应时间**: <100ms
- **内存使用**: <64KB RAM, <1MB Flash
- **功耗**: 典型值 80mA @3.3V
- **GPIO操作速度**: >1000 操作/秒

## 🤝 贡献指南

欢迎贡献代码和示例！

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 发起 Pull Request

### 开发规范
- 遵循Arduino风格的API设计
- 添加详细的注释和文档
- 包含相应的测试示例
- 确保硬件安全性

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- ESP32社区提供的优秀文档和示例
- Arduino项目的API设计灵感
- PlatformIO提供的开发环境

## 📞 支持

如有问题或建议，请：

1. 查看 [examples/README.md](examples/README.md) 获取详细示例
2. 运行 `python3 examples/07_all_channels_test.py` 进行硬件测试
3. 使用 `python3 debug_serial.py` 进行串口调试

---

**让Python像Arduino一样简单！** 🚀