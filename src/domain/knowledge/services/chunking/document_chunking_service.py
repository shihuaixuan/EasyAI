"""
分块服务 - 文档分块的主要入口点
"""

from typing import List, Optional
from dataclasses import dataclass
from .chunker_factory import chunker_factory
from ...entities.document import Document
from ...entities.document_chunk import DocumentChunk
from ...vo.chunking_config import ChunkingConfig


@dataclass
class ChunkingResult:
    """分块结果"""
    chunks: List[str]
    total_chunks: int


class DocumentChunkingService:
    """文档分块服务"""
    
    def __init__(self):
        """初始化分块服务"""
        self.chunker_factory = chunker_factory
    
    async def chunk_document(
        self, 
        document: Document, 
        config: ChunkingConfig
    ) -> List[DocumentChunk]:
        """
        对文档进行分块处理
        
        Args:
            document: 要分块的文档
            config: 分块配置
            
        Returns:
            文档块列表
            
        Raises:
            ValueError: 当策略不支持或文档无效时
        """
        # 验证输入
        if not document:
            raise ValueError("文档不能为空")
        
        if not document.content:
            return []
        
        if not config:
            raise ValueError("分块配置不能为空")
        
        # 检查策略是否支持
        if not self.chunker_factory.is_strategy_supported(config.strategy):
            available_strategies = self.chunker_factory.get_available_strategies()
            raise ValueError(f"不支持的分块策略: {config.strategy}，可用策略: {available_strategies}")
        
        # 创建分块器
        chunker = self.chunker_factory.create_chunker(config.strategy)
        if not chunker:
            raise ValueError(f"无法创建分块器: {config.strategy}")
        
        # 执行分块
        try:
            chunks = await chunker.chunk(document, config)
            
            # 更新文档的分块统计信息
            if hasattr(document, 'chunk_count'):
                document.chunk_count = len(chunks)
            
            if hasattr(document, 'mark_as_processed'):
                document.mark_as_processed(len(chunks))
            
            return chunks
            
        except Exception as e:
            raise ValueError(f"文档分块失败: {str(e)}")
    
    async def chunk_text(
        self, 
        text: str, 
        config: ChunkingConfig
    ) -> "ChunkingResult":
        """
        对纯文本进行分块处理
        
        Args:
            text: 要分块的文本
            config: 分块配置
            
        Returns:
            分块结果
        """
        if not text:
            return ChunkingResult(chunks=[], total_chunks=0)
        
        if not config:
            raise ValueError("分块配置不能为空")
        
        # 根据策略进行分块
        if config.strategy == 'general':
            chunks = await self._chunk_text_general(text, config)
        elif config.strategy == 'parent_child':
            chunks = await self._chunk_text_parent_child(text, config)
        else:
            raise ValueError(f"不支持的分块策略: {config.strategy}")
        
        return ChunkingResult(chunks=chunks, total_chunks=len(chunks))
    
    async def _chunk_text_general(self, text: str, config: ChunkingConfig) -> List[str]:
        """普通分块策略"""
        # 简单实现：按分隔符分割
        separator = config.separator or '\n\n'
        max_length = config.max_length or 1024
        
        # 先按分隔符分割
        parts = text.split(separator)
        chunks = []
        current_chunk = ""
        
        for part in parts:
            if len(current_chunk) + len(part) + len(separator) <= max_length:
                if current_chunk:
                    current_chunk += separator + part
                else:
                    current_chunk = part
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = part
                
                # 如果单个部分太长，进一步分割
                while len(current_chunk) > max_length:
                    chunks.append(current_chunk[:max_length].strip())
                    current_chunk = current_chunk[max_length:]
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return [chunk for chunk in chunks if chunk]
    
    async def _chunk_text_parent_child(self, text: str, config: ChunkingConfig) -> List[str]:
        """父子分块策略"""
        # 简化实现：目前只返回子块
        child_separator = getattr(config, 'child_separator', '\n') or '\n'
        child_max_length = getattr(config, 'child_max_length', 512) or 512
        
        # 创建临时配置用于子块分割
        temp_config = ChunkingConfig(
            strategy='general',
            separator=child_separator,
            max_length=child_max_length,
            overlap_length=config.overlap_length,
            preprocessing=config.preprocessing
        )
        
        return await self._chunk_text_general(text, temp_config)
    
    def get_supported_strategies(self) -> List[str]:
        """
        获取支持的分块策略列表
        
        Returns:
            策略名称列表
        """
        return self.chunker_factory.get_available_strategies()
    
    def register_chunker(self, strategy_name: str, chunker_class):
        """
        注册新的分块器
        
        Args:
            strategy_name: 策略名称
            chunker_class: 分块器类
        """
        self.chunker_factory.register(strategy_name, chunker_class)