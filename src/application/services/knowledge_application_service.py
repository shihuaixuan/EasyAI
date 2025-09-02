"""
知识库应用服务
"""

import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import UploadFile
from ..dto.knowledge_base_dto import (
    KnowledgeBaseCreateRequest,
    KnowledgeBaseResponse,
    KnowledgeBaseListResponse,
    KnowledgeBaseOverviewResponse
)
from ..dto.file_upload_dto import (
    FileUploadResponse,
    FileUploadBatchResponse,
    FileListBatchResponse,
    FileListResponse
)
from ..dto.workflow_dto import (
    WorkflowConfigRequest,
    WorkflowConfigResponse
)
from ...domain.knowledge.entities.knowledge_base import KnowledgeBase
from ...domain.knowledge.entities.document import Document
from ...domain.knowledge.repositories.knowledge_base_repository import KnowledgeBaseRepository
from ...domain.knowledge.repositories.document_repository import DocumentRepository
from ...domain.knowledge.services.knowledge_base_domain_service import KnowledgeBaseDomainService
from ...domain.knowledge.services.file_upload_service import FileUploadService, UploadedFile
from ...domain.knowledge.services.document_parser_service import DocumentParserService
from ...domain.knowledge.services.chunking.document_chunking_service import DocumentChunkingService
from ...domain.knowledge.repositories.document_chunk_repository import DocumentChunkRepository
from ...domain.knowledge.vo.workflow_config import FileUploadConfig
from ...domain.knowledge.vo.chunking_config import ChunkingConfig, TextPreprocessingConfig


class KnowledgeApplicationService:
    """知识库应用服务"""
    
    def __init__(
        self,
        knowledge_base_domain_service: KnowledgeBaseDomainService,
        file_upload_service: FileUploadService,
        document_parser_service: DocumentParserService,
        document_chunking_service: DocumentChunkingService,
        knowledge_base_repo: KnowledgeBaseRepository,
        document_repo: DocumentRepository,
        document_chunk_repo: DocumentChunkRepository
    ):
        self.knowledge_base_domain_service = knowledge_base_domain_service
        self.file_upload_service = file_upload_service
        self.document_parser_service = document_parser_service
        self.document_chunking_service = document_chunking_service
        self.knowledge_base_repo = knowledge_base_repo
        self.document_repo = document_repo
        self.document_chunk_repo = document_chunk_repo
    
    async def create_knowledge_base(
        self, 
        request: KnowledgeBaseCreateRequest, 
        owner_id: str
    ) -> KnowledgeBaseResponse:
        """创建知识库"""
        knowledge_base = await self.knowledge_base_domain_service.create_knowledge_base(
            name=request.name,
            description=request.description,
            owner_id=owner_id,
            config=request.config
        )
        
        return self._to_knowledge_base_response(knowledge_base)
    
    async def get_knowledge_base(self, knowledge_base_id: str) -> Optional[KnowledgeBaseResponse]:
        """获取知识库详情"""
        knowledge_base = await self.knowledge_base_repo.find_by_id(knowledge_base_id)
        if not knowledge_base:
            return None
        
        return self._to_knowledge_base_response(knowledge_base)
    
    async def list_knowledge_bases(self, owner_id: str) -> KnowledgeBaseListResponse:
        """获取用户的知识库列表"""
        knowledge_bases = await self.knowledge_base_repo.find_active_by_owner_id(owner_id)
        
        responses = [self._to_knowledge_base_response(kb) for kb in knowledge_bases]
        
        return KnowledgeBaseListResponse(
            knowledge_bases=responses,
            total=len(responses)
        )
    
    async def get_knowledge_base_overview(
        self, 
        knowledge_base_id: str
    ) -> KnowledgeBaseOverviewResponse:
        """获取知识库概览"""
        overview = await self.knowledge_base_domain_service.get_knowledge_base_overview(
            knowledge_base_id
        )
        
        return KnowledgeBaseOverviewResponse(
            knowledge_base=self._to_knowledge_base_response(overview["knowledge_base"]),
            document_count=overview["document_count"],
            chunk_count=overview["chunk_count"],
            recent_documents=[self._document_to_dict(doc) for doc in overview["recent_documents"]],
            file_types=overview["file_types"],
            total_size=overview["total_size"]
        )
    
    async def update_workflow_config(
        self, 
        knowledge_base_id: str, 
        config_request: WorkflowConfigRequest
    ) -> WorkflowConfigResponse:
        """更新工作流配置"""
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
                    "remove_emails": config_request.chunking.remove_emails  # 新增字段
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
        
        knowledge_base = await self.knowledge_base_domain_service.update_knowledge_base_config(
            knowledge_base_id, config_dict
        )
        
        # 触发文档重新分块处理
        await self.process_documents_chunking(knowledge_base_id, config_dict["chunking"])
        
        return WorkflowConfigResponse(
            knowledge_base_id=knowledge_base_id,
            config=knowledge_base.config or {},
            updated_at=knowledge_base.updated_at or datetime.now()
        )
    
    async def upload_file(
        self, 
        knowledge_base_id: str, 
        file: UploadFile
    ) -> FileUploadResponse:
        """上传单个文件"""
        try:
            # 检查文件名是否为空
            if not file.filename:
                return FileUploadResponse(
                    success=False,
                    filename="unknown",
                    error_message="文件名不能为空"
                )
            
            # 读取文件内容
            content: bytes = await file.read()
            
            # 创建上传文件对象
            uploaded_file = UploadedFile(
                filename=file.filename,
                content=content,
                content_type=file.content_type or "application/octet-stream",
                size=len(content)
            )
            
            # 保存文件
            upload_result = await self.file_upload_service.save_file(
                uploaded_file, knowledge_base_id
            )
            
            if not upload_result.success or not upload_result.file_path:
                return FileUploadResponse(
                    success=False,
                    filename=file.filename or "unknown",
                    error_message=upload_result.error_message or "文件上传失败"
                )
            
            # 解析文档
            try:
                document = await self.document_parser_service.parse_document(
                    upload_result.file_path,
                    upload_result.filename or file.filename or "unknown",
                    knowledge_base_id
                )
                
                # 添加到知识库
                document.original_path = upload_result.file_path
                if upload_result.file_size is not None:
                    document.file_size = upload_result.file_size
                document.content_hash = upload_result.content_hash
                
                saved_document = await self.knowledge_base_domain_service.add_document_to_knowledge_base(
                    knowledge_base_id, document
                )
                
                return FileUploadResponse(
                    success=True,
                    filename=file.filename or "unknown",
                    file_path=upload_result.file_path,
                    document_id=saved_document.document_id,
                    file_size=upload_result.file_size,
                    content_hash=upload_result.content_hash,
                    created_at=saved_document.created_at
                )
                
            except Exception as parse_error:
                # 解析失败，删除已上传的文件
                if upload_result.file_path:
                    await self.file_upload_service.delete_file(upload_result.file_path)
                
                return FileUploadResponse(
                    success=False,
                    filename=file.filename or "unknown",
                    error_message=f"文档解析失败: {str(parse_error)}"
                )
            
        except Exception as e:
            return FileUploadResponse(
                success=False,
                filename=file.filename or "unknown",
                error_message=f"文件上传失败: {str(e)}"
            )
    
    async def upload_files_batch(
        self, 
        knowledge_base_id: str, 
        files: List[UploadFile]
    ) -> FileUploadBatchResponse:
        """批量上传文件"""
        successful_uploads = []
        failed_uploads = []
        
        for file in files:
            result = await self.upload_file(knowledge_base_id, file)
            
            if result.success:
                successful_uploads.append(result)
            else:
                failed_uploads.append(result)
        
        return FileUploadBatchResponse(
            total_files=len(files),
            successful_uploads=successful_uploads,
            failed_uploads=failed_uploads,
            success_count=len(successful_uploads),
            error_count=len(failed_uploads)
        )
    
    async def list_files(self, knowledge_base_id: str) -> FileListBatchResponse:
        """获取知识库文件列表"""
        documents = await self.document_repo.find_by_knowledge_base_id(knowledge_base_id)
        
        file_responses = []
        for doc in documents:
            file_responses.append(FileListResponse(
                document_id=doc.document_id or "",
                filename=doc.filename,
                file_type=doc.file_type,
                file_size=doc.file_size,
                is_processed=doc.is_processed,
                chunk_count=doc.chunk_count,
                created_at=doc.created_at or datetime.now(),
                processed_at=doc.processed_at
            ))
        
        return FileListBatchResponse(
            knowledge_base_id=knowledge_base_id,
            files=file_responses,
            total=len(file_responses)
        )
    
    async def delete_knowledge_base(self, knowledge_base_id: str) -> bool:
        """删除知识库"""
        return await self.knowledge_base_domain_service.delete_knowledge_base(knowledge_base_id)
    
    def _to_knowledge_base_response(self, knowledge_base: KnowledgeBase) -> KnowledgeBaseResponse:
        """转换为知识库响应对象"""
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
    
    def _document_to_dict(self, document: Document) -> Dict[str, Any]:
        """转换文档为字典"""
        return {
            "document_id": document.document_id,
            "filename": document.filename,
            "file_type": document.file_type,
            "file_size": document.file_size,
            "is_processed": document.is_processed,
            "chunk_count": document.chunk_count,
            "created_at": document.created_at.isoformat() if document.created_at else None
        }
    
    async def process_documents_chunking(
        self, 
        knowledge_base_id: str, 
        chunking_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        对知识库中的所有文档进行分块处理
        
        Args:
            knowledge_base_id: 知识库ID
            chunking_config: 分块配置
            
        Returns:
            处理结果统计
        """
        try:
            # 获取知识库中的所有文档
            documents = await self.document_repo.find_by_knowledge_base_id(knowledge_base_id)
            
            if not documents:
                return {"processed_documents": 0, "total_chunks": 0, "message": "没有找到文档"}
            
            # 创建分块配置对象
            config = ChunkingConfig.from_dict(chunking_config)
            
            total_chunks = 0
            processed_documents = 0
            
            for document in documents:
                try:
                    # 清理旧的分块
                    await self.document_chunk_repo.delete_by_document_id(document.document_id or "")
                    
                    # 进行新的分块处理
                    chunks = await self.document_chunking_service.chunk_document(document, config)
                    
                    # 保存分块
                    if chunks:
                        await self.document_chunk_repo.save_batch(chunks)
                        total_chunks += len(chunks)
                    
                    # 更新文档的分块统计
                    document.chunk_count = len(chunks)
                    document.mark_as_processed(len(chunks))
                    await self.document_repo.update(document)
                    
                    processed_documents += 1
                    
                except Exception as e:
                    print(f"处理文档 {document.filename} 时出错: {str(e)}")
                    continue
            
            return {
                "processed_documents": processed_documents,
                "total_chunks": total_chunks,
                "message": f"成功处理 {processed_documents} 个文档，生成 {total_chunks} 个分块"
            }
            
        except Exception as e:
            return {
                "processed_documents": 0,
                "total_chunks": 0,
                "error": f"分块处理失败: {str(e)}"
            }