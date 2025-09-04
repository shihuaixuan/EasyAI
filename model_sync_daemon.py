#!/usr/bin/env python3
"""
模型同步守护进程启动脚本
用于启动定时同步YAML配置文件到数据库的服务
"""

import os
import sys
import asyncio
import argparse
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.infrastructure.services.model_sync_scheduler import ModelSyncDaemon, ModelSyncScheduler


def load_config(config_path: str = None) -> dict:
    """
    加载配置文件
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        配置字典
    """
    default_config = {
        "system_user_id": 0,
        "use_cron": True,
        "cron_expression": "0 */6 * * *",  # 每6小时执行一次
        "interval_minutes": 360,  # 6小时间隔
        "run_immediately": True,
        "models_dir": "src/infrastructure/models"
    }
    
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
                default_config.update(file_config)
        except Exception as e:
            print(f"警告: 加载配置文件失败 {config_path}: {e}")
            print("使用默认配置")
    
    return default_config


async def run_daemon(config: dict):
    """运行守护进程"""
    models_dir = os.path.join(project_root, config['models_dir'])
    daemon = ModelSyncDaemon(models_dir, config)
    await daemon.start()


async def run_once(config: dict):
    """执行一次同步"""
    models_dir = os.path.join(project_root, config['models_dir'])
    scheduler = ModelSyncScheduler(models_dir, config.get('system_user_id', 0))
    
    print("执行一次性模型同步...")
    result = await scheduler.manual_sync()
    
    print("=== 同步结果 ===")
    print(f"模型同步: {result.get('models_synced', 0)}")
    print(f"模型更新: {result.get('models_updated', 0)}")
    
    if result.get('errors'):
        print("错误:")
        for error in result['errors']:
            print(f"  - {error}")
    
    print("同步完成!")


async def show_status(config: dict):
    """显示同步状态"""
    models_dir = os.path.join(project_root, config['models_dir'])
    scheduler = ModelSyncScheduler(models_dir, config.get('system_user_id', 0))
    
    # 获取同步状态
    status = await scheduler.sync_service.get_sync_status()
    
    print("=== 模型同步状态 ===")
    print(f"YAML文件中的模型数量: {status.get('yaml_models_count', 0)}")
    print(f"数据库中的模型数量: {status.get('db_models_count', 0)}")
    print(f"需要同步: {'是' if status.get('sync_needed', False) else '否'}")
    
    print("\n=== 按提供商统计 ===")
    yaml_by_provider = status.get('yaml_by_provider', {})
    db_by_provider = status.get('db_by_provider', {})
    
    all_providers = set(yaml_by_provider.keys()) | set(db_by_provider.keys())
    for provider in sorted(all_providers):
        yaml_count = yaml_by_provider.get(provider, 0)
        db_count = db_by_provider.get(provider, 0)
        print(f"  {provider}: YAML={yaml_count}, DB={db_count}")


def create_sample_config():
    """创建示例配置文件"""
    config = {
        "system_user_id": 0,
        "use_cron": True,
        "cron_expression": "0 */6 * * *",
        "interval_minutes": 360,
        "run_immediately": True,
        "models_dir": "src/infrastructure/models"
    }
    
    config_path = "model_sync_config.json"
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"示例配置文件已创建: {config_path}")
    print("配置说明:")
    print("  - system_user_id: 系统用户ID")
    print("  - use_cron: 是否使用Cron表达式调度")
    print("  - cron_expression: Cron表达式 (默认每6小时)")
    print("  - interval_minutes: 间隔分钟数 (当use_cron=false时使用)")
    print("  - run_immediately: 启动时是否立即执行一次同步")
    print("  - models_dir: 模型配置文件目录")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='模型同步守护进程')
    parser.add_argument('command', choices=['daemon', 'once', 'status', 'config'], 
                       help='执行命令: daemon(守护进程), once(执行一次), status(查看状态), config(创建配置)')
    parser.add_argument('--config', '-c', help='配置文件路径')
    parser.add_argument('--cron', help='Cron表达式 (覆盖配置文件)')
    parser.add_argument('--interval', type=int, help='间隔分钟数 (覆盖配置文件)')
    parser.add_argument('--no-immediate', action='store_true', help='启动时不立即执行同步')
    
    args = parser.parse_args()
    
    if args.command == 'config':
        create_sample_config()
        return
    
    # 加载配置
    config = load_config(args.config)
    
    # 命令行参数覆盖配置
    if args.cron:
        config['use_cron'] = True
        config['cron_expression'] = args.cron
    if args.interval:
        config['use_cron'] = False
        config['interval_minutes'] = args.interval
    if args.no_immediate:
        config['run_immediately'] = False
    
    # 执行命令
    if args.command == 'daemon':
        print("启动模型同步守护进程...")
        print(f"配置: {json.dumps(config, indent=2, ensure_ascii=False)}")
        asyncio.run(run_daemon(config))
    elif args.command == 'once':
        asyncio.run(run_once(config))
    elif args.command == 'status':
        asyncio.run(show_status(config))


if __name__ == "__main__":
    main()
