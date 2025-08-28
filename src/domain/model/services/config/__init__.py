"""配置模块初始化

导入所有配置类以触发自动注册
"""

# 导入配置类以触发自动注册
from .models import OpenAIConfig, DeepSeekConfig

# 导出核心接口
from .base import BaseModelConfig, ModelProvider
from .models import ModelConfigFactory
from .registry import ConfigRegistry, register_config

__all__ = [
    'BaseModelConfig',
    'ModelProvider', 
    'ModelConfigFactory',
    'ConfigRegistry',
    'register_config',
    'OpenAIConfig',
    'DeepSeekConfig'
]