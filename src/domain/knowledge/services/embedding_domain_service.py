"""
知识库领域 - Embedding领域服务
"""
import asyncio
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

from ..entities.document_chunk import DocumentChunk
from ..entities.knowledge_base import KnowledgeBase
from ...model.services.embedding.base import BaseEmbedding


class EmbeddingDomainService:
    """Embedding领域服务"""
    
    def __init__(self, embedding_service: BaseEmbedding):
        """
        初始化Embedding领域服务
        
        Args:
            embedding_service: Embedding服务实例
        """
        self.embedding_service = embedding_service
    
    async def generate_chunk_embeddings(
        self, 
        chunks: List[DocumentChunk]
    ) -> List[DocumentChunk]:
        """
        为文档分块生成embedding向量
        
        Args:
            chunks: 文档分块列表
            
        Returns:
            包含向量的文档分块列表
        """
        if not chunks:
            return []
        
        # 提取需要生成向量的分块
        chunks_to_process = [chunk for chunk in chunks if not chunk.has_vector()]
        
        if not chunks_to_process:
            return chunks
        
        try:
            # 批量生成embedding
            texts = [chunk.content for chunk in chunks_to_process]
            embeddings = await self.embedding_service.embed_texts(texts)
            
            # 设置向量
            for chunk, embedding in zip(chunks_to_process, embeddings):
                chunk.set_vector(embedding)
            
            return chunks
            
        except Exception as e:
            raise Exception(f"生成embedding向量失败: {str(e)}")
    
    async def generate_single_chunk_embedding(
        self, 
        chunk: DocumentChunk
    ) -> DocumentChunk:
        """
        为单个文档分块生成embedding向量
        
        Args:
            chunk: 文档分块
            
        Returns:
            包含向量的文档分块
        """
        if chunk.has_vector():
            return chunk
        
        try:
            embedding = await self.embedding_service.embed_text(chunk.content)
            chunk.set_vector(embedding)
            return chunk
            
        except Exception as e:
            raise Exception(f"生成单个分块embedding向量失败: {str(e)}")
    
    async def regenerate_chunk_embeddings(
        self, 
        chunks: List[DocumentChunk]
    ) -> List[DocumentChunk]:
        """
        重新生成文档分块的embedding向量（强制覆盖现有向量）
        
        Args:
            chunks: 文档分块列表
            
        Returns:
            包含新向量的文档分块列表
        """
        if not chunks:
            return []
        
        try:
            # 批量生成embedding
            texts = [chunk.content for chunk in chunks]
            embeddings = await self.embedding_service.embed_texts(texts)
            
            # 设置向量（覆盖现有向量）
            for chunk, embedding in zip(chunks, embeddings):
                chunk.set_vector(embedding)
            
            return chunks
            
        except Exception as e:
            raise Exception(f"重新生成embedding向量失败: {str(e)}")
    
    def validate_embedding_requirements(
        self, 
        knowledge_base: KnowledgeBase
    ) -> bool:
        """
        验证知识库是否满足embedding要求
        
        Args:
            knowledge_base: 知识库实体
            
        Returns:
            是否满足要求
        """
        if not knowledge_base.config:
            return False
        
        embedding_config = knowledge_base.config.get('embedding', {})
        return embedding_config.get('strategy') == 'high_quality'
    
    def get_model_name(self) -> str:
        """获取当前使用的模型名称"""
        return self.embedding_service.get_model_name()
    
    async def close(self) -> None:
        """关闭embedding服务资源"""
        if hasattr(self.embedding_service, 'close'):
            close_method = getattr(self.embedding_service, 'close')
            if callable(close_method):
                if asyncio.iscoroutinefunction(close_method):
                    await close_method()
                else:
                    close_method()
