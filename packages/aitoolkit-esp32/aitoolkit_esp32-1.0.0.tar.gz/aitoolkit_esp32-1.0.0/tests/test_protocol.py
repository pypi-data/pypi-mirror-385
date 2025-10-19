"""
测试 protocol 模块 - 协议编解码功能
"""
import pytest
from aitoolkit_esp32.protocol import ProtocolEncoder, ProtocolDecoder, ProtocolError
from aitoolkit_esp32.constants import (
    HIGH, LOW, INPUT, OUTPUT, INPUT_PULLUP, INPUT_PULLDOWN,
    RISING, FALLING, CHANGE, Status
)


class TestProtocolEncoder:
    """测试协议编码器"""

    def test_pin_mode_output(self):
        """测试 pinMode OUTPUT 编码"""
        encoder = ProtocolEncoder()
        result = encoder.pin_mode(13, OUTPUT)
        assert result == "M13O\n"

    def test_pin_mode_input(self):
        """测试 pinMode INPUT 编码"""
        encoder = ProtocolEncoder()
        result = encoder.pin_mode(12, INPUT)
        assert result == "M12I\n"

    def test_pin_mode_input_pullup(self):
        """测试 pinMode INPUT_PULLUP 编码"""
        encoder = ProtocolEncoder()
        result = encoder.pin_mode(14, INPUT_PULLUP)
        assert result == "M14U\n"

    def test_pin_mode_input_pulldown(self):
        """测试 pinMode INPUT_PULLDOWN 编码"""
        encoder = ProtocolEncoder()
        result = encoder.pin_mode(15, INPUT_PULLDOWN)
        assert result == "M15D\n"

    def test_pin_mode_invalid(self):
        """测试无效的引脚模式"""
        encoder = ProtocolEncoder()
        with pytest.raises(ProtocolError):
            encoder.pin_mode(13, 99)

    def test_digital_write_high(self):
        """测试 digitalWrite HIGH 编码"""
        encoder = ProtocolEncoder()
        result = encoder.digital_write(13, HIGH)
        assert result == "W13H\n"

    def test_digital_write_low(self):
        """测试 digitalWrite LOW 编码"""
        encoder = ProtocolEncoder()
        result = encoder.digital_write(13, LOW)
        assert result == "W13L\n"

    def test_digital_read(self):
        """测试 digitalRead 编码"""
        encoder = ProtocolEncoder()
        result = encoder.digital_read(12)
        assert result == "R12\n"

    def test_analog_read(self):
        """测试 analogRead 编码"""
        encoder = ProtocolEncoder()
        result = encoder.analog_read(34)
        assert result == "A34\n"

    def test_analog_write(self):
        """测试 analogWrite 编码"""
        encoder = ProtocolEncoder()
        result = encoder.analog_write(25, 128)
        assert result == "P25128\n"

    def test_analog_write_boundary(self):
        """测试 analogWrite 边界值"""
        encoder = ProtocolEncoder()

        # 测试最小值
        result = encoder.analog_write(25, 0)
        assert result == "P25000\n"

        # 测试最大值
        result = encoder.analog_write(25, 255)
        assert result == "P25255\n"

        # 测试超出范围（应该被限制）
        result = encoder.analog_write(25, 300)
        assert result == "P25255\n"

        result = encoder.analog_write(25, -10)
        assert result == "P25000\n"

    def test_tone(self):
        """测试 tone 编码"""
        encoder = ProtocolEncoder()
        result = encoder.tone(26, 440)
        assert result == "T2600440\n"

    def test_no_tone(self):
        """测试 noTone 编码"""
        encoder = ProtocolEncoder()
        result = encoder.no_tone(26)
        assert result == "N26\n"

    def test_pulse_in_high(self):
        """测试 pulseIn HIGH 编码"""
        encoder = ProtocolEncoder()
        result = encoder.pulse_in(15, HIGH)
        assert result == "U15H\n"

    def test_pulse_in_low(self):
        """测试 pulseIn LOW 编码"""
        encoder = ProtocolEncoder()
        result = encoder.pulse_in(15, LOW)
        assert result == "U15L\n"

    def test_attach_interrupt_rising(self):
        """测试 attachInterrupt RISING 编码"""
        encoder = ProtocolEncoder()
        result = encoder.attach_interrupt(27, RISING)
        assert result == "I27R\n"

    def test_attach_interrupt_falling(self):
        """测试 attachInterrupt FALLING 编码"""
        encoder = ProtocolEncoder()
        result = encoder.attach_interrupt(27, FALLING)
        assert result == "I27F\n"

    def test_attach_interrupt_change(self):
        """测试 attachInterrupt CHANGE 编码"""
        encoder = ProtocolEncoder()
        result = encoder.attach_interrupt(27, CHANGE)
        assert result == "I27C\n"

    def test_attach_interrupt_invalid(self):
        """测试无效的中断模式"""
        encoder = ProtocolEncoder()
        with pytest.raises(ProtocolError):
            encoder.attach_interrupt(27, 99)

    def test_detach_interrupt(self):
        """测试 detachInterrupt 编码"""
        encoder = ProtocolEncoder()
        result = encoder.detach_interrupt(27)
        assert result == "D27\n"

    def test_delay(self):
        """测试 delay 编码"""
        encoder = ProtocolEncoder()
        result = encoder.delay(1000)
        assert result == "L01000\n"

    def test_millis(self):
        """测试 millis 编码"""
        encoder = ProtocolEncoder()
        result = encoder.millis()
        assert result == "Q\n"

    def test_ping(self):
        """测试 ping 编码"""
        encoder = ProtocolEncoder()
        result = encoder.ping()
        assert result == "Z\n"

    def test_serial_begin(self):
        """测试 Serial.begin 编码"""
        encoder = ProtocolEncoder()
        result = encoder.serial_begin(1, 9600)
        assert result == "S1009600\n"

    def test_serial_write(self):
        """测试 Serial.write 编码"""
        encoder = ProtocolEncoder()
        result = encoder.serial_write(1, "Hello")
        assert result == "X1Hello\n"

    def test_serial_read(self):
        """测试 Serial.read 编码"""
        encoder = ProtocolEncoder()
        result = encoder.serial_read(1)
        assert result == "Y1\n"


class TestProtocolDecoder:
    """测试协议解码器"""

    def test_parse_response_ok(self):
        """测试解析 OK 响应"""
        decoder = ProtocolDecoder()
        status, data = decoder.parse_response("OK")
        assert status == Status.OK
        assert data is None

    def test_parse_response_ok_with_integer_data(self):
        """测试解析带整数数据的 OK 响应"""
        decoder = ProtocolDecoder()
        status, data = decoder.parse_response("OK1234")
        assert status == Status.OK
        assert data == 1234

    def test_parse_response_ok_with_string_data(self):
        """测试解析带字符串数据的 OK 响应"""
        decoder = ProtocolDecoder()
        status, data = decoder.parse_response("OKHello")
        assert status == Status.OK
        assert data == "Hello"

    def test_parse_response_error(self):
        """测试解析 ERROR 响应"""
        decoder = ProtocolDecoder()
        status, data = decoder.parse_response("ER")
        assert status == Status.ERROR
        assert data is None

    def test_parse_response_timeout(self):
        """测试解析 TIMEOUT 响应"""
        decoder = ProtocolDecoder()
        status, data = decoder.parse_response("TO")
        assert status == Status.TIMEOUT
        assert data is None

    def test_parse_response_invalid(self):
        """测试解析 INVALID 响应"""
        decoder = ProtocolDecoder()
        status, data = decoder.parse_response("IV")
        assert status == Status.INVALID
        assert data is None

    def test_parse_response_empty(self):
        """测试解析空响应"""
        decoder = ProtocolDecoder()
        with pytest.raises(ProtocolError):
            decoder.parse_response("")

    def test_parse_response_too_short(self):
        """测试解析过短的响应"""
        decoder = ProtocolDecoder()
        with pytest.raises(ProtocolError):
            decoder.parse_response("O")

    def test_parse_response_unknown_status(self):
        """测试解析未知状态码"""
        decoder = ProtocolDecoder()
        with pytest.raises(ProtocolError):
            decoder.parse_response("XX")

    def test_parse_response_with_whitespace(self):
        """测试解析带空白字符的响应"""
        decoder = ProtocolDecoder()
        status, data = decoder.parse_response("  OK123  \n")
        assert status == Status.OK
        assert data == 123

    def test_parse_interrupt(self):
        """测试解析中断消息"""
        decoder = ProtocolDecoder()
        pin = decoder.parse_interrupt("INT27")
        assert pin == 27

    def test_parse_interrupt_invalid_format(self):
        """测试解析无效的中断消息"""
        decoder = ProtocolDecoder()
        with pytest.raises(ProtocolError):
            decoder.parse_interrupt("INVALID")

    def test_parse_interrupt_invalid_pin(self):
        """测试解析无效的引脚号"""
        decoder = ProtocolDecoder()
        with pytest.raises(ProtocolError):
            decoder.parse_interrupt("INTXX")

    def test_is_success(self):
        """测试 is_success 方法"""
        decoder = ProtocolDecoder()
        assert decoder.is_success(Status.OK) is True
        assert decoder.is_success(Status.ERROR) is False
        assert decoder.is_success(Status.TIMEOUT) is False
        assert decoder.is_success(Status.INVALID) is False

    def test_is_error(self):
        """测试 is_error 方法"""
        decoder = ProtocolDecoder()
        assert decoder.is_error(Status.OK) is False
        assert decoder.is_error(Status.ERROR) is True
        assert decoder.is_error(Status.TIMEOUT) is True
        assert decoder.is_error(Status.INVALID) is True


class TestProtocolRoundTrip:
    """测试协议的完整编解码流程"""

    def test_digital_write_roundtrip(self):
        """测试 digitalWrite 的完整流程"""
        encoder = ProtocolEncoder()
        decoder = ProtocolDecoder()

        # 编码命令
        command = encoder.digital_write(13, HIGH)
        assert command == "W13H\n"

        # 模拟响应并解码
        status, data = decoder.parse_response("OK")
        assert decoder.is_success(status)

    def test_analog_read_roundtrip(self):
        """测试 analogRead 的完整流程"""
        encoder = ProtocolEncoder()
        decoder = ProtocolDecoder()

        # 编码命令
        command = encoder.analog_read(34)
        assert command == "A34\n"

        # 模拟响应并解码
        status, data = decoder.parse_response("OK2048")
        assert decoder.is_success(status)
        assert data == 2048

    def test_multiple_commands(self):
        """测试多个命令的连续编码"""
        encoder = ProtocolEncoder()

        commands = [
            (encoder.pin_mode(13, OUTPUT), "M13O\n"),
            (encoder.digital_write(13, HIGH), "W13H\n"),
            (encoder.delay(1000), "L01000\n"),
            (encoder.digital_write(13, LOW), "W13L\n"),
        ]

        for actual, expected in commands:
            assert actual == expected
