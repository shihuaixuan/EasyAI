"""
文档解析领域服务
"""

from abc import ABC, abstractmethod
from typing import Dict, Type, List, Optional
from ..entities.document import Document


class DocumentParser(ABC):
    """文档解析器基类"""
    
    @abstractmethod
    async def parse(self, file_path: str, filename: str) -> Document:
        """解析文档，返回文档对象"""
        pass
    
    @abstractmethod
    def supports(self, file_extension: str) -> bool:
        """检查是否支持该文件类型"""
        pass
    
    @abstractmethod
    def get_supported_extensions(self) -> List[str]:
        """获取支持的文件扩展名列表"""
        pass


class DocumentParserRegistry:
    """文档解析器注册表"""
    
    def __init__(self):
        self._parsers: Dict[str, Type[DocumentParser]] = {}
    
    def register(self, extensions: List[str], parser_class: Type[DocumentParser]):
        """注册解析器"""
        for ext in extensions:
            self._parsers[ext.lower()] = parser_class
    
    def get_parser(self, file_extension: str) -> Optional[DocumentParser]:
        """获取对应的解析器实例"""
        parser_class = self._parsers.get(file_extension.lower())
        if not parser_class:
            return None
        return parser_class()
    
    def list_supported_extensions(self) -> List[str]:
        """列出所有支持的扩展名"""
        return list(self._parsers.keys())
    
    def is_supported(self, file_extension: str) -> bool:
        """检查是否支持该文件类型"""
        return file_extension.lower() in self._parsers


class DocumentParserService:
    """文档解析服务"""
    
    def __init__(self, registry: DocumentParserRegistry):
        self.registry = registry
    
    async def parse_document(self, file_path: str, filename: str, knowledge_base_id: str) -> Document:
        """解析文档
        
        Args:
            file_path: 文件路径
            filename: 文件名
            knowledge_base_id: 知识库ID
            
        Returns:
            解析后的文档对象
            
        Raises:
            ValueError: 不支持的文件类型或解析失败
        """
        # 获取文件扩展名
        if '.' not in filename:
            raise ValueError(f"无法确定文件类型: {filename}")
        
        file_extension = '.' + filename.split('.')[-1].lower()
        
        # 获取解析器
        parser = self.registry.get_parser(file_extension)
        if not parser:
            raise ValueError(f"不支持的文件类型: {file_extension}")
        
        try:
            # 解析文档
            document = await parser.parse(file_path, filename)
            
            # 设置知识库ID
            document.knowledge_base_id = knowledge_base_id
            
            return document
            
        except Exception as e:
            raise ValueError(f"文档解析失败: {str(e)}")
    
    def get_supported_file_types(self) -> List[str]:
        """获取支持的文件类型列表"""
        return self.registry.list_supported_extensions()
    
    def is_supported_file_type(self, filename: str) -> bool:
        """检查是否支持该文件类型"""
        if '.' not in filename:
            return False
        
        file_extension = '.' + filename.split('.')[-1].lower()
        return self.registry.is_supported(file_extension)