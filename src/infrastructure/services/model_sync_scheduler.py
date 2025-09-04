"""
模型同步定时任务调度器
使用APScheduler实现定时同步YAML配置到数据库
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

from .model_sync_service import ModelSyncService


class ModelSyncScheduler:
    """模型同步调度器"""
    
    def __init__(self, models_dir: str, system_user_id: str = "system"):
        """
        初始化调度器
        
        Args:
            models_dir: models目录路径
            system_user_id: 系统用户ID（UUID格式）
        """
        self.models_dir = models_dir
        self.system_user_id = system_user_id
        self.sync_service = ModelSyncService(models_dir, system_user_id)
        self.scheduler = AsyncIOScheduler()
        self.last_sync_result: Optional[Dict[str, Any]] = None
        self.last_sync_time: Optional[datetime] = None
        
        # 设置日志
        self.logger = logging.getLogger(__name__)
        
        # 添加事件监听器
        self.scheduler.add_listener(self._job_executed, EVENT_JOB_EXECUTED)
        self.scheduler.add_listener(self._job_error, EVENT_JOB_ERROR)
    
    def _job_executed(self, event):
        """任务执行成功回调"""
        self.logger.info(f"定时任务执行成功: {event.job_id} at {datetime.now()}")
    
    def _job_error(self, event):
        """任务执行失败回调"""
        self.logger.error(f"定时任务执行失败: {event.job_id}, 错误: {event.exception}")
    
    async def sync_models_job(self):
        """同步模型的定时任务"""
        try:
            self.logger.info("开始执行模型同步任务...")
            
            # 执行同步
            result = await self.sync_service.sync_all_models()
            self.last_sync_result = result
            self.last_sync_time = datetime.now()
            
            # 记录同步结果
            self.logger.info(
                f"模型同步完成 - 模型: {result['models_synced']}, "
                f"更新: {result['models_updated']}, "
                f"错误: {len(result['errors'])}"
            )
            
            if result['errors']:
                for error in result['errors']:
                    self.logger.error(f"同步错误: {error}")
            
            # 清理已删除的模型
            clean_result = await self.sync_service.clean_deleted_models()
            if clean_result['cleaned_models'] > 0:
                self.logger.info(f"清理了 {clean_result['cleaned_models']} 个已删除的模型")
                
        except Exception as e:
            self.logger.error(f"模型同步任务执行失败: {str(e)}")
            self.last_sync_result = {"error": str(e)}
            self.last_sync_time = datetime.now()
    
    def start_scheduler(self, 
                       cron_expression: str = "0 */6 * * *",  # 默认每6小时执行一次
                       run_immediately: bool = True):
        """
        启动调度器
        
        Args:
            cron_expression: Cron表达式，默认每6小时执行一次
            run_immediately: 是否立即执行一次同步
        """
        try:
            # 添加定时任务
            self.scheduler.add_job(
                self.sync_models_job,
                CronTrigger.from_crontab(cron_expression),
                id='model_sync_job',
                name='模型配置同步任务',
                replace_existing=True
            )
            
            # 启动调度器
            self.scheduler.start()
            self.logger.info(f"模型同步调度器已启动，Cron表达式: {cron_expression}")
            
            # 立即执行一次同步
            if run_immediately:
                asyncio.create_task(self.sync_models_job())
                self.logger.info("立即执行一次模型同步...")
                
        except Exception as e:
            self.logger.error(f"启动调度器失败: {str(e)}")
            raise
    
    def start_interval_scheduler(self, 
                                interval_minutes: int = 360,  # 默认6小时
                                run_immediately: bool = True):
        """
        启动间隔调度器
        
        Args:
            interval_minutes: 间隔分钟数
            run_immediately: 是否立即执行一次同步
        """
        try:
            # 添加间隔任务
            self.scheduler.add_job(
                self.sync_models_job,
                IntervalTrigger(minutes=interval_minutes),
                id='model_sync_interval_job',
                name='模型配置同步间隔任务',
                replace_existing=True
            )
            
            # 启动调度器
            self.scheduler.start()
            self.logger.info(f"模型同步调度器已启动，间隔: {interval_minutes} 分钟")
            
            # 立即执行一次同步
            if run_immediately:
                asyncio.create_task(self.sync_models_job())
                self.logger.info("立即执行一次模型同步...")
                
        except Exception as e:
            self.logger.error(f"启动间隔调度器失败: {str(e)}")
            raise
    
    def stop_scheduler(self):
        """停止调度器"""
        try:
            self.scheduler.shutdown()
            self.logger.info("模型同步调度器已停止")
        except Exception as e:
            self.logger.error(f"停止调度器失败: {str(e)}")
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """
        获取调度器状态
        
        Returns:
            调度器状态信息
        """
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
        
        return {
            "running": self.scheduler.running,
            "jobs": jobs,
            "last_sync_time": self.last_sync_time.isoformat() if self.last_sync_time else None,
            "last_sync_result": self.last_sync_result
        }
    
    async def manual_sync(self) -> Dict[str, Any]:
        """
        手动触发同步
        
        Returns:
            同步结果
        """
        self.logger.info("手动触发模型同步...")
        await self.sync_models_job()
        return self.last_sync_result or {}


class ModelSyncDaemon:
    """模型同步守护进程"""
    
    def __init__(self, models_dir: str, config: Dict[str, Any] = None):
        """
        初始化守护进程
        
        Args:
            models_dir: models目录路径
            config: 配置字典
        """
        self.models_dir = models_dir
        self.config = config or {}
        self.scheduler = None
        self.logger = logging.getLogger(__name__)
        
        # 设置日志格式
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('model_sync.log')
            ]
        )
    
    async def start(self):
        """启动守护进程"""
        try:
            self.logger.info("启动模型同步守护进程...")
            
            # 创建调度器
            self.scheduler = ModelSyncScheduler(
                self.models_dir,
                self.config.get('system_user_id', "system")
            )
            
            # 根据配置启动调度器
            if self.config.get('use_cron', True):
                cron_expr = self.config.get('cron_expression', '0 */6 * * *')
                self.scheduler.start_scheduler(
                    cron_expression=cron_expr,
                    run_immediately=self.config.get('run_immediately', True)
                )
            else:
                interval = self.config.get('interval_minutes', 360)
                self.scheduler.start_interval_scheduler(
                    interval_minutes=interval,
                    run_immediately=self.config.get('run_immediately', True)
                )
            
            self.logger.info("模型同步守护进程启动成功")
            
            # 保持运行
            while True:
                await asyncio.sleep(60)  # 每分钟检查一次
                
        except KeyboardInterrupt:
            self.logger.info("收到停止信号，正在关闭守护进程...")
        except Exception as e:
            self.logger.error(f"守护进程运行错误: {str(e)}")
        finally:
            await self.stop()
    
    async def stop(self):
        """停止守护进程"""
        if self.scheduler:
            self.scheduler.stop_scheduler()
        self.logger.info("模型同步守护进程已停止")


async def main():
    """测试调度器"""
    models_dir = "/Users/twenty/LLM/EasyAI/src/infrastructure/models"
    
    # 创建调度器
    scheduler = ModelSyncScheduler(models_dir)
    
    print("=== 启动测试调度器 ===")
    # 使用间隔调度器，每2分钟执行一次（仅用于测试）
    scheduler.start_interval_scheduler(interval_minutes=2, run_immediately=True)
    
    try:
        # 运行5分钟后停止
        await asyncio.sleep(300)
    except KeyboardInterrupt:
        print("收到停止信号...")
    finally:
        scheduler.stop_scheduler()
        print("调度器已停止")


if __name__ == "__main__":
    asyncio.run(main())
