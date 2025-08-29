"""Embedding服务模块初始化

自动导入所有embedding实现以触发注册装饰器
"""

# 导入embedding实现以触发自动注册
from .impl.siliconflow import SiliconFlowEmbedding
from .impl.local import LocalEmbedding

# 导出主要接口
from .factory import EmbeddingFactory, create_embedding, create_config, list_providers
from .registry import EmbeddingRegistry, register_embedding
from .base import BaseEmbedding, EmbeddingConfig

__all__ = [
    'EmbeddingFactory',
    'create_embedding',
    'create_config', 
    'list_providers',
    'EmbeddingRegistry',
    'register_embedding',
    'BaseEmbedding',
    'EmbeddingConfig',
    'SiliconFlowEmbedding',
    'LocalEmbedding'
]