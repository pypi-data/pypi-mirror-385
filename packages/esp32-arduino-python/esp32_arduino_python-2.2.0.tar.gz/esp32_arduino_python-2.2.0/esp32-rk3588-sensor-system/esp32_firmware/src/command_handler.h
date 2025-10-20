/*
 * ESP32 传感器控制系统 - 命令处理模块
 * 负责解析和处理串口命令
 */

#ifndef COMMAND_HANDLER_H
#define COMMAND_HANDLER_H

#include <Arduino.h>

// 全局变量声明
extern String input_buffer;
extern bool command_ready;

// 命令处理函数
void handle_serial_input();
void process_command(String cmd);
void handle_read_command(String param);
void handle_set_command(String param);
void handle_get_command(String param);
void handle_pinread_command(String param);
void handle_pinset_command(String param);
void handle_adcread_command(String param);

// Arduino风格的GPIO命令处理
void handle_pinread_command(String param);
void handle_pinset_command(String param);
void handle_adcread_command(String param);

#endif // COMMAND_HANDLER_H