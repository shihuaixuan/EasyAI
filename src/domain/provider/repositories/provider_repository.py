"""
Provider仓储接口
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.provider import Provider


class ProviderRepository(ABC):
    """
    Provider仓储接口，定义数据访问的抽象方法
    """
    
    @abstractmethod
    async def save(self, provider: Provider) -> Provider:
        """
        保存Provider实体
        
        Args:
            provider: Provider实体
            
        Returns:
            保存后的Provider实体（包含ID等信息）
            
        Raises:
            ProviderAlreadyExistsError: 当用户+提供商组合已存在时
            RepositoryError: 其他数据库操作错误
        """
        pass
    
    @abstractmethod
    async def find_by_id(self, provider_id: int) -> Optional[Provider]:
        """
        根据ID查找Provider
        
        Args:
            provider_id: Provider ID
            
        Returns:
            Provider实体或None
        """
        pass
    
    @abstractmethod
    async def find_by_user_and_provider(self, user_id: int, provider_name: str) -> Optional[Provider]:
        """
        根据用户ID和提供商名称查找Provider
        
        Args:
            user_id: 用户ID
            provider_name: 提供商名称
            
        Returns:
            Provider实体或None
        """
        pass
    
    @abstractmethod
    async def find_by_user_id(self, user_id: int) -> List[Provider]:
        """
        根据用户ID查找所有Provider
        
        Args:
            user_id: 用户ID
            
        Returns:
            Provider实体列表
        """
        pass
    
    @abstractmethod
    async def update(self, provider: Provider) -> Provider:
        """
        更新Provider实体
        
        Args:
            provider: 要更新的Provider实体
            
        Returns:
            更新后的Provider实体
            
        Raises:
            ProviderNotFoundError: 当Provider不存在时
            RepositoryError: 其他数据库操作错误
        """
        pass
    
    @abstractmethod
    async def delete(self, provider_id: int) -> bool:
        """
        删除Provider
        
        Args:
            provider_id: Provider ID
            
        Returns:
            删除成功返回True，Provider不存在返回False
            
        Raises:
            RepositoryError: 数据库操作错误
        """
        pass
    
    @abstractmethod
    async def exists(self, user_id: int, provider_name: str) -> bool:
        """
        检查指定用户和提供商的组合是否已存在
        
        Args:
            user_id: 用户ID
            provider_name: 提供商名称
            
        Returns:
            存在返回True，否则返回False
        """
        pass