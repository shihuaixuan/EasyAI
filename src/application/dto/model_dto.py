"""
Model相关的DTO (Data Transfer Objects)
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator


class ModelCreateRequest(BaseModel):
    """
    创建模型请求DTO
    """
    user_id: str = Field(..., min_length=1, description="用户ID（UUID格式）")
    provider: str = Field(..., min_length=1, max_length=50, description="提供商名称")
    model_name: str = Field(..., min_length=1, max_length=100, description="模型名称")
    model_type: str = Field(..., min_length=1, max_length=50, description="模型类型")
    subtype: Optional[str] = Field(None, max_length=50, description="模型子类型")
    metadata: Optional[Dict[str, Any]] = Field(None, description="模型元数据")
    
    @validator('provider')
    def validate_provider(cls, v):
        """验证提供商名称"""
        if not v or not v.strip():
            raise ValueError('提供商名称不能为空')
        return v.strip().lower()
    
    @validator('model_name')
    def validate_model_name(cls, v):
        """验证模型名称"""
        if not v or not v.strip():
            raise ValueError('模型名称不能为空')
        return v.strip()
    
    @validator('model_type')
    def validate_model_type(cls, v):
        """验证模型类型"""
        if not v or not v.strip():
            raise ValueError('模型类型不能为空')
        
        normalized = v.strip().lower()
        supported_types = {'llm', 'embedding', 'rerank'}
        if normalized not in supported_types:
            raise ValueError(f'不支持的模型类型: {normalized}，支持的类型: {supported_types}')
        return normalized


class ModelToggleRequest(BaseModel):
    """
    模型开关请求DTO
    """
    user_id: str = Field(..., min_length=1, description="用户ID（UUID格式）")
    provider: str = Field(..., min_length=1, max_length=50, description="提供商名称")
    model_name: str = Field(..., min_length=1, max_length=100, description="模型名称")
    enabled: bool = Field(..., description="是否启用模型")
    
    @validator('provider')
    def validate_provider(cls, v):
        return v.strip().lower() if v else v
    
    @validator('model_name')
    def validate_model_name(cls, v):
        return v.strip() if v else v


class ModelResponse(BaseModel):
    """
    模型响应DTO
    """
    id: str = Field(..., description="模型ID（UUID格式）")
    provider_name: str = Field(..., description="提供商名称")
    model_name: str = Field(..., description="模型名称")
    type: str = Field(..., description="模型类型")
    subtype: Optional[str] = Field(None, description="模型子类型")
    metadata: Optional[Dict[str, Any]] = Field(None, description="模型元数据")
    enabled: bool = Field(..., description="是否启用")
    created_at: Optional[str] = Field(None, description="创建时间")
    updated_at: Optional[str] = Field(None, description="更新时间")


class ProviderModelInfo(BaseModel):
    """
    提供商模型信息DTO（从配置文件读取）
    """
    model: str = Field(..., description="模型名称")
    model_type: str = Field(..., description="模型类型")
    provider: str = Field(..., description="提供商名称")
    description: Optional[str] = Field(None, description="模型描述")
    capabilities: Optional[List[str]] = Field(None, description="模型能力")
    context_length: Optional[int] = Field(None, description="上下文长度")
    max_tokens: Optional[int] = Field(None, description="最大token数")
    enabled: bool = Field(False, description="是否已启用")


class ProviderModelsResponse(BaseModel):
    """
    提供商模型列表响应DTO
    """
    provider: str = Field(..., description="提供商名称")
    has_api_key: bool = Field(..., description="是否已配置API Key")
    models: List[ProviderModelInfo] = Field(..., description="模型列表")


class ModelOperationResponse(BaseModel):
    """
    模型操作响应DTO
    """
    success: bool = Field(..., description="操作是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[ModelResponse] = Field(None, description="模型数据")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "模型操作成功",
                "data": {
                    "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                    "provider_name": "deepseek",
                    "model_name": "deepseek-chat",
                    "type": "llm",
                    "subtype": "chat",
                    "metadata": {},
                    "enabled": True,
                    "created_at": "2023-12-01T10:00:00Z",
                    "updated_at": "2023-12-01T10:00:00Z"
                }
            }
        }