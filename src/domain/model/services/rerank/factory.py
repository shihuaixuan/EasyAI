from typing import Dict, Any, Optional, Union
import importlib
from .base import BaseRerank, RerankConfig
from .registry import RerankRegistry


class RerankFactory:
    """Rerank工厂类"""
    
    @staticmethod
    def create_rerank(provider: str, 
                     config: Optional[Union[RerankConfig, Dict[str, Any]]] = None,
                     **kwargs) -> BaseRerank:
        """创建rerank实例
        
        Args:
            provider: 提供商名称（如 'siliconflow'）
            config: 配置对象或配置字典
            **kwargs: 额外的配置参数
            
        Returns:
            Rerank实例
            
        Raises:
            ValueError: 当提供商未注册或配置无效时
        """
        
        # 检查提供商是否已注册
        if provider not in RerankRegistry.list_reranks():
            available = list(RerankRegistry.list_reranks().keys())
            raise ValueError(
                f"Provider '{provider}' is not registered. "
                f"Available providers: {available}"
            )
        
        # 获取实现类和配置类
        rerank_class = RerankRegistry.get_rerank_class(provider)
        config_class = RerankRegistry.get_config_class(provider)
        
        if rerank_class is None or config_class is None:
            raise ValueError(f"Failed to get classes for provider '{provider}'")
        
        # 处理配置
        if config is None:
            # 使用默认配置和kwargs
            final_config = config_class(**kwargs)
        elif isinstance(config, dict):
            # 合并字典配置和kwargs
            merged_config = {**config, **kwargs}
            final_config = config_class(**merged_config)
        elif isinstance(config, RerankConfig):
            # 直接使用配置对象，但检查类型
            if not isinstance(config, config_class):
                raise ValueError(
                    f"Config type mismatch. Expected {config_class.__name__}, "
                    f"got {type(config).__name__}"
                )
            final_config = config
        else:
            raise ValueError(
                f"Invalid config type. Expected dict, {config_class.__name__}, "
                f"or None, got {type(config).__name__}"
            )
        
        # 创建rerank实例
        return rerank_class(final_config)
    
    @staticmethod
    def create_config(provider: str, **kwargs) -> RerankConfig:
        """创建配置对象
        
        Args:
            provider: 提供商名称
            **kwargs: 配置参数
            
        Returns:
            配置对象
            
        Raises:
            ValueError: 当提供商未注册时
        """
        if provider not in RerankRegistry.list_reranks():
            available = list(RerankRegistry.list_reranks().keys())
            raise ValueError(
                f"Provider '{provider}' is not registered. "
                f"Available providers: {available}"
            )
        
        config_class = RerankRegistry.get_config_class(provider)
        if config_class is None:
            raise ValueError(f"Failed to get config class for provider '{provider}'")
        
        return config_class(**kwargs)
    
    @staticmethod
    def list_providers() -> list[str]:
        """列出所有可用的提供商
        
        Returns:
            提供商名称列表
        """
        return list(RerankRegistry.list_reranks().keys())
    
    @staticmethod
    def is_provider_available(provider: str) -> bool:
        """检查提供商是否可用
        
        Args:
            provider: 提供商名称
            
        Returns:
            是否可用
        """
        return provider in RerankRegistry.list_reranks()


# 便捷函数
def create_rerank(provider: str, 
                 config: Optional[Union[RerankConfig, Dict[str, Any]]] = None,
                 **kwargs) -> BaseRerank:
    """创建rerank实例的便捷函数
    
    Args:
        provider: 提供商名称（如 'siliconflow'）
        config: 配置对象或配置字典
        **kwargs: 额外的配置参数
        
    Returns:
        Rerank实例
    """
    return RerankFactory.create_rerank(provider, config, **kwargs)


def create_rerank_config(provider: str, **kwargs) -> RerankConfig:
    """创建配置对象的便捷函数
    
    Args:
        provider: 提供商名称
        **kwargs: 配置参数
        
    Returns:
        配置对象
    """
    return RerankFactory.create_config(provider, **kwargs)


def list_rerank_providers() -> list[str]:
    """列出所有可用提供商的便捷函数
    
    Returns:
        提供商名称列表
    """
    return RerankFactory.list_providers()


def is_rerank_provider_available(provider: str) -> bool:
    """检查提供商是否可用的便捷函数
    
    Args:
        provider: 提供商名称
        
    Returns:
        是否可用
    """
    return RerankFactory.is_provider_available(provider)