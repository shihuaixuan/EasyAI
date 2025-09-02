"""
知识库实体
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid


@dataclass
class KnowledgeBase:
    """知识库实体"""
    
    name: str
    description: str
    knowledge_base_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    owner_id: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    is_active: bool = True
    document_count: int = 0
    chunk_count: int = 0
    
    def __post_init__(self):
        if self.knowledge_base_id is None:
            self.knowledge_base_id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.config is None:
            self.config = {}
    
    def update_statistics(self, document_count: int, chunk_count: int) -> None:
        """更新知识库统计信息"""
        self.document_count = document_count
        self.chunk_count = chunk_count
        self.updated_at = datetime.now()
    
    def update_config(self, config: Dict[str, Any]) -> None:
        """更新知识库配置"""
        if self.config is None:
            self.config = {}
        self.config.update(config)
        self.updated_at = datetime.now()
    
    def deactivate(self) -> None:
        """停用知识库"""
        self.is_active = False
        self.updated_at = datetime.now()