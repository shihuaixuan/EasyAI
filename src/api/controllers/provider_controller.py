"""
Provider控制器
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...application.dto.provider_dto import SaveProviderRequest, SaveProviderResponse, ProviderResponse
from ...application.services.provider_application_service import ProviderApplicationService
from ...domain.provider.services.provider_domain_service import ProviderDomainService
from ...infrastructure.repositories.provider.sql_provider_repository import SqlProviderRepository
from ...infrastructure.database import get_database_session


router = APIRouter(prefix="/api/v1/providers", tags=["providers"])


def get_provider_application_service(
    session: AsyncSession = Depends(get_database_session)
) -> ProviderApplicationService:
    """
    获取Provider应用服务实例
    """
    provider_repository = SqlProviderRepository(session)
    provider_domain_service = ProviderDomainService(provider_repository)
    return ProviderApplicationService(provider_domain_service)


@router.post("/save", response_model=SaveProviderResponse, summary="保存Provider配置")
async def save_provider(
    request: SaveProviderRequest,
    service: ProviderApplicationService = Depends(get_provider_application_service)
) -> SaveProviderResponse:
    """
    保存Provider配置
    
    参数:
    - **user_id**: 用户ID
    - **provider**: 提供商名称 (openai, deepseek, siliconflow, anthropic, google)
    - **api_key**: 加密后的API Key
    - **base_url**: 基础URL（可选）
    
    返回:
    - 保存操作的结果信息
    """
    try:
        result = await service.save_provider(request)
        
        # 根据业务结果设置HTTP状态码
        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.message
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"系统内部错误: {str(e)}"
        )


@router.get("/user/{user_id}", response_model=List[ProviderResponse], summary="获取用户的Provider配置")
async def get_user_providers(
    user_id: int,
    service: ProviderApplicationService = Depends(get_provider_application_service)
) -> List[ProviderResponse]:
    """
    获取指定用户的所有Provider配置
    
    参数:
    - **user_id**: 用户ID
    
    返回:
    - 用户的Provider配置列表
    """
    try:
        if user_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户ID必须为正整数"
            )
        
        providers = await service.get_user_providers(user_id)
        return providers
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"系统内部错误: {str(e)}"
        )


@router.get("/health", summary="健康检查")
async def health_check():
    """
    Provider服务健康检查
    """
    return {"status": "healthy", "service": "provider"}