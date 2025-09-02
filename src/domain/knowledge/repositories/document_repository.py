"""
文档仓储接口
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ..entities.document import Document


class DocumentRepository(ABC):
    """文档仓储接口"""
    
    @abstractmethod
    async def save(self, document: Document) -> Document:
        """保存文档"""
        pass
    
    @abstractmethod
    async def find_by_id(self, document_id: str) -> Optional[Document]:
        """根据ID查找文档"""
        pass
    
    @abstractmethod
    async def find_by_knowledge_base_id(self, knowledge_base_id: str) -> List[Document]:
        """根据知识库ID查找文档列表"""
        pass
    
    @abstractmethod
    async def find_unprocessed_by_knowledge_base_id(self, knowledge_base_id: str) -> List[Document]:
        """根据知识库ID查找未处理的文档列表"""
        pass
    
    @abstractmethod
    async def update(self, document: Document) -> Document:
        """更新文档"""
        pass
    
    @abstractmethod
    async def delete_by_id(self, document_id: str) -> bool:
        """根据ID删除文档"""
        pass
    
    @abstractmethod
    async def delete_by_knowledge_base_id(self, knowledge_base_id: str) -> int:
        """根据知识库ID删除所有文档，返回删除数量"""
        pass
    
    @abstractmethod
    async def find_by_content_hash(self, content_hash: str, knowledge_base_id: str) -> Optional[Document]:
        """根据内容哈希查找文档（用于去重）"""
        pass
    
    @abstractmethod
    async def count_by_knowledge_base_id(self, knowledge_base_id: str) -> int:
        """统计知识库中的文档数量"""
        pass
    
    @abstractmethod
    async def find_by_filename_pattern(self, knowledge_base_id: str, pattern: str) -> List[Document]:
        """根据文件名模式查找文档"""
        pass