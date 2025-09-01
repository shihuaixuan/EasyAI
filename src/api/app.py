"""
FastAPI应用配置和路由注册
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from ..infrastructure.database import create_tables
from .controllers.provider_controller import router as provider_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时创建数据库表
    await create_tables()
    yield
    # 关闭时的清理工作（如果需要）


def create_app() -> FastAPI:
    """
    创建FastAPI应用实例
    """
    app = FastAPI(
        title="EasyAI Provider API",
        description="EasyAI模型提供商管理API",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 生产环境应该限制具体域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 注册路由
    app.include_router(provider_router)
    
    # 根路径
    @app.get("/")
    async def root():
        return {"message": "EasyAI Provider API", "version": "1.0.0"}
    
    # 健康检查
    @app.get("/health")
    async def health():
        return {"status": "healthy"}
    
    return app


# 创建应用实例
app = create_app()