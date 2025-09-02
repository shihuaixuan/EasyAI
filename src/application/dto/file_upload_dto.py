"""
文件上传相关DTO
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class FileUploadRequest(BaseModel):
    """文件上传请求"""
    knowledge_base_id: str = Field(..., description="知识库ID")
    filename: str = Field(..., description="文件名")
    content_type: str = Field(..., description="文件类型")
    # 注意：实际的文件内容通过multipart/form-data传输


class FileUploadResponse(BaseModel):
    """文件上传响应"""
    success: bool
    filename: str
    file_path: Optional[str] = None
    document_id: Optional[str] = None
    file_size: Optional[int] = None
    content_hash: Optional[str] = None
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None


class FileUploadBatchRequest(BaseModel):
    """批量文件上传请求"""
    knowledge_base_id: str = Field(..., description="知识库ID")
    # 文件列表通过multipart/form-data传输


class FileUploadBatchResponse(BaseModel):
    """批量文件上传响应"""
    total_files: int
    successful_uploads: List[FileUploadResponse]
    failed_uploads: List[FileUploadResponse]
    success_count: int
    error_count: int


class FileListResponse(BaseModel):
    """文件列表响应"""
    document_id: str
    filename: str
    file_type: str
    file_size: int
    is_processed: bool
    chunk_count: int
    created_at: datetime
    processed_at: Optional[datetime] = None


class FileListBatchResponse(BaseModel):
    """文件批量列表响应"""
    knowledge_base_id: str
    files: List[FileListResponse]
    total: int