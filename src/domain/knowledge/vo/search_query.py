"""
搜索查询值对象
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List


@dataclass(frozen=True)
class SearchQuery:
    """搜索查询值对象"""
    text: str
    knowledge_base_id: str
    filters: Optional[Dict[str, Any]] = None
    include_metadata: bool = True
    max_results: int = 10
    
    def __post_init__(self):
        if self.filters is None:
            object.__setattr__(self, 'filters', {})
    
    def is_valid(self) -> bool:
        """验证查询是否有效"""
        return bool(self.text.strip()) and bool(self.knowledge_base_id.strip())
    
    def get_clean_text(self) -> str:
        """获取清理后的查询文本"""
        return self.text.strip()


@dataclass(frozen=True)
class SearchResult:
    """搜索结果值对象"""
    chunk_id: str
    content: str
    score: float
    document_id: str
    chunk_index: int
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            object.__setattr__(self, 'metadata', {})
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "chunk_id": self.chunk_id,
            "content": self.content,
            "score": self.score,
            "document_id": self.document_id,
            "chunk_index": self.chunk_index,
            "metadata": self.metadata
        }