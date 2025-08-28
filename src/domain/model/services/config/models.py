"""具体模型配置类定义"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import re

from .base import BaseModelConfig, ModelProvider
from .registry import ConfigRegistry, register_config


@register_config(ModelProvider.OPENAI)
@dataclass
class OpenAIConfig(BaseModelConfig):
    """OpenAI配置"""
    
    # OpenAI特有配置
    organization: Optional[str] = None
    project: Optional[str] = None
    
    def get_provider(self) -> ModelProvider:
        return ModelProvider.OPENAI
    
    def get_default_model(self) -> str:
        return "gpt-3.5-turbo"
    
    def get_default_base_url(self) -> Optional[str]:
        return "https://api.openai.com/v1"
    
    def get_env_prefix(self) -> str:
        return "OPENAI"
    
    def _validate_specific(self):
        """OpenAI特定验证"""
        # 验证模型名称格式
        valid_models = [
            "gpt-3.5-turbo", "gpt-3.5-turbo-16k",
            "gpt-4", "gpt-4-32k", "gpt-4-turbo", "gpt-4o",
            "gpt-4o-mini"
        ]
        
        if self.model and not any(self.model.startswith(model) for model in valid_models):
            self.validation_errors.append(f"不支持的OpenAI模型: {self.model}")
    
    def get_client_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_client_kwargs()
        
        if self.organization:
            kwargs['organization'] = self.organization
        
        if self.project:
            kwargs['project'] = self.project
        
        return kwargs


@register_config(ModelProvider.DEEPSEEK)
@dataclass
class DeepSeekConfig(BaseModelConfig):
    """DeepSeek配置"""
    
    def get_provider(self) -> ModelProvider:
        return ModelProvider.DEEPSEEK
    
    def get_default_model(self) -> str:
        return "deepseek-chat"
    
    def get_default_base_url(self) -> Optional[str]:
        return "https://api.deepseek.com/v1"
    
    def get_env_prefix(self) -> str:
        return "DEEPSEEK"
    
    def _validate_specific(self):
        """DeepSeek特定验证"""
        valid_models = [
            "deepseek-chat", "deepseek-coder"
        ]
        
        if self.model and self.model not in valid_models:
            self.validation_errors.append(f"不支持的DeepSeek模型: {self.model}")


@register_config(ModelProvider.SILICONFLOW)
@dataclass
class SiliconflowConfig(BaseModelConfig):
    """Siliconflow配置"""
    
    def get_provider(self) -> ModelProvider:
        return ModelProvider.SILICONFLOW
    
    def get_default_model(self) -> str:
        return "siliconflow-chat"
    
    def get_default_base_url(self) -> Optional[str]:
        return "https://api.siliconflow.cn/v1"
    
    def get_env_prefix(self) -> str:
        return "SILICONFLOW"
    
    def _validate_specific(self):
        """Siliconflow特定验证"""
        valid_models = [
            "siliconflow-chat", "siliconflow-coder"
        ]
        
        if self.model and self.model not in valid_models:
            self.validation_errors.append(f"不支持的Siliconflow模型: {self.model}")



class ModelConfigFactory:
    """模型配置工厂"""
    
    @classmethod
    def create_config(cls, provider: ModelProvider, **kwargs) -> BaseModelConfig:
        """创建指定提供商的配置"""
        config_class = ConfigRegistry.get_config_class(provider)
        if config_class is None:
            raise ValueError(f"不支持的模型提供商: {provider}")
        
        return config_class(**kwargs)

    @classmethod
    def get_config(cls, provider: ModelProvider) -> BaseModelConfig:
        """获取指定提供商的配置类"""
        config_class = ConfigRegistry.get_config_class(provider)
        if config_class is None:
            raise ValueError(f"不支持的模型提供商: {provider}")
        
        return config_class()
    
    @classmethod
    def create_from_dict(cls, data: Dict[str, Any]) -> BaseModelConfig:
        """从字典创建配置"""
        provider_str = data.get('provider')
        if not provider_str:
            raise ValueError("配置中缺少provider字段")
        
        try:
            provider = ModelProvider(provider_str)
        except ValueError:
            raise ValueError(f"不支持的模型提供商: {provider_str}")
        
        # 移除provider字段，避免重复
        config_data = {k: v for k, v in data.items() if k != 'provider'}
        
        return cls.create_config(provider, **config_data)
    
    @classmethod
    def get_supported_providers(cls) -> List[ModelProvider]:
        """获取支持的提供商列表"""
        return list(ConfigRegistry.list_configs().keys())
    
    @classmethod
    def get_config_template(cls, provider: ModelProvider) -> Dict[str, Any]:
        """获取配置模板"""
        config_class = ConfigRegistry.get_config_class(provider)
        if config_class is None:
            raise ValueError(f"不支持的模型提供商: {provider}")
        
        config = config_class()
        
        # 返回模板，隐藏敏感信息
        template = config.to_dict()
        template['api_key'] = "your_api_key_here"
        
        return template
    
    @classmethod
    def validate_config_data(cls, data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """验证配置数据"""
        try:
            config = cls.create_from_dict(data)
            is_valid = config.validate()
            return is_valid, config.validation_errors
        except Exception as e:
            return False, [str(e)]