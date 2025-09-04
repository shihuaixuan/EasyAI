"""
Model仓储接口
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.model import Model


class ModelRepository(ABC):
    """
    Model仓储接口，定义数据访问的抽象方法
    """
    
    @abstractmethod
    async def save(self, model: Model) -> Model:
        """
        保存Model实体
        
        Args:
            model: Model实体
            
        Returns:
            保存后的Model实体（包含ID等信息）
            
        Raises:
            ModelAlreadyExistsError: 当提供商+模型名称组合已存在时
            RepositoryError: 其他数据库操作错误
        """
        pass
    
    @abstractmethod
    async def find_by_id(self, model_id: str) -> Optional[Model]:
        """
        根据ID查找Model
        
        Args:
            model_id: Model ID（UUID格式）
            
        Returns:
            Model实体或None
        """
        pass
    
    @abstractmethod
    async def find_by_provider_and_name(self, provider_name: str, model_name: str) -> Optional[Model]:
        """
        根据提供商名称和模型名称查找Model
        
        Args:
            provider_name: 提供商名称
            model_name: 模型名称
            
        Returns:
            Model实体或None
        """
        pass
    
    @abstractmethod
    async def find_by_provider_name(self, provider_name: str) -> List[Model]:
        """
        根据提供商名称查找所有Model
        
        Args:
            provider_name: 提供商名称
            
        Returns:
            Model实体列表
        """
        pass
    
    @abstractmethod
    async def find_by_type(self, model_type: str) -> List[Model]:
        """
        根据模型类型查找Model
        
        Args:
            model_type: 模型类型
            
        Returns:
            Model实体列表
        """
        pass
    
    @abstractmethod
    async def update(self, model: Model) -> Model:
        """
        更新Model实体
        
        Args:
            model: 要更新的Model实体
            
        Returns:
            更新后的Model实体
            
        Raises:
            ModelNotFoundError: 当Model不存在时
            RepositoryError: 其他数据库操作错误
        """
        pass
    
    @abstractmethod
    async def delete(self, model_id: str) -> bool:
        """
        删除Model
        
        Args:
            model_id: Model ID（UUID格式）
            
        Returns:
            删除成功返回True，Model不存在返回False
            
        Raises:
            RepositoryError: 数据库操作错误
        """
        pass
    
    @abstractmethod
    async def exists(self, provider_name: str, model_name: str) -> bool:
        """
        检查指定提供商和模型名称的组合是否已存在
        
        Args:
            provider_name: 提供商名称
            model_name: 模型名称
            
        Returns:
            存在返回True，否则返回False
        """
        pass