"""
文档分块仓储SQL实现 - 基于旧表结构 chunks 表
旧表字段：id, document_id, dataset_id, parent_chunk_id, chunk_type, chunk_level, content, char_size, token_size, index_in_doc, meta, is_active, created_at
"""

import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.knowledge.entities.document_chunk import DocumentChunk
from ...domain.knowledge.repositories.document_chunk_repository import DocumentChunkRepository
from ...domain.knowledge.vo.search_query import SearchQuery, SearchResult


class DocumentChunkSqlRepository(DocumentChunkRepository):
    """文档分块仓储SQL实现 - 基于 chunks 表"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def save(self, chunk: DocumentChunk) -> DocumentChunk:
        """保存文档块到 chunks 表"""
        sql = """
        INSERT INTO chunks (document_id, dataset_id, content, char_size, index_in_doc, meta, is_active, created_at)
        VALUES (:document_id, :dataset_id, :content, :char_size, :index_in_doc, :meta, :is_active, :created_at)
        RETURNING id
        """
        
        chunk_data = {
            'document_id': int(chunk.document_id),
            'dataset_id': int(chunk.knowledge_base_id),
            'content': chunk.content,
            'char_size': len(chunk.content),
            'index_in_doc': chunk.chunk_index,
            'meta': json.dumps(chunk.metadata or {}),
            'is_active': True,
            'created_at': chunk.created_at or datetime.now(),
        }
        
        result = await self.session.execute(text(sql), chunk_data)
        row = result.fetchone()
        if row:
            chunk.chunk_id = str(row[0])
        
        return chunk
    
    async def save_batch(self, chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        """批量保存文档块"""
        for chunk in chunks:
            await self.save(chunk)
        return chunks
    
    async def find_by_id(self, chunk_id: str) -> Optional[DocumentChunk]:
        """根据ID查找文档块"""
        sql = "SELECT * FROM chunks WHERE id = :chunk_id AND is_active = true"
        result = await self.session.execute(text(sql), {"chunk_id": int(chunk_id)})
        row = result.fetchone()
        return self._from_dict(dict(row._mapping)) if row else None
    
    async def find_by_document_id(self, document_id: str) -> List[DocumentChunk]:
        """根据文档ID查找文档块列表"""
        sql = "SELECT * FROM chunks WHERE document_id = :document_id AND is_active = true ORDER BY index_in_doc ASC"
        result = await self.session.execute(text(sql), {"document_id": int(document_id)})
        rows = result.fetchall()
        return [self._from_dict(dict(row._mapping)) for row in rows]
    
    async def find_by_knowledge_base_id(self, knowledge_base_id: str) -> List[DocumentChunk]:
        """根据知识库ID查找文档块列表"""
        sql = "SELECT * FROM chunks WHERE dataset_id = :dataset_id AND is_active = true ORDER BY created_at DESC"
        result = await self.session.execute(text(sql), {"dataset_id": int(knowledge_base_id)})
        rows = result.fetchall()
        return [self._from_dict(dict(row._mapping)) for row in rows]
    
    async def update(self, chunk: DocumentChunk) -> DocumentChunk:
        """更新文档块"""
        sql = "UPDATE chunks SET content = :content, char_size = :char_size, meta = :meta WHERE id = :chunk_id"
        chunk_data = {
            'content': chunk.content,
            'char_size': len(chunk.content),
            'meta': json.dumps(chunk.metadata or {}),
            'chunk_id': int(chunk.chunk_id or 0)
        }
        await self.session.execute(text(sql), chunk_data)
        return chunk
    
    async def delete_by_id(self, chunk_id: str) -> bool:
        """根据ID删除文档块"""
        sql = "UPDATE chunks SET is_active = false WHERE id = :chunk_id"
        await self.session.execute(text(sql), {"chunk_id": int(chunk_id)})
        return True
    
    async def delete_by_document_id(self, document_id: str) -> int:
        """根据文档ID删除所有文档块"""
        sql = "UPDATE chunks SET is_active = false WHERE document_id = :document_id"
        await self.session.execute(text(sql), {"document_id": int(document_id)})
        return 0
    
    async def delete_by_knowledge_base_id(self, knowledge_base_id: str) -> int:
        """根据知识库ID删除所有文档块"""
        sql = "UPDATE chunks SET is_active = false WHERE dataset_id = :dataset_id"
        await self.session.execute(text(sql), {"dataset_id": int(knowledge_base_id)})
        return 0
    
    async def count_by_knowledge_base_id(self, knowledge_base_id: str) -> int:
        """统计知识库中的文档块数量"""
        sql = "SELECT COUNT(*) FROM chunks WHERE dataset_id = :dataset_id AND is_active = true"
        result = await self.session.execute(text(sql), {"dataset_id": int(knowledge_base_id)})
        return result.scalar() or 0
    
    async def count_by_document_id(self, document_id: str) -> int:
        """统计文档的分块数量"""
        sql = "SELECT COUNT(*) FROM chunks WHERE document_id = :document_id AND is_active = true"
        result = await self.session.execute(text(sql), {"document_id": int(document_id)})
        return result.scalar() or 0
    
    # 实现抽象方法
    async def search_by_content(self, query: SearchQuery) -> List[SearchResult]:
        """根据内容搜索文档块"""
        sql = "SELECT * FROM chunks WHERE dataset_id = :dataset_id AND content LIKE :query_text AND is_active = true LIMIT 10"
        result = await self.session.execute(text(sql), {
            "dataset_id": int(query.knowledge_base_id),
            "query_text": f"%{query.text}%"
        })
        rows = result.fetchall()
        
        search_results = []
        for row in rows:
            data = dict(row._mapping)
            search_result = SearchResult(
                chunk_id=str(data['id']),
                content=data['content'],
                score=1.0,
                document_id=str(data['document_id']),
                chunk_index=data['index_in_doc'],
                metadata=data.get('meta')
            )
            search_results.append(search_result)
        return search_results
    
    async def find_chunks_with_vectors(self, knowledge_base_id: str, limit: int = 100) -> List[DocumentChunk]:
        """查找有向量的文档块"""
        sql = "SELECT * FROM chunks WHERE dataset_id = :dataset_id AND is_active = true LIMIT :limit"
        result = await self.session.execute(text(sql), {
            "dataset_id": int(knowledge_base_id),
            "limit": limit
        })
        rows = result.fetchall()
        return [self._from_dict(dict(row._mapping)) for row in rows]
    
    async def search_similar(self, query: SearchQuery) -> List[SearchResult]:
        """向量相似度搜索"""
        return await self.search_by_content(query)
    
    def _from_dict(self, data: Dict[str, Any]) -> DocumentChunk:
        """从旧表字典转换为文档块实体"""
        # 处理meta字段，可能是JSON字符串也可能是字典
        meta_data = data.get('meta')
        if isinstance(meta_data, str):
            import json
            try:
                meta_data = json.loads(meta_data)
            except json.JSONDecodeError:
                meta_data = {}
        elif not isinstance(meta_data, dict):
            meta_data = {}
        
        return DocumentChunk(
            chunk_id=str(data.get('id', '')),
            content=data['content'],
            chunk_index=data.get('index_in_doc', 0),
            start_offset=0,
            end_offset=data.get('char_size', 0),
            document_id=str(data['document_id']),
            knowledge_base_id=str(data['dataset_id']),
            vector=None,
            metadata=meta_data,
            created_at=data.get('created_at'),
            updated_at=data.get('created_at')
        )