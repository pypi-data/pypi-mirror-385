# ESP32扩展板配置指南

## 扩展板概述

您的ESP32扩展板提供了多种接口，便于连接各种传感器和执行器：

### 接口区域说明

1. **自选做ADC区域**
   - 用于连接模拟传感器
   - 支持0-3.3V模拟信号输入
   - 多个ADC通道可选

2. **自选做SPI区域**
   - 用于连接SPI设备
   - 如显示屏、存储器、传感器模块等

3. **自选做IIC区域**
   - 用于连接I2C设备
   - 如传感器模块、OLED显示屏等

4. **GPIO区域**
   - 数字输入输出引脚
   - 用于LED、继电器、按钮等

## 推荐连接方案

### 方案一：基础传感器系统

```
ADC区域连接：
├── 通道1 → 温度传感器 (如LM35、热敏电阻等)
└── 通道2 → 湿度传感器 (如土壤湿度传感器等)

GPIO区域连接：
├── GPIO2 → LED指示灯
├── GPIO4 → 继电器模块
└── GPIO0 → 按钮开关
```

### 方案二：扩展I2C传感器系统

```
I2C区域连接：
├── SDA → DHT22/SHT30温湿度传感器模块
├── SCL → OLED显示屏
└── 其他I2C设备

GPIO区域连接：
├── GPIO2 → LED指示灯
├── GPIO4 → 继电器模块
└── GPIO0 → 按钮开关
```

## 引脚配置

### 当前默认配置

在 `esp32_firmware/src/pin_config.h` 中定义了默认引脚：

```cpp
// ADC传感器引脚
#define TEMP_SENSOR_PIN 36    // 温度传感器
#define HUMID_SENSOR_PIN 39   // 湿度传感器

// GPIO数字引脚
#define LED_PIN 2             // LED指示灯
#define BUTTON_PIN 0          // 按钮开关
#define RELAY_PIN 4           // 继电器控制

// I2C引脚 (预留扩展)
#define I2C_SDA_PIN 21        // I2C数据线
#define I2C_SCL_PIN 22        // I2C时钟线
```

### 自定义引脚配置

1. 根据您的实际连接情况，修改 `pin_config.h` 文件
2. 确保选择的引脚与扩展板上的标注一致
3. 避免引脚冲突

## 连接步骤

### 1. 确定引脚分配

1. 查看扩展板上的丝印标注
2. 根据您要连接的设备类型选择合适的区域
3. 记录实际使用的引脚号

### 2. 修改代码配置

1. 编辑 `esp32_firmware/src/pin_config.h`
2. 根据实际连接修改引脚定义
3. 重新编译固件

### 3. 硬件连接

1. **温度传感器** (ADC区域)：
   ```
   传感器VCC → 扩展板3.3V
   传感器GND → 扩展板GND
   传感器OUT → 选定的ADC引脚
   ```

2. **湿度传感器** (ADC区域)：
   ```
   传感器VCC → 扩展板3.3V
   传感器GND → 扩展板GND
   传感器OUT → 选定的ADC引脚
   ```

3. **LED指示灯** (GPIO区域)：
   ```
   LED正极 → 220Ω电阻 → 选定GPIO
   LED负极 → 扩展板GND
   ```

4. **继电器模块** (GPIO区域)：
   ```
   继电器VCC → 扩展板5V或3.3V
   继电器GND → 扩展板GND
   继电器IN → 选定GPIO
   ```

5. **按钮开关** (GPIO区域)：
   ```
   按钮一端 → 选定GPIO
   按钮另一端 → 扩展板GND
   ```

## 测试验证

### 1. 编译固件
```bash
cd esp32-rk3588-sensor-system/esp32_firmware
pio run
```

### 2. 刷写固件
```bash
cd ../tools
python3 flash_esp32.py --firmware ../esp32_firmware/.pio/build/esp32dev/firmware.bin
```

### 3. 测试通信
```bash
cd ../rk3588_controller/tests
python3 serial_test.py
```

### 4. 功能测试
- 发送 `READ:TEMP` 测试温度读取
- 发送 `READ:HUMID` 测试湿度读取
- 发送 `SET:LED:ON` 测试LED控制
- 发送 `SET:RELAY:ON` 测试继电器控制

## 故障排除

### 1. ADC读数异常
- 检查传感器供电电压
- 确认ADC引脚连接正确
- 验证传感器输出电压范围

### 2. GPIO控制无效
- 检查引脚定义是否正确
- 确认负载电流不超过GPIO限制
- 验证共地连接

### 3. 通信问题
- 检查USB连接
- 确认波特率设置
- 验证串口权限

## 扩展建议

1. **添加I2C传感器**：
   - 使用I2C区域连接更多传感器
   - 如BME280环境传感器、MPU6050陀螺仪等

2. **添加SPI设备**：
   - 使用SPI区域连接显示屏
   - 如TFT LCD、OLED等

3. **增加更多GPIO设备**：
   - 连接更多LED、按钮
   - 添加蜂鸣器、电机驱动等