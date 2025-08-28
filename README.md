# EasyAI

基于领域驱动设计（DDD）架构的AI应用系统

## 项目结构

```
EasyAI/
├── main.py                    # 应用程序入口
├── requirements.txt           # 项目依赖
├── pyproject.toml            # 项目配置
├── README.md                 # 项目说明
└── src/                      # 源代码目录
    ├── __init__.py
    ├── application/          # 应用层
    │   ├── __init__.py
    │   ├── services/         # 应用服务
    │   ├── dto/             # 数据传输对象
    │   └── interfaces/      # 应用接口
    ├── domain/              # 领域层
    │   ├── __init__.py
    │   ├── user/            # 用户领域
    │   ├── model/           # 模型领域
    │   ├── knowledge/       # 知识库领域
    │   └── shared/          # 共享领域对象
    └── infrastructure/      # 基础设施层
        ├── __init__.py
        ├── config/          # 配置管理
        ├── database/        # 数据库访问
        ├── external/        # 外部服务
        ├── logging/         # 日志系统
        └── repositories/    # 仓储实现
```

## 模块说明

### 用户模块
- 用户认证与授权
- 用户信息管理
- 用户权限控制

### 模型模块
- AI模型管理
- 模型训练与推理
- 模型版本控制

### 知识库模块
- 知识存储与检索
- 向量化处理
- 知识图谱构建

## 安装与运行

1. 安装依赖
```bash
pip install -r requirements.txt
```

2. 运行应用
```bash
python main.py
```

## 开发规范

- 遵循DDD架构原则
- 使用类型注解
- 编写单元测试
- 遵循PEP 8代码规范