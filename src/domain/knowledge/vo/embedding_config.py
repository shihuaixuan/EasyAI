"""
知识库领域 - Embedding配置值对象
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass(frozen=True)
class EmbeddingModelConfig:
    """Embedding模型配置值对象"""
    
    model_id: int
    model_name: str
    provider: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    strategy: str = 'high_quality'
    batch_size: int = 32
    max_tokens: int = 8192
    timeout: int = 30
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'model_id': self.model_id,
            'model_name': self.model_name,
            'provider': self.provider,
            'api_key': self.api_key,
            'base_url': self.base_url,
            'strategy': self.strategy,
            'batch_size': self.batch_size,
            'max_tokens': self.max_tokens,
            'timeout': self.timeout,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EmbeddingModelConfig':
        """从字典创建配置对象"""
        return cls(
            model_id=data['model_id'],
            model_name=data['model_name'],
            provider=data['provider'],
            api_key=data.get('api_key'),
            base_url=data.get('base_url'),
            strategy=data.get('strategy', 'high_quality'),
            batch_size=data.get('batch_size', 32),
            max_tokens=data.get('max_tokens', 8192),
            timeout=data.get('timeout', 30),
        )
    
    def is_valid(self) -> bool:
        """验证配置是否有效"""
        if not self.model_name or not self.provider:
            return False
        
        # 对于非本地模型，需要API密钥和base_url
        if self.provider != 'local':
            if not self.api_key or not self.base_url:
                return False
        
        return True
    
    def get_embedding_service_config(self) -> Dict[str, Any]:
        """获取用于创建embedding服务的配置"""
        config = {
            'model_name': self.model_name,
            'batch_size': self.batch_size,
            'max_tokens': self.max_tokens,
            'timeout': self.timeout,
        }
        
        if self.provider == 'local':
            config.update({
                'normalize_embeddings': True
            })
        else:
            config.update({
                'api_key': self.api_key,
                'base_url': self.base_url
            })
        
        return config


@dataclass(frozen=True)
class EmbeddingProcessResult:
    """Embedding处理结果值对象"""
    
    success: bool
    message: str
    processed_chunks: int = 0
    failed_chunks: int = 0
    model_name: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'success': self.success,
            'message': self.message,
            'processed_chunks': self.processed_chunks,
            'failed_chunks': self.failed_chunks,
            'model_name': self.model_name,
        }
    
    @classmethod
    def success_result(
        cls, 
        processed_chunks: int, 
        failed_chunks: int = 0,
        model_name: Optional[str] = None
    ) -> 'EmbeddingProcessResult':
        """创建成功结果"""
        message = f"处理完成，成功: {processed_chunks}"
        if failed_chunks > 0:
            message += f", 失败: {failed_chunks}"
        
        return cls(
            success=True,
            message=message,
            processed_chunks=processed_chunks,
            failed_chunks=failed_chunks,
            model_name=model_name
        )
    
    @classmethod
    def failure_result(cls, message: str) -> 'EmbeddingProcessResult':
        """创建失败结果"""
        return cls(
            success=False,
            message=message,
            processed_chunks=0,
            failed_chunks=0
        )
