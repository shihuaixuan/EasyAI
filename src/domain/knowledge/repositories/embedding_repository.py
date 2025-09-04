"""
知识库领域 - Embedding配置仓储接口
"""
from abc import ABC, abstractmethod
from typing import Optional

from ..vo.embedding_config import EmbeddingModelConfig


class EmbeddingConfigRepository(ABC):
    """Embedding配置仓储接口"""
    
    @abstractmethod
    async def get_embedding_config_by_knowledge_base_id(
        self, 
        knowledge_base_id: str,
        user_id: str
    ) -> Optional[EmbeddingModelConfig]:
        """
        根据知识库ID获取embedding配置
        
        Args:
            knowledge_base_id: 知识库ID
            user_id: 用户ID
            
        Returns:
            Embedding配置，如果不存在则返回None
        """
        pass
    
    @abstractmethod
    async def get_default_embedding_config(self) -> EmbeddingModelConfig:
        """
        获取默认的embedding配置
        
        Returns:
            默认embedding配置
        """
        pass
