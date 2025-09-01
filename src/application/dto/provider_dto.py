"""
Provider相关的DTO (Data Transfer Objects)
"""
from typing import Optional
from pydantic import BaseModel, Field, validator


class SaveProviderRequest(BaseModel):
    """
    保存Provider请求DTO
    """
    user_id: int = Field(..., gt=0, description="用户ID，必须为正整数")
    provider: str = Field(..., min_length=1, max_length=50, description="提供商名称")
    api_key: str = Field(..., min_length=1, description="加密后的API Key")
    base_url: Optional[str] = Field(None, max_length=500, description="基础URL")
    
    @validator('provider')
    def validate_provider(cls, v):
        """验证提供商名称"""
        if not v or not v.strip():
            raise ValueError('提供商名称不能为空')
        
        # 标准化提供商名称
        normalized = v.strip().lower()
        
        # 验证支持的提供商
        supported_providers = {'openai', 'deepseek', 'siliconflow', 'anthropic', 'google'}
        if normalized not in supported_providers:
            raise ValueError(f'不支持的提供商: {normalized}，支持的提供商: {supported_providers}')
        
        return normalized
    
    @validator('api_key')
    def validate_api_key(cls, v):
        """验证API Key"""
        if not v or not v.strip():
            raise ValueError('API Key不能为空')
        return v.strip()
    
    @validator('base_url')
    def validate_base_url(cls, v):
        """验证Base URL"""
        if v is not None:
            v = v.strip()
            if v == '':
                return None
            
            # 简单的URL格式验证
            if not (v.startswith('http://') or v.startswith('https://')):
                raise ValueError('Base URL必须以http://或https://开头')
        
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": 1,
                "provider": "openai",
                "api_key": "encrypted_api_key_here",
                "base_url": "https://api.openai.com/v1"
            }
        }


class ProviderResponse(BaseModel):
    """
    Provider响应DTO
    """
    id: int = Field(..., description="Provider ID")
    user_id: int = Field(..., description="用户ID")
    provider: str = Field(..., description="提供商名称")
    api_key_masked: Optional[str] = Field(None, description="掉码后的API Key，用于前端显示")
    base_url: Optional[str] = Field(None, description="基础URL")
    created_at: Optional[str] = Field(None, description="创建时间")
    updated_at: Optional[str] = Field(None, description="更新时间")
    
    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1,
                "provider": "openai",
                "api_key_masked": "sk-***1234",
                "base_url": "https://api.openai.com/v1",
                "created_at": "2023-12-01T10:00:00Z",
                "updated_at": "2023-12-01T10:00:00Z"
            }
        }


class SaveProviderResponse(BaseModel):
    """
    保存Provider响应DTO
    """
    success: bool = Field(..., description="操作是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[ProviderResponse] = Field(None, description="Provider数据")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Provider保存成功",
                "data": {
                    "id": 1,
                    "user_id": 1,
                    "provider": "openai",
                    "base_url": "https://api.openai.com/v1",
                    "created_at": "2023-12-01T10:00:00Z",
                    "updated_at": "2023-12-01T10:00:00Z"
                }
            }
        }