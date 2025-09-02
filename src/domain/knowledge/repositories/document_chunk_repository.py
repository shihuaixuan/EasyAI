"""
文档块仓储接口
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ..entities.document_chunk import DocumentChunk
from ..vo.search_query import SearchQuery, SearchResult


class DocumentChunkRepository(ABC):
    """文档块仓储接口"""
    
    @abstractmethod
    async def save(self, chunk: DocumentChunk) -> DocumentChunk:
        """保存文档块"""
        pass
    
    @abstractmethod
    async def save_batch(self, chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        """批量保存文档块"""
        pass
    
    @abstractmethod
    async def find_by_id(self, chunk_id: str) -> Optional[DocumentChunk]:
        """根据ID查找文档块"""
        pass
    
    @abstractmethod
    async def find_by_document_id(self, document_id: str) -> List[DocumentChunk]:
        """根据文档ID查找文档块列表"""
        pass
    
    @abstractmethod
    async def find_by_knowledge_base_id(self, knowledge_base_id: str) -> List[DocumentChunk]:
        """根据知识库ID查找文档块列表"""
        pass
    
    @abstractmethod
    async def update(self, chunk: DocumentChunk) -> DocumentChunk:
        """更新文档块"""
        pass
    
    @abstractmethod
    async def delete_by_id(self, chunk_id: str) -> bool:
        """根据ID删除文档块"""
        pass
    
    @abstractmethod
    async def delete_by_document_id(self, document_id: str) -> int:
        """根据文档ID删除所有文档块，返回删除数量"""
        pass
    
    @abstractmethod
    async def delete_by_knowledge_base_id(self, knowledge_base_id: str) -> int:
        """根据知识库ID删除所有文档块，返回删除数量"""
        pass
    
    @abstractmethod
    async def count_by_knowledge_base_id(self, knowledge_base_id: str) -> int:
        """统计知识库中的文档块数量"""
        pass
    
    @abstractmethod
    async def count_by_document_id(self, document_id: str) -> int:
        """统计文档中的文档块数量"""
        pass
    
    @abstractmethod
    async def search_by_content(self, query: SearchQuery) -> List[SearchResult]:
        """基于内容的全文搜索"""
        pass
    
    @abstractmethod
    async def find_chunks_with_vectors(self, knowledge_base_id: str) -> List[DocumentChunk]:
        """查找有向量的文档块"""
        pass