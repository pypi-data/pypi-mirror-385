"""
ESP32 固件烧录工具
基于 esptool
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import Optional
from .device_detector import find_esp32_device

logger = logging.getLogger(__name__)


class FlashError(Exception):
    """固件烧录错误"""
    pass


def get_firmware_path(firmware_name: str = "esp32_standard.bin") -> Optional[Path]:
    """
    获取固件文件路径

    Args:
        firmware_name: 固件文件名

    Returns:
        固件路径，未找到返回 None
    """
    # 尝试多个可能的路径
    possible_paths = [
        # 安装包内的固件
        Path(__file__).parent.parent / "firmware" / "compiled" / firmware_name,
        # 开发环境的固件
        Path(__file__).parent.parent.parent / "firmware" / "compiled" / firmware_name,
        # 当前目录
        Path(firmware_name),
    ]

    for path in possible_paths:
        if path.exists():
            logger.info(f"找到固件: {path}")
            return path

    logger.warning(f"未找到固件: {firmware_name}")
    return None


def flash_firmware(
    port: str = None,
    firmware_path: str = None,
    baudrate: int = 460800,
    flash_mode: str = "dio",
    flash_freq: str = "40m",
    flash_size: str = "4MB",
    chip: str = "esp32",
) -> bool:
    """
    烧录固件到 ESP32

    Args:
        port: 串口号，None 则自动检测
        firmware_path: 固件文件路径，None 则使用默认固件
        baudrate: 烧录波特率
        flash_mode: Flash 模式 (dio, dout, qio, qout)
        flash_freq: Flash 频率 (40m, 26m, 20m, 80m)
        flash_size: Flash 大小 (2MB, 4MB, 8MB, 16MB)
        chip: 芯片类型 (esp32, esp32s2, esp32s3, esp32c3)

    Returns:
        是否成功烧录

    Raises:
        FlashError: 烧录失败
    """
    # 自动检测端口
    if port is None:
        logger.info("自动检测 ESP32 设备...")
        port = find_esp32_device()

        if port is None:
            raise FlashError("未找到 ESP32 设备")

    # 获取固件路径
    if firmware_path is None:
        firmware_path = get_firmware_path()

        if firmware_path is None:
            raise FlashError("未找到固件文件")
    else:
        firmware_path = Path(firmware_path)

        if not firmware_path.exists():
            raise FlashError(f"固件文件不存在: {firmware_path}")

    logger.info(f"开始烧录固件到 {port}")
    logger.info(f"固件: {firmware_path}")
    logger.info(f"波特率: {baudrate}")

    try:
        # 构建 esptool 命令
        cmd = [
            sys.executable, "-m", "esptool",
            "--chip", chip,
            "--port", port,
            "--baud", str(baudrate),
            "write_flash",
            "-z",
            "--flash_mode", flash_mode,
            "--flash_freq", flash_freq,
            "--flash_size", flash_size,
            "0x1000", str(firmware_path),
        ]

        logger.debug(f"执行命令: {' '.join(cmd)}")

        # 执行烧录
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=120,
        )

        output = result.stdout

        # 打印输出
        print(output)

        if result.returncode == 0:
            logger.info("固件烧录成功!")
            return True
        else:
            logger.error(f"固件烧录失败，返回码: {result.returncode}")
            raise FlashError(f"烧录失败: {output}")

    except subprocess.TimeoutExpired:
        raise FlashError("烧录超时")

    except FileNotFoundError:
        raise FlashError(
            "未找到 esptool，请安装: pip install esptool"
        )

    except Exception as e:
        raise FlashError(f"烧录出错: {e}")


def erase_flash(port: str = None, chip: str = "esp32") -> bool:
    """
    擦除 Flash

    Args:
        port: 串口号
        chip: 芯片类型

    Returns:
        是否成功

    Raises:
        FlashError: 擦除失败
    """
    if port is None:
        port = find_esp32_device()

        if port is None:
            raise FlashError("未找到 ESP32 设备")

    logger.info(f"擦除 Flash: {port}")

    try:
        cmd = [
            sys.executable, "-m", "esptool",
            "--chip", chip,
            "--port", port,
            "erase_flash",
        ]

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=60,
        )

        print(result.stdout)

        if result.returncode == 0:
            logger.info("Flash 擦除成功")
            return True
        else:
            raise FlashError(f"擦除失败: {result.stdout}")

    except Exception as e:
        raise FlashError(f"擦除出错: {e}")


def read_chip_info(port: str = None) -> dict:
    """
    读取芯片信息

    Args:
        port: 串口号

    Returns:
        芯片信息字典

    Raises:
        FlashError: 读取失败
    """
    if port is None:
        port = find_esp32_device()

        if port is None:
            raise FlashError("未找到 ESP32 设备")

    try:
        cmd = [
            sys.executable, "-m", "esptool",
            "--port", port,
            "chip_id",
        ]

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            return {"output": result.stdout, "success": True}
        else:
            return {"output": result.stdout, "success": False}

    except Exception as e:
        raise FlashError(f"读取芯片信息失败: {e}")


# 命令行工具
def main():
    """命令行主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="ESP32 固件烧录工具")
    parser.add_argument("--port", "-p", help="串口号（自动检测）")
    parser.add_argument("--firmware", "-f", help="固件文件路径")
    parser.add_argument("--baudrate", "-b", type=int, default=460800, help="波特率")
    parser.add_argument("--chip", "-c", default="esp32", help="芯片类型")
    parser.add_argument("--erase", action="store_true", help="擦除 Flash")
    parser.add_argument("--info", action="store_true", help="读取芯片信息")

    args = parser.parse_args()

    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )

    try:
        if args.info:
            # 读取芯片信息
            info = read_chip_info(args.port)
            print(info['output'])

        elif args.erase:
            # 擦除 Flash
            erase_flash(args.port, args.chip)

        else:
            # 烧录固件
            flash_firmware(
                port=args.port,
                firmware_path=args.firmware,
                baudrate=args.baudrate,
                chip=args.chip,
            )

    except FlashError as e:
        logger.error(f"错误: {e}")
        sys.exit(1)

    except KeyboardInterrupt:
        logger.info("\n已取消")
        sys.exit(0)


if __name__ == "__main__":
    main()
