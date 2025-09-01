"""
Model应用服务
"""
from typing import List, Optional
from datetime import datetime

from ...application.dto.model_dto import (
    ModelToggleRequest, 
    ModelOperationResponse, 
    ModelResponse,
    ProviderModelsResponse,
    ProviderModelInfo
)
from ...domain.provider.entities.model import Model
from ...domain.provider.entities.provider import Provider
from ...domain.provider.repositories.model_repository import ModelRepository
from ...domain.provider.repositories.provider_repository import ProviderRepository
from ...domain.provider.exceptions import ProviderDomainError, RepositoryError
from ...infrastructure.services import model_config_service


class ModelApplicationService:
    """
    Model应用服务，协调领域对象完成业务用例
    """
    
    def __init__(
        self, 
        model_repository: ModelRepository,
        provider_repository: ProviderRepository
    ):
        self._model_repository = model_repository
        self._provider_repository = provider_repository
    
    async def toggle_model(self, request: ModelToggleRequest) -> ModelOperationResponse:
        """
        切换模型启用状态
        
        Args:
            request: 模型切换请求
            
        Returns:
            模型操作响应
        """
        try:
            # 1. 检查提供商是否存在且已配置API Key
            provider = await self._provider_repository.find_by_user_and_provider(
                request.user_id, request.provider
            )
            
            if not provider:
                return ModelOperationResponse(
                    success=False,
                    message=f"提供商 {request.provider} 未配置，请先配置API Key",
                    data=None
                )
            
            # 2. 查找或创建模型
            existing_model = await self._model_repository.find_by_provider_and_name(
                provider.id, request.model_name
            )
            
            if request.enabled:
                # 启用模型
                if existing_model and not existing_model.is_deleted():
                    # 模型已存在且未删除，无需操作
                    model_response = self._convert_to_response_dto(existing_model)
                    return ModelOperationResponse(
                        success=True,
                        message="模型已启用",
                        data=model_response
                    )
                elif existing_model and existing_model.is_deleted():
                    # 模型已存在但被软删除，恢复它
                    existing_model.restore()
                    updated_model = await self._model_repository.update(existing_model)
                    model_response = self._convert_to_response_dto(updated_model)
                    return ModelOperationResponse(
                        success=True,
                        message="模型已重新启用",
                        data=model_response
                    )
                else:
                    # 创建新模型
                    # 从配置文件获取模型信息
                    model_config = model_config_service.get_model_config(request.provider, request.model_name)
                    if not model_config:
                        return ModelOperationResponse(
                            success=False,
                            message=f"未找到模型 {request.model_name} 的配置信息",
                            data=None
                        )
                    
                    new_model = Model.create(
                        provider_id=provider.id,
                        model_name=request.model_name,
                        model_type=model_config.get('model_type', 'llm'),
                        subtype=model_config.get('subtype'),
                        metadata=model_config
                    )
                    
                    saved_model = await self._model_repository.save(new_model)
                    model_response = self._convert_to_response_dto(saved_model)
                    return ModelOperationResponse(
                        success=True,
                        message="模型已启用",
                        data=model_response
                    )
            else:
                # 禁用模型
                if existing_model and not existing_model.is_deleted():
                    existing_model.mark_as_deleted()
                    updated_model = await self._model_repository.update(existing_model)
                    model_response = self._convert_to_response_dto(updated_model)
                    return ModelOperationResponse(
                        success=True,
                        message="模型已禁用",
                        data=model_response
                    )
                else:
                    return ModelOperationResponse(
                        success=True,
                        message="模型已是禁用状态",
                        data=None
                    )
                    
        except ProviderDomainError as e:
            return ModelOperationResponse(
                success=False,
                message=f"业务错误: {str(e)}",
                data=None
            )
        except RepositoryError as e:
            return ModelOperationResponse(
                success=False,
                message=f"数据存储错误: {str(e)}",
                data=None
            )
        except Exception as e:
            return ModelOperationResponse(
                success=False,
                message=f"系统错误: {str(e)}",
                data=None
            )
    
    async def get_provider_models(self, user_id: int, provider: str) -> ProviderModelsResponse:
        """
        获取提供商的所有模型信息
        
        Args:
            user_id: 用户ID
            provider: 提供商名称
            
        Returns:
            提供商模型列表响应
        """
        try:
            # 1. 检查提供商是否存在
            provider_entity = await self._provider_repository.find_by_user_and_provider(
                user_id, provider
            )
            
            has_api_key = provider_entity is not None
            
            # 2. 从配置文件获取所有可用模型
            available_models = model_config_service.get_provider_models(provider)
            
            # 3. 获取已启用的模型
            enabled_models = []
            if provider_entity:
                enabled_models = await self._model_repository.find_by_provider_id(provider_entity.id)
            
            enabled_model_names = {
                model.model_name for model in enabled_models if not model.is_deleted()
            }
            
            # 4. 构建响应
            model_infos = []
            for model_config in available_models:
                model_info = ProviderModelInfo(
                    model=model_config.get('model', ''),
                    model_type=model_config.get('model_type', 'llm'),
                    provider=model_config.get('provider', provider),
                    description=model_config.get('description'),
                    capabilities=model_config.get('capabilities'),
                    context_length=model_config.get('context_length'),
                    max_tokens=model_config.get('max_tokens'),
                    enabled=model_config.get('model', '') in enabled_model_names
                )
                model_infos.append(model_info)
            
            return ProviderModelsResponse(
                provider=provider,
                has_api_key=has_api_key,
                models=model_infos
            )
            
        except Exception as e:
            # 返回空结果而不是抛出异常
            return ProviderModelsResponse(
                provider=provider,
                has_api_key=False,
                models=[]
            )
    
    def _convert_to_response_dto(self, model: Model) -> ModelResponse:
        """
        将Model实体转换为响应DTO
        
        Args:
            model: Model实体
            
        Returns:
            Model响应DTO
        """
        if model.id is None:
            raise ValueError(f"Model id 不能为 None: {model}")
            
        return ModelResponse(
            id=model.id,
            provider_id=model.provider_id,
            model_name=model.model_name,
            type=model.type,
            subtype=model.subtype,
            metadata=model.metadata,
            enabled=not model.is_deleted(),
            created_at=model.created_at.isoformat() if model.created_at else None,
            updated_at=model.updated_at.isoformat() if model.updated_at else None
        )