/*
 * ESP32 传感器控制系统 - 命令处理模块
 * 负责解析和处理串口命令
 */

#include "command_handler.h"
#include "sensor_manager.h"
#include "hardware_control.h"
#include "dht11_sensor.h"
#include "pin_config.h"
#include <WiFi.h>
#include "driver/adc.h"

// 全局变量
extern float temperature;
extern float humidity;
extern bool led_state;

// 命令缓冲区
String input_buffer = "";
bool command_ready = false;

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
  else if (cmd.startsWith("PINREAD:")) {
    handle_pinread_command(cmd.substring(8));
  }
  else if (cmd.startsWith("PINSET:")) {
    handle_pinset_command(cmd.substring(7));
  }
  else if (cmd.startsWith("ADCREAD:")) {
    handle_adcread_command(cmd.substring(8));
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
    Serial.print(digitalRead(BUTTON_PIN) ? "UP" : "DOWN");
    Serial.print(",sensor_mode=");
    Serial.print(get_sensor_mode() == SENSOR_MODE_DHT11 ? "DHT11" : "ADC");
    Serial.print(",dht11_status=");
    Serial.println(dht11_sensor.getStatusString());
  }
  else if (param == "DHT11_STATUS") {
    Serial.print("OK:");
    Serial.println(dht11_sensor.getSensorInfo());
  }
  else if (param == "SENSOR_STATUS") {
    Serial.print("OK:");
    Serial.println(get_sensor_status());
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
      set_led(true);
      Serial.println("OK:LED ON");
    }
    else if (value == "OFF") {
      set_led(false);
      Serial.println("OK:LED OFF");
    }
    else {
      Serial.println("ERROR:Invalid LED value");
    }
  }
  else if (device == "RELAY") {
    if (value == "ON") {
      set_relay(true);
      Serial.println("OK:RELAY ON");
    }
    else if (value == "OFF") {
      set_relay(false);
      Serial.println("OK:RELAY OFF");
    }
    else {
      Serial.println("ERROR:Invalid RELAY value");
    }
  }
  else if (device == "SENSOR") {
    if (value == "DHT11") {
      set_sensor_mode(SENSOR_MODE_DHT11);
      Serial.println("OK:SENSOR MODE DHT11");
    }
    else if (value == "ADC") {
      set_sensor_mode(SENSOR_MODE_ADC);
      Serial.println("OK:SENSOR MODE ADC");
    }
    else {
      Serial.println("ERROR:Invalid sensor mode");
    }
  }
  else {
    Serial.println("ERROR:Unknown device");
  }
}

// Arduino风格的GPIO命令处理
void handle_pinread_command(String param) {
  int pin = param.toInt();
  if (pin >= 0 && pin <= 39) {
    pinMode(pin, INPUT);
    int value = digitalRead(pin);
    Serial.print("OK:");
    Serial.println(value);
  } else {
    Serial.println("ERROR:Invalid pin number");
  }
}

void handle_pinset_command(String param) {
  int colon_pos = param.indexOf(':');
  if (colon_pos == -1) {
    Serial.println("ERROR:Invalid format, use PINSET:pin:value");
    return;
  }
  
  int pin = param.substring(0, colon_pos).toInt();
  int value = param.substring(colon_pos + 1).toInt();
  
  if (pin >= 0 && pin <= 39 && (value == 0 || value == 1)) {
    pinMode(pin, OUTPUT);
    digitalWrite(pin, value);
    Serial.print("OK:");
    Serial.println(value);
  } else {
    Serial.println("ERROR:Invalid pin or value");
  }
}

void handle_adcread_command(String param) {
  int pin = param.toInt();
  
  // 检查是否为有效的ADC引脚
  adc1_channel_t channel;
  bool valid_adc = false;
  
  switch(pin) {
    case 32: channel = ADC1_CHANNEL_4; valid_adc = true; break;
    case 33: channel = ADC1_CHANNEL_5; valid_adc = true; break;
    case 34: channel = ADC1_CHANNEL_6; valid_adc = true; break;
    case 35: channel = ADC1_CHANNEL_7; valid_adc = true; break;
    case 36: channel = ADC1_CHANNEL_0; valid_adc = true; break;
    case 37: channel = ADC1_CHANNEL_1; valid_adc = true; break;
    case 38: channel = ADC1_CHANNEL_2; valid_adc = true; break;
    case 39: channel = ADC1_CHANNEL_3; valid_adc = true; break;
    default: valid_adc = false; break;
  }
  
  if (valid_adc) {
    int raw_value = adc1_get_raw(channel);
    Serial.print("OK:");
    Serial.println(raw_value);
  } else {
    Serial.println("ERROR:Invalid ADC pin");
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
  else if (param == "INFO") {
    // 支持GET INFO命令，兼容esp32_arduino模块
    Serial.print("OK:");
    Serial.print("ESP32-D0WDR2-V3,");
    Serial.print("16MB Flash,");
    Serial.print("MAC:");
    Serial.print(WiFi.macAddress());
    Serial.print(",Uptime:");
    Serial.print(millis());
    Serial.println("ms");
  }
  else {
    Serial.println("ERROR:Invalid get parameter");
  }
}