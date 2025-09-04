"""
基础设施层 - Embedding配置仓储实现
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ....domain.knowledge.repositories.embedding_repository import EmbeddingConfigRepository
from ....domain.knowledge.vo.embedding_config import EmbeddingModelConfig
from ....infrastructure.repositories.model.sql_model_repository import SqlModelRepository
from ....infrastructure.repositories.provider.sql_provider_repository import SqlProviderRepository
from ....infrastructure.models.knowledge_models import DatasetModel
from ....infrastructure.security.encryption import encryption_service


class EmbeddingConfigRepositoryImpl(EmbeddingConfigRepository):
    """Embedding配置仓储实现"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model_repo = SqlModelRepository(session)
        self.provider_repo = SqlProviderRepository(session)
    
    async def get_embedding_config_by_knowledge_base_id(
        self, 
        knowledge_base_id: str,
        user_id: str
    ) -> Optional[EmbeddingModelConfig]:
        """
        根据知识库ID获取embedding配置
        
        Args:
            knowledge_base_id: 知识库ID
            user_id: 用户ID
            
        Returns:
            Embedding配置，如果不存在则返回None
        """
        try:
            # 1. 从数据库获取知识库的embedding_model_id
            stmt = select(DatasetModel.embedding_model_id, DatasetModel.embedding_model_config).where(
                DatasetModel.id == int(knowledge_base_id),
                DatasetModel.is_deleted == False
            )
            result = await self.session.execute(stmt)
            row = result.first()
            
            if not row or not row.embedding_model_id:
                return None
            
            embedding_model_id = row.embedding_model_id
            embedding_model_config = row.embedding_model_config or {}
            
            # 2. 根据embedding_model_id查找模型信息
            model = await self.model_repo.find_by_id(embedding_model_id)
            if not model:
                return None
            
            # 3. 验证用户权限并获取提供商信息
            provider = await self.provider_repo.find_by_id(model.provider_id)
            if not provider or str(provider.user_id) != str(user_id):
                return None
            
            # 4. 解密API Key
            decrypted_api_key = None
            if provider.api_key and provider.api_key.encrypted_value:
                try:
                    decrypted_api_key = encryption_service.decrypt(provider.api_key.encrypted_value)
                except Exception as e:
                    print(f"解密API Key失败: {str(e)}")
                    decrypted_api_key = None
            
            # 5. 构建配置对象
            config = EmbeddingModelConfig(
                model_id=model.id,
                model_name=model.model_name,
                provider=provider.provider,
                api_key=decrypted_api_key,
                base_url=provider.base_url.url if provider.base_url else None,
                strategy=embedding_model_config.get('strategy', 'high_quality'),
                batch_size=embedding_model_config.get('batch_size', 32),
                max_tokens=embedding_model_config.get('max_tokens', 8192),
                timeout=embedding_model_config.get('timeout', 30),
            )
            
            return config
            
        except Exception as e:
            print(f"获取embedding配置失败: {str(e)}")
            return None
    
    async def get_default_embedding_config(self) -> EmbeddingModelConfig:
        """
        获取默认的embedding配置
        
        Returns:
            默认embedding配置
        """
        return EmbeddingModelConfig(
            model_id=0,
            model_name='BAAI/bge-large-zh-v1.5',
            provider='siliconflow',
            api_key=None,  # 将从环境变量获取
            base_url='https://api.siliconflow.cn/v1',
            strategy='high_quality',
            batch_size=32,
            max_tokens=8192,
            timeout=30,
        )
