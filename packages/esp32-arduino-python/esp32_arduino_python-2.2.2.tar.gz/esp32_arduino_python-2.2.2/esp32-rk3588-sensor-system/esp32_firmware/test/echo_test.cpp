/*
 * ESP32 传感器控制固件
 * 支持串口通信协议与RK3588通信
 * 包含传感器读取、LED控制、GPIO操作等功能
 */

#include "driver/adc.h"
#include "esp_adc_cal.h"
#include <WiFi.h>

// 引脚定义
#define LED_PIN 2          // 内置LED
#define TEMP_SENSOR_PIN 36 // 模拟温度传感器
#define HUMID_SENSOR_PIN 39 // 模拟湿度传感器
#define BUTTON_PIN 0       // 按钮
#define RELAY_PIN 4        // 继电器控制

// 传感器相关
float temperature = 25.0;
float humidity = 60.0;
bool led_state = false;
unsigned long last_sensor_read = 0;
const unsigned long SENSOR_INTERVAL = 1000; // 1秒

// 通信相关
String input_buffer = "";
bool command_ready = false;

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  // 初始化引脚
  pinMode(LED_PIN, OUTPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(RELAY_PIN, OUTPUT);
  
  // 初始化ADC
  adc1_config_width(ADC_WIDTH_BIT_12);
  adc1_config_channel_atten(ADC1_CHANNEL_0, ADC_ATTEN_DB_11); // GPIO36
  adc1_config_channel_atten(ADC1_CHANNEL_3, ADC_ATTEN_DB_11); // GPIO39
  
  // 初始状态
  digitalWrite(LED_PIN, LOW);
  digitalWrite(RELAY_PIN, LOW);
  
  Serial.println("=== ESP32 传感器控制系统 ===");
  Serial.println("固件版本: v1.0");
  Serial.println("芯片型号: ESP32-D0WDR2-V3");
  Serial.println("Flash大小: 16MB");
  Serial.print("MAC地址: ");
  Serial.println(WiFi.macAddress());
  Serial.println("支持命令:");
  Serial.println("  PING - 连接测试");
  Serial.println("  INFO - 获取系统信息");
  Serial.println("  READ:TEMP - 读取温度");
  Serial.println("  READ:HUMID - 读取湿度");
  Serial.println("  READ:ALL - 读取所有传感器");
  Serial.println("  SET:LED:ON/OFF - 控制LED");
  Serial.println("  SET:RELAY:ON/OFF - 控制继电器");
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

void handle_serial_input() {
  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') {
      if (input_buffer.length() > 0) {
        command_ready = true;
      }
    } else {
      input_buffer += c;
    }
  }
}

void process_command(String cmd) {
  cmd.trim();
  cmd.toUpperCase();
  
  if (cmd == "PING") {
    Serial.println("OK:PONG");
  }
  else if (cmd == "INFO") {
    Serial.print("OK:");
    Serial.print("ESP32-D0WDR2-V3,");
    Serial.print("16MB Flash,");
    Serial.print("MAC:");
    Serial.print(WiFi.macAddress());
    Serial.print(",Uptime:");
    Serial.print(millis());
    Serial.println("ms");
  }
  else if (cmd.startsWith("READ:")) {
    handle_read_command(cmd.substring(5));
  }
  else if (cmd.startsWith("SET:")) {
    handle_set_command(cmd.substring(4));
  }
  else if (cmd.startsWith("GET:")) {
    handle_get_command(cmd.substring(4));
  }
  else if (cmd == "RESET") {
    Serial.println("OK:Resetting");
    delay(100);
    ESP.restart();
  }
  else {
    Serial.println("ERROR:Unknown command");
  }
  
  Serial.println("Ready>");
}

void handle_read_command(String param) {
  if (param == "TEMP") {
    Serial.print("OK:");
    Serial.println(temperature, 2);
  }
  else if (param == "HUMID") {
    Serial.print("OK:");
    Serial.println(humidity, 2);
  }
  else if (param == "ALL") {
    Serial.print("OK:temp=");
    Serial.print(temperature, 2);
    Serial.print(",humid=");
    Serial.print(humidity, 2);
    Serial.print(",led=");
    Serial.print(led_state ? "ON" : "OFF");
    Serial.print(",button=");
    Serial.println(digitalRead(BUTTON_PIN) ? "UP" : "DOWN");
  }
  else {
    Serial.println("ERROR:Invalid read parameter");
  }
}

void handle_set_command(String param) {
  int colon_pos = param.indexOf(':');
  if (colon_pos == -1) {
    Serial.println("ERROR:Invalid set format");
    return;
  }
  
  String device = param.substring(0, colon_pos);
  String value = param.substring(colon_pos + 1);
  
  if (device == "LED") {
    if (value == "ON") {
      digitalWrite(LED_PIN, HIGH);
      led_state = true;
      Serial.println("OK:LED ON");
    }
    else if (value == "OFF") {
      digitalWrite(LED_PIN, LOW);
      led_state = false;
      Serial.println("OK:LED OFF");
    }
    else {
      Serial.println("ERROR:Invalid LED value");
    }
  }
  else if (device == "RELAY") {
    if (value == "ON") {
      digitalWrite(RELAY_PIN, HIGH);
      Serial.println("OK:RELAY ON");
    }
    else if (value == "OFF") {
      digitalWrite(RELAY_PIN, LOW);
      Serial.println("OK:RELAY OFF");
    }
    else {
      Serial.println("ERROR:Invalid RELAY value");
    }
  }
  else {
    Serial.println("ERROR:Unknown device");
  }
}

void handle_get_command(String param) {
  if (param.startsWith("GPIO:")) {
    int gpio_num = param.substring(5).toInt();
    if (gpio_num >= 0 && gpio_num <= 39) {
      pinMode(gpio_num, INPUT);
      int state = digitalRead(gpio_num);
      Serial.print("OK:");
      Serial.println(state);
    }
    else {
      Serial.println("ERROR:Invalid GPIO number");
    }
  }
  else {
    Serial.println("ERROR:Invalid get parameter");
  }
}

void update_sensors() {
  unsigned long current_time = millis();
  if (current_time - last_sensor_read >= SENSOR_INTERVAL) {
    // 模拟温度传感器读取 (基于ADC + 噪声)
    int temp_raw = adc1_get_raw(ADC1_CHANNEL_0);
    float temp_voltage = (temp_raw / 4095.0) * 3.3;
    temperature = 20.0 + (temp_voltage * 20.0) + random(-50, 50) / 100.0;
    
    // 模拟湿度传感器读取
    int humid_raw = adc1_get_raw(ADC1_CHANNEL_3);
    float humid_voltage = (humid_raw / 4095.0) * 3.3;
    humidity = 40.0 + (humid_voltage * 30.0) + random(-100, 100) / 100.0;
    
    // 限制范围
    temperature = constrain(temperature, -10.0, 50.0);
    humidity = constrain(humidity, 0.0, 100.0);
    
    last_sensor_read = current_time;
  }
} 