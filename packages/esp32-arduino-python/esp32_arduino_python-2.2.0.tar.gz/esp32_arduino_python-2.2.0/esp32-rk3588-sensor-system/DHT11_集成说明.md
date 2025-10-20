# DHT11传感器集成说明

## 概述

本文档描述了在ESP32传感器控制系统中集成DHT11数字温湿度传感器的完整实现方案。

## 硬件连接

### DHT11传感器连接
```
DHT11传感器 → ESP32扩展板
├── VCC → 3.3V
├── GND → GND
└── DATA → GPIO27 (扩展板CH4)
```

### 注意事项
- 建议在VCC和GND之间添加100nF电容以提高稳定性
- 使用短连接线避免信号干扰
- 确保电源电压稳定（3.3V-5.5V）

## 软件架构

### 新增文件
- `dht11_sensor.h` - DHT11传感器类头文件
- `dht11_sensor.cpp` - DHT11传感器类实现
- `test_dht11.py` - Python测试脚本
- `DHT11_集成说明.md` - 本文档

### 修改文件
- `platformio.ini` - 添加DHT库依赖
- `pin_config.h` - 添加DHT11引脚配置
- `sensor_manager.h/.cpp` - 集成DHT11传感器管理
- `command_handler.cpp` - 添加DHT11相关命令
- `main.cpp` - 更新启动信息

### 依赖库
```ini
lib_deps =
    adafruit/DHT sensor library@^1.4.4
    adafruit/Adafruit Unified Sensor@^1.1.9
```

## 传感器模式

系统支持两种传感器模式：

### 1. DHT11模式（主要）
- 使用DHT11数字传感器
- 精度：温度±2℃，湿度±5%
- 响应时间：2秒间隔

### 2. ADC模式（备用）
- 使用ADC模拟传感器（原方案）
- 用于DHT11故障时的备用方案
- 可手动切换

## 串口命令协议

### 新增命令

#### 读取命令
```
READ:DHT11_STATUS     # 获取DHT11传感器详细信息
READ:SENSOR_STATUS    # 获取传感器系统状态
READ:ALL              # 现在包含传感器模式信息
```

#### 设置命令
```
SET:SENSOR:DHT11      # 切换到DHT11传感器模式
SET:SENSOR:ADC        # 切换到ADC模拟传感器模式
```

### 现有命令（保持兼容）
```
READ:TEMP             # 读取温度
READ:HUMID            # 读取湿度
SET:LED:ON/OFF        # LED控制
SET:RELAY:ON/OFF      # 继电器控制
```

## 编译和部署

### 1. 编译固件
```bash
cd esp32_firmware
pio run
```

### 2. 刷写固件
```bash
pio run --target upload
```

### 3. 测试功能
```bash
cd rk3588_controller
python3 test_dht11.py                    # 自动化测试
python3 test_dht11.py interactive        # 交互式测试
```

## Python API使用

### 基本使用
```python
from esp32_comm import ESP32Communicator

esp32 = ESP32Communicator()
if esp32.connect():
    # 读取DHT11温湿度
    temp = esp32.read_temperature()
    humidity = esp32.read_humidity()
    print(f"温度: {temp}°C, 湿度: {humidity}%")

    # 切换传感器模式
    esp32.send_command("SET", "SENSOR:ADC")  # ADC模式
    esp32.send_command("SET", "SENSOR:DHT11") # DHT11模式

    # 获取DHT11状态
    response = esp32.send_command("READ", "DHT11_STATUS")
    print(response)

    esp32.disconnect()
```

## 故障排除

### DHT11读取失败
1. 检查硬件连接
2. 确认电源稳定
3. 检查引脚配置（GPIO27）
4. 查看串口输出的错误信息

### 编译错误
1. 确认已安装PlatformIO
2. 检查库依赖是否正确安装
3. 清理并重新编译：`pio run --target clean && pio run`

### 通信错误
1. 检查串口设备权限
2. 确认波特率设置（115200）
3. 使用`ls /dev/ttyUSB*`检查设备

## 技术特性

### DHT11传感器特性
- 工作电压：3.3V-5.5V
- 温度范围：0-50℃（精度±2℃）
- 湿度范围：20-90%RH（精度±5%）
- 数字信号输出，单总线通信
- 最小采样间隔：2秒

### 系统特性
- 自动故障检测和恢复
- 双传感器冗余设计
- 实时状态监控
- 向后兼容原有命令协议
- 模块化设计便于维护

## 性能优化

### 已实现优化
1. **错误处理**：连续错误检测和自动模式切换
2. **数据验证**：读取数据合理性检查
3. **时序控制**：严格遵守DHT11时序要求
4. **缓存机制**：避免频繁读取提高性能

### 可选优化
1. **数据平滑**：添加移动平均滤波
2. **功耗管理**：休眠模式支持
3. **校准功能**：传感器精度校准
4. **数据记录**：历史数据存储

## 更新日志

### v1.1 (当前版本)
- ✅ 集成DHT11数字温湿度传感器
- ✅ 添加双传感器模式支持
- ✅ 实现自动故障切换
- ✅ 扩展串口命令协议
- ✅ 完整的Python测试套件

### v1.0 (原始版本)
- ✅ ADC模拟传感器支持
- ✅ 基础GPIO控制
- ✅ 串口通信协议
- ✅ 模块化架构设计

## 许可证

本项目遵循MIT许可证，详见项目根目录LICENSE文件。

---

**维护人员**: ESP32开发团队
**最后更新**: 2024年
**版本**: v1.1