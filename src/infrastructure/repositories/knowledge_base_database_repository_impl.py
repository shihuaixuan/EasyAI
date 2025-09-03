"""
知识库仓储PostgreSQL实现
"""

from typing import List, Optional, Dict, Any
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
            
            # 确保配置是JSON可序列化的
            config_to_save = knowledge_base.config or {}
            if not isinstance(config_to_save, dict):
                config_to_save = {}
            
            print(f"开始更新知识库 {kb_id}, 配置: {config_to_save}")
            
            # 执行更新（添加超时处理）
            stmt = update(DatasetModel).where(
                DatasetModel.id == kb_id
            ).values(
                name=knowledge_base.name,
                description=knowledge_base.description,
                embedding_model_config=config_to_save,
                updated_at=datetime.now()
            )
            
            print(f"正在执行SQL更新语句...")
            
            # 使用asyncio.wait_for添加超时控制
            import asyncio
            try:
                result = await asyncio.wait_for(
                    self.session.execute(stmt), 
                    timeout=30.0  # 30秒超时
                )
                print(f"SQL执行完成，影响行数: {result.rowcount}")
            except asyncio.TimeoutError:
                print(f"错误：SQL执行超时，可能存在数据库锁等待")
                await self.session.rollback()
                raise ValueError(f"数据库更新超时，可能存在锁冲突或长时间事务")
            
            # 检查是否更新成功
            if result.rowcount == 0:
                raise ValueError(f"更新失败：找不到ID为{kb_id}的知识库")
            
            # 更新实体的时间戳
            knowledge_base.updated_at = datetime.now()
            
            print(f"数据库更新成功，直接返回结果")
            
            # 直接返回更新后的实体，不进行数据库验证查询（避免锁等待）
            return knowledge_base
            
        except (ValueError, TypeError) as e:
            print(f"类型错误: {str(e)}")
            raise ValueError(f"更新知识库失败: {str(e)}")
        except Exception as e:
            print(f"简化更新异常: {str(e)}")
            raise ValueError(f"数据库操作失败: {str(e)}")
    
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
        # 确保配置是字典格式
        config: Dict[str, Any] = {}
        if hasattr(db_model, 'embedding_model_config') and db_model.embedding_model_config is not None:
            try:
                if isinstance(db_model.embedding_model_config, dict):
                    config = dict(db_model.embedding_model_config)
                else:
                    # 如果不是字典，尝试解析为JSON
                    import json
                    if isinstance(db_model.embedding_model_config, str):
                        config = json.loads(db_model.embedding_model_config)
                    else:
                        config = {}
            except Exception as e:
                print(f"警告：解析配置失败 - {str(e)}, 使用空配置")
                config = {}
        
        return KnowledgeBase(
            knowledge_base_id=str(db_model.id),
            name=str(getattr(db_model, 'name', '')),
            description=str(getattr(db_model, 'description', '')),
            owner_id=str(getattr(db_model, 'user_id', '')),
            config=config,
            is_active=not bool(getattr(db_model, 'is_deleted', False)),
            created_at=getattr(db_model, 'created_at', None),
            updated_at=getattr(db_model, 'updated_at', None)
        )