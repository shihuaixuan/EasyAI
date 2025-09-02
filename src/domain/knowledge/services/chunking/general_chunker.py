"""
通用分块器 - 实现基础的固定长度分块策略
"""

import re
import unicodedata
from typing import List, Optional
from .base_chunker import BaseChunker
from ...entities.document import Document
from ...entities.document_chunk import DocumentChunk
from ...vo.chunking_config import ChunkingConfig, TextPreprocessingConfig


class GeneralChunker(BaseChunker):
    """通用分块器 - 基础的固定长度分块策略"""
    
    def get_strategy_name(self) -> str:
        """获取策略名称"""
        return "general"
    
    async def chunk(
        self, 
        document: Document, 
        config: ChunkingConfig
    ) -> List[DocumentChunk]:
        """
        通用分块策略实现
        
        Args:
            document: 待分块的文档
            config: 分块配置
            
        Returns:
            文档块列表
        """
        # 验证配置
        self._validate_config(config)
        
        if not document.content:
            return []
        
        # 文本预处理
        processed_content = self._preprocess_text(document.content, config.preprocessing)
        
        # 执行分块
        chunks = self._split_by_separator(document, processed_content, config)
        
        # 添加重叠内容
        if config.overlap_length > 0 and len(chunks) > 1:
            chunks = self._add_overlap(chunks, config.overlap_length)
        
        return chunks
    
    def _preprocess_text(self, text: str, preprocessing: Optional[TextPreprocessingConfig]) -> str:
        """
        文本预处理
        
        Args:
            text: 原始文本
            preprocessing: 预处理配置
            
        Returns:
            预处理后的文本
        """
        if not preprocessing:
            return text
        
        processed_text = text
        
        # Unicode标准化
        if preprocessing.normalize_unicode:
            processed_text = unicodedata.normalize('NFKC', processed_text)
        
        # 移除多余的空白字符
        if preprocessing.remove_extra_whitespace:
            # 将多个连续的空格、制表符替换为单个空格
            processed_text = re.sub(r'[ \t]+', ' ', processed_text)
            # 将多个换行符替换为两个换行符（保持段落分隔）
            processed_text = re.sub(r'\n\s*\n\s*\n+', '\n\n', processed_text)
            processed_text = processed_text.strip()
        
        # 移除URLs
        if preprocessing.remove_urls:
            processed_text = re.sub(r'https?://[^\s]+', '', processed_text)
        
        # 移除邮箱地址
        if preprocessing.remove_emails:
            processed_text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', processed_text)
        
        return processed_text
    
    def _split_by_separator(
        self, 
        document: Document, 
        content: str, 
        config: ChunkingConfig
    ) -> List[DocumentChunk]:
        """
        按分隔符分割文本
        
        Args:
            document: 文档对象
            content: 预处理后的文本内容
            config: 分块配置
            
        Returns:
            文档块列表
        """
        chunks = []
        sections = content.split(config.separator)
        
        current_chunk = ""
        current_start_offset = 0
        chunk_index = 0
        
        for i, section in enumerate(sections):
            # 如果当前块加上新段落不会超过最大长度，则合并
            separator = config.separator if current_chunk else ""
            potential_chunk = current_chunk + separator + section
            
            if len(potential_chunk) <= config.max_length:
                # 记录起始位置（仅在当前块为空时）
                if not current_chunk:
                    current_start_offset = self._find_section_offset(content, section, current_start_offset)
                current_chunk = potential_chunk
            else:
                # 保存当前块（如果不为空）
                if current_chunk:
                    chunk = self._create_chunk(
                        document=document,
                        content=current_chunk,
                        chunk_index=chunk_index,
                        start_offset=current_start_offset,
                        end_offset=current_start_offset + len(current_chunk)
                    )
                    chunks.append(chunk)
                    chunk_index += 1
                
                # 处理过长的单个段落
                if len(section) > config.max_length:
                    # 切分过长的段落
                    section_start = self._find_section_offset(content, section, current_start_offset)
                    sub_chunks = self._split_large_section(
                        document, section, config.max_length, section_start, chunk_index
                    )
                    chunks.extend(sub_chunks)
                    chunk_index += len(sub_chunks)
                    current_chunk = ""
                else:
                    # 开始新块
                    current_start_offset = self._find_section_offset(content, section, current_start_offset)
                    current_chunk = section
        
        # 保存最后一个块
        if current_chunk:
            chunk = self._create_chunk(
                document=document,
                content=current_chunk,
                chunk_index=chunk_index,
                start_offset=current_start_offset,
                end_offset=current_start_offset + len(current_chunk)
            )
            chunks.append(chunk)
        
        return chunks
    
    def _find_section_offset(self, content: str, section: str, start_from: int) -> int:
        """
        查找段落在原文中的位置
        
        Args:
            content: 原文内容
            section: 要查找的段落
            start_from: 开始查找的位置
            
        Returns:
            段落在原文中的偏移量
        """
        offset = content.find(section, start_from)
        return offset if offset != -1 else start_from
    
    def _split_large_section(
        self,
        document: Document,
        section: str,
        max_length: int,
        start_offset: int,
        start_chunk_index: int
    ) -> List[DocumentChunk]:
        """
        切分过长的段落
        
        Args:
            document: 文档对象
            section: 要切分的段落
            max_length: 最大长度
            start_offset: 段落在原文中的起始偏移量
            start_chunk_index: 起始块索引
            
        Returns:
            切分后的块列表
        """
        chunks = []
        chunk_index = start_chunk_index
        
        # 按字符数简单切分
        for i in range(0, len(section), max_length):
            chunk_content = section[i:i + max_length]
            chunk = self._create_chunk(
                document=document,
                content=chunk_content,
                chunk_index=chunk_index,
                start_offset=start_offset + i,
                end_offset=start_offset + i + len(chunk_content)
            )
            chunks.append(chunk)
            chunk_index += 1
        
        return chunks
    
    def _add_overlap(
        self, 
        chunks: List[DocumentChunk], 
        overlap_length: int
    ) -> List[DocumentChunk]:
        """
        为块添加重叠内容
        
        Args:
            chunks: 原始块列表
            overlap_length: 重叠长度
            
        Returns:
            添加重叠后的块列表
        """
        if not chunks or overlap_length <= 0:
            return chunks
        
        overlapped_chunks = []
        
        for i, chunk in enumerate(chunks):
            new_content = chunk.content
            
            # 添加前一个块的尾部内容
            if i > 0:
                prev_chunk = chunks[i - 1]
                prev_tail = prev_chunk.content[-overlap_length:] if len(prev_chunk.content) > overlap_length else prev_chunk.content
                new_content = prev_tail + " " + new_content
            
            # 添加后一个块的头部内容
            if i < len(chunks) - 1:
                next_chunk = chunks[i + 1]
                next_head = next_chunk.content[:overlap_length] if len(next_chunk.content) > overlap_length else next_chunk.content
                new_content = new_content + " " + next_head
            
            # 创建新的块（直接使用DocumentChunk构造函数）
            overlapped_chunk = DocumentChunk(
                content=new_content.strip(),
                chunk_index=chunk.chunk_index,
                start_offset=chunk.start_offset,
                end_offset=chunk.end_offset or (chunk.start_offset + len(chunk.content)),
                document_id=chunk.document_id,
                knowledge_base_id=chunk.knowledge_base_id,
                chunk_id=chunk.chunk_id,
                metadata=chunk.metadata or {},
                created_at=chunk.created_at,
                updated_at=chunk.updated_at
            )
            
            overlapped_chunks.append(overlapped_chunk)
        
        return overlapped_chunks