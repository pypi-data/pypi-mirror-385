# ESP32 传感器控制系统使用指南

## 项目概述

这是一个完整的ESP32固件开发项目，实现了RK3588与ESP32之间的串口通信，支持传感器数据读取、硬件控制等功能。

## 硬件配置

- **主控制器**: RK3588 (Rock 5B Plus)
- **微控制器**: ESP32-D0WDR2-V3 (16MB Flash)
- **连接方式**: USB串口 (/dev/ttyUSB0)
- **波特率**: 115200

## 项目结构

```
hardware/
├── esp32_firmware.ino          # Arduino IDE格式的ESP32固件
├── echo_test.ino              # 简单的回声测试固件
├── esp32_platformio/          # PlatformIO项目目录
│   ├── src/main.cpp          # ESP32主程序源码
│   ├── platformio.ini        # PlatformIO配置
│   └── ...
├── rk3588_controller/         # RK3588控制程序
│   ├── main.py               # 主控制程序
│   ├── esp32_comm.py         # ESP32通信库
│   ├── sensor_manager.py     # 传感器数据管理
│   └── serial_test.py        # 串口测试工具
├── protocol/                  # 通信协议文档
├── flash_esp32.py            # ESP32刷写工具
└── ESP32_使用指南.md         # 本文档
```

## 支持的命令协议

ESP32固件支持以下串口命令（命令格式：`命令\n`）：

### Arduino风格命令 (推荐)
- `PINREAD:pin` - 数字读取，如 `PINREAD:25`
- `PINSET:pin:value` - 数字写入，如 `PINSET:25:1`
- `ADCREAD:pin` - 模拟读取，如 `ADCREAD:32`

### 基本命令
- `PING` - 连接测试，返回 `OK:PONG`
- `INFO` - 获取系统信息
- `RESET` - 重启ESP32

### 传感器读取 (兼容命令)
- `READ:TEMP` - 读取温度值
- `READ:HUMID` - 读取湿度值
- `READ:ALL` - 读取所有传感器数据

### 硬件控制 (兼容命令)
- `SET:LED:ON` - 打开LED
- `SET:LED:OFF` - 关闭LED
- `SET:RELAY:ON` - 打开继电器
- `SET:RELAY:OFF` - 关闭继电器

### GPIO操作 (兼容命令)
- `GET:GPIO:引脚号` - 读取GPIO状态

## 快速开始

### 1. 环境准备

```bash
# 创建虚拟环境
python3 -m venv esp_venv
source esp_venv/bin/activate

# 安装依赖
pip install esptool platformio pyserial
```

### 2. 编译ESP32固件

```bash
# 使用PlatformIO编译
source esp_venv/bin/activate
cd esp32_platformio
pio run

# 编译成功后固件位于：
# .pio/build/esp32dev/firmware.bin
```

### 3. 刷写固件到ESP32

```bash
# 使用我们的刷写工具
python3 flash_esp32.py --erase --firmware esp32_platformio/.pio/build/esp32dev/firmware.bin

# 或者直接使用esptool
source esp_venv/bin/activate
esptool.py --port /dev/ttyUSB0 erase_flash
esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash 0x1000 esp32_platformio/.pio/build/esp32dev/firmware.bin
```

### 4. 测试串口通信

```bash
# 使用串口测试工具
cd rk3588_controller
python3 serial_test.py

# 或者使用主控制程序
python3 main.py
```

## 开发工作流

### 1. 修改ESP32固件
- 编辑 `esp32_platformio/src/main.cpp`
- 使用 `pio run` 编译
- 使用 `pio run --target upload` 直接刷写

### 2. 修改RK3588控制程序
- 编辑 `rk3588_controller/` 目录下的Python文件
- 直接运行测试，无需编译

### 3. 调试方法
```bash
# 查看ESP32串口输出
python3 rk3588_controller/serial_test.py

# 发送测试命令
echo "PING" > /dev/ttyUSB0
cat /dev/ttyUSB0
```

## 故障排除

### 1. ESP32无法检测
```bash
# 检查设备连接
ls -la /dev/ttyUSB*

# 检查权限
sudo chmod 666 /dev/ttyUSB0

# 测试连接
source esp_venv/bin/activate
esptool.py --port /dev/ttyUSB0 chip_id
```

### 2. 编译错误
```bash
# 清理并重新编译
cd esp32_platformio
pio run --target clean
pio run

# 检查工具链
pio platform show espressif32
```

### 3. 串口通信问题
```bash
# 检查波特率
stty -F /dev/ttyUSB0 115200

# 测试回环
echo "test" > /dev/ttyUSB0 && timeout 1 cat /dev/ttyUSB0
```

## 扩展功能

### 添加新传感器
1. 在 `main.cpp` 中定义新引脚
2. 在 `handle_read_command()` 中添加处理逻辑
3. 在 `esp32_comm.py` 中添加对应方法

### 添加新控制设备
1. 在 `main.cpp` 中定义引脚和控制逻辑
2. 在 `handle_set_command()` 中添加处理
3. 在控制程序中添加调用接口

## 性能特性

- **传感器更新频率**: 1Hz (可配置)
- **串口通信**: 115200 bps
- **命令响应时间**: <100ms
- **内存使用**: <64KB RAM, <1MB Flash
- **功耗**: 典型值 80mA @3.3V

## 技术规格

### ESP32硬件
- **芯片**: ESP32-D0WDR2-V3 (revision v3.1)
- **Flash**: 16MB
- **RAM**: 520KB
- **频率**: 240MHz (双核)
- **GPIO**: 34个可用引脚

### 扩展板通道分配 (CH0-CH8)
- **CH0 (GPIO32)**: 温度传感器 (ADC1_CH4)
- **CH1 (GPIO33)**: 湿度传感器 (ADC1_CH5)
- **CH2 (GPIO25)**: LED指示灯
- **CH3 (GPIO26)**: 继电器控制
- **CH4 (GPIO27)**: 备用GPIO
- **CH5 (GPIO13)**: I2C SDA
- **CH6 (GPIO14)**: I2C SCL
- **CH7 (GPIO22)**: I2C SCL (备用)
- **CH8 (GPIO21)**: I2C SDA (备用)

### SPI接口
- **CS (GPIO4)**: SPI片选
- **MISO (GPIO19)**: SPI主入从出
- **MOSI (GPIO23)**: SPI主出从入
- **SCK (GPIO18)**: SPI时钟

## 更新历史

- **v1.0** - 初始版本，基本传感器和控制功能
- 支持温度、湿度读取
- 支持LED、继电器控制
- 完整的串口命令协议

## 许可证

本项目为开源项目，遵循MIT许可证。 
#
# Arduino风格Python API

### 快速开始

```python
#!/usr/bin/env python3
from arduino_esp32 import *

# 初始化ESP32连接
esp32_begin()

# Arduino风格的代码
digitalWrite(CH2, HIGH)  # 点亮LED
delay(1000)              # 延时1秒
digitalWrite(CH2, LOW)   # 关闭LED

# 读取传感器
adc_value = analogRead(CH0)
temp = readTemperature()

# 关闭连接
esp32_close()
```

### API参考

#### 连接管理
```python
esp32_begin()                    # 初始化ESP32连接
esp32_close()                    # 关闭连接
```

#### 数字IO
```python
digitalWrite(pin, HIGH/LOW)      # 数字输出
value = digitalRead(pin)         # 数字输入 (返回HIGH/LOW)
```

#### 模拟输入
```python
adc_value = analogRead(pin)      # ADC读取 (返回0-4095)
```

#### 时间函数
```python
delay(1000)                      # 延时1秒 (毫秒)
uptime = millis()                # 获取运行时间 (毫秒)
```

#### 便捷函数
```python
ledOn()                          # 点亮CH2的LED
ledOff()                         # 关闭CH2的LED
temp = readTemperature()         # 读取CH0温度传感器
humid = readHumidity()           # 读取CH1湿度传感器
```

#### 常量定义
```python
# 电平常量
HIGH = 1
LOW = 0

# 扩展板通道常量
CH0 = 32  # ADC - 温度传感器
CH1 = 33  # ADC - 湿度传感器
CH2 = 25  # GPIO - LED指示灯
CH3 = 26  # GPIO - 继电器控制
CH4 = 27  # GPIO - 通用IO
```

### 示例代码

#### LED闪烁
```python
from arduino_esp32 import *

esp32_begin()

while True:
    ledOn()
    delay(1000)
    ledOff()
    delay(1000)
```

#### 传感器读取
```python
from arduino_esp32 import *

esp32_begin()

while True:
    temp = readTemperature()
    humid = readHumidity()
    print(f"温度: {temp:.1f}°C, 湿度: {humid:.1f}%")
    delay(2000)
```

#### 按钮控制LED
```python
from arduino_esp32 import *

esp32_begin()

while True:
    button = digitalRead(CH4)
    if button == HIGH:
        ledOn()
    else:
        ledOff()
    delay(100)
```

### 完整示例库

查看 `examples/` 目录获取更多示例：

- `01_digital_output.py` - 数字输出基础
- `02_digital_input.py` - 数字输入读取
- `03_analog_input.py` - 模拟输入处理
- `04_pwm_output.py` - PWM亮度控制
- `05_sensor_reading.py` - 传感器监控
- `06_relay_control.py` - 继电器控制
- `07_all_channels_test.py` - 全通道测试

运行示例：
```bash
source /home/mobox/hardware/esp_venv/bin/activate
python3 examples/01_digital_output.py
```