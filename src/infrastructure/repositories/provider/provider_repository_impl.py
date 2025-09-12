"""
SQLAlchemy Provider仓储实现
"""
from sqlalchemy.ext.asyncio.session import AsyncSession


from typing import List, Optional
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_

from ....domain.provider.repositories.provider_repository import ProviderRepository
from ....domain.provider.entities.provider import Provider
from ....domain.provider.value_objects.api_key import ApiKey
from ....domain.provider.value_objects.base_url import BaseUrl
from ....domain.provider.exceptions import ProviderAlreadyExistsError, RepositoryError
from ...models.provider_models import ProviderModel


class ProviderRepositoryImpl(ProviderRepository):
    """
    SQLAlchemy Provider仓储实现
    """
    
    def __init__(self, session: AsyncSession):
        self._session: AsyncSession = session
    
    async def save(self, provider: Provider) -> Provider:
        """保存Provider实体"""
        try:
            # 创建数据模型
            provider_model = ProviderModel(
                user_id=provider.user_id,
                provider=provider.provider,
                api_key=provider.api_key.encrypted_value,
                base_url=str(provider.base_url) if not provider.base_url.is_empty() else None,
                is_delete=provider.is_delete,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # 保存到数据库
            self._session.add(provider_model)
            await self._session.commit()
            await self._session.refresh(provider_model)
            
            # 转换回领域实体
            return self._convert_to_entity(provider_model)
            
        except IntegrityError as e:
            await self._session.rollback()
            if 'unique_user_provider' in str(e):
                raise ProviderAlreadyExistsError(provider.user_id, provider.provider)
            raise RepositoryError(f"数据库完整性错误: {str(e)}")
        except Exception as e:
            await self._session.rollback()
            raise RepositoryError(f"保存Provider失败: {str(e)}")
    
    async def find_by_id(self, provider_id: str) -> Optional[Provider]:
        """根据ID查找Provider（只返回未删除的记录）"""
        try:
            stmt = select(ProviderModel).where(
                and_(
                    ProviderModel.id == provider_id,
                    ProviderModel.is_delete == 0
                )
            )
            result = await self._session.execute(stmt)
            provider_model = result.scalar_one_or_none()
            
            return self._convert_to_entity(provider_model) if provider_model else None
            
        except Exception as e:
            raise RepositoryError(f"查找Provider失败: {str(e)}")
    
    async def find_by_user_and_provider(self, user_id: str, provider_name: str) -> Optional[Provider]:
        """根据用户ID和提供商名称查找Provider（只返回未删除的记录）"""
        try:
            stmt = select(ProviderModel).where(
                and_(
                    ProviderModel.user_id == user_id,
                    ProviderModel.provider == provider_name.lower(),
                    ProviderModel.is_delete == 0
                )
            )
            result = await self._session.execute(stmt)
            provider_model = result.scalar_one_or_none()
            
            return self._convert_to_entity(provider_model) if provider_model else None
            
        except Exception as e:
            raise RepositoryError(f"查找Provider失败: {str(e)}")
    
    async def find_by_user_id(self, user_id: str) -> List[Provider]:
        """根据用户ID查找所有Provider（只返回未删除的记录）"""
        try:
            stmt = select(ProviderModel).where(
                and_(
                    ProviderModel.user_id == user_id,
                    ProviderModel.is_delete == 0
                )
            )
            result = await self._session.execute(stmt)
            provider_models = result.scalars().all()
            
            return [self._convert_to_entity(model) for model in provider_models]
            
        except Exception as e:
            raise RepositoryError(f"查找用户Provider列表失败: {str(e)}")
    
    async def update(self, provider: Provider) -> Provider:
        """更新Provider实体"""
        try:
            # 查找现有记录
            stmt = select(ProviderModel).where(ProviderModel.id == provider.id)
            result = await self._session.execute(stmt)
            provider_model = result.scalar_one_or_none()
            
            if not provider_model:
                raise RepositoryError(f"Provider不存在: ID={provider.id}")
            
            # 更新字段
            provider_model.api_key = provider.api_key.encrypted_value  # type: ignore
            provider_model.base_url = str(provider.base_url) if not provider.base_url.is_empty() else None  # type: ignore
            provider_model.is_delete = provider.is_delete  # type: ignore
            provider_model.updated_at = datetime.now()  # type: ignore
            
            # 提交更改
            await self._session.commit()
            await self._session.refresh(provider_model)
            
            return self._convert_to_entity(provider_model)
            
        except Exception as e:
            await self._session.rollback()
            raise RepositoryError(f"更新Provider失败: {str(e)}")
    
    async def delete(self, provider_id: str) -> bool:
        """软删除Provider（设置is_delete=1）"""
        try:
            stmt = select(ProviderModel).where(
                and_(
                    ProviderModel.id == provider_id,
                    ProviderModel.is_delete == 0
                )
            )
            result = await self._session.execute(stmt)
            provider_model = result.scalar_one_or_none()
            
            if not provider_model:
                return False
            
            provider_model.is_delete = 1  # type: ignore
            provider_model.updated_at = datetime.now()  # type: ignore
            await self._session.commit()
            return True
            
        except Exception as e:
            await self._session.rollback()
            raise RepositoryError(f"删除Provider失败: {str(e)}")
    
    async def exists(self, user_id: str, provider_name: str) -> bool:
        """检查Provider是否存在（只检查未删除的记录）"""
        try:
            stmt = select(ProviderModel.id).where(
                and_(
                    ProviderModel.user_id == user_id,
                    ProviderModel.provider == provider_name.lower(),
                    ProviderModel.is_delete == 0
                )
            )
            result = await self._session.execute(stmt)
            return result.scalar_one_or_none() is not None
            
        except Exception as e:
            raise RepositoryError(f"检查Provider存在性失败: {str(e)}")
    
    def _convert_to_entity(self, model: ProviderModel) -> Provider:
        """将数据模型转换为领域实体"""
        api_key = ApiKey.from_encrypted(model.api_key)  # type: ignore
        base_url = BaseUrl.from_string(model.base_url)  # type: ignore
        
        provider = Provider(
            user_id=model.user_id,  # type: ignore
            provider=model.provider,  # type: ignore
            api_key=api_key,
            base_url=base_url,
            id=model.id,  # type: ignore
            is_delete=model.is_delete,  # type: ignore
            created_at=model.created_at,  # type: ignore
            updated_at=model.updated_at  # type: ignore
        )
        
        return provider