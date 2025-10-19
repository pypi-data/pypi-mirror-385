"""
集成测试 - 测试模块间的协作
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from aitoolkit_esp32 import Arduino, HIGH, LOW, OUTPUT, INPUT
from aitoolkit_esp32.protocol import ProtocolEncoder, ProtocolDecoder
from aitoolkit_esp32.device_detector import find_esp32_device


@pytest.mark.integration
class TestArduinoWorkflow:
    """测试 Arduino 完整工作流程"""

    @patch('aitoolkit_esp32.arduino.SerialConnection')
    def test_blink_led_workflow(self, mock_serial):
        """测试 LED 闪烁完整流程"""
        # 配置 mock
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn
        mock_conn.is_connected.return_value = True
        mock_conn.send_command.return_value = "OK"
        mock_conn.send_command_retry.return_value = "OK"

        # 创建 Arduino 实例
        board = Arduino(port="/dev/ttyUSB0", auto_connect=True)

        # LED 闪烁流程
        board.pinMode(13, OUTPUT)
        board.digitalWrite(13, HIGH)
        board.delay(100)
        board.digitalWrite(13, LOW)

        # 验证调用
        assert mock_conn.send_command_retry.call_count >= 3

    @patch('aitoolkit_esp32.arduino.SerialConnection')
    def test_button_reading_workflow(self, mock_serial):
        """测试按钮读取完整流程"""
        # 配置 mock
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn
        mock_conn.is_connected.return_value = True
        mock_conn.send_command.return_value = "OK"

        # 模拟按钮状态变化
        responses = iter(["OK", "OK1", "OK0", "OK1"])
        mock_conn.send_command_retry.side_effect = lambda x: next(responses)

        # 创建 Arduino 实例
        board = Arduino(port="/dev/ttyUSB0", auto_connect=True)

        # 按钮读取流程
        board.pinMode(12, INPUT)
        state1 = board.digitalRead(12)
        state2 = board.digitalRead(12)
        state3 = board.digitalRead(12)

        # 验证结果
        assert state1 == 1
        assert state2 == 0
        assert state3 == 1


@pytest.mark.integration
class TestProtocolIntegration:
    """测试协议编解码集成"""

    def test_encoder_decoder_integration(self):
        """测试编码器和解码器集成"""
        encoder = ProtocolEncoder()
        decoder = ProtocolDecoder()

        # 测试多个命令的编解码
        commands = [
            (encoder.pin_mode(13, 1), "OK"),
            (encoder.digital_write(13, 1), "OK"),
            (encoder.digital_read(12), "OK1"),
            (encoder.analog_read(34), "OK2048"),
        ]

        for command, response in commands:
            status, data = decoder.parse_response(response)
            assert decoder.is_success(status)

    def test_protocol_command_sequence(self):
        """测试协议命令序列"""
        encoder = ProtocolEncoder()
        decoder = ProtocolDecoder()

        # 模拟 LED 闪烁的命令序列
        sequence = [
            encoder.pin_mode(13, 1),      # pinMode(13, OUTPUT)
            encoder.digital_write(13, 1), # digitalWrite(13, HIGH)
            encoder.delay(1000),          # delay(1000)
            encoder.digital_write(13, 0), # digitalWrite(13, LOW)
        ]

        # 验证所有命令都能正确编码
        assert all(cmd.endswith('\n') for cmd in sequence)

        # 模拟响应
        for cmd in sequence:
            status, data = decoder.parse_response("OK")
            assert decoder.is_success(status)


@pytest.mark.integration
class TestEndToEndScenarios:
    """测试端到端场景"""

    @patch('aitoolkit_esp32.arduino.find_esp32_device')
    @patch('aitoolkit_esp32.arduino.SerialConnection')
    def test_auto_connect_and_use(self, mock_serial, mock_find):
        """测试自动连接并使用"""
        # 配置 mock
        mock_find.return_value = "/dev/ttyUSB0"
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn
        mock_conn.is_connected.return_value = True
        mock_conn.send_command.return_value = "OK"
        mock_conn.send_command_retry.return_value = "OK"

        # 使用 auto() 方法
        board = Arduino.auto()

        # 执行操作
        board.pinMode(13, OUTPUT)
        board.digitalWrite(13, HIGH)

        # 验证
        assert board.port == "/dev/ttyUSB0"
        assert mock_conn.send_command_retry.call_count >= 2

    @patch('aitoolkit_esp32.arduino.SerialConnection')
    def test_pwm_scenario(self, mock_serial):
        """测试 PWM 场景"""
        # 配置 mock
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn
        mock_conn.is_connected.return_value = True
        mock_conn.send_command.return_value = "OK"
        mock_conn.send_command_retry.return_value = "OK"

        # 创建实例
        board = Arduino(port="/dev/ttyUSB0", auto_connect=True)

        # PWM 调光场景
        board.pinMode(25, OUTPUT)
        for brightness in [0, 64, 128, 192, 255]:
            board.analogWrite(25, brightness)

        # 验证调用次数（pinMode + 5次 analogWrite）
        assert mock_conn.send_command_retry.call_count >= 6

    @patch('aitoolkit_esp32.arduino.SerialConnection')
    def test_sensor_reading_scenario(self, mock_serial):
        """测试传感器读取场景"""
        # 配置 mock
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn
        mock_conn.is_connected.return_value = True
        mock_conn.send_command.return_value = "OK"

        # 模拟传感器读数
        responses = iter(["OK", "OK1024", "OK2048", "OK3072"])
        mock_conn.send_command_retry.side_effect = lambda x: next(responses)

        # 创建实例
        board = Arduino(port="/dev/ttyUSB0", auto_connect=True)

        # 传感器读取场景
        board.pinMode(34, INPUT)
        readings = []
        for _ in range(3):
            value = board.analogRead(34)
            readings.append(value)

        # 验证读数
        assert readings == [1024, 2048, 3072]


@pytest.mark.integration
class TestContextManagerIntegration:
    """测试上下文管理器集成"""

    @patch('aitoolkit_esp32.arduino.SerialConnection')
    def test_with_statement_complete_workflow(self, mock_serial):
        """测试 with 语句的完整工作流"""
        # 配置 mock
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn
        mock_conn.is_connected.return_value = True
        mock_conn.send_command.return_value = "OK"
        mock_conn.send_command_retry.return_value = "OK1"

        # 使用 with 语句
        with Arduino(port="/dev/ttyUSB0") as board:
            board.pinMode(13, OUTPUT)
            board.digitalWrite(13, HIGH)
            value = board.digitalRead(12)

        # 验证连接已关闭
        mock_conn.disconnect.assert_called_once()


@pytest.mark.integration
class TestErrorHandlingIntegration:
    """测试错误处理集成"""

    @patch('aitoolkit_esp32.arduino.SerialConnection')
    def test_handle_device_error(self, mock_serial):
        """测试处理设备错误"""
        # 配置 mock
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn
        mock_conn.is_connected.return_value = True
        mock_conn.send_command.return_value = "OK"
        mock_conn.send_command_retry.return_value = "ER"

        # 创建实例
        board = Arduino(port="/dev/ttyUSB0", auto_connect=True)

        # 执行会失败的操作
        from aitoolkit_esp32.arduino import ArduinoError
        with pytest.raises(ArduinoError):
            board.digitalWrite(13, HIGH)

    @patch('aitoolkit_esp32.arduino.find_esp32_device')
    def test_handle_no_device_found(self, mock_find):
        """测试处理未找到设备"""
        mock_find.return_value = None

        from aitoolkit_esp32.arduino import ArduinoError
        with pytest.raises(ArduinoError):
            Arduino.auto()


@pytest.mark.integration
class TestModuleImports:
    """测试模块导入集成"""

    def test_import_all_constants(self):
        """测试导入所有常量"""
        from aitoolkit_esp32 import (
            HIGH, LOW,
            INPUT, OUTPUT, INPUT_PULLUP, INPUT_PULLDOWN,
            RISING, FALLING, CHANGE
        )

        assert HIGH == 1
        assert LOW == 0
        assert INPUT == 0
        assert OUTPUT == 1

    def test_import_main_classes(self):
        """测试导入主要类"""
        from aitoolkit_esp32 import Arduino
        from aitoolkit_esp32.protocol import ProtocolEncoder, ProtocolDecoder

        assert Arduino is not None
        assert ProtocolEncoder is not None
        assert ProtocolDecoder is not None

    def test_import_functions(self):
        """测试导入函数"""
        from aitoolkit_esp32 import find_esp32_device, list_esp32_devices

        assert callable(find_esp32_device)
        assert callable(list_esp32_devices)


@pytest.mark.integration
class TestRealWorldExamples:
    """测试真实世界的使用示例"""

    @patch('aitoolkit_esp32.arduino.SerialConnection')
    def test_traffic_light_example(self, mock_serial):
        """测试交通灯示例"""
        # 配置 mock
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn
        mock_conn.is_connected.return_value = True
        mock_conn.send_command.return_value = "OK"
        mock_conn.send_command_retry.return_value = "OK"

        # 交通灯示例
        board = Arduino(port="/dev/ttyUSB0", auto_connect=True)

        RED_PIN = 13
        YELLOW_PIN = 12
        GREEN_PIN = 14

        # 初始化引脚
        for pin in [RED_PIN, YELLOW_PIN, GREEN_PIN]:
            board.pinMode(pin, OUTPUT)
            board.digitalWrite(pin, LOW)

        # 红灯
        board.digitalWrite(RED_PIN, HIGH)
        board.digitalWrite(GREEN_PIN, LOW)

        # 验证调用
        assert mock_conn.send_command_retry.call_count >= 8

    @patch('aitoolkit_esp32.arduino.SerialConnection')
    def test_temperature_monitor_example(self, mock_serial):
        """测试温度监控示例"""
        # 配置 mock
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn
        mock_conn.is_connected.return_value = True
        mock_conn.send_command.return_value = "OK"

        # 模拟温度读数
        responses = ["OK", "OK1500", "OK1600", "OK1550"]
        mock_conn.send_command_retry.side_effect = responses

        # 温度监控示例
        board = Arduino(port="/dev/ttyUSB0", auto_connect=True)

        TEMP_SENSOR_PIN = 34
        board.pinMode(TEMP_SENSOR_PIN, INPUT)

        # 读取多次温度
        temperatures = []
        for _ in range(3):
            raw_value = board.analogRead(TEMP_SENSOR_PIN)
            temperatures.append(raw_value)

        # 验证读数
        assert len(temperatures) == 3
        assert all(isinstance(t, int) for t in temperatures)
