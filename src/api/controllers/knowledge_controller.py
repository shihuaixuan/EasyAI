"""
知识库API控制器
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from ...infrastructure.database import get_database_session
from ...infrastructure.repositories.knowledge.knowledge_base_database_repository_impl import KnowledgeBaseDatabaseRepositoryImpl
from ...application.services.knowledge_application_service import KnowledgeApplicationService
from ...domain.knowledge.services.knowledge_base_domain_service import KnowledgeBaseDomainService
from ...application.dto.knowledge_base_dto import (
    KnowledgeBaseCreateRequest,
    KnowledgeBaseResponse,
    KnowledgeBaseListResponse,
    KnowledgeBaseOverviewResponse
)
from ...application.dto.file_upload_dto import (
    FileUploadResponse,
    FileUploadBatchResponse,
    FileListBatchResponse
)
from ...application.dto.workflow_dto import (
    WorkflowConfigRequest,
    WorkflowConfigResponse
)
from ..dependencies import get_current_user_id

router = APIRouter(prefix="/api/knowledge", tags=["知识库"])


@router.post("/knowledge-bases", response_model=KnowledgeBaseResponse)
async def create_knowledge_base(
    request: KnowledgeBaseCreateRequest,
    session: AsyncSession = Depends(get_database_session),
    current_user_id: str = Depends(get_current_user_id)
):
    """创建知识库"""
    try:
        # 创建仓储实例
        knowledge_base_repo = KnowledgeBaseDatabaseRepositoryImpl(session)
        
        # 创建知识库实体
        from ...domain.knowledge.entities.knowledge_base import KnowledgeBase
        knowledge_base = KnowledgeBase(
            name=request.name,
            description=request.description,
            owner_id=current_user_id,
            config=request.config or {}
        )
        
        # 检查名称是否重复
        if await knowledge_base_repo.exists_by_name_and_owner(request.name, current_user_id):
            raise HTTPException(status_code=400, detail=f"知识库名称 '{request.name}' 已存在")
        
        # 保存到数据库
        saved_kb = await knowledge_base_repo.save(knowledge_base)
        await session.commit()
        
        # 返回响应
        # __post_init__ 保证 knowledge_base_id 不会为 None
        assert saved_kb.knowledge_base_id is not None
        assert saved_kb.owner_id is not None
        assert saved_kb.created_at is not None
        assert saved_kb.updated_at is not None
        return KnowledgeBaseResponse(
            knowledge_base_id=saved_kb.knowledge_base_id,
            name=saved_kb.name,
            description=saved_kb.description,
            owner_id=saved_kb.owner_id,
            config=saved_kb.config or {},
            is_active=saved_kb.is_active,
            document_count=0,
            chunk_count=0,
            created_at=saved_kb.created_at,
            updated_at=saved_kb.updated_at
        )
        
    except ValueError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"创建知识库失败: {str(e)}")


@router.get("/knowledge-bases", response_model=KnowledgeBaseListResponse)
async def get_knowledge_bases(
    session: AsyncSession = Depends(get_database_session),
    current_user_id: str = Depends(get_current_user_id)
):
    """获取知识库列表"""
    try:
        # 创建仓储实例
        knowledge_base_repo = KnowledgeBaseDatabaseRepositoryImpl(session)
        
        # 获取知识库列表
        knowledge_bases = await knowledge_base_repo.find_by_owner_id(current_user_id)
        
        # 转换为响应对象
        kb_responses = []
        for kb in knowledge_bases:
            # __post_init__ 保证这些字段不会为 None
            if not all([kb.knowledge_base_id, kb.owner_id, kb.created_at, kb.updated_at]):
                print(f"警告：知识库 {kb.name} 的必要字段为空，跳过")
                continue
                
            kb_responses.append(KnowledgeBaseResponse(
                knowledge_base_id=kb.knowledge_base_id or "",
                name=kb.name,
                description=kb.description,
                owner_id=kb.owner_id or "",
                config=kb.config or {},
                is_active=kb.is_active,
                document_count=kb.document_count,
                chunk_count=kb.chunk_count,
                created_at=kb.created_at or datetime.now(),
                updated_at=kb.updated_at or datetime.now()
            ))
        
        return KnowledgeBaseListResponse(
            knowledge_bases=kb_responses,
            total=len(kb_responses)
        )
        
    except Exception as e:
        print(f"获取知识库列表出错: {str(e)}")
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"获取知识库列表失败: {str(e)}")


@router.get("/knowledge-bases/{knowledge_base_id}", response_model=KnowledgeBaseResponse)
async def get_knowledge_base(
    knowledge_base_id: str,
    session: AsyncSession = Depends(get_database_session),
    current_user_id: str = Depends(get_current_user_id)
):
    """获取知识库详情"""
    try:
        # 创建仓储实例
        knowledge_base_repo = KnowledgeBaseDatabaseRepositoryImpl(session)
        
        # 查找知识库
        knowledge_base = await knowledge_base_repo.find_by_id(knowledge_base_id)
        if not knowledge_base:
            raise HTTPException(status_code=404, detail="知识库不存在")
        
        # TODO: 验证用户权限
        return KnowledgeBaseResponse(
            knowledge_base_id=knowledge_base.knowledge_base_id or "",
            name=knowledge_base.name,
            description=knowledge_base.description,
            owner_id=knowledge_base.owner_id or "",
            config=knowledge_base.config or {},
            is_active=knowledge_base.is_active,
            document_count=knowledge_base.document_count,
            chunk_count=knowledge_base.chunk_count,
            created_at=knowledge_base.created_at or datetime.now(),
            updated_at=knowledge_base.updated_at or datetime.now()
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取知识库详情出错: {str(e)}")
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"获取知识库详情失败: {str(e)}")


@router.get("/knowledge-bases/{knowledge_base_id}/overview", response_model=KnowledgeBaseOverviewResponse)
async def get_knowledge_base_overview(
    knowledge_base_id: str,
    session: AsyncSession = Depends(get_database_session),
    current_user_id: str = Depends(get_current_user_id)
):
    """获取知识库概览"""
    try:
        # 创建仓储实例
        from ...infrastructure.repositories.knowledge.document_sql_repository import DocumentSqlRepository
        from ...infrastructure.repositories.knowledge.document_chunk_sql_repository import DocumentChunkSqlRepository
        
        knowledge_base_repo = KnowledgeBaseDatabaseRepositoryImpl(session)
        document_repo = DocumentSqlRepository(session)
        document_chunk_repo = DocumentChunkSqlRepository(session)
        
        # 创建领域服务
        knowledge_base_domain_service = KnowledgeBaseDomainService(
            knowledge_base_repo=knowledge_base_repo,
            document_repo=document_repo,
            chunk_repo=document_chunk_repo
        )
        
        overview = await knowledge_base_domain_service.get_knowledge_base_overview(knowledge_base_id)
        
        # 转换为响应对象
        knowledge_base = overview["knowledge_base"]
        return KnowledgeBaseOverviewResponse(
            knowledge_base=KnowledgeBaseResponse(
                knowledge_base_id=knowledge_base.knowledge_base_id or "",
                name=knowledge_base.name,
                description=knowledge_base.description,
                owner_id=knowledge_base.owner_id or "",
                config=knowledge_base.config or {},
                is_active=knowledge_base.is_active,
                document_count=knowledge_base.document_count,
                chunk_count=knowledge_base.chunk_count,
                created_at=knowledge_base.created_at or datetime.now(),
                updated_at=knowledge_base.updated_at or datetime.now()
            ),
            document_count=overview["document_count"],
            chunk_count=overview["chunk_count"],
            recent_documents=[],  # 简化处理
            file_types=overview["file_types"],
            total_size=overview["total_size"]
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"获取知识库概览出错: {str(e)}")
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"获取知识库概览失败: {str(e)}")


@router.put("/knowledge-bases/{knowledge_base_id}/config", response_model=WorkflowConfigResponse)
async def update_workflow_config(
    knowledge_base_id: str,
    config_request: WorkflowConfigRequest,
    session: AsyncSession = Depends(get_database_session),
    current_user_id: str = Depends(get_current_user_id)
):
    """更新工作流配置"""
    try:
        # 创建使用当前请求会话的仓储实例
        from ...infrastructure.repositories.knowledge.document_sql_repository import DocumentSqlRepository
        from ...infrastructure.repositories.knowledge.document_chunk_sql_repository import DocumentChunkSqlRepository
        
        knowledge_base_repo = KnowledgeBaseDatabaseRepositoryImpl(session)
        document_repo = DocumentSqlRepository(session)
        document_chunk_repo = DocumentChunkSqlRepository(session)
        
        # 创建领域服务（使用当前请求的会话）
        knowledge_base_domain_service = KnowledgeBaseDomainService(
            knowledge_base_repo=knowledge_base_repo,
            document_repo=document_repo,
            chunk_repo=document_chunk_repo
        )
        
        # 验证知识库是否存在
        knowledge_base = await knowledge_base_repo.find_by_id(knowledge_base_id)
        if not knowledge_base:
            raise HTTPException(status_code=404, detail=f"知识库不存在: {knowledge_base_id}")
        
        # 将请求转换为配置字典
        config_dict = {
            "chunking": {
                "strategy": config_request.chunking.strategy,
                "separator": config_request.chunking.separator,
                "max_length": config_request.chunking.max_length,
                "overlap_length": config_request.chunking.overlap_length,
                "preprocessing": {
                    "remove_extra_whitespace": config_request.chunking.remove_extra_whitespace,
                    "remove_urls": config_request.chunking.remove_urls,
                    "remove_emails": config_request.chunking.remove_emails
                }
            },
            "embedding": {
                "strategy": config_request.embedding.strategy,
                "model_name": config_request.embedding.model_name
            },
            "retrieval": {
                "strategy": config_request.retrieval.strategy,
                "top_k": config_request.retrieval.top_k,
                "score_threshold": config_request.retrieval.score_threshold,
                "enable_rerank": config_request.retrieval.enable_rerank,
                "rerank_model": config_request.retrieval.rerank_model
            }
        }
        
        # 添加父子分段特有配置
        if config_request.chunking.strategy == "parent_child":
            config_dict["chunking"].update({
                "parent_separator": config_request.chunking.parent_separator,
                "parent_max_length": config_request.chunking.parent_max_length,
                "child_separator": config_request.chunking.child_separator,
                "child_max_length": config_request.chunking.child_max_length
            })
        
        # 更新配置（使用领域服务）
        updated_knowledge_base = await knowledge_base_domain_service.update_knowledge_base_config(
            knowledge_base_id, config_dict
        )
        
        # 提交数据库事务
        await session.commit()
        
        # 验证配置更新是否成功
        if not updated_knowledge_base.config:
            raise HTTPException(status_code=500, detail="配置更新失败：数据库中没有保存配置")
        
        print(f"配置更新成功：知识库 {knowledge_base_id}, 新配置: {config_dict}")
        
        # 返回响应
        return WorkflowConfigResponse(
            knowledge_base_id=knowledge_base_id,
            config=updated_knowledge_base.config,
            updated_at=updated_knowledge_base.updated_at or datetime.now()
        )
        
    except HTTPException:
        await session.rollback()
        raise
    except ValueError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"更新配置失败: {str(e)}")


@router.post("/knowledge-bases/{knowledge_base_id}/files", response_model=FileUploadResponse)
async def upload_file(
    knowledge_base_id: str,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_database_session),
    current_user_id: str = Depends(get_current_user_id)
):
    """上传单个文件"""
    try:
        # 创建使用当前请求会话的仓储实例
        from ...infrastructure.repositories.knowledge.document_sql_repository import DocumentSqlRepository
        from ...infrastructure.repositories.knowledge.document_chunk_sql_repository import DocumentChunkSqlRepository
        from ...domain.knowledge.services.file_upload_service import FileUploadService
        from ...domain.knowledge.services.document_parser_service import DocumentParserService, DocumentParserRegistry
        from ...domain.knowledge.services.chunking.document_chunking_service import DocumentChunkingService
        from ...domain.knowledge.vo.workflow_config import FileUploadConfig
        from ...infrastructure.parsers.document_parsers import TextDocumentParser, DefaultDocumentParser
        
        knowledge_base_repo = KnowledgeBaseDatabaseRepositoryImpl(session)
        document_repo = DocumentSqlRepository(session)
        document_chunk_repo = DocumentChunkSqlRepository(session)
        
        # 创建领域服务和应用服务
        knowledge_base_domain_service = KnowledgeBaseDomainService(
            knowledge_base_repo=knowledge_base_repo,
            document_repo=document_repo,
            chunk_repo=document_chunk_repo
        )
        
        file_upload_config = FileUploadConfig()
        file_upload_service = FileUploadService(file_upload_config)
        
        parser_registry = DocumentParserRegistry()
        parser_registry.register(['.txt', '.md', '.mdx', '.csv', '.json', '.xml', '.html', '.htm'], TextDocumentParser)
        parser_registry.register(['.pdf', '.doc', '.docx', '.xlsx', '.xls', '.ppt', '.pptx'], DefaultDocumentParser)
        document_parser_service = DocumentParserService(parser_registry)
        
        document_chunking_service = DocumentChunkingService()
        
        application_service = KnowledgeApplicationService(
            knowledge_base_domain_service=knowledge_base_domain_service,
            file_upload_service=file_upload_service,
            document_parser_service=document_parser_service,
            document_chunking_service=document_chunking_service,
            knowledge_base_repo=knowledge_base_repo,
            document_repo=document_repo,
            document_chunk_repo=document_chunk_repo
        )
        
        # TODO: 验证用户对知识库的权限
        result = await application_service.upload_file(knowledge_base_id, file)
        
        # 只有成功时才提交事务，失败时不需要回滚（应用服务内部处理）
        if result.success:
            await session.commit()
        
        return result
    except Exception as e:
        print(f"文件上传出错: {str(e)}")
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")


@router.post("/knowledge-bases/{knowledge_base_id}/files/batch", response_model=FileUploadBatchResponse)
async def upload_files_batch(
    knowledge_base_id: str,
    files: List[UploadFile] = File(...),
    session: AsyncSession = Depends(get_database_session),
    current_user_id: str = Depends(get_current_user_id)
):
    """批量上传文件"""
    try:
        # 创建使用当前请求会话的仓储实例
        from ...infrastructure.repositories.knowledge.document_sql_repository import DocumentSqlRepository
        from ...infrastructure.repositories.knowledge.document_chunk_sql_repository import DocumentChunkSqlRepository
        from ...domain.knowledge.services.file_upload_service import FileUploadService
        from ...domain.knowledge.services.document_parser_service import DocumentParserService, DocumentParserRegistry
        from ...domain.knowledge.services.chunking.document_chunking_service import DocumentChunkingService
        from ...domain.knowledge.vo.workflow_config import FileUploadConfig
        from ...infrastructure.parsers.document_parsers import TextDocumentParser, DefaultDocumentParser
        
        knowledge_base_repo = KnowledgeBaseDatabaseRepositoryImpl(session)
        document_repo = DocumentSqlRepository(session)
        document_chunk_repo = DocumentChunkSqlRepository(session)
        
        # 创建领域服务（使用当前请求的会话）
        knowledge_base_domain_service = KnowledgeBaseDomainService(
            knowledge_base_repo=knowledge_base_repo,
            document_repo=document_repo,
            chunk_repo=document_chunk_repo
        )
        
        # 创建其他服务
        file_upload_config = FileUploadConfig()
        file_upload_service = FileUploadService(file_upload_config)
        
        parser_registry = DocumentParserRegistry()
        parser_registry.register(['.txt', '.md', '.mdx', '.csv', '.json', '.xml', '.html', '.htm'], TextDocumentParser)
        parser_registry.register(['.pdf', '.doc', '.docx', '.xlsx', '.xls', '.ppt', '.pptx'], DefaultDocumentParser)
        document_parser_service = DocumentParserService(parser_registry)
        
        document_chunking_service = DocumentChunkingService()
        
        # 创建应用服务（使用当前请求的会话）
        application_service = KnowledgeApplicationService(
            knowledge_base_domain_service=knowledge_base_domain_service,
            file_upload_service=file_upload_service,
            document_parser_service=document_parser_service,
            document_chunking_service=document_chunking_service,
            knowledge_base_repo=knowledge_base_repo,
            document_repo=document_repo,
            document_chunk_repo=document_chunk_repo
        )
        
        # TODO: 验证用户对知识库的权限
        result = await application_service.upload_files_batch(knowledge_base_id, files)
        
        # 批量上传的事务由应用服务内部管理，这里只需要提交
        await session.commit()
        
        return result
    except Exception as e:
        print(f"批量文件上传出错: {str(e)}")
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"批量文件上传失败: {str(e)}")


@router.get("/knowledge-bases/{knowledge_base_id}/files", response_model=FileListBatchResponse)
async def list_files(
    knowledge_base_id: str,
    session: AsyncSession = Depends(get_database_session),
    current_user_id: str = Depends(get_current_user_id)
):
    """获取文件列表"""
    try:
        # 创建使用当前请求会话的仓储实例
        from ...infrastructure.repositories.knowledge.document_sql_repository import DocumentSqlRepository
        from ...infrastructure.repositories.knowledge.document_chunk_sql_repository import DocumentChunkSqlRepository
        from ...domain.knowledge.services.file_upload_service import FileUploadService
        from ...domain.knowledge.services.document_parser_service import DocumentParserService, DocumentParserRegistry
        from ...domain.knowledge.services.chunking.document_chunking_service import DocumentChunkingService
        from ...domain.knowledge.vo.workflow_config import FileUploadConfig
        from ...infrastructure.parsers.document_parsers import TextDocumentParser, DefaultDocumentParser
        
        knowledge_base_repo = KnowledgeBaseDatabaseRepositoryImpl(session)
        document_repo = DocumentSqlRepository(session)
        document_chunk_repo = DocumentChunkSqlRepository(session)
        
        # 创建领域服务（使用当前请求的会话）
        knowledge_base_domain_service = KnowledgeBaseDomainService(
            knowledge_base_repo=knowledge_base_repo,
            document_repo=document_repo,
            chunk_repo=document_chunk_repo
        )
        
        # 创建其他服务
        file_upload_config = FileUploadConfig()
        file_upload_service = FileUploadService(file_upload_config)
        
        parser_registry = DocumentParserRegistry()
        parser_registry.register(['.txt', '.md', '.mdx', '.csv', '.json', '.xml', '.html', '.htm'], TextDocumentParser)
        parser_registry.register(['.pdf', '.doc', '.docx', '.xlsx', '.xls', '.ppt', '.pptx'], DefaultDocumentParser)
        document_parser_service = DocumentParserService(parser_registry)
        
        document_chunking_service = DocumentChunkingService()
        
        # 创建应用服务（使用当前请求的会话）
        application_service = KnowledgeApplicationService(
            knowledge_base_domain_service=knowledge_base_domain_service,
            file_upload_service=file_upload_service,
            document_parser_service=document_parser_service,
            document_chunking_service=document_chunking_service,
            knowledge_base_repo=knowledge_base_repo,
            document_repo=document_repo,
            document_chunk_repo=document_chunk_repo
        )
        
        # TODO: 验证用户对知识库的权限
        result = await application_service.list_files(knowledge_base_id)
        return result
    except Exception as e:
        print(f"获取文件列表出错: {str(e)}")
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"获取文件列表失败: {str(e)}")


@router.delete("/knowledge-bases/{knowledge_base_id}/files/{file_id}")
async def delete_file(
    knowledge_base_id: str,
    file_id: str,
    session: AsyncSession = Depends(get_database_session),
    current_user_id: str = Depends(get_current_user_id)
):
    """删除单个文件"""
    try:
        # 创建使用当前请求会话的仓储实例
        from ...infrastructure.repositories.knowledge.document_sql_repository import DocumentSqlRepository
        from ...infrastructure.repositories.knowledge.document_chunk_sql_repository import DocumentChunkSqlRepository
        
        knowledge_base_repo = KnowledgeBaseDatabaseRepositoryImpl(session)
        document_repo = DocumentSqlRepository(session)
        document_chunk_repo = DocumentChunkSqlRepository(session)
        
        # 创建领域服务（使用当前请求的会话）
        knowledge_base_domain_service = KnowledgeBaseDomainService(
            knowledge_base_repo=knowledge_base_repo,
            document_repo=document_repo,
            chunk_repo=document_chunk_repo
        )
        
        # 验证知识库是否存在
        knowledge_base = await knowledge_base_repo.find_by_id(knowledge_base_id)
        if not knowledge_base:
            raise HTTPException(status_code=404, detail="知识库不存在")
        
        # TODO: 验证用户对知识库的权限
        
        # 验证文档是否存在
        document = await document_repo.find_by_id(file_id)
        if not document:
            raise HTTPException(status_code=404, detail="文件不存在")
        
        # 验证文档是否属于该知识库
        if document.knowledge_base_id != knowledge_base_id:
            raise HTTPException(status_code=400, detail="文件不属于该知识库")
        
        # 删除文档的所有文档块
        await document_chunk_repo.delete_by_document_id(file_id)
        
        # 删除文档
        await document_repo.delete_by_id(file_id)
        
        # 更新知识库统计信息
        await knowledge_base_domain_service.update_knowledge_base_statistics(knowledge_base_id)
        
        # 提交数据库事务
        await session.commit()
        
        return {"message": "文件删除成功"}
        
    except HTTPException:
        await session.rollback()
        raise
    except Exception as e:
        print(f"删除文件出错: {str(e)}")
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"删除文件失败: {str(e)}")


@router.delete("/knowledge-bases/{knowledge_base_id}")
async def delete_knowledge_base(
    knowledge_base_id: str,
    session: AsyncSession = Depends(get_database_session),
    current_user_id: str = Depends(get_current_user_id)
):
    """删除知识库"""
    try:
        # 创建使用当前请求会话的仓储实例
        from ...infrastructure.repositories.knowledge.document_sql_repository import DocumentSqlRepository
        from ...infrastructure.repositories.knowledge.document_chunk_sql_repository import DocumentChunkSqlRepository
        from ...domain.knowledge.services.file_upload_service import FileUploadService
        from ...domain.knowledge.services.document_parser_service import DocumentParserService, DocumentParserRegistry
        from ...domain.knowledge.services.chunking.document_chunking_service import DocumentChunkingService
        from ...domain.knowledge.vo.workflow_config import FileUploadConfig
        from ...infrastructure.parsers.document_parsers import TextDocumentParser, DefaultDocumentParser
        
        knowledge_base_repo = KnowledgeBaseDatabaseRepositoryImpl(session)
        document_repo = DocumentSqlRepository(session)
        document_chunk_repo = DocumentChunkSqlRepository(session)
        
        # 创建领域服务（使用当前请求的会话）
        knowledge_base_domain_service = KnowledgeBaseDomainService(
            knowledge_base_repo=knowledge_base_repo,
            document_repo=document_repo,
            chunk_repo=document_chunk_repo
        )
        
        # 创建其他服务
        file_upload_config = FileUploadConfig()
        file_upload_service = FileUploadService(file_upload_config)
        
        parser_registry = DocumentParserRegistry()
        parser_registry.register(['.txt', '.md', '.mdx', '.csv', '.json', '.xml', '.html', '.htm'], TextDocumentParser)
        parser_registry.register(['.pdf', '.doc', '.docx', '.xlsx', '.xls', '.ppt', '.pptx'], DefaultDocumentParser)
        document_parser_service = DocumentParserService(parser_registry)
        
        document_chunking_service = DocumentChunkingService()
        
        # 创建应用服务（使用当前请求的会话）
        application_service = KnowledgeApplicationService(
            knowledge_base_domain_service=knowledge_base_domain_service,
            file_upload_service=file_upload_service,
            document_parser_service=document_parser_service,
            document_chunking_service=document_chunking_service,
            knowledge_base_repo=knowledge_base_repo,
            document_repo=document_repo,
            document_chunk_repo=document_chunk_repo
        )
        
        # TODO: 验证用户对知识库的权限
        success = await application_service.delete_knowledge_base(knowledge_base_id)
        if not success:
            raise HTTPException(status_code=404, detail="知识库不存在")
        
        # 提交数据库事务
        await session.commit()
        
        return {"message": "知识库删除成功"}
    except HTTPException:
        await session.rollback()
        raise
    except Exception as e:
        print(f"删除知识库出错: {str(e)}")
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"删除知识库失败: {str(e)}")


@router.get("/embedding-models")
async def get_available_embedding_models(
    session: AsyncSession = Depends(get_database_session),
    current_user_id: str = Depends(get_current_user_id)
):
    """获取用户可用的embedding模型"""
    try:
        from ...infrastructure.repositories.provider.sql_provider_repository import SqlProviderRepository
        from ...infrastructure.models.provider_models import ModelModel, ProviderModel
        from sqlalchemy import select, and_
        
        # 1. 查询用户有权访问的提供商列表
        provider_repo = SqlProviderRepository(session)
        # 直接使用字符串用户ID（UUID格式）
        user_providers = await provider_repo.find_by_user_id(current_user_id)
        
        # 获取用户配置的提供商名称列表
        user_provider_names = {provider.provider for provider in user_providers if not provider.is_delete}
        
        # 2. 从ModelModel表查询所有embedding类型的模型
        stmt = select(ModelModel).where(
            and_(
                ModelModel.type == 'embedding',
                ModelModel.is_delete == 0
            )
        )
        result = await session.execute(stmt)
        all_embedding_models = result.scalars().all()
        
        # 3. 过滤用户有权访问的模型
        available_models = []
        for model in all_embedding_models:
            # 检查用户是否配置了该提供商
            if model.provider_name in user_provider_names:
                metadata = model.get_metadata_dict()
                
                model_info = {
                    "provider": model.provider_name,
                    "model_name": model.model_name,
                    "display_name": model.model_name,
                    "description": metadata.get('description', f'{model.provider_name}的{model.model_name}模型'),
                    "capabilities": metadata.get('capabilities', []),
                    "context_length": metadata.get('context_length', 0),
                    "subtype": model.subtype
                }
                available_models.append(model_info)
        
        # 4. 按提供商和模型名称排序
        available_models.sort(key=lambda x: (x['provider'], x['model_name']))
        
        return {
            "models": available_models,
            "total": len(available_models),
            "user_providers": list(user_provider_names)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取embedding模型列表失败: {str(e)}")


@router.post("/knowledge-bases/{knowledge_base_id}/reprocess-embeddings")
async def reprocess_embeddings(
    knowledge_base_id: str,
    session: AsyncSession = Depends(get_database_session),
    current_user_id: str = Depends(get_current_user_id)
):
    """重新处理知识库的embedding向量"""
    try:
        # 验证知识库是否存在
        from ...infrastructure.repositories.knowledge.knowledge_base_database_repository_impl import KnowledgeBaseDatabaseRepositoryImpl
        knowledge_base_repo = KnowledgeBaseDatabaseRepositoryImpl(session)
        knowledge_base = await knowledge_base_repo.find_by_id(knowledge_base_id)
        
        if not knowledge_base:
            raise HTTPException(status_code=404, detail="知识库不存在")
        
        # 启动异步embedding处理任务
        from ...application.services.embedding_application_service import create_embedding_application_service
        import asyncio
        
        # 创建异步任务（不等待完成）
        async def process_task():
            embedding_app_service = await create_embedding_application_service(session)
            return await embedding_app_service.process_knowledge_base_embeddings(
                knowledge_base_id, current_user_id
            )
        
        task = asyncio.create_task(process_task())
        
        return {
            "success": True,
            "message": "已启动embedding重新处理任务，请稍后查看处理结果",
            "knowledge_base_id": knowledge_base_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"启动embedding重新处理失败: {str(e)}")
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"启动embedding重新处理失败: {str(e)}")


@router.post("/knowledge-bases/{knowledge_base_id}/documents/{document_id}/reprocess-embeddings")
async def reprocess_document_embeddings(
    knowledge_base_id: str,
    document_id: str,
    session: AsyncSession = Depends(get_database_session),
    current_user_id: str = Depends(get_current_user_id)
):
    """重新处理单个文档的embedding向量"""
    try:
        # 验证知识库和文档是否存在
        from ...infrastructure.repositories.knowledge.knowledge_base_database_repository_impl import KnowledgeBaseDatabaseRepositoryImpl
        from ...infrastructure.repositories.knowledge.document_sql_repository import DocumentSqlRepository
        
        knowledge_base_repo = KnowledgeBaseDatabaseRepositoryImpl(session)
        document_repo = DocumentSqlRepository(session)
        
        knowledge_base = await knowledge_base_repo.find_by_id(knowledge_base_id)
        if not knowledge_base:
            raise HTTPException(status_code=404, detail="知识库不存在")
        
        document = await document_repo.find_by_id(document_id)
        if not document or document.knowledge_base_id != knowledge_base_id:
            raise HTTPException(status_code=404, detail="文档不存在或不属于该知识库")
        
        # 启动异步embedding处理任务
        from ...application.services.embedding_application_service import create_embedding_application_service
        import asyncio
        
        # 创建异步任务（不等待完成）
        async def process_task():
            embedding_app_service = await create_embedding_application_service(session)
            return await embedding_app_service.process_document_embeddings(
                knowledge_base_id, document_id, current_user_id
            )
        
        task = asyncio.create_task(process_task())
        
        return {
            "success": True,
            "message": f"已启动文档 {document.filename} 的embedding重新处理任务",
            "knowledge_base_id": knowledge_base_id,
            "document_id": document_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"启动文档embedding重新处理失败: {str(e)}")
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"启动文档embedding重新处理失败: {str(e)}")


@router.get("/knowledge-bases/{knowledge_base_id}/embedding-status")
async def get_embedding_status(
    knowledge_base_id: str,
    session: AsyncSession = Depends(get_database_session),
    current_user_id: str = Depends(get_current_user_id)
):
    """获取知识库的embedding状态"""
    try:
        from ...infrastructure.repositories.knowledge.document_chunk_sql_repository import DocumentChunkSqlRepository
        
        chunk_repo = DocumentChunkSqlRepository(session)
        
        # 获取所有分块
        all_chunks = await chunk_repo.find_by_knowledge_base_id(knowledge_base_id)
        
        # 获取没有向量的分块
        chunks_without_vectors = await chunk_repo.find_chunks_without_vectors(knowledge_base_id)
        
        total_chunks = len(all_chunks)
        chunks_with_vectors = total_chunks - len(chunks_without_vectors)
        
        return {
            "knowledge_base_id": knowledge_base_id,
            "total_chunks": total_chunks,
            "chunks_with_vectors": chunks_with_vectors,
            "chunks_without_vectors": len(chunks_without_vectors),
            "embedding_progress": round((chunks_with_vectors / total_chunks * 100) if total_chunks > 0 else 0, 2)
        }
        
    except Exception as e:
        print(f"获取embedding状态失败: {str(e)}")
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"获取embedding状态失败: {str(e)}")


@router.post("/knowledge-bases/{knowledge_base_id}/process")
async def start_knowledge_processing(
    knowledge_base_id: str,
    session: AsyncSession = Depends(get_database_session),
    current_user_id: str = Depends(get_current_user_id)
):
    """开始知识库处理流程"""
    try:
        # 创建使用当前请求会话的仓储实例
        from ...infrastructure.repositories.knowledge.document_sql_repository import DocumentSqlRepository
        from ...infrastructure.repositories.knowledge.document_chunk_sql_repository import DocumentChunkSqlRepository
        from ...domain.knowledge.services.file_upload_service import FileUploadService
        from ...domain.knowledge.services.document_parser_service import DocumentParserService, DocumentParserRegistry
        from ...domain.knowledge.services.chunking.document_chunking_service import DocumentChunkingService
        from ...domain.knowledge.vo.workflow_config import FileUploadConfig
        from ...infrastructure.parsers.document_parsers import TextDocumentParser, DefaultDocumentParser
        
        knowledge_base_repo = KnowledgeBaseDatabaseRepositoryImpl(session)
        document_repo = DocumentSqlRepository(session)
        document_chunk_repo = DocumentChunkSqlRepository(session)
        
        # 创建领域服务（使用当前请求的会话）
        knowledge_base_domain_service = KnowledgeBaseDomainService(
            knowledge_base_repo=knowledge_base_repo,
            document_repo=document_repo,
            chunk_repo=document_chunk_repo
        )
        
        # 创建其他服务
        file_upload_config = FileUploadConfig()
        file_upload_service = FileUploadService(file_upload_config)
        
        parser_registry = DocumentParserRegistry()
        parser_registry.register(['.txt', '.md', '.mdx', '.csv', '.json', '.xml', '.html', '.htm'], TextDocumentParser)
        parser_registry.register(['.pdf', '.doc', '.docx', '.xlsx', '.xls', '.ppt', '.pptx'], DefaultDocumentParser)
        document_parser_service = DocumentParserService(parser_registry)
        
        document_chunking_service = DocumentChunkingService()
        
        # 创建应用服务（使用当前请求的会话）
        application_service = KnowledgeApplicationService(
            knowledge_base_domain_service=knowledge_base_domain_service,
            file_upload_service=file_upload_service,
            document_parser_service=document_parser_service,
            document_chunking_service=document_chunking_service,
            knowledge_base_repo=knowledge_base_repo,
            document_repo=document_repo,
            document_chunk_repo=document_chunk_repo
        )
        
        # 开始处理流程
        result: Dict[str, Any] = await application_service.start_knowledge_processing(knowledge_base_id, current_user_id)
        
        # 提交数据库事务
        await session.commit()
        
        return result
        
    except ValueError as e:
        # 验证错误，回滚事务
        try:
            await session.rollback()
        except Exception as rollback_error:
            print(f"回滚事务失败: {str(rollback_error)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        # 其他异常，回滚事务
        try:
            await session.rollback()
        except Exception as rollback_error:
            print(f"回滚事务失败: {str(rollback_error)}")
        raise HTTPException(status_code=500, detail=f"开始处理失败: {str(e)}")


@router.get("/supported-file-types")
async def get_supported_file_types():
    """获取支持的文件类型"""
    return {
        "file_types": [
            ".txt", ".md", ".mdx", ".pdf", ".html", ".xlsx", ".xls",
            ".vtt", ".properties", ".doc", ".docx", ".csv", ".eml",
            ".msg", ".pptx", ".xml", ".epub", ".ppt", ".htm"
        ],
        "max_file_size": 15 * 1024 * 1024,  # 15MB
        "description": "支持的文件格式和大小限制"
    }