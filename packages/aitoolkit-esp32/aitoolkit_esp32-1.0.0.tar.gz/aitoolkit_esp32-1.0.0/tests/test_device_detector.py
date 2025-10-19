"""
测试 device_detector 模块 - 设备检测功能
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from aitoolkit_esp32.device_detector import (
    list_serial_ports,
    is_esp32_device,
    list_esp32_devices,
    find_esp32_device,
    get_device_info,
    validate_port,
    ESP32_USB_IDS
)


class MockPortInfo:
    """模拟串口信息"""
    def __init__(self, device, description="", hwid="", vid=None, pid=None,
                 serial_number=None, manufacturer=None, product=None):
        self.device = device
        self.description = description
        self.hwid = hwid
        self.vid = vid
        self.pid = pid
        self.serial_number = serial_number
        self.manufacturer = manufacturer
        self.product = product


class TestListSerialPorts:
    """测试串口列表功能"""

    @patch('serial.tools.list_ports.comports')
    def test_list_serial_ports_empty(self, mock_comports):
        """测试空串口列表"""
        mock_comports.return_value = []
        ports = list_serial_ports()
        assert ports == []

    @patch('serial.tools.list_ports.comports')
    def test_list_serial_ports_single(self, mock_comports):
        """测试单个串口设备"""
        mock_port = MockPortInfo(
            device="/dev/ttyUSB0",
            description="USB Serial Port",
            hwid="USB VID:PID=10C4:EA60",
            vid=0x10C4,
            pid=0xEA60
        )
        mock_comports.return_value = [mock_port]

        ports = list_serial_ports()

        assert len(ports) == 1
        assert ports[0]['port'] == "/dev/ttyUSB0"
        assert ports[0]['description'] == "USB Serial Port"
        assert ports[0]['vid'] == 0x10C4
        assert ports[0]['pid'] == 0xEA60

    @patch('serial.tools.list_ports.comports')
    def test_list_serial_ports_multiple(self, mock_comports):
        """测试多个串口设备"""
        mock_ports = [
            MockPortInfo(device="/dev/ttyUSB0", description="CP2102"),
            MockPortInfo(device="/dev/ttyUSB1", description="CH340"),
        ]
        mock_comports.return_value = mock_ports

        ports = list_serial_ports()

        assert len(ports) == 2
        assert ports[0]['port'] == "/dev/ttyUSB0"
        assert ports[1]['port'] == "/dev/ttyUSB1"


class TestIsESP32Device:
    """测试 ESP32 设备识别"""

    def test_is_esp32_device_by_vid_pid_cp2102(self):
        """测试通过 VID:PID 识别 CP2102"""
        port_info = {
            'port': '/dev/ttyUSB0',
            'description': 'USB Serial',
            'hwid': '',
            'vid': 0x10C4,
            'pid': 0xEA60,
            'serial_number': None,
            'manufacturer': None,
            'product': None,
        }
        assert is_esp32_device(port_info) is True

    def test_is_esp32_device_by_vid_pid_ch340(self):
        """测试通过 VID:PID 识别 CH340"""
        port_info = {
            'port': '/dev/ttyUSB0',
            'description': 'USB Serial',
            'hwid': '',
            'vid': 0x1A86,
            'pid': 0x7523,
            'serial_number': None,
            'manufacturer': None,
            'product': None,
        }
        assert is_esp32_device(port_info) is True

    def test_is_esp32_device_by_description(self):
        """测试通过描述识别 ESP32"""
        port_info = {
            'port': '/dev/ttyUSB0',
            'description': 'CP2102 USB to UART Bridge',
            'hwid': '',
            'vid': None,
            'pid': None,
            'serial_number': None,
            'manufacturer': None,
            'product': None,
        }
        assert is_esp32_device(port_info) is True

    def test_is_esp32_device_by_hwid(self):
        """测试通过硬件 ID 识别 ESP32"""
        port_info = {
            'port': '/dev/ttyUSB0',
            'description': '',
            'hwid': 'USB VID:PID=10C4:EA60 SER=0001 LOCATION=1-1.4',
            'vid': 0x10C4,  # 即使 hwid 包含 VID:PID，通常也会解析到这些字段
            'pid': 0xEA60,
            'serial_number': None,
            'manufacturer': None,
            'product': None,
        }
        assert is_esp32_device(port_info) is True

    def test_is_not_esp32_device(self):
        """测试非 ESP32 设备"""
        port_info = {
            'port': '/dev/ttyS0',
            'description': 'Built-in Serial Port',
            'hwid': 'PNP0501',
            'vid': None,
            'pid': None,
            'serial_number': None,
            'manufacturer': None,
            'product': None,
        }
        assert is_esp32_device(port_info) is False

    def test_is_esp32_device_case_insensitive(self):
        """测试关键字匹配不区分大小写"""
        port_info = {
            'port': '/dev/ttyUSB0',
            'description': 'ch340 usb serial',
            'hwid': '',
            'vid': None,
            'pid': None,
            'serial_number': None,
            'manufacturer': None,
            'product': None,
        }
        assert is_esp32_device(port_info) is True


class TestListESP32Devices:
    """测试 ESP32 设备列表"""

    @patch('aitoolkit_esp32.device_detector.list_serial_ports')
    def test_list_esp32_devices_found(self, mock_list_ports):
        """测试找到 ESP32 设备"""
        mock_list_ports.return_value = [
            {
                'port': '/dev/ttyUSB0',
                'description': 'CP2102 USB to UART',
                'hwid': '',
                'vid': 0x10C4,
                'pid': 0xEA60,
                'serial_number': None,
                'manufacturer': None,
                'product': None,
            },
            {
                'port': '/dev/ttyS0',
                'description': 'Built-in',
                'hwid': '',
                'vid': None,
                'pid': None,
                'serial_number': None,
                'manufacturer': None,
                'product': None,
            }
        ]

        devices = list_esp32_devices()

        assert len(devices) == 1
        assert devices[0]['port'] == '/dev/ttyUSB0'

    @patch('aitoolkit_esp32.device_detector.list_serial_ports')
    def test_list_esp32_devices_not_found(self, mock_list_ports):
        """测试未找到 ESP32 设备"""
        mock_list_ports.return_value = [
            {
                'port': '/dev/ttyS0',
                'description': 'Built-in',
                'hwid': '',
                'vid': None,
                'pid': None,
                'serial_number': None,
                'manufacturer': None,
                'product': None,
            }
        ]

        devices = list_esp32_devices()

        assert len(devices) == 0


class TestFindESP32Device:
    """测试自动查找 ESP32 设备"""

    @patch('aitoolkit_esp32.device_detector.list_esp32_devices')
    @patch('aitoolkit_esp32.device_detector.get_config')
    @patch('aitoolkit_esp32.device_detector.list_serial_ports')
    def test_find_esp32_device_success(self, mock_list_ports, mock_config, mock_list_esp32):
        """测试成功找到 ESP32 设备"""
        mock_config.return_value = []
        mock_list_ports.return_value = []
        mock_list_esp32.return_value = [
            {
                'port': '/dev/ttyUSB0',
                'description': 'CP2102',
                'vid': 0x10C4,
                'pid': 0xEA60,
            }
        ]

        port = find_esp32_device()

        assert port == '/dev/ttyUSB0'

    @patch('aitoolkit_esp32.device_detector.list_esp32_devices')
    @patch('aitoolkit_esp32.device_detector.get_config')
    @patch('aitoolkit_esp32.device_detector.list_serial_ports')
    def test_find_esp32_device_not_found(self, mock_list_ports, mock_config, mock_list_esp32):
        """测试未找到 ESP32 设备"""
        mock_config.return_value = []
        mock_list_ports.return_value = []
        mock_list_esp32.return_value = []

        port = find_esp32_device()

        assert port is None

    @patch('aitoolkit_esp32.device_detector.list_serial_ports')
    @patch('aitoolkit_esp32.device_detector.get_config')
    def test_find_esp32_device_preferred_port(self, mock_config, mock_list_ports):
        """测试使用优先端口"""
        mock_config.return_value = ['/dev/ttyUSB0']
        mock_list_ports.return_value = [
            {
                'port': '/dev/ttyUSB0',
                'description': 'CP2102',
                'vid': 0x10C4,
                'pid': 0xEA60,
            }
        ]

        port = find_esp32_device()

        assert port == '/dev/ttyUSB0'

    @patch('aitoolkit_esp32.device_detector.list_esp32_devices')
    @patch('aitoolkit_esp32.device_detector.list_serial_ports')
    def test_find_esp32_device_with_custom_preferred(self, mock_list_ports, mock_list_esp32):
        """测试使用自定义优先端口列表"""
        mock_list_ports.return_value = [
            {
                'port': '/dev/ttyUSB1',
                'description': 'CP2102',
            }
        ]
        mock_list_esp32.return_value = []

        port = find_esp32_device(preferred_ports=['/dev/ttyUSB1'])

        assert port == '/dev/ttyUSB1'


class TestGetDeviceInfo:
    """测试获取设备信息"""

    @patch('aitoolkit_esp32.device_detector.list_serial_ports')
    def test_get_device_info_found(self, mock_list_ports):
        """测试获取存在的设备信息"""
        mock_list_ports.return_value = [
            {
                'port': '/dev/ttyUSB0',
                'description': 'CP2102',
                'vid': 0x10C4,
                'pid': 0xEA60,
            }
        ]

        info = get_device_info('/dev/ttyUSB0')

        assert info is not None
        assert info['port'] == '/dev/ttyUSB0'
        assert info['description'] == 'CP2102'

    @patch('aitoolkit_esp32.device_detector.list_serial_ports')
    def test_get_device_info_not_found(self, mock_list_ports):
        """测试获取不存在的设备信息"""
        mock_list_ports.return_value = [
            {
                'port': '/dev/ttyUSB0',
                'description': 'CP2102',
            }
        ]

        info = get_device_info('/dev/ttyUSB1')

        assert info is None


class TestValidatePort:
    """测试端口验证"""

    @patch('aitoolkit_esp32.device_detector.get_device_info')
    def test_validate_port_exists(self, mock_get_info):
        """测试验证存在的端口"""
        mock_get_info.return_value = {'port': '/dev/ttyUSB0'}

        result = validate_port('/dev/ttyUSB0')

        assert result is True

    @patch('aitoolkit_esp32.device_detector.get_device_info')
    def test_validate_port_not_exists(self, mock_get_info):
        """测试验证不存在的端口"""
        mock_get_info.return_value = None

        result = validate_port('/dev/ttyUSB99')

        assert result is False


class TestESP32USBIDs:
    """测试 ESP32 USB ID 列表"""

    def test_esp32_usb_ids_contains_cp2102(self):
        """测试列表包含 CP2102"""
        assert (0x10C4, 0xEA60) in ESP32_USB_IDS

    def test_esp32_usb_ids_contains_ch340(self):
        """测试列表包含 CH340"""
        assert (0x1A86, 0x7523) in ESP32_USB_IDS

    def test_esp32_usb_ids_contains_ftdi(self):
        """测试列表包含 FTDI"""
        assert (0x0403, 0x6001) in ESP32_USB_IDS

    def test_esp32_usb_ids_is_list(self):
        """测试 USB ID 列表类型"""
        assert isinstance(ESP32_USB_IDS, list)
        assert len(ESP32_USB_IDS) > 0
