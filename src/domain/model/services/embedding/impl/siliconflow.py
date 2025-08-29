import asyncio
import aiohttp
from typing import List, Optional
from ..base import BaseEmbedding, EmbeddingConfig
from ..registry import register_embedding


class SiliconFlowConfig(EmbeddingConfig):
    """SiliconFlow Embedding配置类"""
    
    def __init__(self, 
                 model_name: str = "BAAI/bge-large-zh-v1.5",
                 api_key: Optional[str] = None,
                 base_url: str = "https://api.siliconflow.cn/v1",
                 **kwargs):
        """初始化SiliconFlow配置
        
        Args:
            model_name: 模型名称，默认使用BAAI/bge-large-zh-v1.5
            api_key: SiliconFlow API密钥
            base_url: API基础URL
            **kwargs: 其他配置参数
        """
        super().__init__(
            model_name=model_name,
            api_key=api_key,
            base_url=base_url,
            **kwargs
        )

@register_embedding('siliconflow', SiliconFlowConfig)
class SiliconFlowEmbedding(BaseEmbedding):
    """SiliconFlow Embedding实现类"""
    
    def __init__(self, config: SiliconFlowConfig):
        """初始化SiliconFlow Embedding
        
        Args:
            config: SiliconFlow配置
        """
        self.config = config
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()
    
    async def close(self):
        """关闭会话"""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """获取HTTP会话
        
        Returns:
            aiohttp客户端会话
        """
        if self._session is None or self._session.closed:
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }
            self._session = aiohttp.ClientSession(headers=headers)
        return self._session
    
    async def embed_text(self, text: str) -> List[float]:
        """将单个文本转换为向量
        
        Args:
            text: 输入文本
            
        Returns:
            文本的向量表示
            
        Raises:
            ValueError: API密钥未设置或请求失败
            aiohttp.ClientError: 网络请求错误
        """
        if not self.config.api_key:
            raise ValueError("SiliconFlow API密钥未设置")
        
        session = await self._get_session()
        url = f"{self.config.base_url}/embeddings"
        
        payload = {
            "model": self.config.model_name,
            "input": text,
            "encoding_format": "float"
        }
        
        try:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise ValueError(f"SiliconFlow API请求失败: {response.status} - {error_text}")
                
                result = await response.json()
                
                # 检查响应格式
                if "data" not in result or not result["data"]:
                    raise ValueError("SiliconFlow API返回数据格式错误")
                
                # 获取embedding向量
                embedding = result["data"][0]["embedding"]
                return embedding
                
        except aiohttp.ClientError as e:
            raise aiohttp.ClientError(f"SiliconFlow API网络请求错误: {str(e)}")
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """将多个文本转换为向量
        
        Args:
            texts: 输入文本列表
            
        Returns:
            文本向量列表
        """
        # 简单实现：逐个调用embed_text
        # 后续可以优化为批量请求
        embeddings = []
        for text in texts:
            embedding = await self.embed_text(text)
            embeddings.append(embedding)
        return embeddings
    
    async def embed_query(self, query: str) -> List[float]:
        """将查询文本转换为向量
        
        Args:
            query: 查询文本
            
        Returns:
            查询向量表示
        """
        # 对于SiliconFlow，查询和文档使用相同的处理方式
        return await self.embed_text(query)
    
    def get_model_name(self) -> str:
        """获取模型名称
        
        Returns:
            模型名称
        """
        return self.config.model_name
    
    async def close(self):
        """关闭HTTP会话"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()