
from typing import List, Dict, Any, Optional
from openai import OpenAI

from ..base import BaseLLM
from ..config.models import SiliconflowConfig
from ..config.base import ModelProvider
from ..registry import register_model


@register_model("siliconflow", ModelProvider.SILICONFLOW)
class Siliconflow(BaseLLM):
    ''' Siliconflow LLM实现'''
    
    def __init__(self, config: Optional[SiliconflowConfig] = None, user_id: Optional[str] = None, config_name: Optional[str] = None):
        """初始化Siliconflow客户端
        
        Args:
            config: Siliconflow配置对象，如果为None则从配置管理器获取
            user_id: 用户ID，用于获取用户特定配置
            config_name: 配置名称，用于获取命名配置
        """
        self._config = config
        
        # 验证配置
        if not self._config.validate():
            raise ValueError(f"Siliconflow配置无效: {', '.join(self._config.validation_errors)}")
        
        # 初始化Siliconflow客户端
        client_kwargs = self._config.get_client_kwargs()
        self._client = OpenAI(**client_kwargs)

    async def complete(self,
                        messages: List[Dict[str, str]],
                        tools: Optional[List[Dict[str, Any]]] = None,
                        response_format: Optional[Dict[str, Any]] = None,
                        tool_choice: Optional[str] = None
                        ) -> Dict[str, Any]:
        """发送聊天请求到DeepSeek服务
        
        Args:
            messages: 消息列表，包含对话历史
            tools: 可选的函数调用工具列表
            response_format: 可选的响应格式配置
            tool_choice: 可选的工具选择配置
        Returns:
            从DeepSeek服务返回的响应消息
        """
        # 准备请求参数
        completion_kwargs = self._config.get_completion_kwargs()
        completion_kwargs.update({
            'messages': messages,
            'tools': tools,
            'response_format': response_format,
            'tool_choice': tool_choice
        })
        
        # 移除None值
        completion_kwargs = {k: v for k, v in completion_kwargs.items() if v is not None}
        
        # 发送请求
        response = self._client.chat.completions.create(**completion_kwargs)
        return response.choices[0].message.model_dump()
