"""
知识库仓储内存实现（测试用）
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from ....domain.knowledge.entities.knowledge_base import KnowledgeBase
from ....domain.knowledge.repositories.knowledge_base_repository import KnowledgeBaseRepository


class KnowledgeBaseRepositoryImpl(KnowledgeBaseRepository):
    """知识库仓储内存实现"""
    
    def __init__(self, session=None):
        self.session = session
        self._storage: Dict[str, KnowledgeBase] = {}
    
    async def save(self, knowledge_base: KnowledgeBase) -> KnowledgeBase:
        """保存知识库"""
        if knowledge_base.knowledge_base_id is None:
            knowledge_base.knowledge_base_id = str(uuid.uuid4())
        
        self._storage[knowledge_base.knowledge_base_id] = knowledge_base
        return knowledge_base
    
    async def find_by_id(self, knowledge_base_id: str) -> Optional[KnowledgeBase]:
        """根据ID查找知识库"""
        return self._storage.get(knowledge_base_id)
    
    async def find_by_user_id(self, user_id: str) -> List[KnowledgeBase]:
        """根据用户ID查找知识库列表"""
        return [kb for kb in self._storage.values() if kb.owner_id == user_id]
    
    async def find_by_owner_id(self, owner_id: str) -> List[KnowledgeBase]:
        """根据所有者ID查找知识库列表"""
        return [kb for kb in self._storage.values() if kb.owner_id == owner_id]
    
    async def find_active_by_owner_id(self, owner_id: str) -> List[KnowledgeBase]:
        """根据所有者ID查找活跃的知识库列表"""
        return [kb for kb in self._storage.values() 
                if kb.owner_id == owner_id and kb.is_active]
    
    async def update(self, knowledge_base: KnowledgeBase) -> KnowledgeBase:
        """更新知识库"""
        knowledge_base.updated_at = datetime.now()
        if knowledge_base.knowledge_base_id is not None:
            self._storage[knowledge_base.knowledge_base_id] = knowledge_base
        return knowledge_base
    
    async def delete_by_id(self, knowledge_base_id: str) -> bool:
        """根据ID删除知识库"""
        if knowledge_base_id in self._storage:
            del self._storage[knowledge_base_id]
            return True
        return False
    
    async def exists_by_name_and_user_id(self, name: str, user_id: str) -> bool:
        """检查指定用户是否已有同名知识库"""
        for kb in self._storage.values():
            if kb.name == name and kb.owner_id == user_id:
                return True
        return False
    
    async def exists_by_name_and_owner(self, name: str, owner_id: str) -> bool:
        """检查指定所有者下是否存在同名知识库"""
        for kb in self._storage.values():
            if kb.name == name and kb.owner_id == owner_id:
                return True
        return False
    
    async def count_by_owner_id(self, owner_id: str) -> int:
        """统计所有者的知识库数量"""
        return len([kb for kb in self._storage.values() if kb.owner_id == owner_id])