"""
YAML模型配置文件解析器
用于解析models目录下的yaml配置文件并转换为数据库模型格式
"""

import os
import yaml
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ModelConfig:
    """模型配置数据类"""
    model_name: str
    model_type: str
    provider: str
    description: str
    capabilities: List[str]
    context_length: int
    max_tokens: int
    pricing: Dict[str, float]
    parameters: Dict[str, Any]
    
    def to_metadata_dict(self) -> Dict[str, Any]:
        """转换为数据库存储的元数据格式"""
        return {
            "description": self.description,
            "capabilities": self.capabilities,
            "context_length": self.context_length,
            "max_tokens": self.max_tokens,
            "pricing": self.pricing,
            "parameters": self.parameters
        }
    
    def get_model_type_and_subtype(self) -> tuple[str, Optional[str]]:
        """获取模型类型和子类型"""
        model_type = self.model_type.lower()
        
        # 根据capabilities推断子类型
        subtype = None
        if "chat" in self.capabilities:
            subtype = "chat"
        elif "completion" in self.capabilities:
            subtype = "completion"
        elif "embedding" in self.capabilities:
            subtype = "embedding"
        elif "rerank" in self.capabilities:
            subtype = "rerank"
            
        return model_type, subtype


class ModelConfigParser:
    """模型配置解析器"""
    
    def __init__(self, models_dir: str):
        """
        初始化解析器
        
        Args:
            models_dir: models目录路径
        """
        self.models_dir = Path(models_dir)
        
    def parse_yaml_file(self, yaml_path: Path) -> Optional[ModelConfig]:
        """
        解析单个YAML文件
        
        Args:
            yaml_path: YAML文件路径
            
        Returns:
            解析后的模型配置，解析失败返回None
        """
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                
            # 验证必需字段
            required_fields = ['model', 'model_type', 'provider']
            for field in required_fields:
                if field not in data:
                    print(f"警告: {yaml_path} 缺少必需字段 '{field}'")
                    return None
                    
            return ModelConfig(
                model_name=data['model'],
                model_type=data['model_type'],
                provider=data['provider'],
                description=data.get('description', ''),
                capabilities=data.get('capabilities', []),
                context_length=data.get('context_length', 0),
                max_tokens=data.get('max_tokens', 0),
                pricing=data.get('pricing', {}),
                parameters=data.get('parameters', {})
            )
            
        except Exception as e:
            print(f"解析YAML文件失败 {yaml_path}: {e}")
            return None
    
    def scan_all_models(self) -> List[ModelConfig]:
        """
        扫描所有YAML配置文件
        
        Returns:
            所有解析成功的模型配置列表
        """
        model_configs = []
        
        # 遍历所有子目录
        for provider_dir in self.models_dir.iterdir():
            if not provider_dir.is_dir() or provider_dir.name.startswith('.') or provider_dir.name == '__pycache__':
                continue
                
            # 扫描提供商目录下的所有yaml文件
            for yaml_file in provider_dir.glob('*.yaml'):
                config = self.parse_yaml_file(yaml_file)
                if config:
                    model_configs.append(config)
                    print(f"成功解析: {yaml_file}")
                    
        return model_configs
    
    def get_provider_configs(self) -> Dict[str, Dict[str, Any]]:
        """
        获取提供商配置信息
        
        Returns:
            提供商配置字典
        """
        # 这里可以扩展为从配置文件读取提供商的默认配置
        # 目前返回基本的提供商信息
        providers = {}
        
        for provider_dir in self.models_dir.iterdir():
            if not provider_dir.is_dir() or provider_dir.name.startswith('.') or provider_dir.name == '__pycache__':
                continue
                
            provider_name = provider_dir.name
            providers[provider_name] = {
                "name": provider_name,
                "base_url": self._get_default_base_url(provider_name),
                "description": f"{provider_name.title()} AI Provider"
            }
            
        return providers
    
    def _get_default_base_url(self, provider: str) -> Optional[str]:
        """获取提供商的默认base_url"""
        default_urls = {
            "openai": "https://api.openai.com/v1",
            "anthropic": "https://api.anthropic.com",
            "deepseek": "https://api.deepseek.com/v1",
            "siliconflow": "https://api.siliconflow.cn/v1"
        }
        return default_urls.get(provider.lower())


if __name__ == "__main__":
    # 测试解析器
    models_dir = "/Users/twenty/LLM/EasyAI/src/infrastructure/models"
    parser = ModelConfigParser(models_dir)
    
    print("=== 扫描所有模型配置 ===")
    configs = parser.scan_all_models()
    for config in configs:
        print(f"模型: {config.model_name}, 类型: {config.model_type}, 提供商: {config.provider}")
    
    print(f"\n总共找到 {len(configs)} 个模型配置")
    
    print("\n=== 提供商配置 ===")
    providers = parser.get_provider_configs()
    for name, info in providers.items():
        print(f"提供商: {name}, Base URL: {info['base_url']}")
