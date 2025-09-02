"""
知识库仓储接口
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ..entities.knowledge_base import KnowledgeBase


class KnowledgeBaseRepository(ABC):
    """知识库仓储接口"""
    
    @abstractmethod
    async def save(self, knowledge_base: KnowledgeBase) -> KnowledgeBase:
        """保存知识库"""
        pass
    
    @abstractmethod
    async def find_by_id(self, knowledge_base_id: str) -> Optional[KnowledgeBase]:
        """根据ID查找知识库"""
        pass
    
    @abstractmethod
    async def find_by_owner_id(self, owner_id: str) -> List[KnowledgeBase]:
        """根据所有者ID查找知识库列表"""
        pass
    
    @abstractmethod
    async def find_active_by_owner_id(self, owner_id: str) -> List[KnowledgeBase]:
        """根据所有者ID查找活跃的知识库列表"""
        pass
    
    @abstractmethod
    async def update(self, knowledge_base: KnowledgeBase) -> KnowledgeBase:
        """更新知识库"""
        pass
    
    @abstractmethod
    async def delete_by_id(self, knowledge_base_id: str) -> bool:
        """根据ID删除知识库"""
        pass
    
    @abstractmethod
    async def exists_by_name_and_owner(self, name: str, owner_id: str) -> bool:
        """检查指定所有者下是否存在同名知识库"""
        pass
    
    @abstractmethod
    async def count_by_owner_id(self, owner_id: str) -> int:
        """统计所有者的知识库数量"""
        pass