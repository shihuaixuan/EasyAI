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
    future=True,
    pool_size=20,           # 连接池大小
    max_overflow=30,        # 最大溢出连接数
    pool_timeout=30,        # 获取连接超时时间
    pool_recycle=3600,      # 连接回收时间
    pool_pre_ping=True      # 连接前ping测试
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=True,   # 修复：提交后过期对象
    autocommit=False,       # 保持手动提交
    autoflush=True          # 修复：启用自动刷新
)

# 声明基类
Base = declarative_base()


async def get_database_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI依赖项：获取数据库会话
    正确的事务管理：手动提交/回滚
    """
    async with AsyncSessionLocal() as session:
        try:
            # 将会话交给调用者管理事务
            yield session
            # 注意：不在这里自动提交，由控制器手动提交
        except Exception as e:
            await session.rollback()
            print(f"数据库会话异常，已回滚: {str(e)}")
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
    from .models.knowledge_models import DatasetModel
    from .models.user_models import UserModel
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables():
    """
    删除数据库表（仅用于测试）
    """
    from .models.provider_models import ProviderModel, ModelModel
    from .models.knowledge_models import DatasetModel
    from .models.user_models import UserModel
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def get_session():
    """
    获取数据库会话（修复版本）
    返回会话上下文管理器，而不是裸会话
    """
    @asynccontextmanager
    async def session_context():
        async with AsyncSessionLocal() as session:
            try:
                yield session
            except Exception as e:
                await session.rollback()
                print(f"临时会话异常，已回滚: {str(e)}")
                raise
            finally:
                await session.close()
    
    return session_context()