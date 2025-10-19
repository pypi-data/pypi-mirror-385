#!/usr/bin/env python3
"""
aitoolkit_esp32 安装脚本
"""

from setuptools import setup, find_packages
import os

# 读取版本号
version = "1.0.0"

# 读取README
readme_path = os.path.join(os.path.dirname(__file__), "README.md")
try:
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "aitoolkit_esp32 - Arduino风格的ESP32控制库"

setup(
    name="aitoolkit-esp32",
    version=version,
    author="Haitao Wang",
    author_email="dianx12@163.com",
    description="Arduino风格的ESP32控制库 - 通过串口控制ESP32，提供完整的Arduino API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dianx12/aitoolkit-esp32",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Embedded Systems",
        "Topic :: System :: Hardware",
        "Topic :: Education",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pyserial>=3.5",
        "esptool>=4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
        "web": [
            "fastapi>=0.68.0",
            "uvicorn>=0.15.0",
            "websockets>=10.0",
            "pydantic>=2.0",
        ],
        "jupyter": [
            "jupyter>=1.0.0",
            "ipython>=7.0.0",
        ],
    },
    include_package_data=True,
    package_data={
        "aitoolkit_esp32": [
            "firmware/compiled/*.bin",
            "firmware/esp32_arduino/*.ino",
            "firmware/esp32_arduino/*.h",
        ],
    },
    zip_safe=False,
    keywords="esp32 arduino serial embedded iot gpio hardware",
    project_urls={
        "Bug Reports": "https://github.com/dianx12/aitoolkit-esp32/issues",
        "Source": "https://github.com/dianx12/aitoolkit-esp32",
        "Documentation": "https://github.com/dianx12/aitoolkit-esp32/blob/main/README.md",
    },
)
