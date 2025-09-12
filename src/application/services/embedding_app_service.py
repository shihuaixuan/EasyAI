"""
应用层 - Embedding应用服务
"""
import asyncio
import logging
import os
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.knowledge.entities.document_chunk import DocumentChunk
from ...domain.knowledge.repositories.embedding_config_repository import EmbeddingConfigRepository
from ...domain.knowledge.repositories.document_chunk_repository import DocumentChunkRepository
from ...domain.knowledge.services.embedding_domain_service import EmbeddingDomainService
from ...domain.knowledge.vo.embedding_config import EmbeddingModelConfig, EmbeddingProcessResult
from ...domain.model.services.embedding.factory import create_embedding
from ...infrastructure.database import get_async_session
from ...infrastructure.repositories.knowledge.embedding_config_repository_impl import EmbeddingConfigRepositoryImpl
from ...infrastructure.repositories.knowledge.document_chunk_repository_impl import DocumentChunkRepositoryImpl

logging.basicConfig(level=logging.DEBUG)

class EmbeddingApplicationService:
    """Embedding应用服务"""
    
    def __init__(
        self,
        embedding_config_repo: EmbeddingConfigRepository,
        document_chunk_repo: DocumentChunkRepository
    ):
        self.embedding_config_repo = embedding_config_repo
        self.document_chunk_repo = document_chunk_repo
    
    async def process_document_embeddings(
        self, 
        knowledge_base_id: str, 
        document_id: str,
        user_id: str
    ) -> EmbeddingProcessResult:
        """
        处理文档的embedding
        
        Args:
            knowledge_base_id: 知识库ID
            document_id: 文档ID
            user_id: 用户ID
            
        Returns:
            处理结果
        """
        try:
            # 1. 获取文档分块
            chunks = await self.document_chunk_repo.find_by_document_id(document_id)
            
            if not chunks:
                logging.info(f"❌ 文档 {document_id} 没有分块数据")
                return EmbeddingProcessResult.failure_result(
                    f"文档 {document_id} 没有分块数据"
                )
            
            logging.info(f"📊 找到 {len(chunks)} 个分块需要处理embedding")
            
            # 2. 获取embedding配置
            logging.info(f"🔍 开始获取embedding配置: knowledge_base_id={knowledge_base_id}, user_id={user_id}")
            embedding_config = await self.embedding_config_repo.get_embedding_config_by_knowledge_base_id(
                knowledge_base_id, user_id
            )
            
            if not embedding_config:
                logging.error(f"⚠️  未找到知识库专用embedding配置，使用默认配置")
            
            # 3. 创建embedding领域服务
            logging.info(f"🔧 正在创建embedding服务...")
            embedding_domain_service = await self._create_embedding_domain_service(embedding_config)
            if not embedding_domain_service:
                logging.error(f"❌ 无法创建embedding服务，请检查配置")
                return EmbeddingProcessResult.failure_result("无法创建embedding服务")
            
            logging.info(f"✅ Embedding服务创建成功")
            
            try:
                # 4. 处理embedding
                processed_count = 0
                failed_count = 0
                
                for i, chunk in enumerate(chunks, 1):
                    try:
                        
                        logging.info(f"🔄 处理分块 {i}/{len(chunks)} (索引: {chunk.chunk_index})")
                        
                        # 生成embedding向量
                        updated_chunk = await embedding_domain_service.generate_single_chunk_embedding(chunk)
                        
                        # 保存更新的分块
                        await self.document_chunk_repo.update(updated_chunk)
                        
                        processed_count += 1
                        logging.info(f"✅ 分块 {i} 向量生成并保存成功")
                        
                    except Exception as chunk_error:
                        logging.error(f"❌ 分块 {chunk.chunk_index} 生成向量失败: {str(chunk_error)}")
                        failed_count += 1
                        continue
                
                return EmbeddingProcessResult.success_result(
                    processed_count, failed_count, embedding_domain_service.get_model_name()
                )
                
            finally:
                # 清理资源
                await embedding_domain_service.close()
                
        except Exception as e:
            logging.error(f"处理文档embedding失败: {str(e)}")
            return EmbeddingProcessResult.failure_result(f"处理失败: {str(e)}")
    
    async def process_knowledge_base_embeddings(
        self, 
        knowledge_base_id: str,
        user_id: str
    ) -> EmbeddingProcessResult:
        """
        处理整个知识库的embedding
        
        Args:
            knowledge_base_id: 知识库ID
            user_id: 用户ID
            
        Returns:
            处理结果
        """
        try:
            # 1. 获取所有需要处理的分块
            chunks_without_vectors = await self.document_chunk_repo.find_chunks_without_vectors(knowledge_base_id)
            
            if not chunks_without_vectors:
                return EmbeddingProcessResult.success_result(0, 0, "所有分块都已有向量")
            
            # 2. 获取embedding配置
            embedding_config = await self.embedding_config_repo.get_embedding_config_by_knowledge_base_id(
                knowledge_base_id, user_id
            )
            
            if not embedding_config:
                embedding_config = await self.embedding_config_repo.get_default_embedding_config()
            
            # 3. 创建embedding领域服务
            embedding_domain_service = await self._create_embedding_domain_service(embedding_config)
            if not embedding_domain_service:
                return EmbeddingProcessResult.failure_result("无法创建embedding服务")
            
            try:
                # 4. 批量处理embedding
                processed_count = 0
                failed_count = 0
                batch_size = embedding_config.batch_size
                
                for i in range(0, len(chunks_without_vectors), batch_size):
                    batch_chunks = chunks_without_vectors[i:i + batch_size]
                    
                    try:
                        # 批量生成embedding
                        updated_chunks = await embedding_domain_service.generate_chunk_embeddings(batch_chunks)
                        
                        # 批量保存更新的分块
                        for chunk in updated_chunks:
                            try:
                                await self.document_chunk_repo.update(chunk)
                                processed_count += 1
                            except Exception as update_error:
                                print(f"更新分块 {chunk.chunk_index} 失败: {str(update_error)}")
                                failed_count += 1
                        
                        print(f"批次处理完成: {len(batch_chunks)} 个分块")
                        
                    except Exception as batch_error:
                        print(f"批次处理失败: {str(batch_error)}")
                        failed_count += len(batch_chunks)
                        continue
                
                return EmbeddingProcessResult.success_result(
                    processed_count, failed_count, embedding_domain_service.get_model_name()
                )
                
            finally:
                # 清理资源
                await embedding_domain_service.close()
                
        except Exception as e:
            print(f"处理知识库embedding失败: {str(e)}")
            return EmbeddingProcessResult.failure_result(f"处理失败: {str(e)}")
    
    async def regenerate_embeddings(
        self, 
        knowledge_base_id: str,
        user_id: str,
        document_id: Optional[str] = None
    ) -> EmbeddingProcessResult:
        """
        重新生成embedding（强制覆盖现有向量）
        
        Args:
            knowledge_base_id: 知识库ID
            user_id: 用户ID
            document_id: 文档ID，如果为None则处理整个知识库
            
        Returns:
            处理结果
        """
        try:
            # 1. 获取分块
            if document_id:
                chunks = await self.document_chunk_repo.find_by_document_id(document_id)
            else:
                chunks = await self.document_chunk_repo.find_by_knowledge_base_id(knowledge_base_id)
            
            if not chunks:
                return EmbeddingProcessResult.failure_result("没有找到分块数据")
            
            # 2. 获取embedding配置
            embedding_config = await self.embedding_config_repo.get_embedding_config_by_knowledge_base_id(
                knowledge_base_id, user_id
            )
            
            if not embedding_config:
                embedding_config = await self.embedding_config_repo.get_default_embedding_config()
            
            # 3. 创建embedding领域服务
            embedding_domain_service = await self._create_embedding_domain_service(embedding_config)
            if not embedding_domain_service:
                return EmbeddingProcessResult.failure_result("无法创建embedding服务")
            
            try:
                # 4. 重新生成embedding
                updated_chunks = await embedding_domain_service.regenerate_chunk_embeddings(chunks)
                
                # 5. 保存更新的分块
                processed_count = 0
                failed_count = 0
                
                for chunk in updated_chunks:
                    try:
                        await self.document_chunk_repo.update(chunk)
                        processed_count += 1
                    except Exception as update_error:
                        print(f"更新分块 {chunk.chunk_index} 失败: {str(update_error)}")
                        failed_count += 1
                
                return EmbeddingProcessResult.success_result(
                    processed_count, failed_count, embedding_domain_service.get_model_name()
                )
                
            finally:
                # 清理资源
                await embedding_domain_service.close()
                
        except Exception as e:
            print(f"重新生成embedding失败: {str(e)}")
            return EmbeddingProcessResult.failure_result(f"重新生成失败: {str(e)}")
    
    async def _create_embedding_domain_service(
        self, 
        embedding_config: EmbeddingModelConfig
    ) -> Optional[EmbeddingDomainService]:
        """
        创建embedding领域服务
        
        Args:
            embedding_config: embedding配置
            
        Returns:
            embedding领域服务实例
        """
        try:
            if not embedding_config.is_valid():
                print("embedding配置无效")
                return None
            
            # 创建embedding服务
            service_config = embedding_config.get_embedding_service_config()
            
            # 处理环境变量API密钥
            if embedding_config.provider != 'local' and not service_config.get('api_key'):
                service_config['api_key'] = os.getenv(f'{embedding_config.provider.upper()}_API_KEY')
            
            embedding_service = create_embedding(embedding_config.provider, service_config)
            
            return EmbeddingDomainService(embedding_service)
            
        except Exception as e:
            print(f"创建embedding领域服务失败: {str(e)}")
            return None


# 工厂函数
async def create_embedding_application_service(session: AsyncSession) -> EmbeddingApplicationService:
    """创建embedding应用服务实例"""
    
    embedding_config_repo = EmbeddingConfigRepositoryImpl(session)
    document_chunk_repo = DocumentChunkRepositoryImpl(session)
    
    return EmbeddingApplicationService(embedding_config_repo, document_chunk_repo)
