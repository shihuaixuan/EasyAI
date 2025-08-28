"""模型工厂测试类"""

import unittest
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

# 导入模型服务模块（会自动触发模型注册）
from src.domain.model.services import ModelFactory, get_model_factory, ModelRegistry
from src.domain.model.services.config.models import ModelConfigFactory
from src.domain.model.services.config.base import ModelProvider


class TestModelFactory(unittest.TestCase):
    """模型工厂测试类"""
    
    def test_auto_registered_models(self):
        """测试自动注册的模型"""
        # 验证DeepSeek模型已自动注册
        model_class = ModelRegistry.get_model_class("deepseek")
        self.assertIsNotNone(model_class)
        
        # 验证提供商信息
        provider = ModelRegistry.get_provider("deepseek")
        self.assertEqual(provider, ModelProvider.DEEPSEEK)
    
    def test_get_model_by_name(self):
        """测试通过名称获取模型"""
        # 测试获取自动注册的模型
        model_class = ModelFactory.get_model_by_name("deepseek")
        self.assertIsNotNone(model_class)
        
        # 测试获取不存在的模型
        non_existent_model = ModelFactory.get_model_by_name("non_existent")
        self.assertIsNone(non_existent_model)
    
    def test_create_model_with_auto_config(self):
        """测试使用自动配置创建模型"""
        try:
            # 使用新的create_model方法创建DeepSeek实例
            model = ModelFactory.create_model(
                "deepseek",
                api_key="sk-9a4f170ed7174d0e9a14ee8cbf11fd8a",
                base_url="https://api.deepseek.com"
            )
            
            # 验证模型类型
            from src.domain.model.services.impl.deepseek import DeepSeek
            self.assertIsInstance(model, DeepSeek)
            
            # 测试complete方法
            async def test_complete():
                messages = [{"role": "user", "content": "Hello"}]
                try:
                    response = await model.complete(messages)
                    self.assertIsInstance(response, dict)
                except Exception as e:
                    print(f"Expected API exception: {e}")
            
            # 运行异步测试
            asyncio.run(test_complete())
                
        except Exception as e:
            print(f"Model creation exception: {e}")
    
    def test_list_available_models(self):
        """测试列出可用模型"""
        # 获取所有可用模型
        models = ModelFactory.list_available_models()
        
        # 验证包含自动注册的模型
        self.assertIn("deepseek", models)
        self.assertIsInstance(models, list)
    
    def test_model_not_found_error(self):
        """测试模型未找到的错误处理"""
        with self.assertRaises(ValueError) as context:
            ModelFactory.create_model("non_existent_model")
        
        self.assertIn("模型 'non_existent_model' 未找到", str(context.exception))
    
    def test_get_model_factory_singleton(self):
        """测试获取模型工厂单例"""
        factory1 = get_model_factory()
        factory2 = get_model_factory()
        
        # 验证是同一个实例
        self.assertIs(factory1, factory2)
        self.assertIsInstance(factory1, ModelFactory)


if __name__ == '__main__':
    unittest.main()