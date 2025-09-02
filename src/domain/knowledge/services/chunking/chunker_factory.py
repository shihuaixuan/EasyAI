"""
分块器工厂 - 管理和创建不同的分块策略
"""

from typing import Dict, Type, Optional
from .base_chunker import BaseChunker
from .general_chunker import GeneralChunker
from ...vo.chunking_config import ChunkingConfig


class ChunkerFactory:
    """分块器工厂类"""
    
    def __init__(self):
        self._chunkers: Dict[str, Type[BaseChunker]] = {}
        self._register_default_chunkers()
    
    def _register_default_chunkers(self):
        """注册默认的分块器"""
        self.register("general", GeneralChunker)
    
    def register(self, strategy_name: str, chunker_class: Type[BaseChunker]):
        """
        注册分块器
        
        Args:
            strategy_name: 策略名称
            chunker_class: 分块器类
        """
        self._chunkers[strategy_name] = chunker_class
    
    def create_chunker(self, strategy_name: str) -> Optional[BaseChunker]:
        """
        创建分块器实例
        
        Args:
            strategy_name: 策略名称
            
        Returns:
            分块器实例，如果策略不存在则返回None
        """
        chunker_class = self._chunkers.get(strategy_name)
        if not chunker_class:
            return None
        
        return chunker_class()
    
    def get_available_strategies(self) -> list[str]:
        """
        获取所有可用的分块策略
        
        Returns:
            策略名称列表
        """
        return list(self._chunkers.keys())
    
    def is_strategy_supported(self, strategy_name: str) -> bool:
        """
        检查策略是否支持
        
        Args:
            strategy_name: 策略名称
            
        Returns:
            True如果支持，False如果不支持
        """
        return strategy_name in self._chunkers


# 全局分块器工厂实例
chunker_factory = ChunkerFactory()