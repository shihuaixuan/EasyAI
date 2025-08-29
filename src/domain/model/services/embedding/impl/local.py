import os
import asyncio
from typing import List, Optional, Union
from pathlib import Path

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    raise ImportError(
        "需要安装sentence-transformers库来加载本地embedding模型。"
        "请运行: pip install sentence-transformers"
    )

from ..base import BaseEmbedding, EmbeddingConfig
from ..registry import register_embedding


class LocalConfig(EmbeddingConfig):
    """本地Embedding配置类"""
    
    def __init__(self, 
                 model_path: str,
                 model_name: Optional[str] = None,
                 device: str = "auto",
                 normalize_embeddings: bool = True,
                 batch_size: int = 32,
                 max_seq_length: Optional[int] = None,
                 **kwargs):
        """初始化本地Embedding配置
        
        Args:
            model_path: 本地模型路径，如 /opt/embedding/bge-m3
            model_name: 模型名称，如果不提供则从路径推断
            device: 设备类型，auto/cpu/cuda
            normalize_embeddings: 是否归一化向量
            batch_size: 批处理大小
            max_seq_length: 最大序列长度
            **kwargs: 其他配置参数
        """
        if model_name is None:
            model_name = Path(model_path).name
            
        super().__init__(
            model_name=model_name,
            batch_size=batch_size,
            **kwargs
        )
        
        self.model_path = model_path
        self.device = device
        self.normalize_embeddings = normalize_embeddings
        self.max_seq_length = max_seq_length


@register_embedding('local', LocalConfig)
class LocalEmbedding(BaseEmbedding):
    """本地Embedding实现类"""
    
    def __init__(self, config: LocalConfig):
        """初始化本地Embedding
        
        Args:
            config: 本地Embedding配置
        """
        self.config = config
        self.model = None
        self._device = None
        
    async def _initialize_model(self):
        """初始化模型"""
        if self.model is not None:
            return
            
        model_path = self.config.model_path
        
        # 检查模型路径是否存在
        if not os.path.exists(model_path):
            raise ValueError(f"模型路径不存在: {model_path}")
            
        # 确定设备
        if self.config.device == "auto":
            try:
                import torch
                if torch.cuda.is_available():
                    self._device = "cuda"
                else:
                    self._device = "cpu"
            except ImportError:
                self._device = "cpu"
        else:
            self._device = self.config.device
            
        # 使用sentence-transformers加载模型
        try:
            self.model = SentenceTransformer(
                model_path,
                device=self._device
            )
            
            # 设置最大序列长度
            if self.config.max_seq_length:
                self.model.max_seq_length = self.config.max_seq_length
                
        except Exception as e:
            raise ValueError(f"加载模型失败: {e}")
    
    async def _encode_texts(self, texts: List[str]) -> List[List[float]]:
        """编码文本为向量"""
        if not isinstance(texts, list):
            texts = [texts]
            
        # 使用sentence-transformers编码
        embeddings = self.model.encode(
            texts,
            batch_size=self.config.batch_size,
            normalize_embeddings=self.config.normalize_embeddings,
            convert_to_numpy=True
        )
        
        return embeddings.tolist()
    
    async def embed_text(self, text: str) -> List[float]:
        """将单个文本转换为向量
        
        Args:
            text: 输入文本
            
        Returns:
            文本的向量表示
        """
        await self._initialize_model()
        embeddings = await self._encode_texts([text])
        return embeddings[0]
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """将多个文本转换为向量
        
        Args:
            texts: 输入文本列表
            
        Returns:
            文本向量列表
        """
        await self._initialize_model()
        return await self._encode_texts(texts)
    
    async def embed_query(self, query: str) -> List[float]:
        """将查询文本转换为向量
        
        Args:
            query: 查询文本
            
        Returns:
            查询向量表示
        """
        # 对于本地模型，查询和文档使用相同的处理方式
        return await self.embed_text(query)
    
    def get_model_name(self) -> str:
        """获取模型名称
        
        Returns:
            模型名称
        """
        return self.config.model_name
    
    async def close(self):
        """清理资源"""
        if self.model is not None:
            if hasattr(self.model, 'cpu'):
                self.model.cpu()
            del self.model
            self.model = None
            
        # 清理GPU缓存
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self._initialize_model()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()