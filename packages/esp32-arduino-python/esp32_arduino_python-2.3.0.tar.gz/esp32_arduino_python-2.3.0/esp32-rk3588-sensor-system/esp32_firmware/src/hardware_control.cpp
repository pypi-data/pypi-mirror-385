/*
 * ESP32 传感器控制系统 - 硬件控制模块
 * 负责控制LED、继电器等硬件
 */

#include "hardware_control.h"

// 全局变量
bool led_state = false;

void init_hardware() {
  // 初始化引脚
  pinMode(LED_PIN, OUTPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(RELAY_PIN, OUTPUT);
  
  // 初始状态
  digitalWrite(LED_PIN, LOW);
  digitalWrite(RELAY_PIN, LOW);
}

void set_led(bool state) {
  digitalWrite(LED_PIN, state ? HIGH : LOW);
  led_state = state;
}

void set_relay(bool state) {
  digitalWrite(RELAY_PIN, state ? HIGH : LOW);
}

bool read_button() {
  return !digitalRead(BUTTON_PIN); // 按钮按下为LOW，返回true表示按下
}