"""模型服务模块初始化

自动导入所有模型实现以触发注册装饰器
"""

# 导入模型实现以触发自动注册
from .impl.deepseek import DeepSeek

# 导出主要接口
from .model_factory import ModelFactory, get_model_factory
from .registry import ModelRegistry, register_model
from .base import BaseLLM

__all__ = [
    'ModelFactory',
    'get_model_factory', 
    'ModelRegistry',
    'register_model',
    'BaseLLM',
    'DeepSeek'
]