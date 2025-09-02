"""
分块服务 - 文档分块的主要入口点
"""

from typing import List, Optional
from .chunker_factory import chunker_factory
from ...entities.document import Document
from ...entities.document_chunk import DocumentChunk
from ...vo.chunking_config import ChunkingConfig


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