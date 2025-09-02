"""
知识库API控制器
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from ...infrastructure.database import get_database_session
from ...infrastructure.repositories.knowledge_base_database_repository_impl import KnowledgeBaseDatabaseRepositoryImpl
from ...application.services.knowledge_application_service import KnowledgeApplicationService
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
from ..dependencies import get_knowledge_service, get_current_user_id

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
async def list_knowledge_bases(
    service: KnowledgeApplicationService = Depends(get_knowledge_service),
    current_user_id: str = Depends(get_current_user_id)
):
    """获取知识库列表"""
    try:
        return await service.list_knowledge_bases(current_user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取知识库列表失败: {str(e)}")


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
            assert kb.knowledge_base_id is not None
            assert kb.owner_id is not None  
            assert kb.created_at is not None
            assert kb.updated_at is not None
            kb_responses.append(KnowledgeBaseResponse(
                knowledge_base_id=kb.knowledge_base_id,
                name=kb.name,
                description=kb.description,
                owner_id=kb.owner_id,
                config=kb.config or {},
                is_active=kb.is_active,
                document_count=kb.document_count,
                chunk_count=kb.chunk_count,
                created_at=kb.created_at,
                updated_at=kb.updated_at
            ))
        
        return KnowledgeBaseListResponse(
            knowledge_bases=kb_responses,
            total=len(kb_responses)
        )
        
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"获取知识库列表失败: {str(e)}")


@router.get("/knowledge-bases/{knowledge_base_id}", response_model=KnowledgeBaseResponse)
async def get_knowledge_base(
    knowledge_base_id: str,
    service: KnowledgeApplicationService = Depends(get_knowledge_service),
    current_user_id: str = Depends(get_current_user_id)
):
    """获取知识库详情"""
    try:
        knowledge_base = await service.get_knowledge_base(knowledge_base_id)
        if not knowledge_base:
            raise HTTPException(status_code=404, detail="知识库不存在")
        
        # TODO: 验证用户权限
        return knowledge_base
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取知识库详情失败: {str(e)}")


@router.get("/knowledge-bases/{knowledge_base_id}/overview", response_model=KnowledgeBaseOverviewResponse)
async def get_knowledge_base_overview(
    knowledge_base_id: str,
    service: KnowledgeApplicationService = Depends(get_knowledge_service),
    current_user_id: str = Depends(get_current_user_id)
):
    """获取知识库概览"""
    try:
        return await service.get_knowledge_base_overview(knowledge_base_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取知识库概览失败: {str(e)}")


@router.put("/knowledge-bases/{knowledge_base_id}/config", response_model=WorkflowConfigResponse)
async def update_workflow_config(
    knowledge_base_id: str,
    config_request: WorkflowConfigRequest,
    service: KnowledgeApplicationService = Depends(get_knowledge_service),
    current_user_id: str = Depends(get_current_user_id)
):
    """更新工作流配置"""
    try:
        return await service.update_workflow_config(knowledge_base_id, config_request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新配置失败: {str(e)}")


@router.post("/knowledge-bases/{knowledge_base_id}/files", response_model=FileUploadResponse)
async def upload_file(
    knowledge_base_id: str,
    file: UploadFile = File(...),
    service: KnowledgeApplicationService = Depends(get_knowledge_service),
    current_user_id: str = Depends(get_current_user_id)
):
    """上传单个文件"""
    try:
        # TODO: 验证用户对知识库的权限
        return await service.upload_file(knowledge_base_id, file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")


@router.post("/knowledge-bases/{knowledge_base_id}/files/batch", response_model=FileUploadBatchResponse)
async def upload_files_batch(
    knowledge_base_id: str,
    files: List[UploadFile] = File(...),
    service: KnowledgeApplicationService = Depends(get_knowledge_service),
    current_user_id: str = Depends(get_current_user_id)
):
    """批量上传文件"""
    try:
        # TODO: 验证用户对知识库的权限
        return await service.upload_files_batch(knowledge_base_id, files)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量文件上传失败: {str(e)}")


@router.get("/knowledge-bases/{knowledge_base_id}/files", response_model=FileListBatchResponse)
async def list_files(
    knowledge_base_id: str,
    service: KnowledgeApplicationService = Depends(get_knowledge_service),
    current_user_id: str = Depends(get_current_user_id)
):
    """获取文件列表"""
    try:
        # TODO: 验证用户对知识库的权限
        return await service.list_files(knowledge_base_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文件列表失败: {str(e)}")


@router.delete("/knowledge-bases/{knowledge_base_id}")
async def delete_knowledge_base(
    knowledge_base_id: str,
    service: KnowledgeApplicationService = Depends(get_knowledge_service),
    current_user_id: str = Depends(get_current_user_id)
):
    """删除知识库"""
    try:
        # TODO: 验证用户对知识库的权限
        success = await service.delete_knowledge_base(knowledge_base_id)
        if not success:
            raise HTTPException(status_code=404, detail="知识库不存在")
        
        return {"message": "知识库删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除知识库失败: {str(e)}")


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