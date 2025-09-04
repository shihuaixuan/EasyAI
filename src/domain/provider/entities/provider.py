"""
Provider实体
"""
from typing import Optional
from dataclasses import dataclass
from datetime import datetime

from ..value_objects.api_key import ApiKey
from ..value_objects.base_url import BaseUrl
from ....infrastructure.utils.uuid_generator import uuid_generator


@dataclass
class Provider:
    """
    模型提供商实体
    """
    user_id: str  # 改为字符串类型以支持UUID
    provider: str  # 提供商名称，如 'openai', 'deepseek', 'siliconflow'
    api_key: ApiKey
    base_url: BaseUrl
    id: Optional[str] = None  # 改为字符串类型以支持UUID
    is_delete: int = 0  # 软删除标记，0-未删除，1-已删除
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        # 生成UUID（如果没有提供ID）
        if not self.id:
            self.id = uuid_generator.generate()
            
        # 验证必填字段
        if not self.user_id or not self.user_id.strip():
            raise ValueError("用户ID不能为空")
        
        if not self.provider or not self.provider.strip():
            raise ValueError("提供商名称不能为空")
        
        # 标准化提供商名称
        self.provider = self.provider.strip().lower()
        
        # 验证支持的提供商
        supported_providers = {'openai', 'deepseek', 'siliconflow', 'anthropic', 'google'}
        if self.provider not in supported_providers:
            raise ValueError(f"不支持的提供商: {self.provider}，支持的提供商: {supported_providers}")
    
    @classmethod
    def create(
        cls, 
        user_id: str, 
        provider: str, 
        encrypted_api_key: str, 
        base_url: Optional[str] = None
    ) -> "Provider":
        """
        创建新的Provider实体
        """
        api_key = ApiKey.from_encrypted(encrypted_api_key)
        base_url_obj = BaseUrl.from_string(base_url)
        
        return cls(
            user_id=user_id,
            provider=provider,
            api_key=api_key,
            base_url=base_url_obj
        )
    
    def update_api_key(self, encrypted_api_key: str) -> None:
        """更新API Key"""
        self.api_key = ApiKey.from_encrypted(encrypted_api_key)
        self.updated_at = datetime.now()
    
    def update_base_url(self, base_url: Optional[str]) -> None:
        """更新Base URL"""
        self.base_url = BaseUrl.from_string(base_url)
        self.updated_at = datetime.now()
    
    def mark_as_deleted(self) -> None:
        """标记为已删除（软删除）"""
        self.is_delete = 1
        self.updated_at = datetime.now()
    
    def restore(self) -> None:
        """恢复已删除的记录"""
        self.is_delete = 0
        self.updated_at = datetime.now()
    
    def is_deleted(self) -> bool:
        """检查是否已被删除"""
        return self.is_delete == 1
    
    def get_unique_key(self) -> str:
        """获取唯一标识键（用户ID + 提供商）"""
        return f"{self.user_id}:{self.provider}"
    
    def __str__(self) -> str:
        return f"Provider(id={self.id}, user_id={self.user_id}, provider={self.provider})"