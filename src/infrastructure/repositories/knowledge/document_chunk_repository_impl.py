"""
文档分块仓储SQL实现 - 基于chunks表和embeddings表
chunks表字段：id, document_id, dataset_id, parent_chunk_id, chunk_type, chunk_level, content, char_size, token_size, index_in_doc, meta, is_active, created_at
embeddings表字段：id, chunk_id, embedding_data(vector), embedding_model_id, version, created_at
"""

import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ....domain.knowledge.entities.document_chunk import DocumentChunk
from ....domain.knowledge.repositories.document_chunk_repository import DocumentChunkRepository
from ....domain.knowledge.vo.search_query import SearchQuery, SearchResult
from .embedding_vector_repository import EmbeddingVectorRepositoryImpl
from ....infrastructure.utils.uuid_generator import uuid_generator


class DocumentChunkRepositoryImpl(DocumentChunkRepository):
    """文档分块仓储SQL实现 - 基于 chunks 表和 embeddings 表"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.embedding_repo = EmbeddingVectorRepositoryImpl(session)
    
    async def save(self, chunk: DocumentChunk) -> DocumentChunk:
        """保存文档块到 chunks 表"""
        # 如果chunk没有ID，生成一个UUID
        if not chunk.chunk_id:
            chunk.chunk_id = uuid_generator.generate()
        
        sql = """
        INSERT INTO chunks (id, document_id, dataset_id, content, char_size, index_in_doc, meta, is_active, created_at)
        VALUES (:id, :document_id, :dataset_id, :content, :char_size, :index_in_doc, :meta, :is_active, :created_at)
        RETURNING id
        """
        
        chunk_data = {
            'id': chunk.chunk_id,
            'document_id': chunk.document_id,
            'dataset_id': chunk.knowledge_base_id,
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
        
        # 如果chunk有向量数据，保存到embeddings表
        if chunk.has_vector():
            await self.embedding_repo.save_embedding(
                chunk_id=chunk.chunk_id,
                embedding_data=chunk.vector,
                embedding_model_id='default',  # 可以从chunk的metadata中获取
                version=1
            )
        
        return chunk
    
    async def save_batch(self, chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        """批量保存文档块"""
        for chunk in chunks:
            await self.save(chunk)
        return chunks
    
    async def find_by_id(self, chunk_id: str) -> Optional[DocumentChunk]:
        """根据ID查找文档块"""
        sql = "SELECT * FROM chunks WHERE id = :chunk_id AND is_active = true"
        result = await self.session.execute(text(sql), {"chunk_id": chunk_id})
        row = result.fetchone()
        return self._from_dict(dict(row._mapping)) if row else None
    
    async def find_by_document_id(self, document_id: str) -> List[DocumentChunk]:
        """根据文档ID查找文档块列表"""
        sql = "SELECT * FROM chunks WHERE document_id = :document_id AND is_active = true ORDER BY index_in_doc ASC"
        result = await self.session.execute(text(sql), {"document_id": document_id})
        rows = result.fetchall()
        return [self._from_dict(dict(row._mapping)) for row in rows]
    
    async def find_by_knowledge_base_id(self, knowledge_base_id: str) -> List[DocumentChunk]:
        """根据知识库ID查找文档块列表"""
        sql = "SELECT * FROM chunks WHERE dataset_id = :dataset_id AND is_active = true ORDER BY created_at DESC"
        result = await self.session.execute(text(sql), {"dataset_id": knowledge_base_id})
        rows = result.fetchall()
        return [self._from_dict(dict(row._mapping)) for row in rows]
    
    async def find_chunks_without_vectors(self, knowledge_base_id: str) -> List[DocumentChunk]:
        """查找没有向量的分块"""
        # 使用embedding仓储查找没有向量的chunk ID
        chunk_ids_without_vectors = await self.embedding_repo.find_chunks_without_embeddings(knowledge_base_id)
        
        if not chunk_ids_without_vectors:
            return []
        
        # 根据chunk ID查询chunk详细信息
        placeholders = ','.join([f':id_{i}' for i in range(len(chunk_ids_without_vectors))])
        sql = f"""
        SELECT * FROM chunks 
        WHERE id IN ({placeholders})
        AND is_active = true 
        ORDER BY created_at DESC
        """
        
        params = {f'id_{i}': chunk_id for i, chunk_id in enumerate(chunk_ids_without_vectors)}
        result = await self.session.execute(text(sql), params)
        rows = result.fetchall()
        return [self._from_dict(dict(row._mapping)) for row in rows]
    
    async def update(self, chunk: DocumentChunk) -> DocumentChunk:
        """更新文档块"""
        sql = "UPDATE chunks SET content = :content, char_size = :char_size, meta = :meta WHERE id = :chunk_id"
        chunk_data = {
            'content': chunk.content,
            'char_size': len(chunk.content),
            'meta': json.dumps(chunk.metadata or {}),
            'chunk_id': chunk.chunk_id  # 修复：使用字符串类型的chunk_id
        }
        await self.session.execute(text(sql), chunk_data)
        
        # 如果chunk有向量数据，更新embeddings表
        if chunk.has_vector():
            await self.embedding_repo.save_embedding(
                chunk_id=chunk.chunk_id,
                embedding_data=chunk.vector,
                embedding_model_id='default',  # 可以从chunk的metadata中获取
                version=1
            )
        
        return chunk
    
    async def delete_by_id(self, chunk_id: str) -> bool:
        """根据ID删除文档块"""
        sql = "UPDATE chunks SET is_active = false WHERE id = :chunk_id"
        await self.session.execute(text(sql), {"chunk_id": chunk_id})
        return True
    
    async def delete_by_document_id(self, document_id: str) -> int:
        """根据文档ID删除所有文档块（硬删除，包括embedding向量）"""
        # 先查询要删除的chunks数量
        count_sql = "SELECT COUNT(*) FROM chunks WHERE document_id = :document_id"
        count_result = await self.session.execute(text(count_sql), {"document_id": document_id})
        deleted_count = count_result.scalar() or 0
        
        # 删除相关的embedding向量
        await self.embedding_repo.delete_embeddings_by_document(document_id)
        
        # 硬删除chunks记录
        delete_sql = "DELETE FROM chunks WHERE document_id = :document_id"
        await self.session.execute(text(delete_sql), {"document_id": document_id})
        
        return deleted_count
    
    async def delete_by_knowledge_base_id(self, knowledge_base_id: str) -> int:
        """根据知识库ID删除所有文档块"""
        sql = "UPDATE chunks SET is_active = false WHERE dataset_id = :dataset_id"
        await self.session.execute(text(sql), {"dataset_id": knowledge_base_id})
        return 0
    
    async def count_by_knowledge_base_id(self, knowledge_base_id: str) -> int:
        """统计知识库中的文档块数量"""
        sql = "SELECT COUNT(*) FROM chunks WHERE dataset_id = :dataset_id AND is_active = true"
        result = await self.session.execute(text(sql), {"dataset_id": knowledge_base_id})
        return result.scalar() or 0
    
    async def count_by_document_id(self, document_id: str) -> int:
        """统计文档的分块数量"""
        sql = "SELECT COUNT(*) FROM chunks WHERE document_id = :document_id AND is_active = true"
        result = await self.session.execute(text(sql), {"document_id": document_id})
        return result.scalar() or 0
    
    # 实现抽象方法
    async def search_by_content(self, query: SearchQuery) -> List[SearchResult]:
        """根据内容搜索文档块"""
        sql = "SELECT * FROM chunks WHERE dataset_id = :dataset_id AND content LIKE :query_text AND is_active = true LIMIT 10"
        result = await self.session.execute(text(sql), {
            "dataset_id": query.knowledge_base_id,
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
        # 使用embedding仓储查找有向量的chunk ID
        chunk_ids_with_vectors = await self.embedding_repo.find_chunks_with_embeddings(knowledge_base_id, limit)
        
        if not chunk_ids_with_vectors:
            return []
        
        # 根据chunk ID查询chunk详细信息
        placeholders = ','.join([f':id_{i}' for i in range(len(chunk_ids_with_vectors))])
        sql = f"""
        SELECT * FROM chunks 
        WHERE id IN ({placeholders})
        AND is_active = true 
        ORDER BY created_at DESC
        """
        
        params = {f'id_{i}': chunk_id for i, chunk_id in enumerate(chunk_ids_with_vectors)}
        result = await self.session.execute(text(sql), params)
        rows = result.fetchall()
        
        # 加载向量数据
        chunks = []
        for row in rows:
            chunk = self._from_dict(dict(row._mapping))
            # 从embeddings表加载向量数据
            vector_data = await self.embedding_repo.get_embedding(chunk.chunk_id)
            if vector_data:
                chunk.set_vector(vector_data)
            chunks.append(chunk)
        
        return chunks
    
    async def search_similar(self, query: SearchQuery) -> List[SearchResult]:
        """向量相似度搜索"""
        if not query.vector:
            # 如果没有向量，回退到内容搜索
            return await self.search_by_content(query)
        
        # 使用embedding仓储进行向量相似度搜索
        search_results_data = await self.embedding_repo.vector_similarity_search(
            query_vector=query.vector,
            knowledge_base_id=query.knowledge_base_id,
            limit=query.limit or 10,
            similarity_threshold=0.0
        )
        
        # 转换为SearchResult对象
        search_results = []
        for data in search_results_data:
            search_result = SearchResult(
                chunk_id=data['chunk_id'],
                content=data['content'],
                score=data['similarity_score'],
                document_id=data['document_id'],
                chunk_index=data['chunk_index'],
                metadata=data['metadata']
            )
            search_results.append(search_result)
        
        return search_results
    
    def _from_dict(self, data: Dict[str, Any]) -> DocumentChunk:
        """从旧表字典转换为文档块实体"""
        # 处理meta字段，可能是JSON字符串也可能是字典
        meta_data = data.get('meta')
        if isinstance(meta_data, str):
            try:
                meta_data = json.loads(meta_data)
            except json.JSONDecodeError:
                meta_data = {}
        elif not isinstance(meta_data, dict):
            meta_data = {}
        
        chunk = DocumentChunk(
            chunk_id=str(data.get('id', '')),
            content=data['content'],
            chunk_index=data.get('index_in_doc', 0),
            start_offset=0,
            end_offset=data.get('char_size', 0),
            document_id=str(data['document_id']),
            knowledge_base_id=str(data['dataset_id']),
            vector=None,  # 向量数据将从embeddings表单独加载
            metadata=meta_data,
            created_at=data.get('created_at'),
            updated_at=data.get('created_at')
        )
        
        return chunk