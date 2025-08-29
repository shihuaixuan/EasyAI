from typing import Protocol, List, Dict, Any, Optional, Union
from abc import abstractmethod


class BaseEmbedding(Protocol):
    """基础Embedding协议"""
    
    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """将单个文本转换为向量
        
        Args:
            text: 输入文本
            
        Returns:
            文本的向量表示
        """
        ...
    
    @abstractmethod
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """将多个文本转换为向量
        
        Args:
            texts: 输入文本列表
            
        Returns:
            文本向量列表
        """
        ...
    
    @abstractmethod
    async def embed_query(self, query: str) -> List[float]:
        """将查询文本转换为向量（可能与普通文本有不同的处理）
        
        Args:
            query: 查询文本
            
        Returns:
            查询向量表示
        """
        ...
    
    
    @abstractmethod
    def get_model_name(self) -> str:
        """获取模型名称
        
        Returns:
            模型名称
        """
        ...


class EmbeddingUtils:
    """Embedding工具类"""
    
    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度
        
        Args:
            vec1: 向量1
            vec2: 向量2
            
        Returns:
            余弦相似度值 (-1到1之间)
        """
        import math
        
        if len(vec1) != len(vec2):
            raise ValueError("向量维度不匹配")
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(a * a for a in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    @staticmethod
    def euclidean_distance(vec1: List[float], vec2: List[float]) -> float:
        """计算欧几里得距离
        
        Args:
            vec1: 向量1
            vec2: 向量2
            
        Returns:
            欧几里得距离
        """
        import math
        
        if len(vec1) != len(vec2):
            raise ValueError("向量维度不匹配")
        
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(vec1, vec2)))
    
    @staticmethod
    def normalize_vector(vector: List[float]) -> List[float]:
        """向量归一化
        
        Args:
            vector: 输入向量
            
        Returns:
            归一化后的向量
        """
        import math
        
        magnitude = math.sqrt(sum(x * x for x in vector))
        if magnitude == 0:
            return vector
        
        return [x / magnitude for x in vector]
    
    @staticmethod
    def batch_cosine_similarity(query_vec: List[float], 
                              doc_vecs: List[List[float]]) -> List[float]:
        """批量计算余弦相似度
        
        Args:
            query_vec: 查询向量
            doc_vecs: 文档向量列表
            
        Returns:
            相似度列表
        """
        return [EmbeddingUtils.cosine_similarity(query_vec, doc_vec) 
                for doc_vec in doc_vecs]


class EmbeddingConfig:
    """Embedding配置基类"""
    
    def __init__(self, 
                 model_name: str,
                 api_key: Optional[str] = None,
                 base_url: Optional[str] = None,
                 max_tokens: int = 8192,
                 batch_size: int = 100,
                 **kwargs):
        """初始化配置
        
        Args:
            model_name: 模型名称
            api_key: API密钥
            base_url: API基础URL
            max_tokens: 最大token数
            batch_size: 批处理大小
            **kwargs: 其他配置参数
        """
        self.model_name = model_name
        self.api_key = api_key
        self.base_url = base_url
        self.max_tokens = max_tokens
        self.batch_size = batch_size
        self.extra_config = kwargs
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典
        
        Returns:
            配置字典
        """
        config = {
            'model_name': self.model_name,
            'api_key': self.api_key,
            'base_url': self.base_url,
            'max_tokens': self.max_tokens,
            'batch_size': self.batch_size
        }
        config.update(self.extra_config)
        return config