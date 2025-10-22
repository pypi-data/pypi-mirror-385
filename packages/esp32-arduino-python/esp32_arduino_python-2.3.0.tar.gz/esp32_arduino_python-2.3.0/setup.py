#!/usr/bin/env python3
"""
ESP32 Arduino风格控制库安装脚本
"""

from setuptools import setup, find_packages
import os

# 读取README文件
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# 读取requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="esp32-arduino-python",
    version="2.2.2",
    author="Haitao Wang",
    author_email="dianx12@163.com",
    description="ESP32 Arduino风格Python控制库 v2.2 - 支持自动检测和固件烧录",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/dianx12/esp32-arduino-python",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Embedded Systems",
        "Topic :: System :: Hardware",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "twine>=4.0",
            "build>=0.8.0",
        ],
        "firmware": [
            "esptool>=4.0",
            "platformio>=6.0",
        ],
        "jupyter": [
            "jupyter>=1.0.0",
            "ipython>=7.0.0",
            "matplotlib>=3.3.0",
        ],
        "dht11": [
            "adafruit-circuitpython-dht>=3.7.8",
        ],
    },
    entry_points={
        "console_scripts": [
            "esp32-test=esp32_arduino.examples.test:main",
            "esp32-dht11-test=esp32_arduino.examples.dht11_test:main",
        ],
    },
    include_package_data=True,
    package_data={
        "esp32_arduino": [
            "examples/*.py",
            "examples/*.md",
            "firmware/*"
        ],
    },
    keywords="esp32 arduino python dht11 sensor temperature humidity iot embedded hardware",
    project_urls={
        "Bug Reports": "https://github.com/dianx12/esp32-arduino-python/issues",
        "Source": "https://github.com/dianx12/esp32-arduino-python",
        "Documentation": "https://github.com/dianx12/esp32-arduino-python/blob/main/README.md",
        "Changelog": "https://github.com/dianx12/esp32-arduino-python/blob/main/CHANGELOG.md",
    },
)