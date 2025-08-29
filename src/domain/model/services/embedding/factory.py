from typing import Dict, Any, Optional, Union
from .base import BaseEmbedding, EmbeddingConfig
from .registry import EmbeddingRegistry


class EmbeddingFactory:
    """Embedding工厂类"""
    
    @staticmethod
    def create_embedding(provider: str, 
                        config: Optional[Union[EmbeddingConfig, Dict[str, Any]]] = None,
                        **kwargs) -> BaseEmbedding:
        """创建embedding实例
        
        Args:
            provider: 提供商名称（如 'siliconflow'）
            config: 配置对象或配置字典
            **kwargs: 额外的配置参数
            
        Returns:
            Embedding实例
            
        Raises:
            ValueError: 当提供商未注册或配置无效时
        """
        # 检查提供商是否已注册
        if provider not in EmbeddingRegistry.list_embeddings():
            available = list(EmbeddingRegistry.list_embeddings().keys())
            raise ValueError(
                f"Provider '{provider}' is not registered. "
                f"Available providers: {available}"
            )
        
        # 获取实现类和配置类
        embedding_class = EmbeddingRegistry.get_embedding_class(provider)
        config_class = EmbeddingRegistry.get_config_class(provider)
        
        if embedding_class is None or config_class is None:
            raise ValueError(f"Failed to get classes for provider '{provider}'")
        
        # 处理配置
        if config is None:
            # 使用默认配置和kwargs
            final_config = config_class(**kwargs)
        elif isinstance(config, dict):
            # 合并字典配置和kwargs
            merged_config = {**config, **kwargs}
            final_config = config_class(**merged_config)
        elif isinstance(config, EmbeddingConfig):
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
        
        # 创建embedding实例
        return embedding_class(final_config)
    
    @staticmethod
    def create_config(provider: str, **kwargs) -> EmbeddingConfig:
        """创建配置对象
        
        Args:
            provider: 提供商名称
            **kwargs: 配置参数
            
        Returns:
            配置对象
            
        Raises:
            ValueError: 当提供商未注册时
        """
        if provider not in EmbeddingRegistry.list_embeddings():
            available = list(EmbeddingRegistry.list_embeddings().keys())
            raise ValueError(
                f"Provider '{provider}' is not registered. "
                f"Available providers: {available}"
            )
        
        config_class = EmbeddingRegistry.get_config_class(provider)
        if config_class is None:
            raise ValueError(f"Failed to get config class for provider '{provider}'")
        
        return config_class(**kwargs)
    
    @staticmethod
    def list_providers() -> list[str]:
        """列出所有可用的提供商
        
        Returns:
            提供商名称列表
        """
        return list(EmbeddingRegistry.list_embeddings().keys())
    
    @staticmethod
    def is_provider_available(provider: str) -> bool:
        """检查提供商是否可用
        
        Args:
            provider: 提供商名称
            
        Returns:
            是否可用
        """
        return provider in EmbeddingRegistry.list_embeddings()


# 便捷函数
def create_embedding(provider: str, 
                    config: Optional[Union[EmbeddingConfig, Dict[str, Any]]] = None,
                    **kwargs) -> BaseEmbedding:
    """创建embedding实例的便捷函数
    
    Args:
        provider: 提供商名称（如 'siliconflow'）
        config: 配置对象或配置字典
        **kwargs: 额外的配置参数
        
    Returns:
        Embedding实例
    """
    return EmbeddingFactory.create_embedding(provider, config, **kwargs)


def create_config(provider: str, **kwargs) -> EmbeddingConfig:
    """创建配置对象的便捷函数
    
    Args:
        provider: 提供商名称
        **kwargs: 配置参数
        
    Returns:
        配置对象
    """
    return EmbeddingFactory.create_config(provider, **kwargs)


def list_providers() -> list[str]:
    """列出所有可用提供商的便捷函数
    
    Returns:
        提供商名称列表
    """
    return EmbeddingFactory.list_providers()