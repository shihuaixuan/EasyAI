#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EasyAI 项目主入口文件
基于DDD架构的AI应用系统
"""

import uvicorn
from src.api.app import app

def main():
    """应用程序主入口"""
    print("EasyAI 应用启动中...")
    
    # 启动FastAPI应用
    uvicorn.run(
        "src.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()