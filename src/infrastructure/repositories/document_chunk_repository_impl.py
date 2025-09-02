"""
文档块仓储内存实现（测试用）
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from ...domain.knowledge.entities.document_chunk import DocumentChunk
from ...domain.knowledge.repositories.document_chunk_repository import DocumentChunkRepository
from ...domain.knowledge.vo.search_query import SearchQuery, SearchResult


class DocumentChunkRepositoryImpl(DocumentChunkRepository):
    """文档块仓储内存实现"""
    
    def __init__(self, session=None):
        self.session = session
        self._storage: Dict[str, DocumentChunk] = {}
    
    async def save(self, chunk: DocumentChunk) -> DocumentChunk:
        """保存文档块"""
        if chunk.chunk_id is None:
            chunk.chunk_id = str(uuid.uuid4())
        
        # 使用一个变量来确保类型安全
        chunk_id: str = chunk.chunk_id  # type: ignore
        self._storage[chunk_id] = chunk
        return chunk
    
    async def save_batch(self, chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        """批量保存文档块"""
        results = []
        for chunk in chunks:
            result = await self.save(chunk)
            results.append(result)
        return results
    
    async def find_by_id(self, chunk_id: str) -> Optional[DocumentChunk]:
        """根据ID查找文档块"""
        return self._storage.get(chunk_id)
    
    async def find_by_document_id(self, document_id: str) -> List[DocumentChunk]:
        """根据文档ID查找文档块列表"""
        return [chunk for chunk in self._storage.values() 
                if chunk.document_id == document_id]
    
    async def find_by_knowledge_base_id(self, knowledge_base_id: str) -> List[DocumentChunk]:
        """根据知识库ID查找文档块列表"""
        return [chunk for chunk in self._storage.values() 
                if chunk.knowledge_base_id == knowledge_base_id]
    
    async def update(self, chunk: DocumentChunk) -> DocumentChunk:
        """更新文档块"""
        chunk.updated_at = datetime.now()
        # 确保 chunk_id 不为 None
        if chunk.chunk_id is None:
            chunk.chunk_id = str(uuid.uuid4())
        chunk_id: str = chunk.chunk_id  # type: ignore
        self._storage[chunk_id] = chunk
        return chunk
    
    async def delete_by_id(self, chunk_id: str) -> bool:
        """根据ID删除文档块"""
        if chunk_id in self._storage:
            del self._storage[chunk_id]
            return True
        return False
    
    async def delete_by_document_id(self, document_id: str) -> int:
        """根据文档ID删除所有文档块，返回删除数量"""
        chunks_to_delete = [chunk_id for chunk_id, chunk in self._storage.items() 
                           if chunk.document_id == document_id]
        
        for chunk_id in chunks_to_delete:
            del self._storage[chunk_id]
        
        return len(chunks_to_delete)
    
    async def delete_by_knowledge_base_id(self, knowledge_base_id: str) -> int:
        """根据知识库ID删除所有文档块，返回删除数量"""
        chunks_to_delete = [chunk_id for chunk_id, chunk in self._storage.items() 
                           if chunk.knowledge_base_id == knowledge_base_id]
        
        for chunk_id in chunks_to_delete:
            del self._storage[chunk_id]
        
        return len(chunks_to_delete)
    
    async def count_by_knowledge_base_id(self, knowledge_base_id: str) -> int:
        """统计知识库中的文档块数量"""
        return len([chunk for chunk in self._storage.values() 
                   if chunk.knowledge_base_id == knowledge_base_id])
    
    async def count_by_document_id(self, document_id: str) -> int:
        """统计文档中的文档块数量"""
        return len([chunk for chunk in self._storage.values() 
                   if chunk.document_id == document_id])
    
    async def search_by_content(self, query: SearchQuery) -> List[SearchResult]:
        """基于内容的全文搜索"""
        results = []
        for chunk in self._storage.values():
            if query.knowledge_base_id and chunk.knowledge_base_id != query.knowledge_base_id:
                continue
            
            # 简单的文本匹配搜索
            if query.text.lower() in chunk.content.lower():
                # 确保 chunk_id 不为 None
                chunk_id = chunk.chunk_id if chunk.chunk_id is not None else str(uuid.uuid4())
                result = SearchResult(
                    chunk_id=chunk_id,
                    content=chunk.content,
                    score=0.8,  # 固定分数
                    document_id=chunk.document_id,
                    chunk_index=chunk.chunk_index,
                    metadata=chunk.metadata or {}
                )
                results.append(result)
        
        return results[:query.max_results] if query.max_results else results
    
    async def find_chunks_with_vectors(self, knowledge_base_id: str) -> List[DocumentChunk]:
        """查找有向量的文档块"""
        return [chunk for chunk in self._storage.values()
                if chunk.knowledge_base_id == knowledge_base_id and chunk.vector is not None]