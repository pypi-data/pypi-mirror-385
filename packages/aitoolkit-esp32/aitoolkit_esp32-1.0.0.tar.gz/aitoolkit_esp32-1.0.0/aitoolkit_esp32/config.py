"""
配置管理模块
"""

import json
import os
from pathlib import Path
from typing import Dict, Any

# 默认配置
DEFAULT_CONFIG = {
    "serial": {
        "baudrate": 115200,
        "timeout": 2.0,
        "write_timeout": 1.0,
    },
    "device": {
        "auto_detect": True,
        "preferred_ports": ["/dev/ttyUSB0", "/dev/ttyACM0", "COM3"],
    },
    "protocol": {
        "response_timeout": 1.0,
        "max_retries": 3,
        "command_delay": 0.01,
    },
    "logging": {
        "level": "INFO",
        "enable_protocol_log": False,
    }
}

# 全局配置
_config = DEFAULT_CONFIG.copy()

# 配置文件路径
CONFIG_DIR = Path.home() / ".aitoolkit_esp32"
CONFIG_FILE = CONFIG_DIR / "config.json"


def get_config(key: str = None) -> Any:
    """
    获取配置项

    Args:
        key: 配置键，支持点号分隔的路径，如 "serial.baudrate"
             如果为 None，返回整个配置字典

    Returns:
        配置值
    """
    if key is None:
        return _config.copy()

    keys = key.split('.')
    value = _config
    for k in keys:
        if isinstance(value, dict):
            value = value.get(k)
        else:
            return None
    return value


def set_config(key: str, value: Any) -> None:
    """
    设置配置项

    Args:
        key: 配置键，支持点号分隔的路径
        value: 配置值
    """
    keys = key.split('.')
    config = _config

    for k in keys[:-1]:
        if k not in config:
            config[k] = {}
        config = config[k]

    config[keys[-1]] = value


def load_config(file_path: str = None) -> Dict[str, Any]:
    """
    从文件加载配置

    Args:
        file_path: 配置文件路径，默认使用 ~/.aitoolkit_esp32/config.json

    Returns:
        加载的配置字典
    """
    global _config

    if file_path is None:
        file_path = CONFIG_FILE

    file_path = Path(file_path)

    if not file_path.exists():
        return _config.copy()

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            loaded_config = json.load(f)

        # 深度合并配置
        _deep_merge(_config, loaded_config)

        return _config.copy()
    except Exception as e:
        import logging
        logging.warning(f"Failed to load config from {file_path}: {e}")
        return _config.copy()


def save_config(file_path: str = None) -> bool:
    """
    保存配置到文件

    Args:
        file_path: 配置文件路径，默认使用 ~/.aitoolkit_esp32/config.json

    Returns:
        是否成功保存
    """
    if file_path is None:
        file_path = CONFIG_FILE

    file_path = Path(file_path)

    # 创建目录
    file_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(_config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        import logging
        logging.error(f"Failed to save config to {file_path}: {e}")
        return False


def reset_config() -> None:
    """重置配置为默认值"""
    global _config
    _config = DEFAULT_CONFIG.copy()


def _deep_merge(base: Dict, update: Dict) -> None:
    """深度合并字典"""
    for key, value in update.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value


# 启动时尝试加载配置
try:
    load_config()
except Exception:
    pass
