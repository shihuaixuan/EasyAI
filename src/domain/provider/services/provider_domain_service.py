"""
Provider领域服务
"""
from typing import Optional

from ..entities.provider import Provider
from ..repositories.provider_repository import ProviderRepository
from ..exceptions import ProviderAlreadyExistsError, ProviderNotFoundError
from ....infrastructure.security import encryption_service


class ProviderDomainService:
    """
    Provider领域服务，处理复杂的业务逻辑
    """
    
    def __init__(self, provider_repository: ProviderRepository):
        self._provider_repository = provider_repository
    
    async def save_provider(
        self,
        user_id: str,
        provider_name: str,
        plain_api_key: str,
        base_url: Optional[str] = None
    ) -> Provider:
        """
        保存提供商信息
        
        实现业务规则：
        1. 检查用户+提供商组合是否已存在
        2. 加密API Key
        3. 如果存在，则更新；如果不存在，则新建
        
        Args:
            user_id: 用户ID
            provider_name: 提供商名称
            plain_api_key: 明文API Key
            base_url: 基础URL（可选）
            
        Returns:
            保存后的Provider实体
        """
        # 加密API Key
        encrypted_api_key = encryption_service.encrypt(plain_api_key)
        
        # 检查是否已存在
        existing_provider = await self._provider_repository.find_by_user_and_provider(
            user_id, provider_name
        )
        
        if existing_provider:
            # 更新现有Provider
            existing_provider.update_api_key(encrypted_api_key)
            existing_provider.update_base_url(base_url)
            return await self._provider_repository.update(existing_provider)
        else:
            # 创建新Provider
            new_provider = Provider.create(
                user_id=user_id,
                provider=provider_name,
                encrypted_api_key=encrypted_api_key,
                base_url=base_url
            )
            return await self._provider_repository.save(new_provider)
    
    async def validate_provider_uniqueness(self, user_id: str, provider_name: str) -> None:
        """
        验证Provider唯一性
        
        Args:
            user_id: 用户ID
            provider_name: 提供商名称
            
        Raises:
            ProviderAlreadyExistsError: 如果组合已存在
        """
        if await self._provider_repository.exists(user_id, provider_name):
            raise ProviderAlreadyExistsError(user_id, provider_name)
    
    async def ensure_provider_exists(self, provider_id: int) -> Provider:
        """
        确保Provider存在
        
        Args:
            provider_id: Provider ID
            
        Returns:
            Provider实体
            
        Raises:
            ProviderNotFoundError: 如果Provider不存在
        """
        provider = await self._provider_repository.find_by_id(provider_id)
        if not provider:
            raise ProviderNotFoundError(f"ID: {provider_id}")
        return provider
    
    async def get_user_providers(self, user_id: str) -> list[Provider]:
        """
        获取用户的所有提供商
        
        Args:
            user_id: 用户ID
            
        Returns:
            Provider实体列表
        """
        return await self._provider_repository.find_by_user_id(user_id)