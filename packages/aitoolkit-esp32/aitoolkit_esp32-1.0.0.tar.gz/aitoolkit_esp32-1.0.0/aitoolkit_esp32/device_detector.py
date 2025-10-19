"""
ESP32 设备检测模块
"""

import serial.tools.list_ports
import logging
from typing import List, Dict, Optional
from .config import get_config

logger = logging.getLogger(__name__)


# ESP32 常见 USB 转串口芯片的 VID:PID
ESP32_USB_IDS = [
    (0x10C4, 0xEA60),  # Silicon Labs CP210x
    (0x1A86, 0x7523),  # QinHeng CH340
    (0x0403, 0x6001),  # FTDI FT232
    (0x0403, 0x6015),  # FTDI FT230X
    (0x067B, 0x2303),  # Prolific PL2303
]

# ESP32 设备描述关键字
ESP32_KEYWORDS = [
    'CP210',
    'CP2102',
    'CH340',
    'CH341',
    'FT232',
    'FTDI',
    'USB-SERIAL',
    'USB SERIAL',
    'UART',
]


def list_serial_ports() -> List[Dict[str, any]]:
    """
    列出所有可用串口

    Returns:
        串口信息列表
    """
    ports = []

    for port in serial.tools.list_ports.comports():
        port_info = {
            'port': port.device,
            'description': port.description,
            'hwid': port.hwid,
            'vid': port.vid,
            'pid': port.pid,
            'serial_number': port.serial_number,
            'manufacturer': port.manufacturer,
            'product': port.product,
        }
        ports.append(port_info)

    return ports


def is_esp32_device(port_info: Dict[str, any]) -> bool:
    """
    判断是否为 ESP32 设备

    Args:
        port_info: 串口信息字典

    Returns:
        是否为 ESP32 设备
    """
    # 检查 VID:PID
    if port_info['vid'] and port_info['pid']:
        if (port_info['vid'], port_info['pid']) in ESP32_USB_IDS:
            return True

    # 检查描述关键字
    description = (port_info['description'] or '').upper()
    for keyword in ESP32_KEYWORDS:
        if keyword in description:
            return True

    # 检查硬件 ID
    hwid = (port_info['hwid'] or '').upper()
    for keyword in ESP32_KEYWORDS:
        if keyword in hwid:
            return True

    return False


def list_esp32_devices() -> List[Dict[str, any]]:
    """
    列出所有 ESP32 设备

    Returns:
        ESP32 设备列表
    """
    all_ports = list_serial_ports()
    esp32_ports = [port for port in all_ports if is_esp32_device(port)]

    logger.info(f"找到 {len(esp32_ports)} 个 ESP32 设备")

    return esp32_ports


def find_esp32_device(preferred_ports: List[str] = None) -> Optional[str]:
    """
    自动查找 ESP32 设备

    Args:
        preferred_ports: 优先尝试的端口列表

    Returns:
        ESP32 串口号，未找到返回 None
    """
    # 获取优先端口列表
    if preferred_ports is None:
        preferred_ports = get_config("device.preferred_ports") or []

    # 先尝试优先端口
    for port in preferred_ports:
        all_ports = list_serial_ports()
        for port_info in all_ports:
            if port_info['port'] == port:
                logger.info(f"使用优先端口: {port}")
                return port

    # 自动检测 ESP32 设备
    esp32_devices = list_esp32_devices()

    if not esp32_devices:
        logger.warning("未找到 ESP32 设备")
        return None

    # 返回第一个找到的设备
    selected_port = esp32_devices[0]['port']
    logger.info(f"自动选择设备: {selected_port}")

    return selected_port


def get_device_info(port: str) -> Optional[Dict[str, any]]:
    """
    获取设备信息

    Args:
        port: 串口号

    Returns:
        设备信息字典，未找到返回 None
    """
    all_ports = list_serial_ports()

    for port_info in all_ports:
        if port_info['port'] == port:
            return port_info

    return None


def validate_port(port: str) -> bool:
    """
    验证端口是否存在

    Args:
        port: 串口号

    Returns:
        是否存在
    """
    return get_device_info(port) is not None


def print_available_devices():
    """打印所有可用设备（用于调试）"""
    print("\n=== 可用串口设备 ===\n")

    all_ports = list_serial_ports()

    if not all_ports:
        print("未找到串口设备")
        return

    for i, port_info in enumerate(all_ports, 1):
        is_esp32 = is_esp32_device(port_info)
        marker = "[ESP32?]" if is_esp32 else ""

        print(f"{i}. {port_info['port']} {marker}")
        print(f"   描述: {port_info['description']}")
        print(f"   硬件ID: {port_info['hwid']}")

        if port_info['vid'] and port_info['pid']:
            print(f"   VID:PID: {port_info['vid']:04X}:{port_info['pid']:04X}")

        if port_info['manufacturer']:
            print(f"   制造商: {port_info['manufacturer']}")

        if port_info['serial_number']:
            print(f"   序列号: {port_info['serial_number']}")

        print()

    esp32_count = sum(1 for p in all_ports if is_esp32_device(p))
    print(f"共找到 {len(all_ports)} 个串口设备，其中 {esp32_count} 个可能是 ESP32\n")


# 命令行工具
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "list":
        print_available_devices()
    else:
        # 查找 ESP32
        port = find_esp32_device()
        if port:
            print(f"找到 ESP32: {port}")
            info = get_device_info(port)
            if info:
                print(f"描述: {info['description']}")
        else:
            print("未找到 ESP32 设备")
            print("\n运行 'python -m aitoolkit_esp32.device_detector list' 查看所有设备")
