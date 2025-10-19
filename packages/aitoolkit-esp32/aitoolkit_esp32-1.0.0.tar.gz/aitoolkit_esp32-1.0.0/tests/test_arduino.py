"""
测试 Arduino 类 - 核心控制功能
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from aitoolkit_esp32.arduino import Arduino, ArduinoError
from aitoolkit_esp32.constants import (
    HIGH, LOW, INPUT, OUTPUT, INPUT_PULLUP, INPUT_PULLDOWN,
    RISING, FALLING, CHANGE
)


class TestArduinoInit:
    """测试 Arduino 初始化"""

    @patch('aitoolkit_esp32.arduino.find_esp32_device')
    @patch('aitoolkit_esp32.arduino.SerialConnection')
    def test_init_with_port(self, mock_serial, mock_find):
        """测试指定端口初始化"""
        # 配置 mock
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn
        mock_conn.is_connected.return_value = True
        mock_conn.send_command.return_value = "OK"

        # 创建实例
        board = Arduino(port="/dev/ttyUSB0", auto_connect=True)

        # 验证
        assert board.port == "/dev/ttyUSB0"
        assert board.baudrate == 115200
        mock_serial.assert_called_once_with("/dev/ttyUSB0", 115200)

    def test_init_without_auto_connect(self):
        """测试不自动连接"""
        board = Arduino(port="/dev/ttyUSB0", auto_connect=False)

        assert board.port == "/dev/ttyUSB0"
        assert board.is_connected() is False

    @patch('aitoolkit_esp32.arduino.find_esp32_device')
    @patch('aitoolkit_esp32.arduino.SerialConnection')
    def test_init_auto_detect(self, mock_serial, mock_find):
        """测试自动检测端口"""
        mock_find.return_value = "/dev/ttyUSB0"
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn
        mock_conn.is_connected.return_value = True
        mock_conn.send_command.return_value = "OK"

        board = Arduino(port=None, auto_connect=True)

        assert board.port == "/dev/ttyUSB0"
        mock_find.assert_called_once()

    @patch('aitoolkit_esp32.arduino.find_esp32_device')
    def test_init_device_not_found(self, mock_find):
        """测试设备未找到"""
        mock_find.return_value = None

        with pytest.raises(ArduinoError):
            Arduino(port=None, auto_connect=True)


class TestArduinoConstants:
    """测试 Arduino 常量"""

    def test_digital_constants(self):
        """测试数字电平常量"""
        assert Arduino.HIGH == HIGH
        assert Arduino.LOW == LOW

    def test_pin_mode_constants(self):
        """测试引脚模式常量"""
        assert Arduino.INPUT == INPUT
        assert Arduino.OUTPUT == OUTPUT
        assert Arduino.INPUT_PULLUP == INPUT_PULLUP
        assert Arduino.INPUT_PULLDOWN == INPUT_PULLDOWN

    def test_interrupt_constants(self):
        """测试中断模式常量"""
        assert Arduino.RISING == RISING
        assert Arduino.FALLING == FALLING
        assert Arduino.CHANGE == CHANGE


class TestArduinoConnection:
    """测试 Arduino 连接管理"""

    def test_is_connected_false(self):
        """测试未连接状态"""
        board = Arduino(port="/dev/ttyUSB0", auto_connect=False)
        assert board.is_connected() is False

    @patch('aitoolkit_esp32.arduino.SerialConnection')
    def test_close(self, mock_serial):
        """测试关闭连接"""
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn
        mock_conn.is_connected.return_value = True
        mock_conn.send_command.return_value = "OK"

        board = Arduino(port="/dev/ttyUSB0", auto_connect=True)
        board.close()

        mock_conn.disconnect.assert_called_once()


class TestArduinoDigitalIO:
    """测试 Arduino 数字 I/O 功能"""

    def setup_method(self):
        """设置测试环境"""
        self.board = Arduino(port="/dev/ttyUSB0", auto_connect=False)
        self.mock_conn = MagicMock()
        self.board._conn = self.mock_conn
        self.mock_conn.is_connected.return_value = True

    def test_pin_mode_output(self):
        """测试 pinMode OUTPUT"""
        self.mock_conn.send_command_retry.return_value = "OK"

        self.board.pinMode(13, OUTPUT)

        # 验证命令
        call_args = self.mock_conn.send_command_retry.call_args[0][0]
        assert "M13O" in call_args

    def test_pin_mode_input(self):
        """测试 pinMode INPUT"""
        self.mock_conn.send_command_retry.return_value = "OK"

        self.board.pinMode(12, INPUT)

        call_args = self.mock_conn.send_command_retry.call_args[0][0]
        assert "M12I" in call_args

    def test_digital_write_high(self):
        """测试 digitalWrite HIGH"""
        self.mock_conn.send_command_retry.return_value = "OK"

        self.board.digitalWrite(13, HIGH)

        call_args = self.mock_conn.send_command_retry.call_args[0][0]
        assert "W13H" in call_args

    def test_digital_write_low(self):
        """测试 digitalWrite LOW"""
        self.mock_conn.send_command_retry.return_value = "OK"

        self.board.digitalWrite(13, LOW)

        call_args = self.mock_conn.send_command_retry.call_args[0][0]
        assert "W13L" in call_args

    def test_digital_read(self):
        """测试 digitalRead"""
        self.mock_conn.send_command_retry.return_value = "OK1"

        value = self.board.digitalRead(12)

        assert value == 1
        call_args = self.mock_conn.send_command_retry.call_args[0][0]
        assert "R12" in call_args

    def test_digital_read_low(self):
        """测试 digitalRead 返回 LOW"""
        self.mock_conn.send_command_retry.return_value = "OK0"

        value = self.board.digitalRead(12)

        assert value == 0


class TestArduinoAnalogIO:
    """测试 Arduino 模拟 I/O 功能"""

    def setup_method(self):
        """设置测试环境"""
        self.board = Arduino(port="/dev/ttyUSB0", auto_connect=False)
        self.mock_conn = MagicMock()
        self.board._conn = self.mock_conn
        self.mock_conn.is_connected.return_value = True

    def test_analog_read(self):
        """测试 analogRead"""
        self.mock_conn.send_command_retry.return_value = "OK2048"

        value = self.board.analogRead(34)

        assert value == 2048
        call_args = self.mock_conn.send_command_retry.call_args[0][0]
        assert "A34" in call_args

    def test_analog_write(self):
        """测试 analogWrite (PWM)"""
        self.mock_conn.send_command_retry.return_value = "OK"

        self.board.analogWrite(25, 128)

        call_args = self.mock_conn.send_command_retry.call_args[0][0]
        assert "P25128" in call_args


class TestArduinoAdvancedFunctions:
    """测试 Arduino 高级功能"""

    def setup_method(self):
        """设置测试环境"""
        self.board = Arduino(port="/dev/ttyUSB0", auto_connect=False)
        self.mock_conn = MagicMock()
        self.board._conn = self.mock_conn
        self.mock_conn.is_connected.return_value = True

    def test_tone(self):
        """测试 tone"""
        self.mock_conn.send_command_retry.return_value = "OK"

        self.board.tone(26, 440)

        call_args = self.mock_conn.send_command_retry.call_args[0][0]
        assert "T26" in call_args
        assert "440" in call_args

    def test_no_tone(self):
        """测试 noTone"""
        self.mock_conn.send_command_retry.return_value = "OK"

        self.board.noTone(26)

        call_args = self.mock_conn.send_command_retry.call_args[0][0]
        assert "N26" in call_args

    def test_pulse_in(self):
        """测试 pulseIn"""
        self.mock_conn.send_command_retry.return_value = "OK1500"

        duration = self.board.pulseIn(15, HIGH)

        assert duration == 1500
        call_args = self.mock_conn.send_command_retry.call_args[0][0]
        assert "U15" in call_args

    def test_attach_interrupt(self):
        """测试 attachInterrupt"""
        self.mock_conn.send_command_retry.return_value = "OK"

        callback = Mock()
        self.board.attachInterrupt(27, callback, RISING)

        assert 27 in self.board._interrupt_callbacks
        call_args = self.mock_conn.send_command_retry.call_args[0][0]
        assert "I27" in call_args

    def test_detach_interrupt(self):
        """测试 detachInterrupt"""
        self.mock_conn.send_command_retry.return_value = "OK"

        # 先绑定
        callback = Mock()
        self.board._interrupt_callbacks[27] = callback

        # 然后解除
        self.board.detachInterrupt(27)

        assert 27 not in self.board._interrupt_callbacks
        call_args = self.mock_conn.send_command_retry.call_args[0][0]
        assert "D27" in call_args

    def test_millis(self):
        """测试 millis"""
        self.mock_conn.send_command_retry.return_value = "OK12345"

        ms = self.board.millis()

        assert ms == 12345
        call_args = self.mock_conn.send_command_retry.call_args[0][0]
        assert "Q" in call_args


class TestArduinoTimeFunctions:
    """测试 Arduino 时间函数"""

    def test_delay(self):
        """测试 delay"""
        board = Arduino(port="/dev/ttyUSB0", auto_connect=False)

        import time
        start = time.time()
        board.delay(100)  # 100ms
        end = time.time()

        # 允许一定误差
        assert 0.08 < (end - start) < 0.15

    def test_delay_microseconds(self):
        """测试 delayMicroseconds"""
        board = Arduino(port="/dev/ttyUSB0", auto_connect=False)

        import time
        start = time.time()
        board.delayMicroseconds(10000)  # 10ms
        end = time.time()

        # 允许一定误差
        assert 0.008 < (end - start) < 0.02


class TestArduinoErrorHandling:
    """测试 Arduino 错误处理"""

    def setup_method(self):
        """设置测试环境"""
        self.board = Arduino(port="/dev/ttyUSB0", auto_connect=False)

    def test_command_when_not_connected(self):
        """测试未连接时发送命令"""
        with pytest.raises(ArduinoError):
            self.board.digitalWrite(13, HIGH)

    def test_command_error_response(self):
        """测试命令返回错误"""
        mock_conn = MagicMock()
        self.board._conn = mock_conn
        mock_conn.is_connected.return_value = True
        mock_conn.send_command_retry.return_value = "ER"

        with pytest.raises(ArduinoError):
            self.board.digitalWrite(13, HIGH)


class TestArduinoContextManager:
    """测试 Arduino 上下文管理器"""

    @patch('aitoolkit_esp32.arduino.SerialConnection')
    def test_context_manager(self, mock_serial):
        """测试 with 语句"""
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn
        mock_conn.is_connected.return_value = True
        mock_conn.send_command.return_value = "OK"
        mock_conn.send_command_retry.return_value = "OK"

        with Arduino(port="/dev/ttyUSB0") as board:
            assert board.is_connected()
            board.digitalWrite(13, HIGH)

        mock_conn.disconnect.assert_called()


class TestArduinoAutoMethod:
    """测试 Arduino.auto() 方法"""

    @patch('aitoolkit_esp32.arduino.find_esp32_device')
    @patch('aitoolkit_esp32.arduino.SerialConnection')
    def test_auto_method(self, mock_serial, mock_find):
        """测试 auto() 类方法"""
        mock_find.return_value = "/dev/ttyUSB0"
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn
        mock_conn.is_connected.return_value = True
        mock_conn.send_command.return_value = "OK"

        board = Arduino.auto()

        assert board.port == "/dev/ttyUSB0"
        assert board.baudrate == 115200


class TestArduinoRepr:
    """测试 Arduino 字符串表示"""

    def test_repr_disconnected(self):
        """测试未连接时的字符串表示"""
        board = Arduino(port="/dev/ttyUSB0", auto_connect=False)

        repr_str = repr(board)

        assert "/dev/ttyUSB0" in repr_str
        assert "disconnected" in repr_str

    @patch('aitoolkit_esp32.arduino.SerialConnection')
    def test_repr_connected(self, mock_serial):
        """测试已连接时的字符串表示"""
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn
        mock_conn.is_connected.return_value = True
        mock_conn.send_command.return_value = "OK"

        board = Arduino(port="/dev/ttyUSB0", auto_connect=True)

        repr_str = repr(board)

        assert "/dev/ttyUSB0" in repr_str
        assert "connected" in repr_str


class TestArduinoSerialPort:
    """测试 Arduino Serial 端口功能"""

    def setup_method(self):
        """设置测试环境"""
        self.board = Arduino(port="/dev/ttyUSB0", auto_connect=False)
        self.mock_conn = MagicMock()
        self.board._conn = self.mock_conn
        self.mock_conn.is_connected.return_value = True

    def test_serial_begin(self):
        """测试 Serial.begin"""
        self.mock_conn.send_command_retry.return_value = "OK"

        self.board.Serial.begin(9600)

        call_args = self.mock_conn.send_command_retry.call_args[0][0]
        assert "S1" in call_args
        assert "9600" in call_args

    def test_serial_write(self):
        """测试 Serial.write"""
        self.mock_conn.send_command_retry.return_value = "OK"

        self.board.Serial.write("Hello")

        call_args = self.mock_conn.send_command_retry.call_args[0][0]
        assert "X1Hello" in call_args

    def test_serial_println(self):
        """测试 Serial.println"""
        self.mock_conn.send_command_retry.return_value = "OK"

        self.board.Serial.println("Hello")

        call_args = self.mock_conn.send_command_retry.call_args[0][0]
        assert "X1Hello\n" in call_args

    def test_serial_read(self):
        """测试 Serial.read"""
        self.mock_conn.send_command_retry.return_value = "OKData"

        data = self.board.Serial.read()

        assert data == "Data"
        call_args = self.mock_conn.send_command_retry.call_args[0][0]
        assert "Y1" in call_args
