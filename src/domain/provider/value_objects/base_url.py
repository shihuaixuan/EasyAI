"""
Base URL 值对象
"""
from typing import Optional
from dataclasses import dataclass
import re


@dataclass(frozen=True)
class BaseUrl:
    """
    Base URL 值对象，代表API服务的基础URL
    """
    value: Optional[str]
    
    def __post_init__(self):
        if self.value is not None:
            # 验证URL格式
            url_pattern = re.compile(
                r'^https?://'  # http:// 或 https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # 域名
                r'localhost|'  # localhost
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP地址
                r'(?::\d+)?'  # 可选端口
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            
            if not url_pattern.match(self.value.strip()):
                raise ValueError(f"无效的URL格式: {self.value}")
    
    @classmethod
    def from_string(cls, url: Optional[str]) -> "BaseUrl":
        """从字符串创建Base URL"""
        if url is None or not url.strip():
            return cls(None)
        return cls(value=url.strip())
    
    def is_empty(self) -> bool:
        """检查URL是否为空"""
        return self.value is None or self.value.strip() == ""
    
    def __str__(self) -> str:
        return self.value or ""