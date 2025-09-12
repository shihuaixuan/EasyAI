"""
基础设施层 - Embedding配置仓储实现
"""
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ....domain.knowledge.repositories.embedding_config_repository import EmbeddingConfigRepository
from ....domain.knowledge.vo.embedding_config import EmbeddingModelConfig
from ....infrastructure.repositories.model.model_repository_impl import ModelRepositoryImpl
from ....infrastructure.repositories.provider.provider_repository_impl import ProviderRepositoryImpl
from ....infrastructure.models.knowledge_models import DatasetModel
from ....infrastructure.security.encryption import encryption_service

logging.basicConfig(level=logging.DEBUG)


class EmbeddingConfigRepositoryImpl(EmbeddingConfigRepository):
    """Embedding配置仓储实现"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model_repo = ModelRepositoryImpl(session)
        self.provider_repo = ProviderRepositoryImpl(session)
    
    async def get_embedding_config_by_knowledge_base_id(
        self, 
        knowledge_base_id: str,
        user_id: str
    ) -> Optional[EmbeddingModelConfig]:
        """
        根据知识库ID获取embedding配置
        """
        try:
            logging.info(f"🔍 开始查询embedding配置: knowledge_base_id={knowledge_base_id}, user_id={user_id}")
            
            # 1. 从数据库获取知识库的embedding配置
            stmt = select(DatasetModel.embedding_model_id, DatasetModel.embedding_model_config, DatasetModel.user_id).where(
                DatasetModel.id == knowledge_base_id,
                DatasetModel.is_deleted == False,
                DatasetModel.user_id == user_id
            )
            result = await self.session.execute(stmt)
            row = result.first()
            
            logging.info(f"📊 数据库查询结果: row={row}")
            
            if not row:
                logging.debug(f"❌ 未找到知识库记录: knowledge_base_id={knowledge_base_id}")
                return None
            
            embedding_model_config = row.embedding_model_config
            embedding_config = embedding_model_config.get('embedding', {})
            if embedding_config is None:
                logging.error(f"❌ embedding_model_config中没有embedding配置")
                return None
            
            # 2. 处理embedding配置
            if embedding_config.get('model_name') is not None:
                
                model_name = embedding_config.get('model_name')
                strategy = embedding_config.get('strategy')
                
                logging.info(f"📋 使用配置文件中的embedding设置: model_name={model_name}, strategy={strategy}")
                
                # 根据模型名称去查提供商
                provider = self._get_provider_name_by_model_name(model_name)
                if provider is None:
                    logging.error(f"❌ 未找到模型的提供商: model_name={model_name}")
                    return None

                # 从数据库获取该用户的提供商配置
                api_key, base_url = await self._get_provider_config_from_db(provider, user_id)
                
                # 构建配置对象
                config = EmbeddingModelConfig(
                    model_id=0,  # 使用0表示配置文件中的模型
                    model_name=model_name,
                    provider=provider,
                    api_key=api_key,
                    base_url=base_url or self._get_default_base_url(provider),
                    strategy=strategy,
                    batch_size=embedding_model_config.get('batch_size', 32),
                    max_tokens=embedding_model_config.get('max_tokens', 8192),
                    timeout=embedding_model_config.get('timeout', 30),
                )
                
                logging.info(f"✅ 成功构建embedding配置: {config.model_name} ({config.provider})")
                return config
            
        except Exception as e:
            logging.error(f"获取embedding配置失败: {str(e)}")
            return None
    
    def _get_default_base_url(self, provider: str) -> str:
        """
        获取提供商的默认Base URL
        """
        provider_urls = {
            'openai': 'https://api.openai.com/v1',
            'siliconflow': 'https://api.siliconflow.cn/v1',
            'deepseek': 'https://api.deepseek.com/v1',
            'anthropic': 'https://api.anthropic.com',
            'local': 'http://localhost:8000'
        }
        return provider_urls.get(provider, 'https://api.siliconflow.cn/v1')
    
    async def _get_provider_name_by_model_name(self, model_name: str) -> str:
        """
        根据模型名称获取提供商名称
        """
        try:
            provider_name = await self.model_repo.find_provider_name_by_model_name(model_name)
            return provider_name
        except Exception as e:
            print(f"❌ 根据模型名称获取提供商名称失败: {str(e)}")
            return None
        

    async def _get_provider_config_from_db(self, provider: str, user_id: str) -> tuple[Optional[str], Optional[str]]:
        """
        从数据库获取提供商配置
        
        Args:
            provider: 提供商名称
            user_id: 用户ID
            
        Returns:
            tuple[api_key, base_url]: API Key和Base URL
        """
        try:
            # 查找该用户的指定提供商配置
            provider_entity = await self.provider_repo.find_by_user_and_provider(user_id, provider)
            
            if not provider_entity:
                print(f"⚠️  用户 {user_id} 没有配置 {provider} 提供商")
                return None, None
            
            # 解密API Key
            decrypted_api_key = None
            if provider_entity.api_key and provider_entity.api_key.encrypted_value:
                try:
                    decrypted_api_key = encryption_service.decrypt(provider_entity.api_key.encrypted_value)
                    print(f"✅ 从数据库获取到 {provider} 的API Key")
                except Exception as e:
                    print(f"❌ 解密 {provider} API Key失败: {str(e)}")
                    decrypted_api_key = None
            else:
                print(f"⚠️  {provider} 提供商没有配置API Key")
            
            # 获取Base URL
            base_url = provider_entity.base_url.value if provider_entity.base_url and not provider_entity.base_url.is_empty() else None
            
            return decrypted_api_key, base_url
            
        except Exception as e:
            print(f"❌ 从数据库获取 {provider} 配置失败: {str(e)}")
            return None, None