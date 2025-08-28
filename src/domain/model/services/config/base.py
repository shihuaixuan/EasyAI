"""基础配置类定义"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import os
from pathlib import Path


class ModelProvider(Enum):
    """模型提供商枚举"""
    DEEPSEEK = "deepseek"
    OPENAI = "openai"
    SILICONFLOW = "siliconflow"


class ConfigSource(Enum):
    """配置来源枚举"""
    RUNTIME = "runtime"  # 运行时传入
    USER_CONFIG = "user_config"  # 用户配置文件
    PROJECT_CONFIG = "project_config"  # 项目配置文件
    ENVIRONMENT = "environment"  # 环境变量
    DEFAULT = "default"  # 默认配置


@dataclass
class BaseModelConfig(ABC):
    """基础模型配置类"""
    
    # 通用配置
    api_key: str = ""
    base_url: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    
    # 模型参数
    model: str = ""
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    
    # 元数据
    provider: ModelProvider = field(init=False)
    config_source: ConfigSource = ConfigSource.DEFAULT
    user_id: Optional[str] = None
    config_name: Optional[str] = None  # 配置名称，用于多配置管理
    
    # 验证和状态
    is_validated: bool = field(default=False, init=False)
    validation_errors: List[str] = field(default_factory=list, init=False)
    
    def __post_init__(self):
        """初始化后处理"""
        self.provider = self.get_provider()
        self._load_from_env()
    
    @abstractmethod
    def get_provider(self) -> ModelProvider:
        """获取模型提供商"""
        pass
    
    @abstractmethod
    def get_default_model(self) -> str:
        """获取默认模型名称"""
        pass
    
    @abstractmethod
    def get_default_base_url(self) -> Optional[str]:
        """获取默认API地址"""
        pass
    
    @abstractmethod
    def get_env_prefix(self) -> str:
        """获取环境变量前缀"""
        pass
    
    def _load_from_env(self):
        """从环境变量加载配置"""
        prefix = self.get_env_prefix()
        
        # 加载API密钥
        if not self.api_key:
            self.api_key = os.getenv(f"{prefix}_API_KEY", "")
        
        # 加载基础URL
        if not self.base_url:
            self.base_url = os.getenv(f"{prefix}_BASE_URL", self.get_default_base_url())
        
        # 加载模型名称
        if not self.model:
            self.model = os.getenv(f"{prefix}_MODEL", self.get_default_model())
        
        # 加载其他参数
        self.timeout = int(os.getenv(f"{prefix}_TIMEOUT", str(self.timeout)))
        self.max_retries = int(os.getenv(f"{prefix}_MAX_RETRIES", str(self.max_retries)))
        self.temperature = float(os.getenv(f"{prefix}_TEMPERATURE", str(self.temperature)))
        
        if os.getenv(f"{prefix}_MAX_TOKENS"):
            self.max_tokens = int(os.getenv(f"{prefix}_MAX_TOKENS"))
    
    def validate(self) -> bool:
        """验证配置"""
        self.validation_errors.clear()
        
        # 验证必需字段
        if not self.api_key:
            self.validation_errors.append(f"API密钥不能为空 ({self.provider.value})")
        
        if not self.model:
            self.validation_errors.append(f"模型名称不能为空 ({self.provider.value})")
        
        # 验证数值范围
        if self.temperature < 0 or self.temperature > 2:
            self.validation_errors.append("temperature必须在0-2之间")
        
        if self.top_p < 0 or self.top_p > 1:
            self.validation_errors.append("top_p必须在0-1之间")
        
        if self.timeout <= 0:
            self.validation_errors.append("timeout必须大于0")
        
        if self.max_retries < 0:
            self.validation_errors.append("max_retries不能小于0")
        
        if self.max_tokens is not None and self.max_tokens <= 0:
            self.validation_errors.append("max_tokens必须大于0")
        
        # 执行特定验证
        self._validate_specific()
        
        self.is_validated = len(self.validation_errors) == 0
        return self.is_validated
    
    @abstractmethod
    def _validate_specific(self):
        """特定模型的验证逻辑"""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {}
        for key, value in self.__dict__.items():
            if not key.startswith('_') and key not in ['validation_errors', 'is_validated']:
                if isinstance(value, Enum):
                    result[key] = value.value
                else:
                    result[key] = value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseModelConfig':
        """从字典创建配置"""
        # 过滤掉不存在的字段
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        
        # 处理枚举类型
        if 'config_source' in filtered_data and isinstance(filtered_data['config_source'], str):
            filtered_data['config_source'] = ConfigSource(filtered_data['config_source'])
        
        return cls(**filtered_data)
    
    def merge_with(self, other: 'BaseModelConfig') -> 'BaseModelConfig':
        """与另一个配置合并（优先使用非空值）"""
        merged_data = self.to_dict()
        other_data = other.to_dict()
        
        for key, value in other_data.items():
            if value and (not merged_data.get(key) or other.config_source.value < self.config_source.value):
                merged_data[key] = value
        
        return self.__class__.from_dict(merged_data)
    
    def get_client_kwargs(self) -> Dict[str, Any]:
        """获取客户端初始化参数"""
        kwargs = {
            'api_key': self.api_key,
            'timeout': self.timeout,
            'max_retries': self.max_retries
        }
        
        if self.base_url:
            kwargs['base_url'] = self.base_url
        
        return kwargs
    
    def get_completion_kwargs(self) -> Dict[str, Any]:
        """获取补全请求参数"""
        kwargs = {
            'model': self.model,
            'temperature': self.temperature,
            'top_p': self.top_p,
            'frequency_penalty': self.frequency_penalty,
            'presence_penalty': self.presence_penalty
        }
        
        if self.max_tokens:
            kwargs['max_tokens'] = self.max_tokens
        
        return kwargs
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(provider={self.provider.value}, model={self.model}, source={self.config_source.value})"
    
    def __repr__(self) -> str:
        return self.__str__()