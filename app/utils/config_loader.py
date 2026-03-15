import os
import re
import yaml
from pathlib import Path
from typing import Any, Dict, Optional


class ConfigLoader:
    """YAML配置文件加载器，支持环境变量替换"""

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置加载器

        Args:
            config_path: 配置文件路径，默认为项目根目录的 config.yaml
        """
        if config_path is None:
            # 获取项目根目录（app目录的上级目录的上级目录）
            root_dir = Path(__file__).parent.parent.parent
            config_path = root_dir / "config.yaml"

        self.config_path = Path(config_path)
        self._config_data: Optional[Dict[str, Any]] = None

    def _substitute_env_vars(self, text: str) -> str:
        """
        替换文本中的环境变量
        支持格式：${VAR_NAME:默认值}

        Args:
            text: 包含环境变量的文本

        Returns:
            替换后的文本
        """
        # 匹配 ${VAR_NAME:默认值} 格式
        pattern = r'\$\{([^}]+)\}'

        def replace_match(match):
            var_expression = match.group(1)

            # 检查是否有默认值 (VAR_NAME:default_value)
            if ':' in var_expression:
                var_name, default_value = var_expression.split(':', 1)
            else:
                var_name = var_expression
                default_value = ''

            # 返回环境变量值或默认值
            return os.getenv(var_name.strip(), default_value)

        return re.sub(pattern, replace_match, text)

    def _process_config_data(self, data: Any) -> Any:
        """
        递归处理配置数据，替换其中的环境变量

        Args:
            data: 配置数据（任意类型）

        Returns:
            处理后的配置数据
        """
        if isinstance(data, str):
            return self._substitute_env_vars(data)
        elif isinstance(data, dict):
            return {key: self._process_config_data(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._process_config_data(item) for item in data]
        else:
            return data

    def load_config(self) -> Dict[str, Any]:
        """
        加载配置文件

        Returns:
            配置数据字典

        Raises:
            FileNotFoundError: 配置文件不存在
            yaml.YAMLError: YAML格式错误
        """
        if self._config_data is not None:
            return self._config_data

        if not self.config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                raw_data = yaml.safe_load(f)

            # 处理环境变量替换
            self._config_data = self._process_config_data(raw_data) if raw_data else {}

            return self._config_data

        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"配置文件格式错误: {e}")
        except Exception as e:
            raise Exception(f"加载配置文件失败: {e}")

    def get_section(self, section_name: str) -> Dict[str, Any]:
        """
        获取配置文件的指定部分

        Args:
            section_name: 配置节名称

        Returns:
            配置节数据
        """
        config = self.load_config()
        return config.get(section_name, {})

    def get_value(self, key_path: str, default: Any = None) -> Any:
        """
        根据键路径获取配置值

        Args:
            key_path: 键路径，如 'app.server.port'
            default: 默认值

        Returns:
            配置值
        """
        config = self.load_config()

        # 分割键路径
        keys = key_path.split('.')
        value = config

        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    def reload(self) -> Dict[str, Any]:
        """
        重新加载配置文件

        Returns:
            重新加载的配置数据
        """
        self._config_data = None
        return self.load_config()


# 全局配置加载器实例
_config_loader = ConfigLoader()


def get_config() -> Dict[str, Any]:
    """获取完整配置"""
    return _config_loader.load_config()


def get_section(section_name: str) -> Dict[str, Any]:
    """获取配置节"""
    return _config_loader.get_section(section_name)


def get_value(key_path: str, default: Any = None) -> Any:
    """获取配置值"""
    return _config_loader.get_value(key_path, default)
