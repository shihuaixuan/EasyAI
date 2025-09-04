"""
文档块实体
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid


@dataclass
class DocumentChunk:
    """文档块实体"""
    
    content: str
    chunk_index: int
    start_offset: int
    document_id: str
    knowledge_base_id: str
    chunk_id: Optional[str] = None
    end_offset: Optional[int] = None
    content_hash: Optional[str] = None
    vector: Optional[List[float]] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_indexed: bool = False
    
    def __post_init__(self):
        if self.chunk_id is None:
            self.chunk_id = str(uuid.uuid4())
        if self.end_offset is None:
            self.end_offset = self.start_offset + len(self.content)
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def set_vector(self, vector: List[float]) -> None:
        """设置向量"""
        self.vector = vector
        if self.metadata is None:
            self.metadata = {}
        self.metadata['has_vector'] = True
        self.updated_at = datetime.now()
    
    def mark_as_indexed(self) -> None:
        """标记为已索引"""
        self.is_indexed = True
        self.updated_at = datetime.now()
    
    def add_metadata(self, key: str, value: Any) -> None:
        """添加元数据"""
        if self.metadata is None:
            self.metadata = {}
        self.metadata[key] = value
        self.updated_at = datetime.now()
    
    def get_char_count(self) -> int:
        """获取字符数"""
        return len(self.content)
    
    def get_word_count(self) -> int:
        """获取词数（简单按空格分割）"""
        return len(self.content.split())
    
    def has_vector(self) -> bool:
        """检查是否有向量"""
        return self.vector is not None and len(self.vector) > 0
    
    def get_vector_dimension(self) -> int:
        """获取向量维度"""
        if not self.has_vector():
            return 0
        return len(self.vector)
    
    def clear_vector(self) -> None:
        """清除向量"""
        self.vector = None
        if self.metadata:
            self.metadata.pop('has_vector', None)
        self.updated_at = datetime.now()
    
    def is_embedding_required(self) -> bool:
        """检查是否需要生成embedding"""
        return not self.has_vector() and len(self.content.strip()) > 0