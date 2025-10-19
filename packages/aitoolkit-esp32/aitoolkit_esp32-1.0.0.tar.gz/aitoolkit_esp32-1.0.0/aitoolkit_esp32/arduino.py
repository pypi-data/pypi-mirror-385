"""
Arduino 类 - 核心控制类
完全 Arduino 风格的 API
"""

import time
import logging
from typing import Optional, Callable, Dict
from .serial_comm import SerialConnection, SerialCommunicationError
from .protocol import ProtocolEncoder, ProtocolDecoder, ProtocolError
from .device_detector import find_esp32_device
from .constants import *
from .firmware_manager import FirmwareManager, ensure_firmware_before_connect

logger = logging.getLogger(__name__)


class ArduinoError(Exception):
    """Arduino 操作错误"""
    pass


class Arduino:
    """
    Arduino 风格的 ESP32 控制类

    示例:
        board = Arduino(port="/dev/ttyUSB0")
        board.pinMode(13, board.OUTPUT)
        board.digitalWrite(13, board.HIGH)
    """

    # 常量（可以通过 board.HIGH 访问）
    HIGH = HIGH
    LOW = LOW
    INPUT = INPUT
    OUTPUT = OUTPUT
    INPUT_PULLUP = INPUT_PULLUP
    INPUT_PULLDOWN = INPUT_PULLDOWN
    RISING = RISING
    FALLING = FALLING
    CHANGE = CHANGE

    def __init__(self, port: str = None, baudrate: int = 115200, auto_connect: bool = True,
                 auto_firmware: bool = True, firmware_version: str = None):
        """
        初始化 Arduino 对象

        Args:
            port: 串口号，None 则自动检测
            baudrate: 波特率
            auto_connect: 是否自动连接
            auto_firmware: 是否自动检查和安装固件
            firmware_version: 指定的固件版本，None则使用默认版本
        """
        self.port = port
        self.baudrate = baudrate
        self._auto_firmware = auto_firmware
        self._firmware_version = firmware_version

        self._conn: Optional[SerialConnection] = None
        self._encoder = ProtocolEncoder()
        self._decoder = ProtocolDecoder()
        self._interrupt_callbacks: Dict[int, Callable] = {}

        if auto_connect:
            self.connect()

    def connect(self):
        """连接到 ESP32 设备"""
        # 自动检测端口
        if self.port is None:
            logger.info("自动检测 ESP32 设备...")
            self.port = find_esp32_device()

            if self.port is None:
                raise ArduinoError("未找到 ESP32 设备")

        # 检查和安装固件（如果启用）
        if self._auto_firmware:
            logger.info("检查设备固件状态...")
            success, message = ensure_firmware_before_connect(
                port=self.port,
                firmware_version=self._firmware_version
            )

            if not success:
                logger.warning(f"固件检查失败: {message}")
                # 继续尝试连接，让用户知道可能的问题
            else:
                logger.info(f"固件状态正常: {message}")

        # 创建串口连接
        self._conn = SerialConnection(self.port, self.baudrate)

        try:
            self._conn.connect()
            logger.info(f"成功连接到 ESP32: {self.port}")

            # 测试连接
            self._test_connection()

            # 启动监听线程（用于中断）
            self._conn.start_listening(self._handle_async_message)

        except Exception as e:
            raise ArduinoError(f"连接失败: {e}")

    def close(self):
        """关闭连接"""
        if self._conn:
            self._conn.disconnect()
            logger.info("已断开连接")

    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self._conn is not None and self._conn.is_connected()

    def _test_connection(self):
        """测试连接"""
        try:
            command = self._encoder.ping()
            response = self._conn.send_command(command, timeout=2.0)

            if response:
                status, _ = self._decoder.parse_response(response)
                if self._decoder.is_success(status):
                    logger.debug("连接测试成功")
                    return

            raise ArduinoError("设备无响应")

        except Exception as e:
            raise ArduinoError(f"连接测试失败: {e}")

    def _send_command(self, command: str) -> tuple:
        """
        发送命令并返回解析后的响应

        Returns:
            (status, data) 元组
        """
        if not self.is_connected():
            raise ArduinoError("未连接到设备")

        try:
            response = self._conn.send_command_retry(command)

            if not response:
                raise ArduinoError("设备无响应")

            status, data = self._decoder.parse_response(response)

            if self._decoder.is_error(status):
                raise ArduinoError(f"命令执行失败: {command.strip()} -> {response}")

            return status, data

        except (SerialCommunicationError, ProtocolError) as e:
            raise ArduinoError(f"通信错误: {e}")

    def _handle_async_message(self, message: str):
        """处理异步消息（中断等）"""
        try:
            if message.startswith("INT"):
                # 中断消息
                pin = self._decoder.parse_interrupt(message)
                if pin in self._interrupt_callbacks:
                    callback = self._interrupt_callbacks[pin]
                    callback()
        except Exception as e:
            logger.error(f"处理异步消息失败: {e}")

    # ===== Arduino API 实现 =====

    def pinMode(self, pin: int, mode: int):
        """
        设置引脚模式

        Args:
            pin: 引脚号
            mode: OUTPUT, INPUT, INPUT_PULLUP, INPUT_PULLDOWN
        """
        command = self._encoder.pin_mode(pin, mode)
        self._send_command(command)
        logger.debug(f"pinMode({pin}, {mode})")

    def digitalWrite(self, pin: int, value: int):
        """
        数字输出

        Args:
            pin: 引脚号
            value: HIGH (1) or LOW (0)
        """
        command = self._encoder.digital_write(pin, value)
        self._send_command(command)
        logger.debug(f"digitalWrite({pin}, {value})")

    def digitalRead(self, pin: int) -> int:
        """
        数字读取

        Args:
            pin: 引脚号

        Returns:
            0 or 1
        """
        command = self._encoder.digital_read(pin)
        _, value = self._send_command(command)
        logger.debug(f"digitalRead({pin}) = {value}")
        return int(value) if value is not None else 0

    def analogRead(self, pin: int) -> int:
        """
        模拟读取 (ADC)

        Args:
            pin: 引脚号

        Returns:
            0-4095
        """
        command = self._encoder.analog_read(pin)
        _, value = self._send_command(command)
        logger.debug(f"analogRead({pin}) = {value}")
        return int(value) if value is not None else 0

    def analogWrite(self, pin: int, value: int):
        """
        模拟输出 (PWM)

        Args:
            pin: 引脚号
            value: 0-255
        """
        command = self._encoder.analog_write(pin, value)
        self._send_command(command)
        logger.debug(f"analogWrite({pin}, {value})")

    def tone(self, pin: int, frequency: int):
        """
        在引脚上生成方波

        Args:
            pin: 引脚号
            frequency: 频率 (Hz)
        """
        command = self._encoder.tone(pin, frequency)
        self._send_command(command)
        logger.debug(f"tone({pin}, {frequency})")

    def noTone(self, pin: int):
        """
        停止方波

        Args:
            pin: 引脚号
        """
        command = self._encoder.no_tone(pin)
        self._send_command(command)
        logger.debug(f"noTone({pin})")

    def pulseIn(self, pin: int, value: int, timeout: int = 1000000) -> int:
        """
        测量脉冲宽度

        Args:
            pin: 引脚号
            value: HIGH or LOW
            timeout: 超时（微秒）

        Returns:
            脉冲宽度（微秒）
        """
        command = self._encoder.pulse_in(pin, value)
        _, duration = self._send_command(command)
        logger.debug(f"pulseIn({pin}, {value}) = {duration}")
        return int(duration) if duration is not None else 0

    def attachInterrupt(self, pin: int, callback: Callable, mode: int):
        """
        绑定中断

        Args:
            pin: 引脚号
            callback: 回调函数
            mode: RISING, FALLING, CHANGE
        """
        # 保存回调函数
        self._interrupt_callbacks[pin] = callback

        # 发送命令
        command = self._encoder.attach_interrupt(pin, mode)
        self._send_command(command)
        logger.debug(f"attachInterrupt({pin}, {mode})")

    def detachInterrupt(self, pin: int):
        """
        解除中断

        Args:
            pin: 引脚号
        """
        # 移除回调
        if pin in self._interrupt_callbacks:
            del self._interrupt_callbacks[pin]

        # 发送命令
        command = self._encoder.detach_interrupt(pin)
        self._send_command(command)
        logger.debug(f"detachInterrupt({pin})")

    def delay(self, ms: int):
        """
        延时（毫秒）

        Args:
            ms: 毫秒数
        """
        time.sleep(ms / 1000.0)

    def delayMicroseconds(self, us: int):
        """
        延时（微秒）

        Args:
            us: 微秒数
        """
        time.sleep(us / 1000000.0)

    def millis(self) -> int:
        """
        获取 ESP32 运行时间（毫秒）

        Returns:
            毫秒数
        """
        command = self._encoder.millis()
        _, value = self._send_command(command)
        return int(value) if value is not None else 0

    # ===== 便捷方法 =====

    @classmethod
    def auto(cls, baudrate: int = 115200, auto_firmware: bool = True, firmware_version: str = None) -> 'Arduino':
        """
        自动检测并连接 ESP32

        Args:
            baudrate: 波特率
            auto_firmware: 是否自动检查和安装固件
            firmware_version: 指定的固件版本，None则使用默认版本

        Returns:
            Arduino 实例
        """
        return cls(port=None, baudrate=baudrate, auto_connect=True,
                  auto_firmware=auto_firmware, firmware_version=firmware_version)

    def reset(self):
        """重置 ESP32 设备"""
        if self._conn:
            self._conn.reset()

    # ===== Serial 类（嵌套类） =====

    class SerialPort:
        """ESP32 的硬件串口类"""

        def __init__(self, arduino_instance, uart_num: int = 1):
            self._arduino = arduino_instance
            self._uart = uart_num

        def begin(self, baudrate: int):
            """配置串口"""
            command = self._arduino._encoder.serial_begin(self._uart, baudrate)
            self._arduino._send_command(command)

        def write(self, data: str):
            """发送数据"""
            command = self._arduino._encoder.serial_write(self._uart, data)
            self._arduino._send_command(command)

        def println(self, data: str):
            """发送一行数据"""
            self.write(data + '\n')

        def read(self) -> str:
            """读取数据"""
            command = self._arduino._encoder.serial_read(self._uart)
            _, data = self._arduino._send_command(command)
            return data if data is not None else ""

        def readLine(self) -> str:
            """读取一行数据"""
            return self.read()

    @property
    def Serial(self):
        """获取 Serial1 对象"""
        return self.SerialPort(self, uart_num=1)

    # ===== 上下文管理器 =====

    def __enter__(self):
        """上下文管理器入口"""
        if not self.is_connected():
            self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.close()

    def __del__(self):
        """析构函数"""
        self.close()

    def __repr__(self):
        """字符串表示"""
        status = "connected" if self.is_connected() else "disconnected"
        return f"<Arduino port={self.port} status={status}>"
