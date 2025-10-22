#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ESP32设备管理器
自动检测ESP32设备，检查固件状态，并在需要时自动烧录固件

作者: 王海涛
版本: 1.0.0
"""

import os
import sys
import time
import subprocess
import logging
from typing import Optional, Dict, Any, Tuple
from pathlib import Path

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ESP32DeviceManager:
    """ESP32设备管理器"""

    def __init__(self, port: str = "/dev/ttyUSB0", baudrate: int = 115200):
        self.port = port
        self.baudrate = baudrate

        # 固件文件查找路径优先级
        self.package_firmware = Path(__file__).parent / "firmware" / "firmware.bin"
        self.local_firmware = Path(__file__).parent.parent / "esp32-rk3588-sensor-system" / "esp32_firmware" / ".pio" / "build" / "esp32dev" / "firmware.bin"
        self.default_firmware = self.package_firmware  # 优先使用包内固件

    def detect_device(self) -> bool:
        """
        检测ESP32设备是否存在

        Returns:
            bool: 设备是否存在
        """
        try:
            # 检查串口设备是否存在
            if not os.path.exists(self.port):
                logger.warning(f"串口设备不存在: {self.port}")
                return False

            # 使用esptool检测ESP32 - 优先使用系统esptool，然后是python模块
            cmd = [sys.executable, "-m", "esptool", "--port", self.port, "chip_id"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                logger.info(f"ESP32设备检测成功: {self.port}")
                return True
            else:
                logger.warning(f"ESP32设备检测失败: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("ESP32设备检测超时")
            return False
        except Exception as e:
            logger.error(f"ESP32设备检测异常: {e}")
            return False

    def check_firmware(self) -> Tuple[bool, str]:
        """
        检查ESP32是否已烧录正确的固件

        Returns:
            Tuple[bool, str]: (是否有固件, 固件版本信息)
        """
        try:
            # 尝试导入ESP32通信模块进行测试 - 修复路径
            comm_path = Path(__file__).parent.parent / "esp32-rk3588-sensor-system" / "rk3588_controller"
            sys.path.insert(0, str(comm_path))

            # 检查通信模块是否存在
            comm_file = comm_path / "esp32_comm.py"
            if not comm_file.exists():
                logger.warning(f"通信模块不存在: {comm_file}")
                return False, "通信模块缺失"

            from esp32_comm import ESP32Communicator
            logger.info(f"成功导入通信模块: {comm_file}")

            # 简化连接测试，只验证基本通信
            try:
                comm = ESP32Communicator(self.port, self.baudrate, timeout=1.0)
                if comm.connect():
                    # 测试基本命令PING
                    response = comm.send_command("PING")
                    comm.disconnect()

                    if response == "OK:PONG":
                        logger.info("ESP32基本通信正常")
                        return True, "通信正常"
                    else:
                        logger.warning(f"PING测试失败: {response}")
                        return False, "通信异常"
                else:
                    logger.warning("无法连接到ESP32")
                    return False, "连接失败"

            except Exception as e:
                logger.warning(f"通信测试异常: {e}")
                return False, f"通信异常: {e}"

        except ImportError:
            logger.warning("无法导入ESP32通信模块")
            return False, "模块缺失"
        except Exception as e:
            logger.warning(f"固件检查异常: {e}")
            return False, f"检查异常: {e}"

    def find_firmware_file(self) -> Optional[Path]:
        """
        查找可用的固件文件

        Returns:
            Optional[Path]: 固件文件路径，如果找不到返回None
        """
        # 优先级1: 使用包内预编译固件
        if self.package_firmware.exists():
            logger.info(f"找到包内预编译固件: {self.package_firmware}")
            return self.package_firmware

        # 优先级2: 使用本地开发目录中的固件
        if self.local_firmware.exists():
            logger.info(f"找到本地编译固件: {self.local_firmware}")
            return self.local_firmware

        # 优先级3: 查找固件目录下的所有.bin文件
        firmware_dir = Path(__file__).parent.parent / "esp32-rk3588-sensor-system" / "esp32_firmware"
        if firmware_dir.exists():
            firmware_files = list(firmware_dir.rglob("*.bin"))

            # 优先查找包含"firmware"的文件
            for fw_file in firmware_files:
                if "firmware" in fw_file.name.lower():
                    logger.info(f"找到固件文件: {fw_file}")
                    return fw_file

            # 如果没有找到，返回第一个.bin文件
            if firmware_files:
                logger.info(f"使用第一个找到的固件文件: {firmware_files[0]}")
                return firmware_files[0]

        logger.warning("未找到任何固件文件，将无法自动烧录")
        return None

    def compile_firmware(self) -> bool:
        """
        编译固件

        Returns:
            bool: 编译是否成功
        """
        if not self.firmware_dir.exists():
            logger.warning(f"固件源码目录不存在: {self.firmware_dir}")
            logger.info("在Docker环境中，固件编译不可用，使用模拟模式")
            return False

        try:
            logger.info("开始编译ESP32固件...")

            # 进入固件目录
            original_cwd = os.getcwd()
            os.chdir(self.firmware_dir)

            # 检查pio是否可用
            pio_available = True
            try:
                subprocess.run(["pio", "--version"], capture_output=True, check=True, timeout=10)
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                print("⚠️  PlatformIO不可用，跳过编译")
                pio_available = False

            if pio_available:
                # 使用pio编译
                cmd = ["pio", "run"]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

                os.chdir(original_cwd)

                if result.returncode == 0:
                    logger.info("固件编译成功")
                    return True
                else:
                    logger.error(f"固件编译失败: {result.stderr}")
                    return False
            else:
                os.chdir(original_cwd)
                logger.info("在Docker环境中，固件编译不可用，使用预编译固件")
                return False

        except subprocess.TimeoutExpired:
            logger.error("固件编译超时")
            return False
        except Exception as e:
            logger.error(f"固件编译异常: {e}")
            return False

    def flash_firmware(self, firmware_path: Optional[Path] = None) -> bool:
        """
        烧录固件到ESP32

        Args:
            firmware_path: 固件文件路径，如果为None则自动查找

        Returns:
            bool: 烧录是否成功
        """
        if firmware_path is None:
            firmware_path = self.find_firmware_file()

        if firmware_path is None:
            logger.error("找不到固件文件，尝试编译...")
            if not self.compile_firmware():
                logger.error("编译固件失败")
                return False
            firmware_path = self.find_firmware_file()

        if not firmware_path or not firmware_path.exists():
            logger.error(f"固件文件不存在: {firmware_path}")
            return False

        try:
            logger.info(f"开始烧录固件: {firmware_path}")

            # 擦除Flash
            logger.info("擦除ESP32 Flash...")
            erase_cmd = [sys.executable, "-m", "esptool", "--port", self.port, "erase-flash"]
            result = subprocess.run(erase_cmd, capture_output=True, text=True, timeout=60)

            if result.returncode != 0:
                logger.error(f"擦除Flash失败: {result.stderr}")
                return False

            # 烧录固件
            logger.info("烧录固件到ESP32...")
            flash_cmd = [
                sys.executable, "-m", "esptool",
                "--port", self.port,
                "--baud", "460800",
                "write-flash",
                "0x1000",
                str(firmware_path)
            ]
            result = subprocess.run(flash_cmd, capture_output=True, text=True, timeout=120)

            if result.returncode == 0:
                logger.info("固件烧录成功")
                return True
            else:
                logger.error(f"固件烧录失败: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("固件烧录超时")
            return False
        except Exception as e:
            logger.error(f"固件烧录异常: {e}")
            return False

    def wait_for_device_ready(self, timeout: int = 60) -> bool:
        """
        等待设备重启并准备就绪

        Args:
            timeout: 超时时间（秒）

        Returns:
            bool: 设备是否准备就绪
        """
        logger.info("等待ESP32设备重启...")
        start_time = time.time()

        # 等待设备重启，先给设备足够的时间重启
        logger.info("等待设备重启（3秒）...")
        time.sleep(3)

        while time.time() - start_time < timeout:
            # 先检查设备是否可以被检测到
            if self.detect_device():
                logger.info("设备检测成功，检查固件...")

                # 再检查固件是否正常工作
                has_firmware, firmware_info = self.check_firmware()
                if has_firmware:
                    logger.info("ESP32设备已准备就绪")
                    return True
                else:
                    logger.debug(f"固件尚未就绪: {firmware_info}")

            # 等待更长时间再重试
            time.sleep(3)

        logger.error("等待设备准备就绪超时")
        return False

    def auto_setup(self) -> Tuple[bool, str]:
        """
        自动设置ESP32设备
        1. 检测设备
        2. 检查固件
        3. 如果需要，烧录固件
        4. 验证设备状态

        Returns:
            Tuple[bool, str]: (是否成功, 状态信息)
        """
        logger.info("开始ESP32设备自动设置...")

        # 1. 检测设备
        if not self.detect_device():
            return False, "未检测到ESP32设备"

        # 2. 检查固件
        has_firmware, firmware_info = self.check_firmware()

        if has_firmware:
            logger.info(f"ESP32已有固件: {firmware_info}")
            return True, f"设备已就绪: {firmware_info}"

        # 3. 烧录固件
        logger.info("ESP32没有固件或固件不兼容，开始烧录...")

        if not self.flash_firmware():
            return False, "固件烧录失败"

        # 4. 等待设备重启并验证
        if not self.wait_for_device_ready():
            return False, "设备启动后验证失败"

        has_firmware, firmware_info = self.check_firmware()
        if has_firmware:
            logger.info(f"ESP32设备自动设置完成: {firmware_info}")
            return True, f"自动设置完成: {firmware_info}"
        else:
            return False, "设备验证失败"

# 便捷函数
def auto_setup_esp32(port: str = "/dev/ttyUSB0", baudrate: int = 115200) -> Tuple[bool, str]:
    """
    自动设置ESP32设备的便捷函数

    Args:
        port: 串口端口
        baudrate: 波特率

    Returns:
        Tuple[bool, str]: (是否成功, 状态信息)
    """
    manager = ESP32DeviceManager(port, baudrate)
    return manager.auto_setup()

# 主函数用于测试
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="ESP32设备管理器")
    parser.add_argument("--port", default="/dev/ttyUSB0", help="串口端口")
    parser.add_argument("--baudrate", type=int, default=115200, help="波特率")
    parser.add_argument("--detect", action="store_true", help="仅检测设备")
    parser.add_argument("--check-firmware", action="store_true", help="仅检查固件")
    parser.add_argument("--compile", action="store_true", help="编译固件")
    parser.add_argument("--flash", action="store_true", help="烧录固件")
    parser.add_argument("--auto-setup", action="store_true", help="自动设置")

    args = parser.parse_args()

    manager = ESP32DeviceManager(args.port, args.baudrate)

    if args.detect:
        success = manager.detect_device()
        print(f"设备检测: {'成功' if success else '失败'}")

    elif args.check_firmware:
        has_firmware, info = manager.check_firmware()
        print(f"固件状态: {'有' if has_firmware else '无'} - {info}")

    elif args.compile:
        success = manager.compile_firmware()
        print(f"固件编译: {'成功' if success else '失败'}")

    elif args.flash:
        success = manager.flash_firmware()
        print(f"固件烧录: {'成功' if success else '失败'}")

    elif args.auto_setup:
        success, info = manager.auto_setup()
        print(f"自动设置: {'成功' if success else '失败'} - {info}")

    else:
        # 默认执行自动设置
        success, info = manager.auto_setup()
        print(f"自动设置: {'成功' if success else '失败'} - {info}")