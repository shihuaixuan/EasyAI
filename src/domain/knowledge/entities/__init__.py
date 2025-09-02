"""
知识库领域实体模块
"""

from .knowledge_base import KnowledgeBase
from .document import Document
from .document_chunk import DocumentChunk

__all__ = ['KnowledgeBase', 'Document', 'DocumentChunk']