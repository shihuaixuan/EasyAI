"""模型注册装饰器和注册表"""
from typing import Dict, Type, Optional
from .base import BaseLLM
from .config.base import ModelProvider


class ModelRegistry:
    """模型注册表"""
    _models: Dict[str, Type[BaseLLM]] = {}
    _providers: Dict[str, ModelProvider] = {}
    
    @classmethod
    def register(cls, name: str, model_class: Type[BaseLLM], provider: ModelProvider) -> None:
        """注册模型
        
        Args:
            name: 模型名称
            model_class: 模型类
            provider: 模型提供商
        """
        cls._models[name] = model_class
        cls._providers[name] = provider
    
    @classmethod
    def get_model_class(cls, name: str) -> Optional[Type[BaseLLM]]:
        """获取模型类
        
        Args:
            name: 模型名称
            
        Returns:
            模型类或None
        """
        return cls._models.get(name)
    
    @classmethod
    def get_provider(cls, name: str) -> Optional[ModelProvider]:
        """获取模型提供商
        
        Args:
            name: 模型名称
            
        Returns:
            模型提供商或None
        """
        return cls._providers.get(name)
    
    @classmethod
    def list_models(cls) -> Dict[str, Type[BaseLLM]]:
        """列出所有注册的模型
        
        Returns:
            模型名称到模型类的映射
        """
        return cls._models.copy()
    
    @classmethod
    def clear(cls) -> None:
        """清空注册表（主要用于测试）"""
        cls._models.clear()
        cls._providers.clear()


def register_model(name: str, provider: ModelProvider):
    """模型注册装饰器
    
    Args:
        name: 模型名称
        provider: 模型提供商
        
    Returns:
        装饰器函数
    """
    def decorator(model_class: Type[BaseLLM]) -> Type[BaseLLM]:
        ModelRegistry.register(name, model_class, provider)
        return model_class
    return decorator