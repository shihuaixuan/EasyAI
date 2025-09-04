import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Email:
    """邮箱值对象"""
    value: str
    
    def __post_init__(self):
        """初始化后验证邮箱格式"""
        if not self.is_valid():
            raise ValueError(f"邮箱格式不正确: {self.value}")
    
    def is_valid(self) -> bool:
        """验证邮箱格式"""
        if not self.value:
            return False
        
        # 基本的邮箱格式验证
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, self.value) is not None
    
    @classmethod
    def create(cls, email: str) -> 'Email':
        """创建邮箱值对象"""
        return cls(value=email.lower().strip())
    
    def get_domain(self) -> str:
        """获取邮箱域名"""
        return self.value.split('@')[1] if '@' in self.value else ''
    
    def get_local_part(self) -> str:
        """获取邮箱本地部分"""
        return self.value.split('@')[0] if '@' in self.value else ''
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Email):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        return hash(self.value)