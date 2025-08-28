"""配置类注册装饰器和注册表"""
from typing import Dict, Type, Optional
from .base import BaseModelConfig, ModelProvider


class ConfigRegistry:
    """配置类注册表"""
    _configs: Dict[ModelProvider, Type[BaseModelConfig]] = {}
    
    @classmethod
    def register(cls, provider: ModelProvider, config_class: Type[BaseModelConfig]) -> None:
        """注册配置类
        
        Args:
            provider: 模型提供商
            config_class: 配置类
        """
        cls._configs[provider] = config_class
    
    @classmethod
    def get_config_class(cls, provider: ModelProvider) -> Optional[Type[BaseModelConfig]]:
        """获取配置类
        
        Args:
            provider: 模型提供商
            
        Returns:
            配置类或None
        """
        return cls._configs.get(provider)
    
    @classmethod
    def list_configs(cls) -> Dict[ModelProvider, Type[BaseModelConfig]]:
        """列出所有注册的配置类
        
        Returns:
            提供商到配置类的映射
        """
        return cls._configs.copy()
    
    @classmethod
    def clear(cls) -> None:
        """清空注册表（主要用于测试）"""
        cls._configs.clear()


def register_config(provider: ModelProvider):
    """配置类注册装饰器
    
    Args:
        provider: 模型提供商
        
    Returns:
        装饰器函数
    """
    def decorator(config_class: Type[BaseModelConfig]) -> Type[BaseModelConfig]:
        ConfigRegistry.register(provider, config_class)
        return config_class
    return decorator