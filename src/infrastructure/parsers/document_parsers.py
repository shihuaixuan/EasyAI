"""
基础文档解析器实现
"""

import os
from typing import List
from ...domain.knowledge.services.document_parser_service import DocumentParser
from ...domain.knowledge.entities.document import Document


class TextDocumentParser(DocumentParser):
    """文本文档解析器"""
    
    async def parse(self, file_path: str, filename: str) -> Document:
        """解析文本文档"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # 尝试其他编码
            try:
                with open(file_path, 'r', encoding='gb2312') as f:
                    content = f.read()
            except UnicodeDecodeError:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
        
        file_size = os.path.getsize(file_path)
        file_extension = self._get_file_extension(filename)
        
        return Document(
            filename=filename,
            content=content,
            file_type=file_extension,
            file_size=file_size,
            knowledge_base_id="",  # 将在服务层设置
            original_path=file_path
        )
    
    def supports(self, file_extension: str) -> bool:
        """检查是否支持该文件类型"""
        return file_extension.lower() in self.get_supported_extensions()
    
    def get_supported_extensions(self) -> List[str]:
        """获取支持的文件扩展名列表"""
        return ['.txt', '.md', '.mdx', '.csv', '.json', '.xml', '.html', '.htm']
    
    def _get_file_extension(self, filename: str) -> str:
        """获取文件扩展名"""
        if '.' not in filename:
            return 'unknown'
        return filename.split('.')[-1].lower()


class DefaultDocumentParser(DocumentParser):
    """默认文档解析器（用于不支持的文件类型）"""
    
    async def parse(self, file_path: str, filename: str) -> Document:
        """解析文档（作为二进制文件读取）"""
        file_size = os.path.getsize(file_path)
        file_extension = self._get_file_extension(filename)
        
        # 对于不支持的文件类型，返回空内容
        return Document(
            filename=filename,
            content="[Binary file - content not extracted]",
            file_type=file_extension,
            file_size=file_size,
            knowledge_base_id="",  # 将在服务层设置
            original_path=file_path,
            metadata={
                "note": "This file type is not supported for content extraction"
            }
        )
    
    def supports(self, file_extension: str) -> bool:
        """默认解析器支持所有文件类型"""
        return True
    
    def get_supported_extensions(self) -> List[str]:
        """返回通用支持的扩展名"""
        return ['.pdf', '.doc', '.docx', '.xlsx', '.xls', '.ppt', '.pptx']
    
    def _get_file_extension(self, filename: str) -> str:
        """获取文件扩展名"""
        if '.' not in filename:
            return 'unknown'
        return filename.split('.')[-1].lower()