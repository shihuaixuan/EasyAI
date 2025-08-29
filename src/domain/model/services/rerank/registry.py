"""Rerank注册装饰器和注册表"""
from typing import Dict, Type, Optional
from .base import BaseRerank, RerankConfig


class RerankRegistry:
    """Rerank注册表"""
    _reranks: Dict[str, Type[BaseRerank]] = {}
    _configs: Dict[str, Type[RerankConfig]] = {}
    
    @classmethod
    def register(cls, name: str, rerank_class: Type[BaseRerank], config_class: Type[RerankConfig]) -> None:
        """注册rerank
        
        Args:
            name: rerank名称
            rerank_class: rerank类
            config_class: 配置类
        """
        cls._reranks[name] = rerank_class
        cls._configs[name] = config_class
    
    @classmethod
    def get_rerank_class(cls, name: str) -> Optional[Type[BaseRerank]]:
        """获取rerank类
        
        Args:
            name: rerank名称
            
        Returns:
            rerank类或None
        """
        return cls._reranks.get(name)
    
    @classmethod
    def get_config_class(cls, name: str) -> Optional[Type[RerankConfig]]:
        """获取配置类
        
        Args:
            name: rerank名称
            
        Returns:
            配置类或None
        """
        return cls._configs.get(name)
    
    @classmethod
    def list_reranks(cls) -> Dict[str, Type[BaseRerank]]:
        """列出所有注册的rerank
        
        Returns:
            rerank名称到rerank类的映射
        """
        return cls._reranks.copy()
    
    @classmethod
    def clear(cls) -> None:
        """清空注册表（主要用于测试）"""
        cls._reranks.clear()
        cls._configs.clear()


def register_rerank(name: str, config_class: Type[RerankConfig]):
    """Rerank注册装饰器
    
    Args:
        name: rerank名称
        config_class: 配置类
        
    Returns:
        装饰器函数
    """
    def decorator(rerank_class: Type[BaseRerank]) -> Type[BaseRerank]:
        RerankRegistry.register(name, rerank_class, config_class)
        return rerank_class
    return decorator