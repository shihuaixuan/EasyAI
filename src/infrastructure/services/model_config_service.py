"""
模型配置读取服务
"""
import os
import yaml
from typing import List, Dict, Any, Optional
from pathlib import Path

class ModelConfigService:
    """
    模型配置服务，用于读取模型配置文件
    """
    
    def __init__(self, models_dir: str = None):
        """
        初始化模型配置服务
        
        Args:
            models_dir: 模型配置文件目录路径
        """
        if models_dir is None:
            current_dir = Path(__file__).parent.parent
            self.models_dir = current_dir / "models"
        else:
            self.models_dir = Path(models_dir)
    
    def get_provider_models(self, provider: str) -> List[Dict[str, Any]]:
        """
        获取指定提供商的所有模型配置
        
        Args:
            provider: 提供商名称（如：deepseek, openai, anthropic, siliconflow）
            
        Returns:
            模型配置列表
        """
        provider_dir = self.models_dir / provider
        
        if not provider_dir.exists():
            return []
        
        models = []
        for yaml_file in provider_dir.glob("*.yaml"):
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    if config:
                        models.append(config)
            except Exception as e:
                print(f"Error loading model config {yaml_file}: {e}")
        
        return models
    
    def get_model_config(self, provider: str, model_name: str) -> Optional[Dict[str, Any]]:
        """
        获取指定模型的配置
        
        Args:
            provider: 提供商名称
            model_name: 模型名称
            
        Returns:
            模型配置字典，如果不存在则返回None
        """
        models = self.get_provider_models(provider)
        for model_config in models:
            if model_config.get('model') == model_name:
                return model_config
        return None
    
    def get_all_providers(self) -> List[str]:
        """
        获取所有可用的提供商列表
        
        Returns:
            提供商名称列表
        """
        if not self.models_dir.exists():
            return []
        
        providers = []
        for item in self.models_dir.iterdir():
            if item.is_dir():
                providers.append(item.name)
        
        return sorted(providers)
    
    def get_all_models(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取所有提供商的所有模型配置
        
        Returns:
            按提供商分组的模型配置字典
        """
        all_models = {}
        for provider in self.get_all_providers():
            all_models[provider] = self.get_provider_models(provider)
        
        return all_models


# 全局模型配置服务实例
model_config_service = ModelConfigService()