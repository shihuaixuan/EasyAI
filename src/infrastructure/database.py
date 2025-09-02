"""
数据库配置和连接管理
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from contextlib import asynccontextmanager
import os

# 数据库URL配置
# PostgreSQL配置
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://twenty:123456@localhost:5432/esayai"  # 使用正确的数据库名称
)

# 创建异步引擎
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # 开发环境下显示SQL语句
    future=True
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# 声明基类
Base = declarative_base()


async def get_database_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI依赖项：获取数据库会话
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_async_session():
    """
    上下文管理器：获取异步数据库会话
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables():
    """
    创建数据库表
    """
    # 导入所有模型以确保它们被注册
    from .models.provider_models import ProviderModel, ModelModel
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables():
    """
    删除数据库表（仅用于测试）
    """
    from .models.provider_models import ProviderModel, ModelModel
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def get_session():
    """
    获取数据库会话（简单版本用于测试）
    """
    return AsyncSessionLocal()