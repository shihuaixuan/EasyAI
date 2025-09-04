import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from ..value_objects.user_status import UserStatus
from ..value_objects.username import Username
from ..value_objects.email import Email
from ..value_objects.password import HashedPassword


@dataclass
class User:
    """用户实体"""
    id: str
    username: Username
    email: Email
    password_hash: HashedPassword
    status: UserStatus
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def create(
        cls,
        username: Username,
        email: Email,
        password_hash: HashedPassword,
        status: Optional[UserStatus] = None
    ) -> 'User':
        """创建新用户"""
        now = datetime.utcnow()
        return cls(
            id=str(uuid.uuid4()),
            username=username,
            email=email,
            password_hash=password_hash,
            status=status or UserStatus.ACTIVE,
            created_at=now,
            updated_at=now
        )
    
    def can_login(self) -> bool:
        """检查用户是否可以登录"""
        return self.status.can_login()
    
    def activate(self) -> None:
        """激活用户"""
        self.status = UserStatus.ACTIVE
        self.updated_at = datetime.utcnow()
    
    def disable(self) -> None:
        """禁用用户"""
        self.status = UserStatus.DISABLED
        self.updated_at = datetime.utcnow()
    
    def update_password(self, new_password_hash: HashedPassword) -> None:
        """更新密码"""
        self.password_hash = new_password_hash
        self.updated_at = datetime.utcnow()
    
    def update_email(self, new_email: Email) -> None:
        """更新邮箱"""
        self.email = new_email
        self.updated_at = datetime.utcnow()
    
    def touch(self) -> None:
        """更新最后修改时间"""
        self.updated_at = datetime.utcnow()
    
    def is_active(self) -> bool:
        """检查用户是否为激活状态"""
        return self.status == UserStatus.ACTIVE
    
    def is_disabled(self) -> bool:
        """检查用户是否被禁用"""
        return self.status == UserStatus.DISABLED
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, User):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        return hash(self.id)