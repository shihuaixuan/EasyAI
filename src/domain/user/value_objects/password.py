import re
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Password:
    """密码值对象"""
    value: str
    
    def __post_init__(self):
        """初始化后验证密码格式"""
        if not self.is_valid():
            raise ValueError("密码格式不符合要求")
    
    def is_valid(self) -> bool:
        """验证密码格式
        
        要求：
        - 长度至少8位
        - 包含至少一个字母
        - 包含至少一个数字
        """
        if len(self.value) < 8:
            return False
        
        # 检查是否包含字母
        if not re.search(r'[a-zA-Z]', self.value):
            return False
        
        # 检查是否包含数字
        if not re.search(r'\d', self.value):
            return False
        
        return True
    
    @classmethod
    def create(cls, password: str) -> 'Password':
        """创建密码值对象"""
        return cls(value=password)
    
    def __str__(self) -> str:
        return "[PROTECTED]"
    
    def __repr__(self) -> str:
        return "Password([PROTECTED])"


@dataclass(frozen=True)
class HashedPassword:
    """加密后的密码值对象"""
    hash_value: str
    
    @classmethod
    def create(cls, hash_value: str) -> 'HashedPassword':
        """创建加密密码值对象"""
        if not hash_value:
            raise ValueError("密码哈希值不能为空")
        return cls(hash_value=hash_value)
    
    def __str__(self) -> str:
        return "[HASHED]"
    
    def __repr__(self) -> str:
        return "HashedPassword([HASHED])"