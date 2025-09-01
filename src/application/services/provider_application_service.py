"""
Provider应用服务
"""
from typing import List
from datetime import datetime

from ...application.dto.provider_dto import SaveProviderRequest, SaveProviderResponse, ProviderResponse
from ...domain.provider.services.provider_domain_service import ProviderDomainService
from ...domain.provider.entities.provider import Provider
from ...domain.provider.exceptions import ProviderDomainError, RepositoryError
from ...infrastructure.security import encryption_service


class ProviderApplicationService:
    """
    Provider应用服务，协调领域对象完成业务用例
    """
    
    def __init__(self, provider_domain_service: ProviderDomainService):
        self._provider_domain_service = provider_domain_service
    
    async def save_provider(self, request: SaveProviderRequest) -> SaveProviderResponse:
        """
        保存Provider应用用例
        
        Args:
            request: 保存Provider请求
            
        Returns:
            保存Provider响应
        """
        try:
            # 调用领域服务保存Provider（传递明文API Key）
            provider = await self._provider_domain_service.save_provider(
                user_id=request.user_id,
                provider_name=request.provider,
                plain_api_key=request.api_key,  # 传递明文API Key
                base_url=request.base_url
            )
            
            # 转换为响应DTO
            provider_response = self._convert_to_response_dto(provider)
            
            return SaveProviderResponse(
                success=True,
                message="Provider保存成功",
                data=provider_response
            )
            
        except ProviderDomainError as e:
            # 领域异常
            return SaveProviderResponse(
                success=False,
                message=f"业务错误: {str(e)}",
                data=None
            )
        except RepositoryError as e:
            # 仓储异常
            return SaveProviderResponse(
                success=False,
                message=f"数据存储错误: {str(e)}",
                data=None
            )
        except Exception as e:
            # 其他未预期异常
            return SaveProviderResponse(
                success=False,
                message=f"系统错误: {str(e)}",
                data=None
            )
    
    async def get_user_providers(self, user_id: int) -> List[ProviderResponse]:
        """
        获取用户的所有Provider
        
        Args:
            user_id: 用户ID
            
        Returns:
            Provider响应列表
        """
        try:
            providers = await self._provider_domain_service.get_user_providers(user_id)
            return [self._convert_to_response_dto(provider) for provider in providers]
        except Exception:
            # 查询失败时返回空列表
            return []
    
    def _convert_to_response_dto(self, provider: Provider) -> ProviderResponse:
        """
        将Provider实体转换为响应DTO
        
        Args:
            provider: Provider实体
            
        Returns:
            Provider响应DTO
        """
        # 确保 id 不为 None，如果为 None 则抛出异常
        if provider.id is None:
            raise ValueError(f"Provider id 不能为 None: {provider}")
        
        # 解密API Key并生成掉码显示
        try:
            decrypted_api_key = encryption_service.decrypt(provider.api_key.encrypted_value)
            masked_api_key = encryption_service.mask_api_key(decrypted_api_key)
        except Exception:
            # 如果解密失败，使用默认掉码
            masked_api_key = "***"
            
        return ProviderResponse(
            id=provider.id,
            user_id=provider.user_id,
            provider=provider.provider,
            api_key_masked=masked_api_key,
            base_url=str(provider.base_url) if not provider.base_url.is_empty() else None,
            created_at=provider.created_at.isoformat() if provider.created_at else None,
            updated_at=provider.updated_at.isoformat() if provider.updated_at else None
        )