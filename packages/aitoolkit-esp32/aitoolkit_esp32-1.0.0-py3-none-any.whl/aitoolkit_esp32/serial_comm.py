"""
串口通信模块
"""

import serial
import serial.tools.list_ports
import time
import logging
import threading
from typing import Optional, Callable
from .config import get_config

logger = logging.getLogger(__name__)


class SerialCommunicationError(Exception):
    """串口通信错误"""
    pass


class SerialConnection:
    """串口连接管理类"""

    def __init__(self, port: str, baudrate: int = None, timeout: float = None):
        """
        初始化串口连接

        Args:
            port: 串口号
            baudrate: 波特率（默认从配置读取）
            timeout: 超时时间（秒）
        """
        self.port = port
        self.baudrate = baudrate or get_config("serial.baudrate")
        self.timeout = timeout or get_config("serial.timeout")
        self.write_timeout = get_config("serial.write_timeout")

        self._serial: Optional[serial.Serial] = None
        self._lock = threading.Lock()
        self._interrupt_callback: Optional[Callable] = None
        self._listen_thread: Optional[threading.Thread] = None
        self._listening = False

    def connect(self) -> bool:
        """
        建立串口连接

        Returns:
            是否成功连接

        Raises:
            SerialCommunicationError: 连接失败
        """
        try:
            logger.info(f"连接到串口: {self.port} @ {self.baudrate}")

            self._serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                write_timeout=self.write_timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
            )

            # 清空缓冲区
            self._serial.reset_input_buffer()
            self._serial.reset_output_buffer()

            # 等待设备稳定
            time.sleep(0.5)

            logger.info(f"成功连接到: {self.port}")
            return True

        except serial.SerialException as e:
            logger.error(f"连接失败: {e}")
            raise SerialCommunicationError(f"Failed to connect to {self.port}: {e}")

    def disconnect(self):
        """断开串口连接"""
        self._listening = False

        if self._listen_thread and self._listen_thread.is_alive():
            self._listen_thread.join(timeout=2.0)

        if self._serial and self._serial.is_open:
            logger.info(f"断开连接: {self.port}")
            self._serial.close()
            self._serial = None

    def is_connected(self) -> bool:
        """
        检查是否已连接

        Returns:
            是否已连接
        """
        return self._serial is not None and self._serial.is_open

    def write(self, data: str) -> bool:
        """
        发送数据

        Args:
            data: 要发送的字符串

        Returns:
            是否成功发送

        Raises:
            SerialCommunicationError: 发送失败
        """
        if not self.is_connected():
            raise SerialCommunicationError("Not connected")

        try:
            with self._lock:
                self._serial.write(data.encode('ascii'))
                self._serial.flush()

                # 命令间延时
                delay = get_config("protocol.command_delay")
                if delay:
                    time.sleep(delay)

                return True

        except serial.SerialException as e:
            logger.error(f"发送数据失败: {e}")
            raise SerialCommunicationError(f"Failed to write data: {e}")

    def read_line(self, timeout: float = None) -> Optional[str]:
        """
        读取一行数据

        Args:
            timeout: 超时时间（秒），None 使用默认值

        Returns:
            读取的字符串，超时返回 None

        Raises:
            SerialCommunicationError: 读取失败
        """
        if not self.is_connected():
            raise SerialCommunicationError("Not connected")

        try:
            old_timeout = self._serial.timeout
            if timeout is not None:
                self._serial.timeout = timeout

            with self._lock:
                line = self._serial.readline()

            # 恢复超时设置
            if timeout is not None:
                self._serial.timeout = old_timeout

            if line:
                return line.decode('ascii', errors='ignore').strip()
            return None

        except serial.SerialException as e:
            logger.error(f"读取数据失败: {e}")
            raise SerialCommunicationError(f"Failed to read data: {e}")

    def send_command(self, command: str, wait_response: bool = True, timeout: float = None) -> Optional[str]:
        """
        发送命令并等待响应

        Args:
            command: 命令字符串
            wait_response: 是否等待响应
            timeout: 响应超时时间（秒）

        Returns:
            响应字符串，如果不等待响应则返回 None

        Raises:
            SerialCommunicationError: 通信失败
        """
        if timeout is None:
            timeout = get_config("protocol.response_timeout")

        # 发送命令
        self.write(command)

        if not wait_response:
            return None

        # 等待响应
        response = self.read_line(timeout=timeout)

        if response is None:
            logger.warning(f"命令超时: {command.strip()}")

        return response

    def send_command_retry(self, command: str, max_retries: int = None) -> str:
        """
        发送命令并重试

        Args:
            command: 命令字符串
            max_retries: 最大重试次数

        Returns:
            响应字符串

        Raises:
            SerialCommunicationError: 重试失败
        """
        if max_retries is None:
            max_retries = get_config("protocol.max_retries")

        last_error = None

        for attempt in range(max_retries):
            try:
                response = self.send_command(command)
                if response:
                    return response

                logger.warning(f"命令无响应 (尝试 {attempt + 1}/{max_retries}): {command.strip()}")

            except SerialCommunicationError as e:
                last_error = e
                logger.warning(f"命令失败 (尝试 {attempt + 1}/{max_retries}): {e}")

            # 短暂延时后重试
            if attempt < max_retries - 1:
                time.sleep(0.1)

        raise SerialCommunicationError(
            f"Command failed after {max_retries} retries: {command.strip()}"
        ) from last_error

    def start_listening(self, callback: Callable[[str], None]):
        """
        开始监听串口数据（用于中断等异步消息）

        Args:
            callback: 数据回调函数
        """
        if self._listening:
            logger.warning("Already listening")
            return

        self._interrupt_callback = callback
        self._listening = True
        self._listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._listen_thread.start()

        logger.info("开始监听串口数据")

    def stop_listening(self):
        """停止监听"""
        if not self._listening:
            return

        self._listening = False

        if self._listen_thread and self._listen_thread.is_alive():
            self._listen_thread.join(timeout=2.0)

        logger.info("停止监听串口数据")

    def _listen_loop(self):
        """监听循环（在独立线程中运行）"""
        while self._listening and self.is_connected():
            try:
                # 非阻塞读取
                if self._serial.in_waiting > 0:
                    line = self.read_line(timeout=0.1)
                    if line and self._interrupt_callback:
                        self._interrupt_callback(line)
                else:
                    time.sleep(0.01)  # 避免 CPU 占用过高

            except Exception as e:
                logger.error(f"监听线程错误: {e}")
                time.sleep(0.1)

    def reset(self):
        """重置设备（通过 DTR 信号）"""
        if not self.is_connected():
            raise SerialCommunicationError("Not connected")

        logger.info("重置设备")
        self._serial.setDTR(False)
        time.sleep(0.1)
        self._serial.setDTR(True)
        time.sleep(0.5)

    def __enter__(self):
        """上下文管理器入口"""
        if not self.is_connected():
            self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.disconnect()

    def __del__(self):
        """析构函数"""
        self.disconnect()
