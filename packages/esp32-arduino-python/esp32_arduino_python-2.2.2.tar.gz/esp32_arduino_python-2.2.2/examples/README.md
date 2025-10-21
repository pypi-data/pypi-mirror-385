# ESP32 Arduino风格示例

这个目录包含了使用Arduino风格Python库控制ESP32的各种示例。所有示例都基于扩展板的通道配置。

## 📋 扩展板通道配置

| 通道 | GPIO | 类型 | 功能描述 |
|------|------|------|----------|
| CH0  | 32   | ADC  | 温度传感器输入 |
| CH1  | 33   | ADC  | 湿度传感器输入 |
| CH2  | 25   | GPIO | LED指示灯输出 |
| CH3  | 26   | GPIO | 继电器控制输出 |
| CH4  | 27   | GPIO | 通用数字IO |
| CH5  | 13   | I2C  | I2C SDA (预留) |
| CH6  | 14   | I2C  | I2C SCL (预留) |
| CH7  | 22   | I2C  | I2C SCL (预留) |
| CH8  | 21   | I2C  | I2C SDA (预留) |

## 📚 示例列表

### 基础示例

#### [01_digital_output.py](01_digital_output.py) - 数字输出
- **功能**: 控制LED开关
- **学习内容**: `digitalWrite()`, `delay()`
- **硬件**: LED连接到CH2
- **难度**: ⭐

```python
digitalWrite(CH2, HIGH)  # 点亮LED
delay(1000)              # 延时1秒
digitalWrite(CH2, LOW)   # 关闭LED
```

#### [02_digital_input.py](02_digital_input.py) - 数字输入
- **功能**: 读取按钮或开关状态
- **学习内容**: `digitalRead()`
- **硬件**: 按钮连接到CH4
- **难度**: ⭐

```python
button_state = digitalRead(CH4)
if button_state == HIGH:
    print("按钮按下")
```

#### [03_analog_input.py](03_analog_input.py) - 模拟输入
- **功能**: 读取ADC值和电压
- **学习内容**: `analogRead()`, ADC转换
- **硬件**: 传感器连接到CH0, CH1
- **难度**: ⭐⭐

```python
adc_value = analogRead(CH0)
voltage = (adc_value / 4095.0) * 3.3
```

### 进阶示例

#### [04_pwm_output.py](04_pwm_output.py) - PWM输出
- **功能**: 模拟PWM控制LED亮度
- **学习内容**: PWM原理, 软件PWM实现
- **硬件**: LED连接到CH2
- **难度**: ⭐⭐⭐

```python
def pwm_write(pin, duty_cycle):
    # 通过快速开关模拟PWM
    high_time = period * duty_cycle / 100
    digitalWrite(pin, HIGH)
    delay(high_time)
    digitalWrite(pin, LOW)
    delay(period - high_time)
```

#### [05_sensor_reading.py](05_sensor_reading.py) - 传感器读取
- **功能**: 温湿度监控和报警
- **学习内容**: 传感器数据处理, 报警逻辑
- **硬件**: 温湿度传感器, LED指示
- **难度**: ⭐⭐⭐

```python
temp, temp_adc = read_temperature()
humid, humid_adc = read_humidity()
alerts = check_alerts(temp, humid)
```

#### [06_relay_control.py](06_relay_control.py) - 继电器控制
- **功能**: 控制继电器开关设备
- **学习内容**: 继电器控制, 安全操作
- **硬件**: 继电器模块连接到CH3
- **难度**: ⭐⭐
- **⚠️ 安全提示**: 操作继电器时注意电气安全

```python
def relay_on():
    digitalWrite(CH3, HIGH)
    print("继电器已打开")

def relay_off():
    digitalWrite(CH3, LOW)
    print("继电器已关闭")
```

### 综合示例

#### [07_all_channels_test.py](07_all_channels_test.py) - 全通道测试
- **功能**: 测试扩展板所有功能
- **学习内容**: 硬件验证, 系统测试
- **硬件**: 完整的扩展板配置
- **难度**: ⭐⭐⭐⭐

## 🚀 快速开始

### 1. 环境准备

```bash
# 激活虚拟环境
source /home/mobox/hardware/esp_venv/bin/activate

# 确保ESP32已连接到/dev/ttyUSB0
ls -la /dev/ttyUSB*
```

### 2. 运行示例

```bash
# 运行基础LED控制示例
python3 examples/01_digital_output.py

# 运行传感器读取示例
python3 examples/05_sensor_reading.py

# 运行全通道测试
python3 examples/07_all_channels_test.py
```

### 3. 硬件连接

根据示例需求连接相应硬件：

- **LED**: 连接到CH2 (GPIO25)，注意限流电阻
- **按钮**: 连接到CH4 (GPIO27)，建议使用上拉电阻
- **传感器**: 连接到CH0/CH1 (GPIO32/33)，注意电压范围0-3.3V
- **继电器**: 连接到CH3 (GPIO26)，注意驱动能力

## 📖 Arduino风格API参考

### 基础函数

```python
# 初始化
esp32_begin()                    # 初始化ESP32连接
esp32_close()                    # 关闭连接

# 数字IO
digitalWrite(pin, value)         # 数字输出 (value: HIGH/LOW)
digitalRead(pin)                 # 数字输入 (返回: HIGH/LOW)

# 模拟输入
analogRead(pin)                  # ADC读取 (返回: 0-4095)

# 时间函数
delay(ms)                        # 延时 (毫秒)
millis()                         # 获取运行时间 (毫秒)

# 常量
HIGH = 1                         # 高电平
LOW = 0                          # 低电平
```

### 扩展板专用函数

```python
# 便捷函数
ledOn()                          # 点亮CH2的LED
ledOff()                         # 关闭CH2的LED
readTemperature()                # 读取CH0温度传感器
readHumidity()                   # 读取CH1湿度传感器

# 通道常量
CH0, CH1, CH2, CH3, CH4          # 扩展板通道0-4
CH5, CH6, CH7, CH8               # I2C通道 (预留)
```

## 🔧 故障排除

### 常见问题

1. **连接失败**
   ```bash
   # 检查设备连接
   ls -la /dev/ttyUSB*
   
   # 检查权限
   sudo chmod 666 /dev/ttyUSB0
   ```

2. **ADC读数异常**
   - 检查输入电压是否在0-3.3V范围内
   - 确认传感器连接正确
   - 检查是否有干扰信号

3. **数字IO不工作**
   - 确认引脚配置正确
   - 检查硬件连接
   - 验证电源供应

### 调试技巧

```python
# 添加调试信息
print(f"ADC值: {analogRead(CH0)}")
print(f"GPIO状态: {digitalRead(CH2)}")

# 使用系统信息
info = _esp32_instance.getInfo()
print(f"ESP32信息: {info}")
```

## 📝 开发建议

1. **从简单示例开始**: 先运行基础示例，熟悉API
2. **逐步增加复杂度**: 理解基础后再尝试复杂功能
3. **注意硬件安全**: 特别是继电器等高压设备
4. **添加错误处理**: 在实际项目中添加异常处理
5. **测试硬件**: 使用全通道测试验证硬件功能

## 🤝 贡献

欢迎提交新的示例或改进现有示例！请确保：

- 代码风格与现有示例一致
- 包含详细的注释和说明
- 测试过硬件功能
- 更新相应的文档