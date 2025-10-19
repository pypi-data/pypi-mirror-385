"""
ESP32 固件管理器
提供固件检查、自动安装和版本管理功能
"""

import os
import sys
import logging
import time
from pathlib import Path
from typing import Optional, Tuple, Dict
from .device_detector import find_esp32_device
from .firmware_flasher import flash_firmware, FlashError, read_chip_info
from .serial_comm import SerialConnection, SerialCommunicationError
from .protocol import ProtocolEncoder, ProtocolDecoder, ProtocolError

logger = logging.getLogger(__name__)


class FirmwareManagerError(Exception):
    """固件管理器错误"""
    pass


class FirmwareManager:
    """
    ESP32 固件管理器

    功能:
    - 检查设备固件状态
    - 自动安装固件
    - 固件版本管理
    """

    # 支持的固件版本和对应的功能
    SUPPORTED_FIRMWARE_VERSIONS = {
        "1.0.0": {
            "name": "Standard Firmware v1.0.0",
            "features": ["basic_gpio", "analog_read", "pwm", "serial"],
            "filename": "esp32_standard_v1.0.0.bin"
        },
        "1.1.0": {
            "name": "Enhanced Firmware v1.1.0",
            "features": ["basic_gpio", "analog_read", "pwm", "serial", "interrupts"],
            "filename": "esp32_enhanced_v1.1.0.bin"
        },
        "1.2.0": {
            "name": "Sensor Firmware v1.2.0",
            "features": ["basic_gpio", "analog_read", "pwm", "serial", "interrupts", "sensors"],
            "filename": "esp32_sensor_v1.2.0.bin"
        }
    }

    # 默认固件版本
    DEFAULT_FIRMWARE_VERSION = "1.2.0"

    def __init__(self, port: str = None, auto_detect: bool = True):
        """
        初始化固件管理器

        Args:
            port: 串口号，None则自动检测
            auto_detect: 是否自动检测设备
        """
        self.port = port
        self._conn: Optional[SerialConnection] = None
        self._encoder = ProtocolEncoder()
        self._decoder = ProtocolDecoder()

        if auto_detect:
            self.detect_device()

    def detect_device(self) -> bool:
        """
        检测ESP32设备

        Returns:
            是否找到设备
        """
        if self.port is None:
            logger.info("自动检测ESP32设备...")
            self.port = find_esp32_device()

            if self.port is None:
                logger.warning("未找到ESP32设备")
                return False

        logger.info(f"找到ESP32设备: {self.port}")
        return True

    def check_firmware_status(self) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """
        检查设备固件状态

        Returns:
            (has_firmware, version, info) 元组
            - has_firmware: 是否有固件
            - version: 固件版本（如果有）
            - info: 附加信息字典
        """
        if not self.port:
            return False, None, {"error": "未找到设备"}

        logger.info("检查设备固件状态...")

        try:
            # 尝试建立串口连接
            self._conn = SerialConnection(self.port, 115200)
            self._conn.connect()

            # 尝试发送ping命令测试固件响应
            command = self._encoder.ping()
            response = self._conn.send_command(command, timeout=3.0)

            if response:
                status, data = self._decoder.parse_response(response)
                if self._decoder.is_success(status):
                    # 设备有固件，尝试获取版本信息
                    version = self._get_firmware_version()
                    info = {
                        "status": "firmware_present",
                        "ping_response": response,
                        "connection": "successful"
                    }
                    if version:
                        info["firmware_version"] = version
                    return True, version, info

            # 如果ping失败，尝试读取芯片信息判断是否为空芯片
            chip_info = read_chip_info(self.port)
            if chip_info.get("success"):
                info = {
                    "status": "no_firmware",
                    "chip_info": chip_info["output"],
                    "connection": "chip_detected_no_firmware"
                }
                return False, None, info
            else:
                info = {
                    "status": "unknown",
                    "error": "无法读取芯片信息",
                    "chip_info": chip_info["output"]
                }
                return False, None, info

        except (SerialCommunicationError, ProtocolError) as e:
            logger.warning(f"通信失败，可能没有固件: {e}")
            info = {
                "status": "communication_failed",
                "error": str(e),
                "suggestion": "设备可能需要烧录固件"
            }
            return False, None, info

        except Exception as e:
            logger.error(f"检查固件状态失败: {e}")
            info = {
                "status": "check_failed",
                "error": str(e)
            }
            return False, None, info

        finally:
            if self._conn:
                self._conn.disconnect()
                self._conn = None

    def _get_firmware_version(self) -> Optional[str]:
        """
        获取固件版本

        Returns:
            固件版本字符串，获取失败返回None
        """
        try:
            # 发送版本查询命令
            command = self._encoder.get_version()
            response = self._conn.send_command(command, timeout=2.0)

            if response:
                status, data = self._decoder.parse_response(response)
                if self._decoder.is_success(status) and data:
                    logger.info(f"检测到固件版本: {data}")
                    return data

        except Exception as e:
            logger.debug(f"获取固件版本失败: {e}")

        return None

    def needs_firmware_update(self, required_version: str = None) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """
        检查是否需要更新固件

        Args:
            required_version: 需要的固件版本，None则使用默认版本

        Returns:
            (needs_update, current_version, info) 元组
        """
        if required_version is None:
            required_version = self.DEFAULT_FIRMWARE_VERSION

        has_firmware, current_version, info = self.check_firmware_status()

        if not has_firmware:
            return True, None, {**info, "reason": "no_firmware"}

        if current_version is None:
            return True, current_version, {**info, "reason": "version_unknown"}

        # 简单的版本比较
        if self._compare_versions(current_version, required_version) < 0:
            return True, current_version, {**info, "reason": "version_outdated"}

        return False, current_version, {**info, "reason": "version_ok"}

    def _compare_versions(self, v1: str, v2: str) -> int:
        """
        比较版本号

        Args:
            v1: 版本1
            v2: 版本2

        Returns:
            -1: v1 < v2, 0: v1 == v2, 1: v1 > v2
        """
        try:
            v1_parts = [int(x) for x in v1.split('.')]
            v2_parts = [int(x) for x in v2.split('.')]

            # 补齐版本号长度
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts.extend([0] * (max_len - len(v1_parts)))
            v2_parts.extend([0] * (max_len - len(v2_parts)))

            for a, b in zip(v1_parts, v2_parts):
                if a < b:
                    return -1
                elif a > b:
                    return 1
            return 0
        except:
            return -1  # 解析失败，认为需要更新

    def auto_install_firmware(self, firmware_version: str = None, force: bool = False) -> bool:
        """
        自动安装固件

        Args:
            firmware_version: 要安装的固件版本，None则使用默认版本
            force: 是否强制重新安装

        Returns:
            是否安装成功
        """
        if firmware_version is None:
            firmware_version = self.DEFAULT_FIRMWARE_VERSION

        # 检查是否需要安装
        if not force:
            needs_update, current_version, info = self.needs_firmware_update(firmware_version)
            if not needs_update:
                logger.info(f"固件已是最新版本 {current_version}，无需更新")
                return True

        logger.info(f"开始自动安装固件版本 {firmware_version}")

        try:
            # 获取固件文件信息
            if firmware_version not in self.SUPPORTED_FIRMWARE_VERSIONS:
                raise FirmwareManagerError(f"不支持的固件版本: {firmware_version}")

            firmware_info = self.SUPPORTED_FIRMWARE_VERSIONS[firmware_version]
            firmware_filename = firmware_info["filename"]

            # 查找固件文件
            firmware_path = self._find_firmware_file(firmware_filename)
            if not firmware_path:
                raise FirmwareManagerError(f"未找到固件文件: {firmware_filename}")

            logger.info(f"使用固件文件: {firmware_path}")

            # 烧录固件
            success = flash_firmware(
                port=self.port,
                firmware_path=str(firmware_path),
                baudrate=460800
            )

            if success:
                logger.info("固件安装成功!")
                # 等待设备重启
                logger.info("等待设备重启...")
                time.sleep(3)

                # 验证安装
                has_firmware, version, info = self.check_firmware_status()
                if has_firmware:
                    logger.info(f"固件验证成功，版本: {version}")
                    return True
                else:
                    logger.warning("固件安装完成但验证失败")
                    return False
            else:
                raise FirmwareManagerError("固件烧录失败")

        except FlashError as e:
            logger.error(f"固件烧录错误: {e}")
            return False
        except FirmwareManagerError as e:
            logger.error(f"固件管理错误: {e}")
            return False
        except Exception as e:
            logger.error(f"自动安装固件失败: {e}")
            return False

    def _find_firmware_file(self, filename: str) -> Optional[Path]:
        """
        查找固件文件

        Args:
            filename: 固件文件名

        Returns:
            固件文件路径，未找到返回None
        """
        # 可能的搜索路径
        search_paths = [
            # 安装包内的固件目录
            Path(__file__).parent.parent / "firmware" / "compiled" / filename,
            # 开发环境的固件目录
            Path(__file__).parent.parent.parent / "firmware" / "compiled" / filename,
            # 当前目录的firmware子目录
            Path.cwd() / "firmware" / "compiled" / filename,
            # 当前目录
            Path.cwd() / filename,
        ]

        for path in search_paths:
            if path.exists():
                logger.debug(f"找到固件文件: {path}")
                return path

        logger.warning(f"未找到固件文件: {filename}")
        logger.debug(f"搜索路径: {[str(p) for p in search_paths]}")
        return None

    def ensure_firmware(self, firmware_version: str = None, auto_install: bool = True) -> Tuple[bool, str]:
        """
        确保设备有可用的固件

        Args:
            firmware_version: 需要的固件版本
            auto_install: 是否自动安装缺失的固件

        Returns:
            (success, message) 元组
        """
        if firmware_version is None:
            firmware_version = self.DEFAULT_FIRMWARE_VERSION

        logger.info(f"检查固件状态，目标版本: {firmware_version}")

        # 检查设备是否存在
        if not self.port and not self.detect_device():
            return False, "未找到ESP32设备"

        # 检查固件状态
        needs_update, current_version, info = self.needs_firmware_update(firmware_version)

        if not needs_update:
            return True, f"固件已是最新版本 {current_version}"

        # 需要更新固件
        reason = info.get("reason", "unknown")
        logger.info(f"需要更新固件，原因: {reason}")

        if not auto_install:
            return False, f"需要安装固件版本 {firmware_version}，但自动安装已禁用"

        # 自动安装固件
        logger.info("开始自动安装固件...")
        success = self.auto_install_firmware(firmware_version)

        if success:
            return True, f"固件安装成功，版本: {firmware_version}"
        else:
            return False, f"固件安装失败，目标版本: {firmware_version}"

    @classmethod
    def quick_check(cls) -> Tuple[bool, Optional[str], str]:
        """
        快速检查固件状态

        Returns:
            (is_ok, version, message) 元组
        """
        try:
            manager = cls()
            has_firmware, version, info = manager.check_firmware_status()

            if has_firmware:
                return True, version, f"设备固件正常，版本: {version}"
            else:
                return False, None, f"设备需要安装固件: {info.get('status', 'unknown')}"

        except Exception as e:
            return False, None, f"检查失败: {e}"


# 便捷函数
def ensure_firmware_before_connect(port: str = None, firmware_version: str = None) -> Tuple[bool, str]:
    """
    在连接前确保设备有正确的固件

    Args:
        port: 串口号
        firmware_version: 需要的固件版本

    Returns:
        (success, message) 元组
    """
    manager = FirmwareManager(port=port, auto_detect=False)

    if port:
        manager.port = port

    return manager.ensure_firmware(firmware_version=firmware_version, auto_install=True)