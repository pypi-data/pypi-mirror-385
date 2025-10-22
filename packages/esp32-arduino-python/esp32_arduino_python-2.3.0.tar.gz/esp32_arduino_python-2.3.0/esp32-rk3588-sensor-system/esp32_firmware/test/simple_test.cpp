/*
 * ESP32 简单测试固件
 * 用于验证ESP32硬件是否正常工作
 */

#include <Arduino.h>

#define LED_PIN 2  // 内置LED引脚

void setup() {
  // 初始化串口
  Serial.begin(115200);
  delay(2000);  // 等待串口稳定

  // 初始化LED
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  // 打印启动信息
  Serial.println();
  Serial.println("=== ESP32 简单测试程序 ===");
  Serial.println("固件版本: v1.0-test");
  Serial.println("功能测试:");
  Serial.println("  - 串口通信");
  Serial.println("  - LED闪烁");
  Serial.println("  - 基本GPIO");
  Serial.println("Ready>");
}

void loop() {
  static unsigned long last_led_toggle = 0;
  static bool led_state = false;
  static unsigned long last_status = 0;

  unsigned long current_time = millis();

  // 每秒切换LED状态
  if (current_time - last_led_toggle >= 1000) {
    led_state = !led_state;
    digitalWrite(LED_PIN, led_state ? HIGH : LOW);
    last_led_toggle = current_time;
  }

  // 每5秒打印状态
  if (current_time - last_status >= 5000) {
    Serial.print("STATUS:uptime=");
    Serial.print(current_time);
    Serial.print("ms,led=");
    Serial.println(led_state ? "ON" : "OFF");
    last_status = current_time;
  }

  // 处理串口输入
  handle_serial_input();
}

void handle_serial_input() {
  while (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    cmd.toUpperCase();

    if (cmd == "PING") {
      Serial.println("OK:PONG");
    }
    else if (cmd == "STATUS") {
      Serial.print("OK:uptime=");
      Serial.print(millis());
      Serial.print("ms,led=");
      Serial.print(digitalRead(LED_PIN) ? "ON" : "OFF");
      Serial.println(",free_heap=" + String(ESP.getFreeHeap()));
    }
    else if (cmd == "LED ON") {
      digitalWrite(LED_PIN, HIGH);
      Serial.println("OK:LED ON");
    }
    else if (cmd == "LED OFF") {
      digitalWrite(LED_PIN, LOW);
      Serial.println("OK:LED OFF");
    }
    else if (cmd == "RESET") {
      Serial.println("OK:RESETTING");
      delay(100);
      ESP.restart();
    }
    else if (cmd == "HELP") {
      Serial.println("可用命令:");
      Serial.println("  PING - 测试连接");
      Serial.println("  STATUS - 系统状态");
      Serial.println("  LED ON/OFF - 控制LED");
      Serial.println("  RESET - 重启系统");
      Serial.println("  HELP - 显示帮助");
    }
    else {
      Serial.println("ERROR:未知命令，输入HELP查看帮助");
    }

    Serial.println("Ready>");
  }
}