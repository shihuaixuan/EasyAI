"""API控制器模块

包含所有API控制器的定义和路由配置。
"""

from .user_controller import router as user_router

__all__ = [
    "user_router"
]