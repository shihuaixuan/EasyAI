"""
模型同步服务
负责将YAML配置文件中的模型信息同步到数据库
"""

import asyncio
import json
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.dialects.postgresql import insert

from ..database import get_async_session
from ..models.provider_models import ProviderModel, ModelModel
from .model_config_parser import ModelConfigParser, ModelConfig


class ModelSyncService:
    """模型同步服务"""
    
    def __init__(self, models_dir: str, system_user_id: int = 0):
        """
        初始化同步服务
        
        Args:
            models_dir: models目录路径
            system_user_id: 系统用户ID，用于存储系统级别的模型配置
        """
        self.parser = ModelConfigParser(models_dir)
        self.system_user_id = system_user_id
        
    async def sync_all_models(self) -> Dict[str, Any]:
        """
        同步所有模型配置到数据库
        
        Returns:
            同步结果统计
        """
        result = {
            "models_synced": 0,
            "models_updated": 0,
            "errors": []
        }
        
        try:
            # 解析所有配置文件
            model_configs = self.parser.scan_all_models()
            
            async with get_async_session() as session:
                # 直接同步模型，不再需要处理providers表
                model_result = await self._sync_models(session, model_configs)
                result["models_synced"] = model_result["synced"]
                result["models_updated"] = model_result["updated"]
                result["errors"].extend(model_result["errors"])
                
                await session.commit()
                
        except Exception as e:
            result["errors"].append(f"同步过程中发生错误: {str(e)}")
            
        return result
    

    
    async def _sync_models(self, session: AsyncSession, model_configs: List[ModelConfig]) -> Dict[str, Any]:
        """
        同步模型配置
        
        Args:
            session: 数据库会话
            model_configs: 模型配置列表
            
        Returns:
            同步结果
        """
        result = {"synced": 0, "updated": 0, "errors": []}
        
        for config in model_configs:
            try:
                model_type, subtype = config.get_model_type_and_subtype()
                metadata = config.to_metadata_dict()
                
                # 使用UPSERT操作，基于provider_name和model_name的组合
                stmt = insert(ModelModel).values(
                    model_name=config.model_name,
                    type=model_type,
                    subtype=subtype,
                    model_metadata=json.dumps(metadata, ensure_ascii=False),
                    is_delete=0,
                    provider_name=config.provider
                )
                
                # 如果存在则更新（基于provider_name和model_name的唯一约束）
                stmt = stmt.on_conflict_do_update(
                    index_elements=['provider_name', 'model_name'],
                    set_=dict(
                        type=stmt.excluded.type,
                        subtype=stmt.excluded.subtype,
                        model_metadata=stmt.excluded.model_metadata,
                        is_delete=0,
                        updated_at=stmt.excluded.updated_at
                    )
                )
                
                await session.execute(stmt)
                result["synced"] += 1
                
            except Exception as e:
                error_msg = f"同步模型 {config.provider}/{config.model_name} 失败: {str(e)}"
                result["errors"].append(error_msg)
                print(error_msg)
                
        return result
    

    
    async def clean_deleted_models(self) -> Dict[str, Any]:
        """
        清理已删除的模型配置（软删除）
        
        Returns:
            清理结果
        """
        result = {"cleaned_models": 0, "errors": []}
        
        try:
            # 获取当前YAML文件中的所有模型
            current_configs = self.parser.scan_all_models()
            current_model_names = {(config.provider, config.model_name) for config in current_configs}
            
            async with get_async_session() as session:
                # 获取数据库中的所有模型
                stmt = select(ModelModel).where(ModelModel.is_delete == 0)
                db_models = await session.execute(stmt)
                
                # 找出需要删除的模型
                models_to_delete = []
                for model in db_models.scalars():
                    if (model.provider_name, model.model_name) not in current_model_names:
                        models_to_delete.append(model.id)
                
                # 软删除不存在的模型
                if models_to_delete:
                    stmt = update(ModelModel).where(
                        ModelModel.id.in_(models_to_delete)
                    ).values(is_delete=1)
                    
                    await session.execute(stmt)
                    await session.commit()
                    result["cleaned_models"] = len(models_to_delete)
                    
        except Exception as e:
            result["errors"].append(f"清理过程中发生错误: {str(e)}")
            
        return result
    
    async def get_sync_status(self) -> Dict[str, Any]:
        """
        获取同步状态信息
        
        Returns:
            同步状态信息
        """
        try:
            # 统计YAML文件数量
            yaml_configs = self.parser.scan_all_models()
            yaml_count = len(yaml_configs)
            yaml_by_provider = {}
            for config in yaml_configs:
                yaml_by_provider[config.provider] = yaml_by_provider.get(config.provider, 0) + 1
            
            # 统计数据库中的模型数量
            async with get_async_session() as session:
                stmt = select(ModelModel).where(ModelModel.is_delete == 0)
                db_models = await session.execute(stmt)
                db_models_list = list(db_models.scalars())
                db_count = len(db_models_list)
                
                # 按提供商统计数据库模型
                db_by_provider = {}
                for model in db_models_list:
                    provider_name = model.provider_name
                    db_by_provider[provider_name] = db_by_provider.get(provider_name, 0) + 1
            
            return {
                "yaml_models_count": yaml_count,
                "db_models_count": db_count,
                "yaml_by_provider": yaml_by_provider,
                "db_by_provider": db_by_provider,
                "sync_needed": yaml_count != db_count
            }
            
        except Exception as e:
            return {"error": f"获取同步状态失败: {str(e)}"}


async def main():
    """测试同步服务"""
    models_dir = "/Users/twenty/LLM/EasyAI/src/infrastructure/models"
    sync_service = ModelSyncService(models_dir)
    
    print("=== 获取同步状态 ===")
    status = await sync_service.get_sync_status()
    print(f"YAML模型数量: {status.get('yaml_models_count', 0)}")
    print(f"数据库模型数量: {status.get('db_models_count', 0)}")
    print(f"需要同步: {status.get('sync_needed', False)}")
    
    print("\n=== 开始同步 ===")
    result = await sync_service.sync_all_models()
    print(f"模型同步: {result['models_synced']}")
    print(f"模型更新: {result['models_updated']}")
    if result['errors']:
        print("错误:")
        for error in result['errors']:
            print(f"  - {error}")
    
    print("\n=== 清理已删除的模型 ===")
    clean_result = await sync_service.clean_deleted_models()
    print(f"清理模型数量: {clean_result['cleaned_models']}")


if __name__ == "__main__":
    asyncio.run(main())
