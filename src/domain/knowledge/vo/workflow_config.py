"""
工作流配置值对象
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from .chunking_config import ChunkingConfig


@dataclass(frozen=True)
class FileUploadConfig:
    """文件上传配置"""
    max_file_size: int = 15 * 1024 * 1024  # 15MB
    allowed_extensions: Optional[List[str]] = None
    upload_directory: str = "uploads"
    
    def __post_init__(self):
        if self.allowed_extensions is None:
            object.__setattr__(self, 'allowed_extensions', [
                '.txt', '.md', '.mdx', '.pdf', '.html', '.xlsx', '.xls',
                '.vtt', '.properties', '.doc', '.docx', '.csv', '.eml',
                '.msg', '.pptx', '.xml', '.epub', '.ppt', '.htm'
            ])
    
    def is_allowed_file(self, filename: str) -> bool:
        """检查文件是否被允许"""
        if '.' not in filename:
            return False
        extension = '.' + filename.split('.')[-1].lower()
        if self.allowed_extensions is None:
            return False
        return extension in self.allowed_extensions


@dataclass(frozen=True)
class EmbeddingConfig:
    """嵌入配置"""
    strategy: str  # "high_quality" or "economic"
    model_name: Optional[str] = None
    batch_size: int = 32
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {
            "strategy": self.strategy,
            "batch_size": self.batch_size
        }
        if self.model_name is not None:
            result["model_name"] = self.model_name
        return result


@dataclass(frozen=True)
class RetrievalConfig:
    """检索配置"""
    strategy: str  # "vector_search", "fulltext_search", "hybrid_search"
    top_k: int = 10
    score_threshold: float = 0.0
    enable_rerank: bool = False
    rerank_model: Optional[str] = None
    final_top_k: int = 5
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {
            "strategy": self.strategy,
            "top_k": self.top_k,
            "score_threshold": self.score_threshold,
            "enable_rerank": self.enable_rerank,
            "final_top_k": self.final_top_k
        }
        if self.rerank_model is not None:
            result["rerank_model"] = self.rerank_model
        return result


@dataclass(frozen=True)
class WorkflowConfig:
    """知识库工作流配置"""
    chunking: ChunkingConfig
    embedding: EmbeddingConfig
    retrieval: RetrievalConfig
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "chunking": self.chunking.to_dict(),
            "embedding": self.embedding.to_dict(),
            "retrieval": self.retrieval.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkflowConfig':
        """从字典创建配置对象"""
        chunking = ChunkingConfig.from_dict(data['chunking'])
        
        embedding_data = data['embedding']
        embedding = EmbeddingConfig(
            strategy=embedding_data['strategy'],
            model_name=embedding_data.get('model_name'),
            batch_size=embedding_data.get('batch_size', 32)
        )
        
        retrieval_data = data['retrieval']
        retrieval = RetrievalConfig(
            strategy=retrieval_data['strategy'],
            top_k=retrieval_data.get('top_k', 10),
            score_threshold=retrieval_data.get('score_threshold', 0.0),
            enable_rerank=retrieval_data.get('enable_rerank', False),
            rerank_model=retrieval_data.get('rerank_model'),
            final_top_k=retrieval_data.get('final_top_k', 5)
        )
        
        return cls(
            chunking=chunking,
            embedding=embedding,
            retrieval=retrieval
        )