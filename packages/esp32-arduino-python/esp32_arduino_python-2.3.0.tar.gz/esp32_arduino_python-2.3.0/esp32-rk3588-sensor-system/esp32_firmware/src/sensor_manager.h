/*
 * ESP32 传感器控制系统 - 传感器管理模块
 * 负责读取和管理传感器数据
 */

#ifndef SENSOR_MANAGER_H
#define SENSOR_MANAGER_H

#include <Arduino.h>
#include "pin_config.h"

// 传感器更新间隔
#define SENSOR_INTERVAL 1000 // 1秒

// 传感器模式
enum SensorMode {
    SENSOR_MODE_DHT11 = 0,   // 使用DHT11数字传感器
    SENSOR_MODE_ADC           // 使用ADC模拟传感器（备用）
};

// 传感器初始化
void init_sensors();

// 更新传感器数据
void update_sensors();

// 读取温度
float read_temperature();

// 读取湿度
float read_humidity();

// 设置传感器模式
void set_sensor_mode(SensorMode mode);

// 获取当前传感器模式
SensorMode get_sensor_mode();

// 检查DHT11是否可用
bool is_dht11_available();

// 获取传感器状态信息
String get_sensor_status();

#endif // SENSOR_MANAGER_H