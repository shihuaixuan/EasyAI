from typing import Optional, Protocol, List, Dict, Any


class BaseLLM(Protocol):
    '''基础LLM协议'''
    async def complete(self,
                        messages: List[Dict[str, str]],
                        tools: Optional[List[Dict[str, Any]]] = None,
                        response_format: Optional[Dict[str, Any]] = None,
                        tool_choice: Optional[str] = None
                        ) -> Dict[str, Any]:
        """发送聊天请求到AI服务
        
        Args:
            messages: 消息列表，包含对话历史
            tools: 可选的函数调用工具列表
            response_format: 可选的响应格式配置
            tool_choice: 可选的工具选择配置
        Returns:
            从AI服务返回的响应消息
        """
        ...