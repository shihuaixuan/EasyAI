from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
import re


class UserRegisterRequest(BaseModel):
    """用户注册请求DTO"""
    
    username: str = Field(
        ...,
        min_length=3,
        max_length=20,
        description="用户名，3-20个字符，只能包含字母、数字和下划线，必须以字母开头"
    )
    email: EmailStr = Field(
        ...,
        description="邮箱地址"
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="密码，至少8个字符，必须包含字母和数字"
    )
    
    @validator('username')
    def validate_username(cls, v):
        """验证用户名格式"""
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', v):
            raise ValueError('用户名只能包含字母、数字和下划线，且必须以字母开头')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        """验证密码强度"""
        if not re.search(r'[a-zA-Z]', v):
            raise ValueError('密码必须包含至少一个字母')
        if not re.search(r'\d', v):
            raise ValueError('密码必须包含至少一个数字')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "password": "password123"
            }
        }


class UserLoginRequest(BaseModel):
    """用户登录请求DTO"""
    
    identifier: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="登录标识符（用户名或邮箱）"
    )
    password: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="密码"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "identifier": "john_doe",
                "password": "password123"
            }
        }


class TokenResponse(BaseModel):
    """令牌响应DTO"""
    
    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    
    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


class UserResponse(BaseModel):
    """用户信息响应DTO"""
    
    id: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱")
    status: int = Field(..., description="用户状态（0=未激活，1=正常，2=禁用）")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "username": "john_doe",
                "email": "john@example.com",
                "status": 1,
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-15T10:30:00"
            }
        }


class UserRegisterResponse(BaseModel):
    """用户注册响应DTO"""
    
    user: UserResponse = Field(..., description="用户信息")
    tokens: TokenResponse = Field(..., description="认证令牌")
    
    class Config:
        schema_extra = {
            "example": {
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "username": "john_doe",
                    "email": "john@example.com",
                    "status": 1,
                    "created_at": "2024-01-15T10:30:00",
                    "updated_at": "2024-01-15T10:30:00"
                },
                "tokens": {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer"
                }
            }
        }


class UserLoginResponse(BaseModel):
    """用户登录响应DTO"""
    
    user: UserResponse = Field(..., description="用户信息")
    tokens: TokenResponse = Field(..., description="认证令牌")
    
    class Config:
        schema_extra = {
            "example": {
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "username": "john_doe",
                    "email": "john@example.com",
                    "status": 1,
                    "created_at": "2024-01-15T10:30:00",
                    "updated_at": "2024-01-15T10:30:00"
                },
                "tokens": {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer"
                }
            }
        }


class RefreshTokenRequest(BaseModel):
    """刷新令牌请求DTO"""
    
    refresh_token: str = Field(..., description="刷新令牌")
    
    class Config:
        schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


class RefreshTokenResponse(BaseModel):
    """刷新令牌响应DTO"""
    
    access_token: str = Field(..., description="新的访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    
    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


class ChangePasswordRequest(BaseModel):
    """修改密码请求DTO"""
    
    old_password: str = Field(..., min_length=1, max_length=128, description="旧密码")
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="新密码，至少8个字符，必须包含字母和数字"
    )
    
    @validator('new_password')
    def validate_new_password(cls, v):
        """验证新密码强度"""
        if not re.search(r'[a-zA-Z]', v):
            raise ValueError('密码必须包含至少一个字母')
        if not re.search(r'\d', v):
            raise ValueError('密码必须包含至少一个数字')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "old_password": "oldpassword123",
                "new_password": "newpassword456"
            }
        }


class ChangePasswordResponse(BaseModel):
    """修改密码响应DTO"""
    
    message: str = Field(..., description="操作结果消息")
    updated_at: str = Field(..., description="更新时间")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "密码修改成功",
                "updated_at": "2024-01-15T10:30:00"
            }
        }


class ErrorResponse(BaseModel):
    """错误响应DTO"""
    
    error: str = Field(..., description="错误类型")
    message: str = Field(..., description="错误消息")
    details: Optional[str] = Field(None, description="错误详情")
    
    class Config:
        schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "输入验证失败",
                "details": "用户名格式不正确"
            }
        }