"""Rerank服务模块初始化

自动导入所有rerank实现以触发注册装饰器
"""

# 导入rerank实现以触发自动注册
from .impl.siliconflow import SiliconFlowRerank

# 导出主要接口
from .factory import RerankFactory, create_rerank, create_rerank_config, list_rerank_providers
from .registry import RerankRegistry, register_rerank
from .base import BaseRerank, RerankConfig, RerankResult

__all__ = [
    'RerankFactory',
    'create_rerank',
    'create_rerank_config',
    'list_rerank_providers', 
    'RerankRegistry',
    'register_rerank',
    'BaseRerank',
    'RerankConfig',
    'RerankResult',
    'SiliconFlowRerank'
]