/*
 * ESP32 传感器控制系统 - 硬件控制模块
 * 负责控制LED、继电器等硬件
 */

#ifndef HARDWARE_CONTROL_H
#define HARDWARE_CONTROL_H

#include <Arduino.h>
#include "pin_config.h"

// 初始化硬件
void init_hardware();

// LED控制
void set_led(bool state);

// 继电器控制
void set_relay(bool state);

// 读取按钮状态
bool read_button();

#endif // HARDWARE_CONTROL_H