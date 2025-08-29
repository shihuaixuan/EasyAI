# -*- coding: utf-8 -*-
"""
SiliconFlow重排序服务实现

本模块实现了基于SiliconFlow API的文本重排序服务。
SiliconFlow提供高质量的重排序模型，能够根据查询对候选文档进行精确的相关性排序。
"""

import asyncio
import json
from typing import List, Optional, Dict, Any
import aiohttp
import logging

from ..base import BaseRerank, RerankConfig, RerankResult
from ..registry import register_rerank

# 配置日志
logger = logging.getLogger(__name__)


class SiliconFlowConfig(RerankConfig):
    """SiliconFlow重排序配置类
    
    继承自RerankConfig，添加SiliconFlow特定的配置参数。
    """
    
    def __init__(self,
                 model_name: str = "BAAI/bge-reranker-v2-m3",
                 api_key: Optional[str] = None,
                 base_url: str = "https://api.siliconflow.cn/v1",
                 top_k: Optional[int] = None,
                 max_retries: int = 3,
                 timeout: float = 30.0,
                 **kwargs):
        """初始化SiliconFlow配置
        
        Args:
            model_name: 模型名称，默认使用BAAI/bge-reranker-v2-m3
            api_key: SiliconFlow API密钥
            base_url: API基础URL
            top_k: 返回的top-k结果数量
            max_retries: 最大重试次数
            timeout: 请求超时时间（秒）
            **kwargs: 其他配置参数
        """
        super().__init__(model_name=model_name, top_k=top_k, **kwargs)
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.max_retries = max_retries
        self.timeout = timeout
        
        # 验证必要参数
        if not self.api_key:
            raise ValueError("api_key是必需的参数")
    
    def get_headers(self) -> Dict[str, str]:
        """获取请求头
        
        Returns:
            包含认证信息的请求头
        """
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "EasyAI-SiliconFlow-Rerank/1.0"
        }
    
    def get_endpoint(self) -> str:
        """获取重排序API端点
        
        Returns:
            完整的API端点URL
        """
        return f"{self.base_url}/rerank"


@register_rerank("siliconflow", SiliconFlowConfig)
class SiliconFlowRerank(BaseRerank):
    """SiliconFlow重排序服务实现
    
    使用SiliconFlow API进行文本重排序的具体实现。
    """
    
    def __init__(self, config: SiliconFlowConfig):
        """初始化SiliconFlow重排序服务
        
        Args:
            config: SiliconFlow配置
        """
        if not isinstance(config, SiliconFlowConfig):
            raise TypeError("config必须是SiliconFlowConfig的实例")
        super().__init__(config)
        self.config: SiliconFlowConfig = config
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """获取或创建HTTP会话
        
        Returns:
            aiohttp客户端会话
        """
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                headers=self.config.get_headers()
            )
        return self._session
    
    async def _make_request(self, query: str, texts: List[str]) -> Dict[str, Any]:
        """发送重排序请求
        
        Args:
            query: 查询文本
            texts: 待重排序的文本列表
            
        Returns:
            API响应数据
            
        Raises:
            RuntimeError: 当API请求失败时
        """
        session = await self._get_session()
        
        # 构建请求数据
        request_data = {
            "model": self.config.model_name,
            "query": query,
            "documents": texts
        }
        
        # 添加top_k参数（如果配置了）
        if self.config.top_k is not None:
            request_data["top_k"] = self.config.top_k
        
        last_exception = None
        
        # 重试逻辑
        for attempt in range(self.config.max_retries + 1):
            try:
                async with session.post(
                    self.config.get_endpoint(),
                    json=request_data
                ) as response:
                    
                    # 检查响应状态
                    if response.status == 200:
                        return await response.json()
                    
                    # 处理错误响应
                    error_text = await response.text()
                    error_msg = f"API请求失败，状态码: {response.status}, 响应: {error_text}"
                    
                    if response.status == 401:
                        raise RuntimeError(f"认证失败，请检查API密钥: {error_msg}")
                    elif response.status == 429:
                        if attempt < self.config.max_retries:
                            wait_time = 2 ** attempt
                            logger.warning(f"请求频率限制，等待{wait_time}秒后重试...")
                            await asyncio.sleep(wait_time)
                            continue
                        raise RuntimeError(f"请求频率限制: {error_msg}")
                    elif response.status >= 500:
                        if attempt < self.config.max_retries:
                            wait_time = 2 ** attempt
                            logger.warning(f"服务器错误，等待{wait_time}秒后重试...")
                            await asyncio.sleep(wait_time)
                            continue
                        raise RuntimeError(f"服务器错误: {error_msg}")
                    else:
                        raise RuntimeError(error_msg)
                        
            except aiohttp.ClientError as e:
                last_exception = e
                if attempt < self.config.max_retries:
                    wait_time = 2 ** attempt
                    logger.warning(f"网络错误，等待{wait_time}秒后重试: {str(e)}")
                    await asyncio.sleep(wait_time)
                    continue
                break
        
        # 所有重试都失败了
        if last_exception:
            raise RuntimeError(f"网络请求失败: {str(last_exception)}")
        else:
            raise RuntimeError("重排序请求失败，已达到最大重试次数")
    
    def _parse_response(self, response_data: Dict[str, Any], original_texts: List[str]) -> List[RerankResult]:
        """解析API响应数据
        
        Args:
            response_data: API响应数据
            original_texts: 原始文本列表
            
        Returns:
            重排序结果列表
            
        Raises:
            RuntimeError: 当响应格式无效时
        """
        try:
            # 检查响应格式
            if "results" not in response_data:
                raise RuntimeError("API响应格式无效：缺少results字段")
            
            results = []
            for item in response_data["results"]:
                # 验证必需字段
                if "index" not in item or "relevance_score" not in item:
                    logger.warning(f"跳过无效的结果项: {item}")
                    continue
                
                index = item["index"]
                score = item["relevance_score"]
                
                # 验证索引范围
                if not (0 <= index < len(original_texts)):
                    logger.warning(f"跳过无效的索引: {index}")
                    continue
                
                # 创建结果对象
                result = RerankResult(
                    text=original_texts[index],
                    score=float(score),
                    index=index
                )
                results.append(result)
            
            # 按分数降序排序
            results.sort(key=lambda x: x.score, reverse=True)
            
            return results
            
        except (KeyError, ValueError, TypeError) as e:
            raise RuntimeError(f"解析API响应失败: {str(e)}")
    
    async def rerank(self, query: str, texts: List[str]) -> List[RerankResult]:
        """对文本列表进行重排序
        
        Args:
            query: 查询文本
            texts: 待重排序的文本列表
            
        Returns:
            重排序结果列表，按相关性分数降序排列
            
        Raises:
            ValueError: 当输入参数无效时
            RuntimeError: 当重排序过程出现错误时
        """
        # 验证输入参数
        self._validate_inputs(query, texts)
        
        try:
            # 发送API请求
            response_data = await self._make_request(query, texts)
            
            # 解析响应
            results = self._parse_response(response_data, texts)
            
            # 应用top_k限制
            results = self._apply_top_k(results)
            
            logger.info(f"成功重排序{len(texts)}个文档，返回{len(results)}个结果")
            return results
            
        except Exception as e:
            logger.error(f"重排序失败: {str(e)}")
            raise
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()
    
    async def close(self):
        """关闭HTTP会话"""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None
    
    def __repr__(self) -> str:
        """SiliconFlow重排序服务的字符串表示"""
        return f"SiliconFlowRerank(model={self.config.model_name}, base_url={self.config.base_url})"


# 便捷函数
async def create_siliconflow_rerank(api_key: str,
                                   model_name: str = "BAAI/bge-reranker-v2-m3",
                                   **kwargs) -> SiliconFlowRerank:
    """创建SiliconFlow重排序服务实例
    
    Args:
        api_key: SiliconFlow API密钥
        model_name: 模型名称
        **kwargs: 其他配置参数
        
    Returns:
        SiliconFlow重排序服务实例
    """
    config = SiliconFlowConfig(
        api_key=api_key,
        model_name=model_name,
        **kwargs
    )
    return SiliconFlowRerank(config)