"""
API Key 值对象
"""
from typing import Optional
from dataclasses import dataclass


@dataclass(frozen=True)
class ApiKey:
    """
    API Key 值对象，代表加密后的API密钥
    
    注意：前端会进行加密传输，这里存储的是加密后的值
    """
    encrypted_value: str
    
    def __post_init__(self):
        if not self.encrypted_value or not self.encrypted_value.strip():
            raise ValueError("API Key不能为空")
    
    @classmethod
    def from_encrypted(cls, encrypted_value: str) -> "ApiKey":
        """从加密后的值创建API Key"""
        return cls(encrypted_value=encrypted_value.strip())
    
    def __str__(self) -> str:
        """隐藏敏感信息的字符串表示"""
        return f"ApiKey(***{self.encrypted_value[-4:] if len(self.encrypted_value) > 4 else '***'})"