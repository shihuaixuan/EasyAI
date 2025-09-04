from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.user import User
from ..value_objects.username import Username
from ..value_objects.email import Email


class UserRepository(ABC):
    """用户仓储接口"""
    
    @abstractmethod
    async def save(self, user: User) -> User:
        """保存用户"""
        pass
    
    @abstractmethod
    async def find_by_id(self, user_id: str) -> Optional[User]:
        """根据ID查找用户"""
        pass
    
    @abstractmethod
    async def find_by_username(self, username: Username) -> Optional[User]:
        """根据用户名查找用户"""
        pass
    
    @abstractmethod
    async def find_by_email(self, email: Email) -> Optional[User]:
        """根据邮箱查找用户"""
        pass
    
    @abstractmethod
    async def find_by_username_or_email(self, username_or_email: str) -> Optional[User]:
        """根据用户名或邮箱查找用户"""
        pass
    
    @abstractmethod
    async def exists_by_username(self, username: Username) -> bool:
        """检查用户名是否存在"""
        pass
    
    @abstractmethod
    async def exists_by_email(self, email: Email) -> bool:
        """检查邮箱是否存在"""
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        """更新用户"""
        pass
    
    @abstractmethod
    async def delete(self, user_id: str) -> bool:
        """删除用户"""
        pass
    
    @abstractmethod
    async def find_all(self, limit: int = 100, offset: int = 0) -> List[User]:
        """查找所有用户（分页）"""
        pass