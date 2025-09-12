from typing import Optional

from src.domain.user.entities.user import User
from src.domain.user.repositories.user_repository import UserRepository
from src.domain.user.value_objects.username import Username
from src.domain.user.value_objects.email import Email
from src.domain.user.value_objects.password import Password


class UserDomainService:
    """用户领域服务 - 处理用户相关的业务规则和验证"""
    
    def __init__(self, user_repository: UserRepository):
        """初始化用户领域服务
        
        Args:
            user_repository: 用户仓储接口
        """
        self._user_repository = user_repository
    
    async def is_username_available(self, username: Username) -> bool:
        """检查用户名是否可用
        
        Args:
            username: 用户名值对象
            
        Returns:
            用户名是否可用（不存在）
        """
        return not await self._user_repository.exists_by_username(username)
    
    async def is_email_available(self, email: Email) -> bool:
        """检查邮箱是否可用
        
        Args:
            email: 邮箱值对象
            
        Returns:
            邮箱是否可用（不存在）
        """
        return not await self._user_repository.exists_by_email(email)
    
    async def validate_user_uniqueness(self, username: Username, email: Email) -> None:
        """验证用户唯一性
        
        Args:
            username: 用户名值对象
            email: 邮箱值对象
            
        Raises:
            ValueError: 当用户名或邮箱已存在时
        """
        if not await self.is_username_available(username):
            raise ValueError(f"用户名 '{username.value}' 已存在")
        
        if not await self.is_email_available(email):
            raise ValueError(f"邮箱 '{email.value}' 已存在")
    
    async def find_user_by_login_identifier(self, identifier: str) -> Optional[User]:
        """根据登录标识符查找用户
        
        Args:
            identifier: 登录标识符（用户名或邮箱）
            
        Returns:
            用户实体，未找到返回None
        """
        # 首先尝试作为用户名查找
        try:
            username = Username.create(identifier)
            user = await self._user_repository.find_by_username(username)
            if user:
                return user
        except ValueError:
            pass  # 不是有效的用户名格式
        
        # 然后尝试作为邮箱查找
        try:
            email = Email.create(identifier)
            user = await self._user_repository.find_by_email(email)
            return user
        except ValueError:
            pass  # 不是有效的邮箱格式
        
        return None
    
    async def validate_user_can_login(self, user: User) -> None:
        """验证用户是否可以登录
        
        Args:
            user: 用户实体
            
        Raises:
            ValueError: 当用户状态不允许登录时
        """
        if not user.can_login():
            if user.status.is_disabled():
                raise ValueError("账户已被禁用，无法登录")
            elif user.status.is_inactive():
                raise ValueError("账户未激活，无法登录")
            else:
                raise ValueError("账户状态异常，无法登录")
    
    async def check_user_exists(self, user_id: str) -> bool:
        """检查用户是否存在
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户是否存在
        """
        user = await self._user_repository.find_by_id(user_id)
        return user is not None
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """根据ID获取用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户实体，未找到返回None
        """
        return await self._user_repository.find_by_id(user_id)
    
    def validate_password_strength(self, password: str) -> None:
        """验证密码强度
        
        Args:
            password: 明文密码
            
        Raises:
            ValueError: 当密码不符合强度要求时
        """
        
        try:
            Password.create(password)
        except ValueError as e:
            raise ValueError(f"密码强度不足: {str(e)}")
    
    def validate_email_format(self, email: str) -> None:
        """验证邮箱格式
        
        Args:
            email: 邮箱字符串
            
        Raises:
            ValueError: 当邮箱格式不正确时
        """
        try:
            Email.create(email)
        except ValueError as e:
            raise ValueError(f"邮箱格式不正确: {str(e)}")
    
    def validate_username_format(self, username: str) -> None:
        """验证用户名格式
        
        Args:
            username: 用户名字符串
            
        Raises:
            ValueError: 当用户名格式不正确时
        """
        try:
            Username.create(username)
        except ValueError as e:
            raise ValueError(f"用户名格式不正确: {str(e)}")