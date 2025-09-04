import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from src.domain.user.entities.user import User
from src.domain.user.repositories.user_repository import UserRepository
from src.domain.user.services.user_domain_service import UserDomainService
from src.domain.user.value_objects.username import Username
from src.domain.user.value_objects.email import Email
from src.domain.user.value_objects.password import Password, HashedPassword
from src.domain.user.value_objects.user_status import UserStatus
from src.infrastructure.services.password_service import PasswordService
from src.infrastructure.services.jwt_service import JWTService


class UserApplicationService:
    """用户应用服务 - 协调用户注册和登录的业务逻辑"""
    
    def __init__(
        self,
        user_repository: UserRepository,
        user_domain_service: UserDomainService,
        password_service: PasswordService,
        jwt_service: JWTService
    ):
        """初始化用户应用服务
        
        Args:
            user_repository: 用户仓储
            user_domain_service: 用户领域服务
            password_service: 密码服务
            jwt_service: JWT服务
        """
        self._user_repository = user_repository
        self._user_domain_service = user_domain_service
        self._password_service = password_service
        self._jwt_service = jwt_service
    
    async def register_user(
        self,
        username: str,
        email: str,
        password: str
    ) -> Dict[str, Any]:
        """用户注册
        
        Args:
            username: 用户名
            email: 邮箱
            password: 密码
            
        Returns:
            注册结果，包含用户信息和令牌
            
        Raises:
            ValueError: 当输入验证失败或用户已存在时
        """
        # 1. 输入验证
        self._user_domain_service.validate_username_format(username)
        self._user_domain_service.validate_email_format(email)
        self._user_domain_service.validate_password_strength(password)
        
        # 2. 创建值对象
        username_vo = Username.create(username)
        email_vo = Email.create(email)
        password_vo = Password.create(password)
        
        # 3. 验证唯一性
        await self._user_domain_service.validate_user_uniqueness(username_vo, email_vo)
        
        # 4. 加密密码
        hashed_password = self._password_service.hash_password(password_vo)
        
        # 5. 创建用户实体
        user = User.create(
            username=username_vo,
            email=email_vo,
            password_hash=hashed_password,
            status=UserStatus.ACTIVE  # 默认激活状态
        )
        
        # 6. 保存用户
        saved_user = await self._user_repository.save(user)
        
        # 7. 生成令牌
        access_token = self._jwt_service.create_access_token(saved_user)
        refresh_token = self._jwt_service.create_refresh_token(saved_user)
        
        return {
            'user': {
                'id': saved_user.id,
                'username': saved_user.username.value,
                'email': saved_user.email.value,
                'status': saved_user.status.value,
                'created_at': saved_user.created_at.isoformat(),
                'updated_at': saved_user.updated_at.isoformat()
            },
            'tokens': {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_type': 'bearer'
            }
        }
    
    async def login_user(
        self,
        identifier: str,
        password: str
    ) -> Dict[str, Any]:
        """用户登录
        
        Args:
            identifier: 登录标识符（用户名或邮箱）
            password: 密码
            
        Returns:
            登录结果，包含用户信息和令牌
            
        Raises:
            ValueError: 当登录失败时
        """
        # 1. 查找用户
        user = await self._user_domain_service.find_user_by_login_identifier(identifier)
        if not user:
            raise ValueError("用户名或密码错误")
        
        # 2. 验证用户状态
        await self._user_domain_service.validate_user_can_login(user)
        
        # 3. 验证密码
        if not self._password_service.verify_password(password, user.password_hash):
            raise ValueError("用户名或密码错误")
        
        # 4. 更新最后登录时间
        user.touch()
        await self._user_repository.update(user)
        
        # 5. 生成令牌
        access_token = self._jwt_service.create_access_token(user)
        refresh_token = self._jwt_service.create_refresh_token(user)
        
        return {
            'user': {
                'id': user.id,
                'username': user.username.value,
                'email': user.email.value,
                'status': user.status.value,
                'created_at': user.created_at.isoformat(),
                'updated_at': user.updated_at.isoformat()
            },
            'tokens': {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_type': 'bearer'
            }
        }
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """刷新访问令牌
        
        Args:
            refresh_token: 刷新令牌
            
        Returns:
            新的访问令牌
            
        Raises:
            ValueError: 当刷新令牌无效时
        """
        # 1. 验证刷新令牌
        payload = self._jwt_service.verify_token(refresh_token)
        if not payload or payload.get('type') != 'refresh':
            raise ValueError("无效的刷新令牌")
        
        # 2. 获取用户ID
        user_id = payload.get('sub')
        if not user_id:
            raise ValueError("无效的刷新令牌")
        
        # 3. 查找用户
        user = await self._user_domain_service.get_user_by_id(user_id)
        if not user:
            raise ValueError("用户不存在")
        
        # 4. 验证用户状态
        await self._user_domain_service.validate_user_can_login(user)
        
        # 5. 生成新的访问令牌
        new_access_token = self._jwt_service.create_access_token(user)
        
        return {
            'access_token': new_access_token,
            'token_type': 'bearer'
        }
    
    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """获取用户资料
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户资料
            
        Raises:
            ValueError: 当用户不存在时
        """
        user = await self._user_domain_service.get_user_by_id(user_id)
        if not user:
            raise ValueError("用户不存在")
        
        return {
            'id': user.id,
            'username': user.username.value,
            'email': user.email.value,
            'status': user.status.value,
            'created_at': user.created_at.isoformat(),
            'updated_at': user.updated_at.isoformat()
        }
    
    async def change_password(
        self,
        user_id: str,
        old_password: str,
        new_password: str
    ) -> Dict[str, Any]:
        """修改密码
        
        Args:
            user_id: 用户ID
            old_password: 旧密码
            new_password: 新密码
            
        Returns:
            修改结果
            
        Raises:
            ValueError: 当修改失败时
        """
        # 1. 查找用户
        user = await self._user_domain_service.get_user_by_id(user_id)
        if not user:
            raise ValueError("用户不存在")
        
        # 2. 验证旧密码
        if not self._password_service.verify_password(old_password, user.password_hash):
            raise ValueError("旧密码错误")
        
        # 3. 验证新密码强度
        self._user_domain_service.validate_password_strength(new_password)
        
        # 4. 加密新密码
        new_password_vo = Password.create(new_password)
        new_hashed_password = self._password_service.hash_password(new_password_vo)
        
        # 5. 更新密码
        user.update_password(new_hashed_password)
        await self._user_repository.update(user)
        
        return {
            'message': '密码修改成功',
            'updated_at': user.updated_at.isoformat()
        }
    
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """验证令牌
        
        Args:
            token: JWT令牌
            
        Returns:
            令牌载荷，验证失败返回None
        """
        return self._jwt_service.verify_token(token)