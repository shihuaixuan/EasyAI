"""
工作流相关DTO
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime


class ChunkingConfigRequest(BaseModel):
    """分块配置请求"""
    strategy: Literal["parent_child", "general"] = Field(..., description="分块策略")
    separator: str = Field("\n\n", description="分隔符")
    max_length: int = Field(1024, ge=1, le=10000, description="最大长度")
    overlap_length: int = Field(50, ge=0, le=1000, description="重叠长度")
    remove_extra_whitespace: bool = Field(False, description="移除多余空格")
    remove_urls: bool = Field(False, description="移除URL")
    
    # 父子分段特有配置
    parent_separator: Optional[str] = Field(None, description="父块分隔符")
    parent_max_length: Optional[int] = Field(None, description="父块最大长度")
    child_separator: Optional[str] = Field(None, description="子块分隔符")
    child_max_length: Optional[int] = Field(None, description="子块最大长度")


class EmbeddingConfigRequest(BaseModel):
    """嵌入配置请求"""
    strategy: Literal["high_quality", "economic"] = Field(..., description="嵌入策略")
    model_name: Optional[str] = Field(None, description="模型名称")


class RetrievalConfigRequest(BaseModel):
    """检索配置请求"""
    strategy: Literal["vector_search", "fulltext_search", "hybrid_search"] = Field(..., description="检索策略")
    top_k: int = Field(10, ge=1, le=100, description="返回数量")
    score_threshold: float = Field(0.0, ge=0.0, le=1.0, description="分数阈值")
    enable_rerank: bool = Field(False, description="启用重排序")
    rerank_model: Optional[str] = Field(None, description="重排序模型")


class WorkflowConfigRequest(BaseModel):
    """工作流配置请求"""
    chunking: ChunkingConfigRequest
    embedding: EmbeddingConfigRequest  
    retrieval: RetrievalConfigRequest


class WorkflowConfigResponse(BaseModel):
    """工作流配置响应"""
    knowledge_base_id: str
    config: Dict[str, Any]
    updated_at: datetime


class WorkflowStartRequest(BaseModel):
    """启动工作流请求"""
    knowledge_base_id: str = Field(..., description="知识库ID")
    document_ids: List[str] = Field(..., description="要处理的文档ID列表")
    config: WorkflowConfigRequest = Field(..., description="工作流配置")


class WorkflowTaskInfo(BaseModel):
    """工作流任务信息"""
    task_id: str
    document_id: str
    filename: str
    status: Literal["pending", "processing", "completed", "failed"]
    progress: int = Field(0, ge=0, le=100)
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class WorkflowStatusResponse(BaseModel):
    """工作流状态响应"""
    workflow_id: str
    knowledge_base_id: str
    status: Literal["pending", "processing", "completed", "failed", "cancelled"]
    total_documents: int
    processed_documents: int
    failed_documents: int
    tasks: List[WorkflowTaskInfo]
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class WorkflowResultResponse(BaseModel):
    """工作流结果响应"""
    workflow_id: str
    knowledge_base_id: str
    total_documents: int
    successful_documents: int
    failed_documents: int
    total_chunks: int
    processing_time: float  # 秒
    errors: List[Dict[str, Any]]