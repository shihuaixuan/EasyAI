from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
import logging

from src.api.dtos.user_dtos import (
    UserRegisterRequest,
    UserLoginRequest,
    UserRegisterResponse,
    UserLoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    ChangePasswordRequest,
    ChangePasswordResponse,
    UserResponse,
    ErrorResponse
)
from src.application.services.user_application_service import UserApplicationService
from src.domain.user.repositories.user_repository import UserRepository
from src.domain.user.services.user_domain_service import UserDomainService
from src.infrastructure.repositories.sql_user_repository import SqlUserRepository
from src.infrastructure.services.password_service import password_service
from src.infrastructure.services.jwt_service import jwt_service
from src.infrastructure.database import get_database_session
from src.api.dependencies import get_current_user_id

# 设置日志
logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/api/v1/auth", tags=["用户认证"])


# 依赖注入
def get_user_application_service(
    session: AsyncSession = Depends(get_database_session)
) -> UserApplicationService:
    """获取用户应用服务实例"""
    user_repository = SqlUserRepository(session)
    user_domain_service = UserDomainService(user_repository)
    
    return UserApplicationService(
        user_repository=user_repository,
        user_domain_service=user_domain_service,
        password_service=password_service,
        jwt_service=jwt_service
    )


# get_current_user_id 现在从 dependencies.py 导入


@router.post(
    "/register",
    response_model=UserRegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="用户注册",
    description="注册新用户账户",
    responses={
        201: {"description": "注册成功", "model": UserRegisterResponse},
        400: {"description": "请求参数错误", "model": ErrorResponse},
        409: {"description": "用户名或邮箱已存在", "model": ErrorResponse},
        422: {"description": "输入验证失败", "model": ErrorResponse}
    }
)
async def register(
    request: UserRegisterRequest,
    user_service: UserApplicationService = Depends(get_user_application_service)
) -> UserRegisterResponse:
    """用户注册接口"""
    try:
        result = await user_service.register_user(
            username=request.username,
            email=request.email,
            password=request.password
        )
        
        logger.info(f"用户注册成功: {request.username}")
        return UserRegisterResponse(**result)
        
    except ValueError as e:
        logger.warning(f"用户注册失败: {str(e)}")
        if "已存在" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    except Exception as e:
        import traceback
        logger.error(f"用户注册异常: {str(e)}")
        logger.error(f"错误堆栈: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="注册失败，请稍后重试"
        )


@router.post(
    "/login",
    response_model=UserLoginResponse,
    summary="用户登录",
    description="用户登录验证",
    responses={
        200: {"description": "登录成功", "model": UserLoginResponse},
        400: {"description": "请求参数错误", "model": ErrorResponse},
        401: {"description": "用户名或密码错误", "model": ErrorResponse},
        403: {"description": "账户被禁用或未激活", "model": ErrorResponse},
        422: {"description": "输入验证失败", "model": ErrorResponse}
    }
)
async def login(
    request: UserLoginRequest,
    user_service: UserApplicationService = Depends(get_user_application_service)
) -> UserLoginResponse:
    """用户登录接口"""
    try:
        result = await user_service.login_user(
            identifier=request.identifier,
            password=request.password
        )
        
        logger.info(f"用户登录成功: {request.identifier}")
        return UserLoginResponse(**result)
        
    except ValueError as e:
        logger.warning(f"用户登录失败: {str(e)}")
        error_msg = str(e)
        
        if "用户名或密码错误" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=error_msg
            )
        elif "禁用" in error_msg or "未激活" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=error_msg
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
    except Exception as e:
        logger.error(f"用户登录异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录失败，请稍后重试"
        )


@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    summary="刷新访问令牌",
    description="使用刷新令牌获取新的访问令牌",
    responses={
        200: {"description": "刷新成功", "model": RefreshTokenResponse},
        400: {"description": "请求参数错误", "model": ErrorResponse},
        401: {"description": "刷新令牌无效或已过期", "model": ErrorResponse},
        422: {"description": "输入验证失败", "model": ErrorResponse}
    }
)
async def refresh_token(
    request: RefreshTokenRequest,
    user_service: UserApplicationService = Depends(get_user_application_service)
) -> RefreshTokenResponse:
    """刷新访问令牌接口"""
    try:
        result = await user_service.refresh_token(request.refresh_token)
        
        logger.info("访问令牌刷新成功")
        return RefreshTokenResponse(**result)
        
    except ValueError as e:
        logger.warning(f"令牌刷新失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"令牌刷新异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="令牌刷新失败，请稍后重试"
        )


@router.get(
    "/profile",
    response_model=UserResponse,
    summary="获取用户资料",
    description="获取当前登录用户的资料信息",
    responses={
        200: {"description": "获取成功", "model": UserResponse},
        401: {"description": "未授权访问", "model": ErrorResponse},
        404: {"description": "用户不存在", "model": ErrorResponse}
    }
)
async def get_profile(
    current_user_id: str = Depends(get_current_user_id),
    user_service: UserApplicationService = Depends(get_user_application_service)
) -> UserResponse:
    """获取用户资料接口"""
    try:
        result = await user_service.get_user_profile(current_user_id)
        
        logger.info(f"获取用户资料成功: {current_user_id}")
        return UserResponse(**result)
        
    except ValueError as e:
        logger.warning(f"获取用户资料失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"获取用户资料异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户资料失败，请稍后重试"
        )


@router.post(
    "/change-password",
    response_model=ChangePasswordResponse,
    summary="修改密码",
    description="修改当前登录用户的密码",
    responses={
        200: {"description": "修改成功", "model": ChangePasswordResponse},
        400: {"description": "请求参数错误", "model": ErrorResponse},
        401: {"description": "未授权访问或旧密码错误", "model": ErrorResponse},
        404: {"description": "用户不存在", "model": ErrorResponse},
        422: {"description": "输入验证失败", "model": ErrorResponse}
    }
)
async def change_password(
    request: ChangePasswordRequest,
    current_user_id: str = Depends(get_current_user_id),
    user_service: UserApplicationService = Depends(get_user_application_service)
) -> ChangePasswordResponse:
    """修改密码接口"""
    try:
        result = await user_service.change_password(
            user_id=current_user_id,
            old_password=request.old_password,
            new_password=request.new_password
        )
        
        logger.info(f"用户修改密码成功: {current_user_id}")
        return ChangePasswordResponse(**result)
        
    except ValueError as e:
        logger.warning(f"修改密码失败: {str(e)}")
        error_msg = str(e)
        
        if "不存在" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_msg
            )
        elif "旧密码错误" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=error_msg
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
    except Exception as e:
        logger.error(f"修改密码异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="修改密码失败，请稍后重试"
        )


@router.post(
    "/logout",
    summary="用户登出",
    description="用户登出（客户端需要清除本地令牌）",
    responses={
        200: {"description": "登出成功"},
        401: {"description": "未授权访问", "model": ErrorResponse}
    }
)
async def logout(
    current_user_id: str = Depends(get_current_user_id)
) -> Dict[str, str]:
    """用户登出接口
    
    注意：由于JWT是无状态的，服务端无法主动使令牌失效。
    实际的登出逻辑需要客户端清除本地存储的令牌。
    如果需要服务端控制令牌失效，可以考虑使用令牌黑名单机制。
    """
    logger.info(f"用户登出: {current_user_id}")
    return {"message": "登出成功，请清除本地令牌"}