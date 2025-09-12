"""
SQLAlchemy Model仓储实现
"""
from typing import List, Optional
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_

from ....domain.provider.repositories.model_repository import ModelRepository
from ....domain.provider.entities.model import Model
from ....domain.provider.exceptions import ModelAlreadyExistsError, RepositoryError
from ...models.provider_models import ModelModel


class ModelRepositoryImpl(ModelRepository):
    """
    SQLAlchemy Model仓储实现
    """
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def save(self, model: Model) -> Model:
        """保存Model实体"""
        try:
            # 创建数据模型
            model_data = ModelModel(
                model_name=model.model_name,
                type=model.type,
                subtype=model.subtype,
                model_metadata=model.get_metadata_json(),
                provider_name=model.provider_name,
                is_delete=model.is_delete,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # 保存到数据库
            self._session.add(model_data)
            await self._session.commit()
            await self._session.refresh(model_data)
            
            # 转换回领域实体
            return self._convert_to_entity(model_data)
            
        except IntegrityError as e:
            await self._session.rollback()
            if 'unique_provider_model' in str(e):
                raise ModelAlreadyExistsError(model.provider_name, model.model_name)
            raise RepositoryError(f"数据库完整性错误: {str(e)}")
        except Exception as e:
            await self._session.rollback()
            raise RepositoryError(f"保存Model失败: {str(e)}")
    
    async def find_by_id(self, model_id: str) -> Optional[Model]:
        """根据ID查找Model"""
        try:
            stmt = select(ModelModel).where(ModelModel.id == model_id)
            result = await self._session.execute(stmt)
            model_data = result.scalar_one_or_none()
            
            return self._convert_to_entity(model_data) if model_data else None
            
        except Exception as e:
            raise RepositoryError(f"查找Model失败: {str(e)}")
    
    async def find_by_provider_and_name(self, provider_name: str, model_name: str) -> Optional[Model]:
        """根据提供商名称和模型名称查找Model"""
        try:
            stmt = select(ModelModel).where(
                and_(
                    ModelModel.provider_name == provider_name,
                    ModelModel.model_name == model_name
                )
            )
            result = await self._session.execute(stmt)
            model_data = result.scalar_one_or_none()
            
            return self._convert_to_entity(model_data) if model_data else None
            
        except Exception as e:
            raise RepositoryError(f"查找Model失败: {str(e)}")
    
    async def find_provider_name_by_model_name(self, model_name: str) -> Optional[str]:
        """根据模型名称查找提供商名称"""
        try:
            stmt = select(ModelModel.provider_name).where(ModelModel.model_name == model_name)
            result = await self._session.execute(stmt)
            provider_name = result.scalar_one_or_none()
            
            return provider_name
            
        except Exception as e:
            raise RepositoryError(f"查找Model的Provider名称失败: {str(e)}")

    async def find_by_provider_name(self, provider_name: str) -> List[Model]:
        """根据提供商名称查找所有Model"""
        try:
            stmt = select(ModelModel).where(ModelModel.provider_name == provider_name)
            result = await self._session.execute(stmt)
            model_data_list = result.scalars().all()
            
            return [self._convert_to_entity(model_data) for model_data in model_data_list]
            
        except Exception as e:
            raise RepositoryError(f"查找Provider的Model列表失败: {str(e)}")
    
    async def find_by_type(self, model_type: str) -> List[Model]:
        """根据模型类型查找Model"""
        try:
            stmt = select(ModelModel).where(ModelModel.type == model_type.lower())
            result = await self._session.execute(stmt)
            model_data_list = result.scalars().all()
            
            return [self._convert_to_entity(model_data) for model_data in model_data_list]
            
        except Exception as e:
            raise RepositoryError(f"按类型查找Model失败: {str(e)}")
    
    async def update(self, model: Model) -> Model:
        """更新Model实体"""
        try:
            # 查找现有记录
            stmt = select(ModelModel).where(ModelModel.id == model.id)
            result = await self._session.execute(stmt)
            model_data = result.scalar_one_or_none()
            
            if not model_data:
                raise RepositoryError(f"Model不存在: ID={model.id}")
            
            # 更新字段
            model_data.model_name = model.model_name  # type: ignore
            model_data.type = model.type  # type: ignore
            model_data.subtype = model.subtype  # type: ignore
            model_data.model_metadata = model.get_metadata_json()  # type: ignore
            model_data.is_delete = model.is_delete  # type: ignore
            model_data.updated_at = datetime.now()  # type: ignore
            
            # 提交更改
            await self._session.commit()
            await self._session.refresh(model_data)
            
            return self._convert_to_entity(model_data)
            
        except Exception as e:
            await self._session.rollback()
            raise RepositoryError(f"更新Model失败: {str(e)}")
    
    async def delete(self, model_id: int) -> bool:
        """删除Model"""
        try:
            stmt = select(ModelModel).where(ModelModel.id == model_id)
            result = await self._session.execute(stmt)
            model_data = result.scalar_one_or_none()
            
            if not model_data:
                return False
            
            await self._session.delete(model_data)
            await self._session.commit()
            return True
            
        except Exception as e:
            await self._session.rollback()
            raise RepositoryError(f"删除Model失败: {str(e)}")
    
    async def exists(self, provider_name: str, model_name: str) -> bool:
        """检查Model是否存在"""
        try:
            stmt = select(ModelModel.id).where(
                and_(
                    ModelModel.provider_name == provider_name,
                    ModelModel.model_name == model_name
                )
            )
            result = await self._session.execute(stmt)
            return result.scalar_one_or_none() is not None
            
        except Exception as e:
            raise RepositoryError(f"检查Model存在性失败: {str(e)}")
    
    def _convert_to_entity(self, model_data: ModelModel) -> Model:
        """将数据模型转换为领域实体"""
        model = Model(
            provider_name=model_data.provider_name,  # type: ignore
            model_name=model_data.model_name,  # type: ignore
            type=model_data.type,  # type: ignore
            subtype=model_data.subtype,  # type: ignore
            metadata=model_data.get_metadata_dict(),
            id=model_data.id,  # type: ignore
            is_delete=model_data.is_delete,  # type: ignore
            created_at=model_data.created_at,  # type: ignore
            updated_at=model_data.updated_at  # type: ignore
        )
        
        return model