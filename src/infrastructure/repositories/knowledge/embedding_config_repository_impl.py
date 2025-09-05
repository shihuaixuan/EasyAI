"""
基础设施层 - Embedding配置仓储实现
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ....domain.knowledge.repositories.embedding_config_repository import EmbeddingConfigRepository
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
        """
        try:
            print(f"🔍 开始查询embedding配置: knowledge_base_id={knowledge_base_id}, user_id={user_id}")
            
            # 1. 从数据库获取知识库的embedding配置
            stmt = select(DatasetModel.embedding_model_id, DatasetModel.embedding_model_config, DatasetModel.user_id).where(
                DatasetModel.id == knowledge_base_id,
                DatasetModel.is_deleted == False
            )
            result = await self.session.execute(stmt)
            row = result.first()
            
            print(f"📊 数据库查询结果: row={row}")
            
            if not row:
                print(f"❌ 未找到知识库记录: knowledge_base_id={knowledge_base_id}")
                return None
            
            # 检查知识库所有者权限
            if str(row.user_id) != str(user_id):
                print(f"❌ 用户权限不匹配: 知识库所有者={row.user_id}, 请求用户={user_id}")
                return None
            
            embedding_model_id = row.embedding_model_id
            embedding_model_config = row.embedding_model_config or {}
            
            print(f"📋 找到embedding配置: model_id={embedding_model_id}, config={embedding_model_config}")
            
            # 2. 处理不同的embedding_model_id情况
            if embedding_model_id == "default" or not embedding_model_id:
                # 使用embedding_model_config中的配置
                embedding_config = embedding_model_config.get('embedding', {})
                
                if not embedding_config:
                    print(f"❌ embedding_model_config中没有embedding配置")
                    return None
                
                model_name = embedding_config.get('model_name')
                strategy = embedding_config.get('strategy')
                
                print(f"📋 使用配置文件中的embedding设置: model_name={model_name}, strategy={strategy}")
                
                # 根据模型名称推断提供商
                provider = self._infer_provider_from_model_name(model_name)
                
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
                
                print(f"✅ 成功构建embedding配置: {config.model_name} ({config.provider})")
                return config
                
            else:
                # 尝试通过embedding_model_id查找数据库中的模型配置
                try:
                    model = await self.model_repo.find_by_id(embedding_model_id)
                    if not model:
                        print(f"❌ 未找到模型记录: model_id={embedding_model_id}，使用默认配置")
                        return None
                    
                    print(f"📋 找到模型信息: model_name={model.model_name}")
                    
                    # 获取提供商信息
                    provider = await self.provider_repo.find_by_id(model.provider_id)
                    if not provider:
                        print(f"❌ 未找到提供商记录: provider_id={model.provider_id}")
                        return None
                    
                    # 验证提供商所有者权限
                    if str(provider.user_id) != str(user_id):
                        print(f"❌ 提供商权限不匹配: 提供商所有者={provider.user_id}, 请求用户={user_id}")
                        return None
                    
                    print(f"📋 找到提供商信息: provider={provider.provider}, user_id={provider.user_id}")
                    
                    # 解密API Key
                    decrypted_api_key = None
                    if provider.api_key and provider.api_key.encrypted_value:
                        try:
                            decrypted_api_key = encryption_service.decrypt(provider.api_key.encrypted_value)
                            print(f"✅ API Key解密成功")
                        except Exception as e:
                            print(f"❌ 解密API Key失败: {str(e)}")
                            decrypted_api_key = None
                    else:
                        print(f"⚠️  提供商没有配置API Key")
                    
                    # 构建配置对象
                    config = EmbeddingModelConfig(
                        model_id=model.id,
                        model_name=model.model_name,
                        provider=provider.provider,
                        api_key=decrypted_api_key,
                        base_url=provider.base_url.value if provider.base_url and not provider.base_url.is_empty() else None,
                        strategy=embedding_model_config.get('embedding', {}).get('strategy', 'high_quality'),
                        batch_size=embedding_model_config.get('batch_size', 32),
                        max_tokens=embedding_model_config.get('max_tokens', 8192),
                        timeout=embedding_model_config.get('timeout', 30),
                    )
                    
                    print(f"✅ 成功构建embedding配置: {config.model_name} ({config.provider})")
                    return config
                    
                except Exception as e:
                    print(f"❌ 处理数据库模型配置失败: {str(e)}，使用默认配置")
                    return None
            
        except Exception as e:
            print(f"获取embedding配置失败: {str(e)}")
            return None
    
    async def get_default_embedding_config(self) -> EmbeddingModelConfig:
        """
        获取默认的embedding配置
        """
        # 尝试从数据库获取任何用户的SiliconFlow配置作为默认配置
        try:
            from sqlalchemy import text
            result = await self.session.execute(text("""
                SELECT api_key, base_url 
                FROM providers 
                WHERE provider = 'siliconflow'
                LIMIT 1
            """))
            
            provider_row = result.fetchone()
            decrypted_api_key = None
            base_url = 'https://api.siliconflow.cn/v1'
            
            if provider_row and provider_row.api_key:
                try:
                    decrypted_api_key = encryption_service.decrypt(provider_row.api_key)
                    if provider_row.base_url:
                        base_url = provider_row.base_url
                except Exception as e:
                    print(f"解密默认API Key失败: {str(e)}")
                    decrypted_api_key = None
            
            return EmbeddingModelConfig(
                model_id=0,
                model_name='BAAI/bge-large-zh-v1.5',
                provider='siliconflow',
                api_key=decrypted_api_key,
                base_url=base_url,
                strategy='high_quality',
                batch_size=32,
                max_tokens=8192,
                timeout=30,
            )
            
        except Exception as e:
            print(f"获取默认embedding配置失败: {str(e)}")
            # 如果数据库查询失败，返回基本配置
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
    
    def _infer_provider_from_model_name(self, model_name: str) -> str:
        """
        根据模型名称推断提供商
        """
        if 'text-embedding' in model_name.lower():
            return 'openai'
        elif 'bge-' in model_name.lower() or 'baai/' in model_name.lower():
            return 'siliconflow'
        elif 'm3e-' in model_name.lower():
            return 'local'
        else:
            # 默认使用siliconflow
            return 'siliconflow'
    
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