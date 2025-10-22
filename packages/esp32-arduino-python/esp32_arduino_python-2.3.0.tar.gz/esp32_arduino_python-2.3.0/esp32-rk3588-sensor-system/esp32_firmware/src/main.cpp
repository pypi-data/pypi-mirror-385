/*
 * ESP32 传感器控制系统 - 主程序
 * 基于模块化设计的ESP32固件
 */

#include <Arduino.h>
#include <WiFi.h>
#include "command_handler.h"
#include "sensor_manager.h"
#include "hardware_control.h"
#include "dht11_sensor.h"

void setup() {
  // 初始化串口
  Serial.begin(115200);
  delay(1000);
  
  // 初始化硬件
  init_hardware();
  
  // 初始化传感器
  init_sensors();
  
  // 初始化WiFi以获取MAC地址
  WiFi.mode(WIFI_MODE_STA);
  WiFi.disconnect();

  // 打印启动信息
  Serial.println("=== ESP32 传感器控制系统 ===");
  Serial.println("固件版本: v1.1 (支持DHT11)");
  Serial.println("芯片型号: ESP32-D0WDR2-V3");
  Serial.println("Flash大小: 16MB");
  Serial.print("MAC地址: ");
  Serial.println(WiFi.macAddress());
  Serial.println("扩展板配置:");
  Serial.print("  DHT11传感器: GPIO");
  Serial.println(DHT11_PIN);
  Serial.print("  备用温度传感器: GPIO");
  Serial.println(TEMP_SENSOR_PIN);
  Serial.print("  备用湿度传感器: GPIO");
  Serial.println(HUMID_SENSOR_PIN);
  Serial.print("  LED指示灯: GPIO");
  Serial.println(LED_PIN);
  Serial.print("  继电器: GPIO");
  Serial.println(RELAY_PIN);
  Serial.print("  按钮: GPIO");
  Serial.println(BUTTON_PIN);
  Serial.println("支持命令:");
  Serial.println("  PING - 连接测试");
  Serial.println("  INFO - 获取系统信息");
  Serial.println("  READ:TEMP - 读取温度");
  Serial.println("  READ:HUMID - 读取湿度");
  Serial.println("  READ:ALL - 读取所有传感器");
  Serial.println("  READ:DHT11_STATUS - DHT11状态信息");
  Serial.println("  READ:SENSOR_STATUS - 传感器系统状态");
  Serial.println("  SET:LED:ON/OFF - 控制LED");
  Serial.println("  SET:RELAY:ON/OFF - 控制继电器");
  Serial.println("  SET:SENSOR:DHT11/ADC - 切换传感器模式");
  Serial.println("  PINREAD:pin - Arduino风格数字读取");
  Serial.println("  PINSET:pin:value - Arduino风格数字写入");
  Serial.println("  ADCREAD:pin - ADC读取");
  Serial.println("  GET:GPIO:引脚号 - 读取GPIO状态");
  Serial.println("  RESET - 重启系统");
  Serial.println("Ready>");
}

void loop() {
  // 读取串口数据
  handle_serial_input();
  
  // 处理命令
  if (command_ready) {
    process_command(input_buffer);
    input_buffer = "";
    command_ready = false;
  }
  
  // 定期更新传感器数据
  update_sensors();
  
  delay(10);
}