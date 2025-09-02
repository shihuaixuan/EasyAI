"""
知识库仓储接口模块
"""

from .knowledge_base_repository import KnowledgeBaseRepository
from .document_repository import DocumentRepository
from .document_chunk_repository import DocumentChunkRepository

__all__ = ['KnowledgeBaseRepository', 'DocumentRepository', 'DocumentChunkRepository']