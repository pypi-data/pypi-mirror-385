"""
Arduino 风格常量定义
"""

# 数字电平
HIGH = 1
LOW = 0

# 引脚模式
INPUT = 0
OUTPUT = 1
INPUT_PULLUP = 2
INPUT_PULLDOWN = 3

# 中断模式
RISING = 1
FALLING = 2
CHANGE = 3

# PWM 相关
PWM_MIN = 0
PWM_MAX = 255

# ADC 相关
ADC_MIN = 0
ADC_MAX = 4095

# 串口波特率常用值
BAUD_9600 = 9600
BAUD_19200 = 19200
BAUD_38400 = 38400
BAUD_57600 = 57600
BAUD_115200 = 115200

# ESP32-C3 SuperMini 特定引脚定义 (根据实际引脚布局)
LED_BUILTIN = 9  # ESP32-C3 SuperMini 内置LED在GPIO9

# ESP32-C3 SuperMini 可用引脚分组
PINS_3V3 = [32, 33]  # 3.3V电源组引脚
PINS_5V = [25, 26, 27]  # 5V电源组引脚
PINS_SPI = [18, 19, 23]  # SPI专用引脚 (首选)
PINS_OTHER = [13, 14, 16, 17, 21, 22]  # 其他5V组引脚

# ESP32-C3 SuperMini 所有可用GPIO引脚
ALL_PINS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19, 20, 21, 22, 23, 25, 26, 27, 32, 33]

# ESP32-C3 SuperMini ADC 可用引脚 (支持12位ADC，范围0-4095)
ADC_PINS = [0, 1, 2, 3, 4]  # ESP32-C3的ADC引脚

# ESP32-C3 SuperMini PWM 可用引脚 (所有GPIO都支持PWM)
PWM_PINS = ALL_PINS.copy()

# ESP32-C3 SuperMini I2C 引脚
I2C_SDA = 9   # GPIO9
I2C_SCL = 8   # GPIO8

# ESP32-C3 SuperMini SPI 引脚 (实际硬件布局)
SPI_MOSI = 23  # GPIO23 (SPI专用)
SPI_MISO = 19  # GPIO19 (SPI专用)
SPI_SCK = 18   # GPIO18 (SPI专用)
SPI_CS = 5     # GPIO5 (片选)

# ESP32-C3 SuperMini 串口引脚
UART_TX = 20  # GPIO20
UART_RX = 21  # GPIO21

# ESP32-C3 特殊功能引脚
BOOT_PIN = 0  # GPIO0，启动模式选择
TOUCH_PINS = []  # ESP32-C3 不支持触摸功能

# ESP32-C3 可用作输入的引脚
INPUT_PINS = ALL_PINS.copy()

# ESP32-C3 可用作输出的引脚
OUTPUT_PINS = ALL_PINS.copy()

# ESP32-C3 支持中断的引脚
INTERRUPT_PINS = ALL_PINS.copy()

# 协议命令常量（内部使用）
class Commands:
    """通信协议命令定义"""
    PIN_MODE = 'M'
    DIGITAL_WRITE = 'W'
    DIGITAL_READ = 'R'
    ANALOG_READ = 'A'
    ANALOG_WRITE = 'P'
    TONE = 'T'
    NO_TONE = 'N'
    PULSE_IN = 'U'
    ATTACH_INTERRUPT = 'I'
    DETACH_INTERRUPT = 'D'
    DELAY = 'L'
    MILLIS = 'Q'
    SERIAL_BEGIN = 'S'
    SERIAL_WRITE = 'X'
    SERIAL_READ = 'Y'
    PING = 'Z'

# 响应状态
class Status:
    """响应状态码"""
    OK = 'OK'
    ERROR = 'ER'
    TIMEOUT = 'TO'
    INVALID = 'IV'
