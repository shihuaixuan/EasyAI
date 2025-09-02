"""
知识库仓储PostgreSQL实现
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError

from ...domain.knowledge.entities.knowledge_base import KnowledgeBase
from ...domain.knowledge.repositories.knowledge_base_repository import KnowledgeBaseRepository
from ..models.knowledge_models import DatasetModel


class KnowledgeBaseDatabaseRepositoryImpl(KnowledgeBaseRepository):
    """知识库仓储PostgreSQL实现"""
    
    def __init__(self, session: AsyncSession):
        if session is None:
            raise ValueError("Database session cannot be None")
        self.session = session
    
    async def save(self, knowledge_base: KnowledgeBase) -> KnowledgeBase:
        """保存知识库"""
        try:
            # 创建数据库模型实例
            db_model = DatasetModel(
                name=knowledge_base.name,
                user_id=knowledge_base.owner_id or "default_user",
                description=knowledge_base.description,
                embedding_model_id="default",  # 暂时使用默认值
                embedding_model_config=knowledge_base.config or {},
                parser_config={},
                meta={},
                is_public=False,
                is_deleted=False
            )
            
            # 添加到会话并刷新获取ID和时间戳
            self.session.add(db_model)
            await self.session.flush()
            await self.session.refresh(db_model)
            
            # 更新实体的ID和时间戳
            knowledge_base.knowledge_base_id = str(db_model.id)
            # SQLAlchemy 实例的属性是实际值，不是Column类型
            knowledge_base.created_at = db_model.created_at  # type: ignore
            knowledge_base.updated_at = db_model.updated_at  # type: ignore
            
            return knowledge_base
            
        except IntegrityError as e:
            await self.session.rollback()
            raise ValueError(f"保存知识库失败: {str(e)}")
    
    async def find_by_id(self, knowledge_base_id: str) -> Optional[KnowledgeBase]:
        """根据ID查找知识库"""
        try:
            kb_id = int(knowledge_base_id)
            stmt = select(DatasetModel).where(
                DatasetModel.id == kb_id,
                DatasetModel.is_deleted == False
            )
            result = await self.session.execute(stmt)
            db_model = result.scalar_one_or_none()
            
            if db_model is None:
                return None
            
            return self._convert_to_entity(db_model)
            
        except (ValueError, TypeError):
            return None
    
    async def find_by_owner_id(self, owner_id: str) -> List[KnowledgeBase]:
        """根据所有者ID查找知识库列表"""
        stmt = select(DatasetModel).where(
            DatasetModel.user_id == owner_id,
            DatasetModel.is_deleted == False
        ).order_by(DatasetModel.created_at.desc())
        
        result = await self.session.execute(stmt)
        db_models = result.scalars().all()
        
        return [self._convert_to_entity(db_model) for db_model in db_models]
    
    async def find_active_by_owner_id(self, owner_id: str) -> List[KnowledgeBase]:
        """根据所有者ID查找活跃的知识库列表"""
        # 在这个实现中，我们假设非deleted的即为active
        return await self.find_by_owner_id(owner_id)
    
    async def update(self, knowledge_base: KnowledgeBase) -> KnowledgeBase:
        """更新知识库"""
        try:
            if knowledge_base.knowledge_base_id is None:
                raise ValueError("知识库ID不能为空")
            kb_id = int(knowledge_base.knowledge_base_id)
            
            stmt = update(DatasetModel).where(
                DatasetModel.id == kb_id
            ).values(
                name=knowledge_base.name,
                description=knowledge_base.description,
                embedding_model_config=knowledge_base.config or {},
                updated_at=datetime.now()
            )
            
            await self.session.execute(stmt)
            knowledge_base.updated_at = datetime.now()
            
            return knowledge_base
            
        except (ValueError, TypeError) as e:
            raise ValueError(f"更新知识库失败: {str(e)}")
    
    async def delete_by_id(self, knowledge_base_id: str) -> bool:
        """根据ID删除知识库（软删除）"""
        try:
            kb_id = int(knowledge_base_id)
            
            stmt = update(DatasetModel).where(
                DatasetModel.id == kb_id
            ).values(
                is_deleted=True,
                updated_at=datetime.now()
            )
            
            result = await self.session.execute(stmt)
            return result.rowcount > 0
            
        except (ValueError, TypeError):
            return False
    
    async def exists_by_name_and_owner(self, name: str, owner_id: str) -> bool:
        """检查指定所有者下是否存在同名知识库"""
        stmt = select(DatasetModel.id).where(
            DatasetModel.name == name,
            DatasetModel.user_id == owner_id,
            DatasetModel.is_deleted == False
        )
        
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    async def count_by_owner_id(self, owner_id: str) -> int:
        """统计所有者的知识库数量"""
        stmt = select(DatasetModel.id).where(
            DatasetModel.user_id == owner_id,
            DatasetModel.is_deleted == False
        )
        
        result = await self.session.execute(stmt)
        return len(result.scalars().all())
    
    def _convert_to_entity(self, db_model: DatasetModel) -> KnowledgeBase:
        """将数据库模型转换为领域实体"""
        return KnowledgeBase(
            knowledge_base_id=str(db_model.id),
            name=str(db_model.name),  # type: ignore
            description=str(db_model.description or ""),  # type: ignore
            owner_id=str(db_model.user_id),  # type: ignore
            config=dict(db_model.embedding_model_config or {}),  # type: ignore
            is_active=not bool(db_model.is_deleted),  # type: ignore
            created_at=db_model.created_at,  # type: ignore
            updated_at=db_model.updated_at  # type: ignore
        )