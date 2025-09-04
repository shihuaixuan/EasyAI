import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Username:
    """用户名值对象"""
    value: str
    
    def __post_init__(self):
        """初始化后验证用户名格式"""
        if not self.is_valid():
            raise ValueError(f"用户名格式不正确: {self.value}")
    
    def is_valid(self) -> bool:
        """验证用户名格式
        
        要求：
        - 长度3-20位
        - 只能包含字母、数字、下划线
        - 必须以字母开头
        """
        if not self.value:
            return False
        
        # 检查长度
        if len(self.value) < 3 or len(self.value) > 20:
            return False
        
        # 检查格式：以字母开头，只包含字母、数字、下划线
        username_pattern = r'^[a-zA-Z][a-zA-Z0-9_]*$'
        return re.match(username_pattern, self.value) is not None
    
    @classmethod
    def create(cls, username: str) -> 'Username':
        """创建用户名值对象"""
        return cls(value=username.strip())
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Username):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        return hash(self.value)