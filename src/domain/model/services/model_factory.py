"""简化的模型工厂类"""

from typing import Dict, Type, Optional, Union
from .registry import ModelRegistry
from .config.models import ModelConfigFactory


class ModelFactory:
    """模型工厂类，支持自动注册的模型管理"""
    

    
    @classmethod
    def get_model_by_name(cls, name: str) -> Optional[Type]:
        """通过名称获取模型类
        
        Args:
            name: 模型名称
            
        Returns:
            模型类或None
        """
        return ModelRegistry.get_model_class(name)
    
    @classmethod
    def create_model(cls, name: str, **config_kwargs):
        """通过名称创建模型实例（自动处理配置）
        
        Args:
            name: 模型名称
            **config_kwargs: 配置参数
            
        Returns:
            模型实例
            
        Raises:
            ValueError: 模型未找到或配置创建失败
        """
        # 获取模型类
        model_class = cls.get_model_by_name(name)
        if model_class is None:
            raise ValueError(f"模型 '{name}' 未找到")
        
        # 获取模型提供商
        provider = ModelRegistry.get_provider(name)
        if provider is None:
            raise ValueError(f"模型 '{name}' 的提供商信息未找到")
        
        # 创建配置
        config = ModelConfigFactory.create_config(provider, **config_kwargs)
        return model_class(config)
    
    @classmethod
    def list_available_models(cls) -> list[str]:
        """列出所有可用模型
        
        Returns:
            模型名称列表
        """
        return list(ModelRegistry.list_models().keys())


# 全局模型工厂实例
_model_factory = ModelFactory()


def get_model_factory() -> ModelFactory:
    """获取模型工厂单例"""
    return _model_factory