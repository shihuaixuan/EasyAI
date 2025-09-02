"""
分块器基类 - 定义分块策略的接口
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ...entities.document import Document
from ...entities.document_chunk import DocumentChunk
from ...vo.chunking_config import ChunkingConfig


class BaseChunker(ABC):
    """分块器基类"""
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """获取策略名称"""
        pass
    
    @abstractmethod
    async def chunk(
        self, 
        document: Document, 
        config: ChunkingConfig
    ) -> List[DocumentChunk]:
        """
        对文档进行分块
        
        Args:
            document: 待分块的文档
            config: 分块配置
            
        Returns:
            文档块列表
        """
        pass
    
    def _create_chunk(
        self,
        document: Document,
        content: str,
        chunk_index: int,
        start_offset: int,
        end_offset: Optional[int] = None,
        chunk_type: str = "flat",
        parent_chunk_id: Optional[str] = None,
        chunk_level: int = 0,
        metadata: Optional[Dict[str, Any]]= None
    ) -> DocumentChunk:
        """
        创建文档块的通用方法
        
        Args:
            document: 原始文档
            content: 块内容
            chunk_index: 块索引
            start_offset: 起始偏移量
            end_offset: 结束偏移量
            chunk_type: 块类型 ("flat", "parent", "child")
            parent_chunk_id: 父块ID (用于层次结构)
            chunk_level: 块层级
            metadata: 额外的元数据
            
        Returns:
            DocumentChunk对象
        """
        if end_offset is None:
            end_offset = start_offset + len(content)
        
        chunk_metadata = {
            "chunk_type": chunk_type,
            "chunk_level": chunk_level,
            "document_filename": document.filename,
            "document_file_type": document.file_type,
            "parent_chunk_id": parent_chunk_id
        }
        
        if metadata:
            chunk_metadata.update(metadata)
        
        return DocumentChunk(
            content=content.strip(),
            chunk_index=chunk_index,
            start_offset=start_offset,
            end_offset=end_offset,
            document_id=document.document_id or "",
            knowledge_base_id=document.knowledge_base_id,
            metadata=chunk_metadata
        )
    
    def _validate_config(self, config: ChunkingConfig) -> None:
        """
        验证配置参数
        
        Args:
            config: 分块配置
            
        Raises:
            ValueError: 配置参数无效时抛出异常
        """
        if config.max_length <= 0:
            raise ValueError("max_length 必须大于 0")
        
        if config.overlap_length < 0:
            raise ValueError("overlap_length 不能小于 0")
        
        if config.overlap_length >= config.max_length:
            raise ValueError("overlap_length 不能大于等于 max_length")