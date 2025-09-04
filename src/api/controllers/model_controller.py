"""
Model API控制器
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ...application.services.model_application_service import ModelApplicationService
from ...application.dto.model_dto import (
    ModelToggleRequest,
    ModelOperationResponse,
    ProviderModelsResponse
)
from ...domain.provider.services.provider_domain_service import ProviderDomainService
from ...infrastructure.repositories.provider.sql_provider_repository import SqlProviderRepository
from ...infrastructure.repositories.model.sql_model_repository import SqlModelRepository
from ...infrastructure.database import get_database_session
from ...api.dependencies import get_current_user_id

router = APIRouter(prefix="/api/v1/models", tags=["models"])


def get_model_application_service(
    db_session: AsyncSession = Depends(get_database_session)
) -> ModelApplicationService:
    """获取Model应用服务实例"""
    model_repository = SqlModelRepository(db_session)
    provider_repository = SqlProviderRepository(db_session)
    return ModelApplicationService(model_repository, provider_repository)


@router.post("/toggle", response_model=ModelOperationResponse)
async def toggle_model(
    request: ModelToggleRequest,
    service: ModelApplicationService = Depends(get_model_application_service)
):
    """
    切换模型启用状态
    
    - **user_id**: 用户ID
    - **provider**: 提供商名称（如：deepseek, openai等）
    - **model_name**: 模型名称（如：deepseek-chat, gpt-4o等）
    - **enabled**: 是否启用模型
    """
    try:
        result = await service.toggle_model(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")


@router.get("/provider/{provider}", response_model=ProviderModelsResponse)
async def get_provider_models(
    provider: str,
    current_user_id: str = Depends(get_current_user_id),
    service: ModelApplicationService = Depends(get_model_application_service)
):
    """
    获取指定提供商的所有模型信息
    
    - **provider**: 提供商名称（如：deepseek, openai等）
    
    返回该提供商的所有可用模型及其启用状态
    """
    try:
        # 直接使用字符串用户ID（UUID格式）
        result = await service.get_provider_models(current_user_id, provider)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")


@router.get("/health")
async def health_check():
    """模型服务健康检查"""
    return {"status": "healthy", "service": "model_service"}