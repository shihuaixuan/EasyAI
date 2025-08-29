# -*- coding: utf-8 -*-
"""
Rerank服务基类模块

本模块定义了重排序服务的基础抽象类和配置类，为不同的重排序实现提供统一的接口。
重排序服务用于对检索到的文档进行重新排序，提高检索结果的相关性。
"""

from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Any, Dict, Protocol, runtime_checkable
from dataclasses import dataclass


class RerankConfig:
    """重排序配置基类
    
    所有重排序服务的配置都应该继承此类，提供基础的配置参数。
    """
    
    def __init__(self, 
                 model_name: str,
                 top_k: Optional[int] = None,
                 **kwargs):
        """初始化重排序配置
        
        Args:
            model_name: 模型名称
            top_k: 返回的top-k结果数量，None表示返回所有结果
            **kwargs: 其他配置参数
        """
        self.model_name = model_name
        self.top_k = top_k
        
        # 存储额外的配置参数
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """将配置转换为字典
        
        Returns:
            配置字典
        """
        return {
            'model_name': self.model_name,
            'top_k': self.top_k,
            **{k: v for k, v in self.__dict__.items() 
               if k not in ['model_name', 'top_k']}
        }
    
    def __repr__(self) -> str:
        """配置的字符串表示"""
        return f"{self.__class__.__name__}({self.to_dict()})"


@dataclass
class RerankResult:
    """重排序结果
    
    包含重排序后的文本和对应的相关性分数。
    """
    text: str
    score: float
    index: int  # 原始索引位置
    
    def __post_init__(self):
        """验证结果数据"""
        if not isinstance(self.text, str):
            raise ValueError("text必须是字符串类型")
        if not isinstance(self.score, (int, float)):
            raise ValueError("score必须是数值类型")
        if not isinstance(self.index, int) or self.index < 0:
            raise ValueError("index必须是非负整数")


@runtime_checkable
class BaseRerank(Protocol):
    """重排序服务抽象基类
    
    定义了重排序服务的基本接口，所有具体的重排序实现都应该继承此类。
    重排序服务的主要功能是根据查询对候选文档进行重新排序。
    """
    
    def __init__(self, config: RerankConfig):
        """初始化重排序服务
        
        Args:
            config: 重排序配置
        """
        if not isinstance(config, RerankConfig):
            raise TypeError("config必须是RerankConfig的实例")
        self.config = config
    
    @abstractmethod
    async def rerank(self, 
                    query: str, 
                    texts: List[str]) -> List[RerankResult]:
        """对文本列表进行重排序
        
        根据查询对候选文本进行重新排序，返回按相关性分数降序排列的结果。
        
        Args:
            query: 查询文本
            texts: 待重排序的文本列表
            
        Returns:
            重排序结果列表，按相关性分数降序排列
            
        Raises:
            ValueError: 当输入参数无效时
            RuntimeError: 当重排序过程出现错误时
        """
        pass
    
    def get_model_name(self) -> str:
        """获取模型名称
        
        Returns:
            模型名称
        """
        return self.config.model_name
    
    def get_config(self) -> RerankConfig:
        """获取配置
        
        Returns:
            重排序配置
        """
        return self.config
    
    def _validate_inputs(self, query: str, texts: List[str]) -> None:
        """验证输入参数
        
        Args:
            query: 查询文本
            texts: 文本列表
            
        Raises:
            ValueError: 当输入参数无效时
        """
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query必须是非空字符串")
        
        if not isinstance(texts, list):
            raise ValueError("texts必须是列表类型")
        
        if not texts:
            raise ValueError("texts不能为空列表")
        
        for i, text in enumerate(texts):
            if not isinstance(text, str):
                raise ValueError(f"texts[{i}]必须是字符串类型")
    
    def _apply_top_k(self, results: List[RerankResult]) -> List[RerankResult]:
        """应用top-k限制
        
        Args:
            results: 重排序结果列表
            
        Returns:
            应用top-k限制后的结果列表
        """
        if self.config.top_k is not None and self.config.top_k > 0:
            return results[:self.config.top_k]
        return results
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        # 子类可以重写此方法来实现资源清理
        pass
    
    def __repr__(self) -> str:
        """重排序服务的字符串表示"""
        return f"{self.__class__.__name__}(config={self.config})"