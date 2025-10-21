/*
 * ESP32 扩展板引脚配置
 * 根据实际硬件连接情况调整引脚定义
 */

#ifndef PIN_CONFIG_H
#define PIN_CONFIG_H

// ===========================================
// 引脚配置说明
// ===========================================
// 请根据您的ESP32扩展板实际连接情况修改以下引脚定义
// 扩展板有以下区域：
// - ADC区域：用于模拟传感器
// - GPIO区域：用于数字输入输出
// - I2C区域：用于I2C设备 (预留扩展)
// - SPI区域：用于SPI设备 (预留扩展)

// ===========================================
// ADC传感器引脚 (ADC区域 - 扩展板CH0-CH1)
// ===========================================
// 扩展板ADC通道：CH0=IO32, CH1=IO33
#define TEMP_SENSOR_PIN 32    // 温度传感器ADC引脚 (扩展板CH0)
#define HUMID_SENSOR_PIN 33   // 湿度传感器ADC引脚 (扩展板CH1)

// ESP32硬件ADC通道映射 (注意：ESP32硬件通道与扩展板编号不同)
#define TEMP_ADC_CHANNEL ADC1_CHANNEL_4   // GPIO32 = ESP32硬件ADC1_CH4
#define HUMID_ADC_CHANNEL ADC1_CHANNEL_5  // GPIO33 = ESP32硬件ADC1_CH5

// ===========================================
// GPIO数字引脚 (常规PIN口区域 - 扩展板CH2-CH4)
// ===========================================
// 扩展板常规PIN口通道：CH2=IO25, CH3=IO26, CH4=IO27
#define LED_PIN 25            // LED指示灯 (扩展板CH2)
#define BUTTON_PIN 0          // 按钮开关 (保持原有配置)
#define RELAY_PIN 26          // 继电器控制 (扩展板CH3)

// 常规PIN口可用引脚
#define GPIO_PIN_25 25        // 扩展板CH2
#define GPIO_PIN_26 26        // 扩展板CH3
#define GPIO_PIN_27 27        // 扩展板CH4 - 现在用于DHT11传感器

// ===========================================
// I2C引脚 (IIC区域 - 扩展板CH5-CH8) - 预留扩展
// ===========================================
// 扩展板IIC通道：CH5-CH6=14/13, CH6-CH7=16/17, CH7-CH8=22/21
#define I2C_SDA_PIN 21        // I2C数据线 (扩展板CH8)
#define I2C_SCL_PIN 22        // I2C时钟线 (扩展板CH7)

// 其他可用I2C引脚组合
#define I2C_SDA_PIN_ALT1 13   // I2C数据线 (扩展板CH5)
#define I2C_SCL_PIN_ALT1 14   // I2C时钟线 (扩展板CH6)
#define I2C_SDA_PIN_ALT2 17   // I2C数据线 (扩展板CH6)
#define I2C_SCL_PIN_ALT2 16   // I2C时钟线 (扩展板CH7)

// ===========================================
// SPI引脚 (SPI区域) - 预留扩展
// ===========================================
// 根据扩展板实际SPI引脚：4, 19, 23, 18
#define SPI_CS_PIN 4          // SPI片选
#define SPI_MISO_PIN 19       // SPI主入从出
#define SPI_MOSI_PIN 23       // SPI主出从入
#define SPI_SCK_PIN 18        // SPI时钟

// ===========================================
// 扩展板通道布局总结 (按照扩展板编号CH0-CH8)
// ===========================================
// 
// ADC区域 (CH0-CH1)：
//   CH0: IO32 - 温度传感器
//   CH1: IO33 - 湿度传感器
//
// 常规PIN口区域 (CH2-CH4)：
//   CH2: IO25 - LED指示灯
//   CH3: IO26 - 继电器控制
//   CH4: IO27 - 备用GPIO
//
// SPI区域：CS=4, MISO=19, MOSI=23, SCK=18
//   用于SPI设备通信
//
// I2C区域 (CH5-CH8，3组可选)：
//   组合1: CH5=13(SDA), CH6=14(SCL)
//   组合2: CH6=17(SDA), CH7=16(SCL)  
//   组合3: CH8=21(SDA), CH7=22(SCL) (默认使用)
//
// ===========================================
// DHT11数字温湿度传感器配置
// ===========================================
// 使用扩展板CH4 (GPIO27) 作为DHT11数据引脚
#define DHT11_PIN 27           // DHT11数据引脚 (扩展板CH4)
#define DHTTYPE DHT11          // DHT传感器类型定义

// 当前配置：
// - 温度传感器: IO32 (扩展板CH0) - 备用ADC传感器
// - 湿度传感器: IO33 (扩展板CH1) - 备用ADC传感器
// - LED: IO25 (扩展板CH2)
// - 继电器: IO26 (扩展板CH3)
// - DHT11温湿度传感器: IO27 (扩展板CH4) - 新增

#endif // PIN_CONFIG_H