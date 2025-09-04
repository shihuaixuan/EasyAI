"""
UUID生成工具
"""
import uuid
from typing import Optional


class UUIDGenerator:
    """UUID生成器"""
    
    @staticmethod
    def generate() -> str:
        """
        生成新的UUID字符串
        
        Returns:
            UUID字符串，格式如：8c9d8f16-278f-4b16-a5c0-4d1ccf348f93
        """
        return str(uuid.uuid4())
    
    @staticmethod
    def is_valid_uuid(uuid_string: str) -> bool:
        """
        验证UUID字符串是否有效
        
        Args:
            uuid_string: 要验证的UUID字符串
            
        Returns:
            True如果是有效的UUID，否则False
        """
        try:
            uuid.UUID(uuid_string)
            return True
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def normalize_uuid(uuid_string: Optional[str]) -> Optional[str]:
        """
        标准化UUID字符串（转换为小写，去除空格）
        
        Args:
            uuid_string: 要标准化的UUID字符串
            
        Returns:
            标准化后的UUID字符串，如果输入无效则返回None
        """
        if not uuid_string:
            return None
            
        try:
            # 去除空格并转换为小写
            normalized = uuid_string.strip().lower()
            # 验证格式
            uuid.UUID(normalized)
            return normalized
        except (ValueError, TypeError):
            return None


# 全局实例
uuid_generator = UUIDGenerator()
