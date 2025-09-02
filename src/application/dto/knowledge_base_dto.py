"""
知识库相关DTO
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class KnowledgeBaseCreateRequest(BaseModel):
    """创建知识库请求"""
    name: str = Field(..., min_length=1, max_length=100, description="知识库名称")
    description: str = Field("", max_length=500, description="知识库描述")
    config: Optional[Dict[str, Any]] = Field(None, description="知识库配置")


class KnowledgeBaseResponse(BaseModel):
    """知识库响应"""
    knowledge_base_id: str
    name: str
    description: str
    owner_id: str
    config: Dict[str, Any]
    is_active: bool
    document_count: int
    chunk_count: int
    created_at: datetime
    updated_at: datetime


class KnowledgeBaseListResponse(BaseModel):
    """知识库列表响应"""
    knowledge_bases: List[KnowledgeBaseResponse]
    total: int
    
    
class KnowledgeBaseOverviewResponse(BaseModel):
    """知识库概览响应"""
    knowledge_base: KnowledgeBaseResponse
    document_count: int
    chunk_count: int
    recent_documents: List[Dict[str, Any]]
    file_types: List[str]
    total_size: int