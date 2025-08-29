"""Embedding注册装饰器和注册表"""
from typing import Dict, Type, Optional
from .base import BaseEmbedding, EmbeddingConfig


class EmbeddingRegistry:
    """Embedding注册表"""
    _embeddings: Dict[str, Type[BaseEmbedding]] = {}
    _configs: Dict[str, Type[EmbeddingConfig]] = {}
    
    @classmethod
    def register(cls, name: str, embedding_class: Type[BaseEmbedding], config_class: Type[EmbeddingConfig]) -> None:
        """注册embedding
        
        Args:
            name: embedding名称
            embedding_class: embedding类
            config_class: 配置类
        """
        cls._embeddings[name] = embedding_class
        cls._configs[name] = config_class
    
    @classmethod
    def get_embedding_class(cls, name: str) -> Optional[Type[BaseEmbedding]]:
        """获取embedding类
        
        Args:
            name: embedding名称
            
        Returns:
            embedding类或None
        """
        return cls._embeddings.get(name)
    
    @classmethod
    def get_config_class(cls, name: str) -> Optional[Type[EmbeddingConfig]]:
        """获取配置类
        
        Args:
            name: embedding名称
            
        Returns:
            配置类或None
        """
        return cls._configs.get(name)
    
    @classmethod
    def list_embeddings(cls) -> Dict[str, Type[BaseEmbedding]]:
        """列出所有注册的embedding
        
        Returns:
            embedding名称到embedding类的映射
        """
        return cls._embeddings.copy()
    
    @classmethod
    def clear(cls) -> None:
        """清空注册表（主要用于测试）"""
        cls._embeddings.clear()
        cls._configs.clear()


def register_embedding(name: str, config_class: Type[EmbeddingConfig]):
    """Embedding注册装饰器
    
    Args:
        name: embedding名称
        config_class: 配置类
        
    Returns:
        装饰器函数
    """
    def decorator(embedding_class: Type[BaseEmbedding]) -> Type[BaseEmbedding]:
        EmbeddingRegistry.register(name, embedding_class, config_class)
        return embedding_class
    return decorator
