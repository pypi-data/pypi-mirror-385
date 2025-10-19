"""
通信协议编解码模块
"""

from typing import Union, Tuple
from .constants import Commands, Status, HIGH, LOW, INPUT, OUTPUT, INPUT_PULLUP, INPUT_PULLDOWN, RISING, FALLING, CHANGE


class ProtocolError(Exception):
    """协议错误"""
    pass


class ProtocolEncoder:
    """协议编码器 - 将 Python 命令编码为串口命令"""

    @staticmethod
    def pin_mode(pin: int, mode: int) -> str:
        """
        编码 pinMode 命令

        Args:
            pin: 引脚号
            mode: 引脚模式 (INPUT, OUTPUT, INPUT_PULLUP, INPUT_PULLDOWN)

        Returns:
            命令字符串
        """
        mode_map = {
            OUTPUT: 'O',
            INPUT: 'I',
            INPUT_PULLUP: 'U',
            INPUT_PULLDOWN: 'D',
        }

        if mode not in mode_map:
            raise ProtocolError(f"Invalid pin mode: {mode}")

        return f"M{pin:02d}{mode_map[mode]}\n"

    @staticmethod
    def digital_write(pin: int, value: int) -> str:
        """
        编码 digitalWrite 命令

        Args:
            pin: 引脚号
            value: 电平值 (HIGH or LOW)

        Returns:
            命令字符串
        """
        value_char = 'H' if value else 'L'
        return f"W{pin:02d}{value_char}\n"

    @staticmethod
    def digital_read(pin: int) -> str:
        """
        编码 digitalRead 命令

        Args:
            pin: 引脚号

        Returns:
            命令字符串
        """
        return f"R{pin:02d}\n"

    @staticmethod
    def analog_read(pin: int) -> str:
        """
        编码 analogRead 命令

        Args:
            pin: 引脚号

        Returns:
            命令字符串
        """
        return f"A{pin:02d}\n"

    @staticmethod
    def analog_write(pin: int, value: int) -> str:
        """
        编码 analogWrite (PWM) 命令

        Args:
            pin: 引脚号
            value: PWM 值 (0-255)

        Returns:
            命令字符串
        """
        value = max(0, min(255, value))  # 限制范围
        return f"P{pin:02d}{value:03d}\n"

    @staticmethod
    def tone(pin: int, frequency: int) -> str:
        """
        编码 tone 命令

        Args:
            pin: 引脚号
            frequency: 频率 (Hz)

        Returns:
            命令字符串
        """
        return f"T{pin:02d}{frequency:05d}\n"

    @staticmethod
    def no_tone(pin: int) -> str:
        """
        编码 noTone 命令

        Args:
            pin: 引脚号

        Returns:
            命令字符串
        """
        return f"N{pin:02d}\n"

    @staticmethod
    def pulse_in(pin: int, value: int) -> str:
        """
        编码 pulseIn 命令

        Args:
            pin: 引脚号
            value: HIGH or LOW

        Returns:
            命令字符串
        """
        value_char = 'H' if value else 'L'
        return f"U{pin:02d}{value_char}\n"

    @staticmethod
    def attach_interrupt(pin: int, mode: int) -> str:
        """
        编码 attachInterrupt 命令

        Args:
            pin: 引脚号
            mode: 中断模式 (RISING, FALLING, CHANGE)

        Returns:
            命令字符串
        """
        mode_map = {
            RISING: 'R',
            FALLING: 'F',
            CHANGE: 'C',
        }

        if mode not in mode_map:
            raise ProtocolError(f"Invalid interrupt mode: {mode}")

        return f"I{pin:02d}{mode_map[mode]}\n"

    @staticmethod
    def detach_interrupt(pin: int) -> str:
        """
        编码 detachInterrupt 命令

        Args:
            pin: 引脚号

        Returns:
            命令字符串
        """
        return f"D{pin:02d}\n"

    @staticmethod
    def delay(ms: int) -> str:
        """
        编码 delay 命令

        Args:
            ms: 延时毫秒数

        Returns:
            命令字符串
        """
        return f"L{ms:05d}\n"

    @staticmethod
    def millis() -> str:
        """
        编码 millis 命令

        Returns:
            命令字符串
        """
        return "Q\n"

    @staticmethod
    def ping() -> str:
        """
        编码 ping 命令

        Returns:
            命令字符串
        """
        return "Z\n"

    @staticmethod
    def get_version() -> str:
        """
        编码获取固件版本命令

        Returns:
            命令字符串
        """
        return "V\n"

    @staticmethod
    def serial_begin(uart: int, baudrate: int) -> str:
        """
        编码 Serial.begin 命令

        Args:
            uart: UART 编号 (1 or 2)
            baudrate: 波特率

        Returns:
            命令字符串
        """
        return f"S{uart}{baudrate:06d}\n"

    @staticmethod
    def serial_write(uart: int, data: str) -> str:
        """
        编码 Serial.write 命令

        Args:
            uart: UART 编号
            data: 要发送的数据

        Returns:
            命令字符串
        """
        return f"X{uart}{data}\n"

    @staticmethod
    def serial_read(uart: int) -> str:
        """
        编码 Serial.read 命令

        Args:
            uart: UART 编号

        Returns:
            命令字符串
        """
        return f"Y{uart}\n"


class ProtocolDecoder:
    """协议解码器 - 解析串口响应"""

    @staticmethod
    def parse_response(response: str) -> Tuple[str, Union[str, int, None]]:
        """
        解析响应

        Args:
            response: 响应字符串

        Returns:
            (status, data) 元组
            - status: 'OK', 'ER', 'TO', 'IV'
            - data: 数据（如果有）

        Raises:
            ProtocolError: 解析失败
        """
        response = response.strip()

        if not response:
            raise ProtocolError("Empty response")

        # 提取状态码（前两个字符）
        if len(response) < 2:
            raise ProtocolError(f"Invalid response: {response}")

        status = response[:2]

        # 验证状态码
        if status not in [Status.OK, Status.ERROR, Status.TIMEOUT, Status.INVALID]:
            raise ProtocolError(f"Unknown status code: {status}")

        # 提取数据
        data = None
        if len(response) > 2:
            data_str = response[2:]
            # 尝试转换为整数
            try:
                data = int(data_str)
            except ValueError:
                data = data_str

        return status, data

    @staticmethod
    def parse_interrupt(message: str) -> int:
        """
        解析中断通知

        Args:
            message: 中断消息，格式: "INT<pin>"

        Returns:
            引脚号

        Raises:
            ProtocolError: 解析失败
        """
        if not message.startswith("INT"):
            raise ProtocolError(f"Invalid interrupt message: {message}")

        try:
            pin = int(message[3:5])
            return pin
        except (ValueError, IndexError):
            raise ProtocolError(f"Invalid interrupt pin in message: {message}")

    @staticmethod
    def is_success(status: str) -> bool:
        """
        检查状态是否为成功

        Args:
            status: 状态码

        Returns:
            是否成功
        """
        return status == Status.OK

    @staticmethod
    def is_error(status: str) -> bool:
        """
        检查状态是否为错误

        Args:
            status: 状态码

        Returns:
            是否错误
        """
        return status in [Status.ERROR, Status.TIMEOUT, Status.INVALID]


# 便捷访问
encoder = ProtocolEncoder()
decoder = ProtocolDecoder()
