"""
aitoolkit_esp32 - Arduino风格的ESP32-C3 SuperMini控制库
========================================================

通过串口控制ESP32-C3 SuperMini开发板，提供完整的Arduino风格API。

支持的硬件: ESP32-C3 SuperMini开发板

ESP32-C3 SuperMini 实际引脚布局：
- 内置LED: GPIO9
- ADC引脚: GPIO0, GPIO1, GPIO2, GPIO3, GPIO4 (12位ADC，范围0-4095)
- I2C: GPIO8(SCL), GPIO9(SDA)
- SPI (硬件专用): GPIO18(SCK), GPIO19(MISO), GPIO23(MOSI), GPIO5(CS)
- UART: GPIO20(TX), GPIO21(RX)
- 3.3V电源组: GPIO32, GPIO33
- 5V电源组: GPIO25, GPIO26, GPIO27
- SPI专用组: GPIO18, GPIO19, GPIO23 (首选SPI通信)
- 其他5V组: GPIO13, GPIO14, GPIO16, GPIO17, GPIO21, GPIO22
- 启动模式: GPIO0 (下载模式时需拉低)
- PWM: 所有GPIO都支持PWM输出
- 中断: 所有GPIO都支持外部中断

可用GPIO总数: GPIO0-12, GPIO13-14, GPIO16-23, GPIO25-27, GPIO32-33

基本使用:
    from aitoolkit_esp32 import Arduino

    # 连接ESP32-C3 SuperMini
    board = Arduino(port="/dev/ttyUSB0", baudrate=115200)

    # 使用内置LED (GPIO9)
    board.pinMode(board.LED_BUILTIN, board.OUTPUT)
    board.digitalWrite(board.LED_BUILTIN, board.HIGH)
    board.delay(1000)
    board.digitalWrite(board.LED_BUILTIN, board.LOW)

自动检测设备:
    board = Arduino.auto()  # 自动查找ESP32设备

上下文管理器:
    with Arduino(port="/dev/ttyUSB0") as board:
        board.digitalWrite(13, board.HIGH)

FastAPI集成:
    from aitoolkit_esp32 import add_esp32_routes
    from fastapi import FastAPI

    app = FastAPI()
    add_esp32_routes(app, port="/dev/ttyUSB0")
"""

# 导入核心类
from .arduino import Arduino

# 导入常量
from .constants import (
    HIGH, LOW,
    INPUT, OUTPUT, INPUT_PULLUP, INPUT_PULLDOWN,
    RISING, FALLING, CHANGE,
    LED_BUILTIN, ADC_PINS, PWM_PINS,
    I2C_SDA, I2C_SCL, SPI_MOSI, SPI_MISO, SPI_SCK, SPI_CS,
    UART_TX, UART_RX, BOOT_PIN, TOUCH_PINS,
    INPUT_PINS, OUTPUT_PINS, INTERRUPT_PINS,
    PINS_3V3, PINS_5V, PINS_SPI, PINS_OTHER, ALL_PINS,
)

# 导入配置管理
from .config import get_config, set_config, load_config, save_config

# 导入设备检测
from .device_detector import list_esp32_devices, find_esp32_device

# 导入固件烧录工具
from .firmware_flasher import flash_firmware, FlashError

# 导入固件管理工具
from .firmware_manager import FirmwareManager, ensure_firmware_before_connect

# 尝试导入FastAPI集成（可选）
try:
    from .fastapi_adapter import add_esp32_routes, esp32_manager
    _fastapi_available = True
except ImportError:
    _fastapi_available = False

__version__ = "1.0.0"
__author__ = "Haitao Wang"

# 导出列表
__all__ = [
    # 核心类
    'Arduino',

    # 常量
    'HIGH', 'LOW',
    'INPUT', 'OUTPUT', 'INPUT_PULLUP', 'INPUT_PULLDOWN',
    'RISING', 'FALLING', 'CHANGE',
    'LED_BUILTIN', 'ADC_PINS', 'PWM_PINS',
    'I2C_SDA', 'I2C_SCL', 'SPI_MOSI', 'SPI_MISO', 'SPI_SCK', 'SPI_CS',
    'UART_TX', 'UART_RX', 'BOOT_PIN', 'TOUCH_PINS',
    'INPUT_PINS', 'OUTPUT_PINS', 'INTERRUPT_PINS',
    'PINS_3V3', 'PINS_5V', 'PINS_SPI', 'PINS_OTHER', 'ALL_PINS',

    # 配置管理
    'get_config', 'set_config', 'load_config', 'save_config',

    # 设备检测
    'list_esp32_devices', 'find_esp32_device',

    # 固件烧录
    'flash_firmware', 'FlashError',

    # 固件管理
    'FirmwareManager', 'ensure_firmware_before_connect',
]

if _fastapi_available:
    __all__.extend(['add_esp32_routes', 'esp32_manager'])

# 设置日志级别
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
