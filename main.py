#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EasyAI 项目主入口文件
基于DDD架构的AI应用系统
"""

from src.application.services.app_service import AppService
from src.infrastructure.config.settings import Settings
from src.infrastructure.logging.logger import setup_logger


def main():
    """应用程序主入口"""
    # 初始化配置
    settings = Settings()
    
    # 设置日志
    logger = setup_logger(settings.log_level)
    
    # 启动应用服务
    app_service = AppService(settings)
    
    try:
        logger.info("EasyAI 应用启动中...")
        app_service.start()
    except KeyboardInterrupt:
        logger.info("接收到停止信号，正在关闭应用...")
    except Exception as e:
        logger.error(f"应用运行出错: {e}")
    finally:
        app_service.stop()
        logger.info("EasyAI 应用已停止")


if __name__ == "__main__":
    main()