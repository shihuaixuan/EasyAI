"""
基础设施层 - Embedding向量仓储实现
处理embeddings表中的vector类型数据
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from sqlalchemy.future import select
import json

from ....infrastructure.models.knowledge_models import EmbeddingModel
from ....domain.knowledge.entities.document_chunk import DocumentChunk


class EmbeddingVectorRepository:
    """Embedding向量仓储实现"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def save_embedding(
        self, 
        chunk_id: str, 
        embedding_data: List[float], 
        embedding_model_id: str,
        version: int = 1
    ) -> bool:
        """
        保存embedding向量数据
        
        Args:
            chunk_id: 分块ID
            embedding_data: 向量数据
            embedding_model_id: 模型ID
            version: 版本号
            
        Returns:
            是否保存成功
        """
        try:
            # 生成UUID作为主键
            from ....infrastructure.utils.uuid_generator import uuid_generator
            embedding_id = uuid_generator.generate()
            
            # 验证向量维度（现在支持1024维）
            if len(embedding_data) != 1024:
                print(f"警告：向量维度不匹配，期望1024维，实际{len(embedding_data)}维")
            
            # 使用UPSERT操作（INSERT ... ON CONFLICT DO UPDATE）
            sql = """
            INSERT INTO embeddings (id, chunk_id, embedding_data, embedding_model_id, version)
            VALUES (:id, :chunk_id, :embedding_data, :embedding_model_id, :version)
            ON CONFLICT (chunk_id) 
            DO UPDATE SET 
                embedding_data = EXCLUDED.embedding_data,
                embedding_model_id = EXCLUDED.embedding_model_id,
                version = EXCLUDED.version,
                created_at = CURRENT_TIMESTAMP
            """
            
            # 将Python list转换为PostgreSQL vector格式
            vector_str = '[' + ','.join(map(str, embedding_data)) + ']'
            
            await self.session.execute(text(sql), {
                'id': embedding_id,
                'chunk_id': chunk_id,
                'embedding_data': vector_str,  # 使用字符串格式的向量
                'embedding_model_id': embedding_model_id,
                'version': version
            })
            
            return True
            
        except Exception as e:
            print(f"保存embedding向量失败: {str(e)}")
            return False
    
    async def get_embedding(self, chunk_id: str) -> Optional[List[float]]:
        """
        获取embedding向量数据
        
        Args:
            chunk_id: 分块ID
            
        Returns:
            向量数据或None
        """
        try:
            sql = "SELECT embedding_data FROM embeddings WHERE chunk_id = :chunk_id"
            result = await self.session.execute(text(sql), {'chunk_id': chunk_id})
            row = result.fetchone()
            
            if row and row[0] is not None:
                vector_data = row[0]
                # 如果是字符串格式，需要解析为list
                if isinstance(vector_data, str):
                    # 去掉方括号并分割
                    vector_str = vector_data.strip('[]')
                    return [float(x.strip()) for x in vector_str.split(',')]
                else:
                    # 如果已经是list格式，直接返回
                    return list(vector_data)
            
            return None
            
        except Exception as e:
            print(f"获取embedding向量失败: {str(e)}")
            return None
    
    async def batch_save_embeddings(
        self, 
        embeddings_data: List[Dict[str, Any]]
    ) -> int:
        """
        批量保存embedding向量数据
        
        Args:
            embeddings_data: 包含chunk_id, embedding_data, embedding_model_id等的字典列表
            
        Returns:
            成功保存的数量
        """
        success_count = 0
        
        for data in embeddings_data:
            success = await self.save_embedding(
                chunk_id=data['chunk_id'],
                embedding_data=data['embedding_data'],
                embedding_model_id=data['embedding_model_id'],
                version=data.get('version', 1)
            )
            if success:
                success_count += 1
        
        return success_count
    
    async def delete_embedding(self, chunk_id: str) -> bool:
        """
        删除embedding向量数据
        
        Args:
            chunk_id: 分块ID
            
        Returns:
            是否删除成功
        """
        try:
            sql = "DELETE FROM embeddings WHERE chunk_id = :chunk_id"
            await self.session.execute(text(sql), {'chunk_id': chunk_id})
            return True
            
        except Exception as e:
            print(f"删除embedding向量失败: {str(e)}")
            return False
    
    async def delete_embeddings_by_document(self, document_id: str) -> int:
        """
        删除文档相关的所有embedding向量
        
        Args:
            document_id: 文档ID
            
        Returns:
            删除的数量
        """
        try:
            sql = """
            DELETE FROM embeddings 
            WHERE chunk_id IN (
                SELECT id FROM chunks WHERE document_id = :document_id
            )
            """
            result = await self.session.execute(text(sql), {'document_id': document_id})
            return result.rowcount or 0
            
        except Exception as e:
            print(f"删除文档embedding向量失败: {str(e)}")
            return 0
    
    async def find_chunks_without_embeddings(self, knowledge_base_id: str) -> List[str]:
        """
        查找没有embedding向量的分块ID列表
        
        Args:
            knowledge_base_id: 知识库ID
            
        Returns:
            没有向量的分块ID列表
        """
        try:
            sql = """
            SELECT c.id 
            FROM chunks c 
            LEFT JOIN embeddings e ON c.id = e.chunk_id 
            WHERE c.dataset_id = :dataset_id 
              AND c.is_active = true 
              AND e.chunk_id IS NULL
            ORDER BY c.created_at DESC
            """
            result = await self.session.execute(text(sql), {'dataset_id': knowledge_base_id})
            rows = result.fetchall()
            return [str(row[0]) for row in rows]
            
        except Exception as e:
            print(f"查找无向量分块失败: {str(e)}")
            return []
    
    async def find_chunks_with_embeddings(self, knowledge_base_id: str, limit: int = 100) -> List[str]:
        """
        查找有embedding向量的分块ID列表
        
        Args:
            knowledge_base_id: 知识库ID
            limit: 限制数量
            
        Returns:
            有向量的分块ID列表
        """
        try:
            sql = """
            SELECT c.id 
            FROM chunks c 
            INNER JOIN embeddings e ON c.id = e.chunk_id 
            WHERE c.dataset_id = :dataset_id 
              AND c.is_active = true 
            ORDER BY c.created_at DESC
            LIMIT :limit
            """
            result = await self.session.execute(text(sql), {
                'dataset_id': knowledge_base_id,
                'limit': limit
            })
            rows = result.fetchall()
            return [str(row[0]) for row in rows]
            
        except Exception as e:
            print(f"查找有向量分块失败: {str(e)}")
            return []
    
    async def vector_similarity_search(
        self, 
        query_vector: List[float], 
        knowledge_base_id: str,
        limit: int = 10,
        similarity_threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        向量相似度搜索
        
        Args:
            query_vector: 查询向量
            knowledge_base_id: 知识库ID
            limit: 返回结果数量限制
            similarity_threshold: 相似度阈值
            
        Returns:
            相似度搜索结果列表
        """
        try:
            # 使用余弦相似度搜索（<=> 操作符）
            sql = """
            SELECT 
                c.id as chunk_id,
                c.content,
                c.document_id,
                c.index_in_doc,
                c.meta,
                (1 - (e.embedding_data <=> :query_vector)) as similarity_score
            FROM chunks c
            INNER JOIN embeddings e ON c.id = e.chunk_id
            WHERE c.dataset_id = :dataset_id 
              AND c.is_active = true
              AND (1 - (e.embedding_data <=> :query_vector)) >= :threshold
            ORDER BY e.embedding_data <=> :query_vector ASC
            LIMIT :limit
            """
            
            # 将查询向量转换为PostgreSQL vector格式
            query_vector_str = '[' + ','.join(map(str, query_vector)) + ']'
            
            result = await self.session.execute(text(sql), {
                'query_vector': query_vector_str,
                'dataset_id': knowledge_base_id,
                'threshold': similarity_threshold,
                'limit': limit
            })
            
            rows = result.fetchall()
            search_results = []
            
            for row in rows:
                # 处理meta字段
                meta_data = row.meta
                if isinstance(meta_data, str):
                    try:
                        meta_data = json.loads(meta_data)
                    except json.JSONDecodeError:
                        meta_data = {}
                elif not isinstance(meta_data, dict):
                    meta_data = {}
                
                search_results.append({
                    'chunk_id': str(row.chunk_id),
                    'content': row.content,
                    'document_id': str(row.document_id),
                    'chunk_index': row.index_in_doc,
                    'metadata': meta_data,
                    'similarity_score': float(row.similarity_score)
                })
            
            return search_results
            
        except Exception as e:
            print(f"向量相似度搜索失败: {str(e)}")
            return []
    
    async def count_embeddings_by_knowledge_base(self, knowledge_base_id: str) -> int:
        """
        统计知识库中的embedding向量数量
        
        Args:
            knowledge_base_id: 知识库ID
            
        Returns:
            向量数量
        """
        try:
            sql = """
            SELECT COUNT(e.id)
            FROM embeddings e
            INNER JOIN chunks c ON e.chunk_id = c.id
            WHERE c.dataset_id = :dataset_id AND c.is_active = true
            """
            result = await self.session.execute(text(sql), {'dataset_id': knowledge_base_id})
            return result.scalar() or 0
            
        except Exception as e:
            print(f"统计embedding向量数量失败: {str(e)}")
            return 0
