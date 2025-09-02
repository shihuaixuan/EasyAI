"""
文档实体
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid


@dataclass
class Document:
    """文档实体"""
    
    filename: str
    content: str
    file_type: str
    file_size: int
    knowledge_base_id: str
    document_id: Optional[str] = None
    original_path: Optional[str] = None
    content_hash: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    is_processed: bool = False
    chunk_count: int = 0
    
    def __post_init__(self):
        if self.document_id is None:
            self.document_id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.metadata is None:
            self.metadata = {}
    
    def mark_as_processed(self, chunk_count: int) -> None:
        """标记文档为已处理"""
        self.is_processed = True
        self.processed_at = datetime.now()
        self.chunk_count = chunk_count
        self.updated_at = datetime.now()
    
    def update_metadata(self, metadata: Dict[str, Any]) -> None:
        """更新文档元数据"""
        if self.metadata is None:
            self.metadata = {}
        self.metadata.update(metadata)
        self.updated_at = datetime.now()
    
    def get_file_extension(self) -> str:
        """获取文件扩展名"""
        if '.' in self.filename:
            return self.filename.split('.')[-1].lower()
        return ''