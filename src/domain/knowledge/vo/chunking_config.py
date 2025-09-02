"""
分块配置值对象
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass(frozen=True)
class TextPreprocessingConfig:
    """文本预处理配置"""
    remove_extra_whitespace: bool = False
    remove_urls: bool = False
    remove_emails: bool = False
    normalize_unicode: bool = True


@dataclass(frozen=True)
class ChunkingConfig:
    """分块配置值对象"""
    strategy: str  # "parent_child" or "general"
    separator: str = "\n\n"
    max_length: int = 1024
    overlap_length: int = 50
    preprocessing: Optional[TextPreprocessingConfig] = None
    
    # 父子分段特有配置
    parent_separator: Optional[str] = None
    parent_max_length: Optional[int] = None
    child_separator: Optional[str] = None
    child_max_length: Optional[int] = None
    
    def __post_init__(self):
        if self.preprocessing is None:
            object.__setattr__(self, 'preprocessing', TextPreprocessingConfig())
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        preprocessing = self.preprocessing or TextPreprocessingConfig()
        result = {
            "strategy": self.strategy,
            "separator": self.separator,
            "max_length": self.max_length,
            "overlap_length": self.overlap_length,
            "preprocessing": {
                "remove_extra_whitespace": preprocessing.remove_extra_whitespace,
                "remove_urls": preprocessing.remove_urls,
                "remove_emails": preprocessing.remove_emails,
                "normalize_unicode": preprocessing.normalize_unicode
            }
        }
        
        if self.parent_separator is not None:
            result["parent_separator"] = self.parent_separator
        if self.parent_max_length is not None:
            result["parent_max_length"] = self.parent_max_length
        if self.child_separator is not None:
            result["child_separator"] = self.child_separator
        if self.child_max_length is not None:
            result["child_max_length"] = self.child_max_length
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChunkingConfig':
        """从字典创建配置对象"""
        preprocessing_data = data.get('preprocessing', {})
        preprocessing = TextPreprocessingConfig(
            remove_extra_whitespace=preprocessing_data.get('remove_extra_whitespace', False),
            remove_urls=preprocessing_data.get('remove_urls', False),
            remove_emails=preprocessing_data.get('remove_emails', False),
            normalize_unicode=preprocessing_data.get('normalize_unicode', True)
        )
        
        return cls(
            strategy=data['strategy'],
            separator=data.get('separator', '\n\n'),
            max_length=data.get('max_length', 1024),
            overlap_length=data.get('overlap_length', 50),
            preprocessing=preprocessing,
            parent_separator=data.get('parent_separator'),
            parent_max_length=data.get('parent_max_length'),
            child_separator=data.get('child_separator'),
            child_max_length=data.get('child_max_length')
        )