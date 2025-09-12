from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.exc import IntegrityError

from src.domain.user.repositories.user_repository import UserRepository
from src.domain.user.entities.user import User
from src.domain.user.value_objects import Username, Email, HashedPassword, UserStatus
from src.infrastructure.models.user_models import UserModel


class UserRepositoryImpl(UserRepository):
    """用户仓储SQL实现"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def save(self, user: User) -> User:
        """保存用户"""
        user_model = self._to_model(user)
        
        try:
            self.session.add(user_model)
            await self.session.commit()
            await self.session.refresh(user_model)
            return self._to_entity(user_model)
        except IntegrityError as e:
            await self.session.rollback()
            if 'username' in str(e):
                raise ValueError(f"用户名 '{user.username.value}' 已存在")
            elif 'email' in str(e):
                raise ValueError(f"邮箱 '{user.email.value}' 已存在")
            else:
                raise ValueError("保存用户失败：数据完整性错误")
        except Exception as e:
            await self.session.rollback()
            raise ValueError(f"保存用户失败: {str(e)}")
    
    async def find_by_id(self, user_id: str) -> Optional[User]:
        """根据ID查找用户"""
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()
        
        return self._to_entity(user_model) if user_model else None
    
    async def find_by_username(self, username: Username) -> Optional[User]:
        """根据用户名查找用户"""
        stmt = select(UserModel).where(UserModel.username == username.value)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()
        
        return self._to_entity(user_model) if user_model else None
    
    async def find_by_email(self, email: Email) -> Optional[User]:
        """根据邮箱查找用户"""
        stmt = select(UserModel).where(UserModel.email == email.value)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()
        
        return self._to_entity(user_model) if user_model else None
    
    async def find_by_username_or_email(self, username_or_email: str) -> Optional[User]:
        """根据用户名或邮箱查找用户"""
        stmt = select(UserModel).where(
            or_(
                UserModel.username == username_or_email,
                UserModel.email == username_or_email
            )
        )
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()
        
        return self._to_entity(user_model) if user_model else None
    
    async def exists_by_username(self, username: Username) -> bool:
        """检查用户名是否存在"""
        stmt = select(UserModel.id).where(UserModel.username == username.value)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    async def exists_by_email(self, email: Email) -> bool:
        """检查邮箱是否存在"""
        stmt = select(UserModel.id).where(UserModel.email == email.value)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    async def update(self, user: User) -> User:
        """更新用户"""
        stmt = select(UserModel).where(UserModel.id == user.id)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()
        
        if not user_model:
            raise ValueError(f"用户不存在: {user.id}")
        
        # 更新字段
        user_model.username = user.username.value
        user_model.email = user.email.value
        user_model.password_hash = user.password_hash.hash_value
        user_model.status = int(user.status)
        user_model.updated_at = user.updated_at
        
        try:
            await self.session.commit()
            await self.session.refresh(user_model)
            return self._to_entity(user_model)
        except IntegrityError as e:
            await self.session.rollback()
            if 'username' in str(e):
                raise ValueError(f"用户名 '{user.username.value}' 已存在")
            elif 'email' in str(e):
                raise ValueError(f"邮箱 '{user.email.value}' 已存在")
            else:
                raise ValueError("更新用户失败：数据完整性错误")
        except Exception as e:
            await self.session.rollback()
            raise ValueError(f"更新用户失败: {str(e)}")
    
    async def delete(self, user_id: str) -> bool:
        """删除用户"""
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()
        
        if not user_model:
            return False
        
        try:
            await self.session.delete(user_model)
            await self.session.commit()
            return True
        except Exception as e:
            await self.session.rollback()
            raise ValueError(f"删除用户失败: {str(e)}")
    
    async def find_all(self, limit: int = 100, offset: int = 0) -> List[User]:
        """查找所有用户（分页）"""
        stmt = select(UserModel).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        user_models = result.scalars().all()
        
        return [self._to_entity(model) for model in user_models]
    
    def _to_entity(self, model: UserModel) -> User:
        """将数据库模型转换为领域实体"""
        return User(
            id=model.id,
            username=Username.create(model.username),
            email=Email.create(model.email),
            password_hash=HashedPassword.create(model.password_hash),
            status=UserStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at
        )
    
    def _to_model(self, entity: User) -> UserModel:
        """将领域实体转换为数据库模型"""
        return UserModel(
            id=entity.id,
            username=entity.username.value,
            email=entity.email.value,
            password_hash=entity.password_hash.hash_value,
            status=int(entity.status),
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )