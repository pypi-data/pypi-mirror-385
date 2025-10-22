#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ESP32通信模块 - 内置实现
提供与ESP32设备的串口通信功能
"""

import serial
import time
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

class ESP32Communicator:
    """ESP32通信器"""

    def __init__(self, port: str = "/dev/ttyUSB0", baudrate: int = 115200, timeout: float = 3.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None
        self.connected = False

    def connect(self) -> bool:
        """
        连接到ESP32设备

        Returns:
            bool: 连接是否成功
        """
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )

            # 等待设备稳定
            time.sleep(1)

            # 清空输入缓冲区
            self.ser.flushInput()
            time.sleep(0.5)

            self.connected = True
            logger.info(f"ESP32连接成功: {self.port}")
            return True

        except Exception as e:
            logger.error(f"ESP32连接失败: {e}")
            self.connected = False
            return False

    def disconnect(self) -> None:
        """断开ESP32连接"""
        if self.ser and self.ser.is_open:
            try:
                self.ser.close()
                logger.info("ESP32连接已断开")
            except Exception as e:
                logger.warning(f"断开连接时异常: {e}")

        self.connected = False
        self.ser = None

    def send_command(self, command: str, param: str = "") -> Optional[str]:
        """
        发送命令到ESP32

        Args:
            command: 命令类型
            param: 命令参数

        Returns:
            Optional[str]: ESP32响应，失败返回None
        """
        if not self.connected or not self.ser:
            logger.error("ESP32未连接")
            return None

        try:
            # 构建完整命令 - 支持带冒号的命令格式
            if param:
                # 如果param包含冒号，说明是完整命令（如READ:TEMP）
                if ':' in param:
                    full_command = param
                else:
                    full_command = f"{command}:{param}"
            else:
                full_command = command

            # 清空输入缓冲区
            self.ser.flushInput()

            # 发送命令
            self.ser.write((full_command + "\n").encode())
            logger.debug(f"发送命令: {full_command}")

            # 等待响应
            time.sleep(0.5)

            # 读取响应
            response = ""
            start_time = time.time()

            while time.time() - start_time < self.timeout:
                if self.ser.in_waiting > 0:
                    data = self.ser.read(self.ser.in_waiting).decode('ascii', errors='ignore')
                    response += data

                    # 检查是否收到完整响应
                    if response.strip().endswith('\n') or '\n' in response:
                        break

                time.sleep(0.1)

            response = response.strip()
            logger.debug(f"收到响应: {repr(response)}")

            return response if response else None

        except Exception as e:
            logger.error(f"发送命令异常: {e}")
            return None

    def ping(self) -> bool:
        """
        测试ESP32连接

        Returns:
            bool: PING是否成功
        """
        response = self.send_command("PING")
        return response and ("PONG" in response or "OK" in response)

    def get_system_info(self) -> dict:
        """
        获取ESP32系统信息

        Returns:
            dict: 系统信息
        """
        info = {}

        try:
            # 获取芯片信息
            response = self.send_command("INFO")
            if response:
                info['chip_info'] = response

            # 获取固件版本
            response = self.send_command("VERSION")
            if response:
                info['firmware'] = response

            # 获取状态
            response = self.send_command("STATUS")
            if response:
                info['status'] = response

        except Exception as e:
            logger.error(f"获取系统信息异常: {e}")
            info['error'] = str(e)

        return info

    def read_sensor_data(self, sensor_type: str = "DHT11") -> Tuple[Optional[float], Optional[float]]:
        """
        读取传感器数据

        Args:
            sensor_type: 传感器类型

        Returns:
            Tuple[Optional[float], Optional[float]]: (温度, 湿度)
        """
        try:
            # 优先使用一次性读取所有数据
            all_response = self.send_command("", "READ:ALL")
            if all_response and all_response.startswith("OK:"):
                data_str = all_response[3:].strip()  # 去掉"OK:"
                # 解析格式: temp=25.50,humid=60.20,led=OFF,button=UP,sensor_mode=DHT11,dht11_status=
                temp = None
                hum = None

                for item in data_str.split(','):
                    if '=' in item:
                        key, value = item.split('=', 1)
                        key = key.strip()
                        value = value.strip()

                        if key == 'temp':
                            try:
                                temp = float(value)
                            except:
                                pass
                        elif key == 'humid':
                            try:
                                hum = float(value)
                            except:
                                pass

                if temp is not None and hum is not None:
                    logger.debug(f"通过ALL命令解析传感器数据: 温度={temp}, 湿度={hum}")
                    return temp, hum

            # 如果ALL命令失败，尝试分别读取
            # 读取温度数据
            temp_response = self.send_command("", "READ:TEMP")
            temp = None
            if temp_response and temp_response.startswith("OK:"):
                try:
                    temp = float(temp_response.split(':')[1].strip())
                except:
                    pass

            # 读取湿度数据
            humid_response = self.send_command("", "READ:HUMID")
            hum = None
            if humid_response and humid_response.startswith("OK:"):
                try:
                    hum = float(humid_response.split(':')[1].strip())
                except:
                    pass

            logger.debug(f"解析传感器数据: 温度={temp}, 湿度={hum}")
            return temp, hum

        except Exception as e:
            logger.error(f"读取传感器数据异常: {e}")
            return None, None

    def set_led(self, state: bool) -> bool:
        """
        控制LED状态

        Args:
            state: LED状态 (True=开, False=关)

        Returns:
            bool: 设置是否成功
        """
        cmd = "LED:ON" if state else "LED:OFF"
        response = self.send_command("SET", cmd)
        return response and ("OK:" in response or "SUCCESS" in response)

    def set_gpio(self, pin: int, value: int) -> bool:
        """
        设置GPIO输出

        Args:
            pin: GPIO引脚号
            value: 输出值 (0或1)

        Returns:
            bool: 设置是否成功
        """
        cmd = f"PINSET:{pin}:{value}"
        response = self.send_command("", cmd)
        return response and ("OK:" in response or "SUCCESS" in response)

    def get_gpio(self, pin: int) -> int:
        """
        读取GPIO输入

        Args:
            pin: GPIO引脚号

        Returns:
            int: GPIO值 (0或1)
        """
        cmd = f"PINREAD:{pin}"
        response = self.send_command("", cmd)

        if response and ("OK:" in response or "VALUE:" in response):
            try:
                # 提取数值
                for token in response.split():
                    try:
                        val = int(token)
                        return val
                    except:
                        continue
            except:
                pass

        return 0

    def get_adc(self, pin: int) -> int:
        """
        读取ADC输入

        Args:
            pin: ADC引脚号

        Returns:
            int: ADC值
        """
        cmd = f"ADCREAD:{pin}"
        response = self.send_command("", cmd)

        if response and ("OK:" in response or "VALUE:" in response):
            try:
                # 提取数值
                for token in response.split():
                    try:
                        val = int(token)
                        return val
                    except:
                        continue
            except:
                pass

        return 0

# 全局实例
_global_communicator = None

def get_communicator(port: str = "/dev/ttyUSB0", baudrate: int = 115200) -> ESP32Communicator:
    """获取全局通信器实例"""
    global _global_communicator
    if _global_communicator is None:
        _global_communicator = ESP32Communicator(port, baudrate)
    return _global_communicator

def cleanup():
    """清理全局实例"""
    global _global_communicator
    if _global_communicator:
        _global_communicator.disconnect()
        _global_communicator = None

# 模块清理时自动断开连接
import atexit
atexit.register(cleanup)