"""
知识库应用服务
"""

import os
import asyncio
from src.domain.knowledge.entities.document_chunk import DocumentChunk
from src.domain.knowledge.entities.knowledge_base import KnowledgeBase
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
from ...domain.knowledge.entities.document_chunk import DocumentChunk
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
        try:
            # 验证知识库是否存在
            knowledge_base = await self.knowledge_base_repo.find_by_id(knowledge_base_id)
            if not knowledge_base:
                raise ValueError(f"知识库不存在: {knowledge_base_id}")
            
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
            
            # 更新配置（使用改进后的方法）
            updated_knowledge_base = await self.knowledge_base_domain_service.update_knowledge_base_config(
                knowledge_base_id, config_dict
            )
            
            # 验证配置更新是否成功
            if not updated_knowledge_base.config:
                raise ValueError("配置更新失败：数据库中没有保存配置")
            
            # 记录配置更新成功
            print(f"配置更新成功：知识库 {knowledge_base_id}, 新配置: {config_dict}")
            
            # 异步触发文档分块处理（不阻塞配置更新）
            try:
                # 检查是否有未处理的文件（从文件系统扫描）
                upload_dir = f"uploads/{knowledge_base_id}"
                if os.path.exists(upload_dir):
                    uploaded_files = [f for f in os.listdir(upload_dir) if os.path.isfile(os.path.join(upload_dir, f))]
                    if uploaded_files:
                        print(f"开始处理 {len(uploaded_files)} 个未处理的文件")
                        # 异步处理所有未处理的文件
                        import asyncio
                        asyncio.create_task(self._process_unprocessed_documents_async(
                            knowledge_base_id, config_dict
                        ))
                    else:
                        print(f"知识库 {knowledge_base_id} 没有未处理的文件")
                else:
                    print(f"知识库 {knowledge_base_id} 的上传目录不存在")
            except Exception as process_error:
                # 文档处理失败不影响配置更新的成功
                print(f"警告：文档处理失败 - {str(process_error)}")
            
            # 返回响应
            return WorkflowConfigResponse(
                knowledge_base_id=knowledge_base_id,
                config=updated_knowledge_base.config,
                updated_at=updated_knowledge_base.updated_at or datetime.now()
            )
            
        except ValueError as ve:
            raise ve
        except Exception as e:
            raise ValueError(f"更新工作流配置失败: {str(e)}")
    
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
            
            # 解析文档（但不保存到数据库）
            try:
                document = await self.document_parser_service.parse_document(
                    upload_result.file_path,
                    upload_result.filename or file.filename or "unknown",
                    knowledge_base_id
                )
                
                # 设置文档属性（但不保存到数据库）
                document.original_path = upload_result.file_path
                if upload_result.file_size is not None:
                    document.file_size = upload_result.file_size
                document.content_hash = upload_result.content_hash
                
                # 注意：此时不保存文档到数据库，只保留文件和基本信息
                # 文档将在用户点击"开始分块"时与分块数据一起保存到数据库
                
                return FileUploadResponse(
                    success=True,
                    filename=file.filename or "unknown",
                    file_path=upload_result.file_path,
                    document_id=None,  # 此时还没有数据库ID
                    file_size=upload_result.file_size,
                    content_hash=upload_result.content_hash,
                    created_at=None,  # 此时还没有创建时间
                    chunk_count=0  # 初始上传时没有分块
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
        
        # 逐个处理文件，每个文件在独立事务中处理
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
    
    async def start_knowledge_processing(
        self, 
        knowledge_base_id: str
    ) -> Dict[str, Any]:
        """开始知识库处理流程（从文件系统读取文件）"""
        try:
            # 1. 获取知识库和配置（在事务开始前验证）
            knowledge_base: KnowledgeBase | None = await self.knowledge_base_repo.find_by_id(knowledge_base_id)
            if not knowledge_base:
                raise ValueError(f"知识库不存在: {knowledge_base_id}")
            
            if not knowledge_base.config:
                raise ValueError("知识库配置为空，请先配置工作流参数")
            
            # 2. 从文件系统扫描未处理的文件
            upload_dir = f"uploads/{knowledge_base_id}"
            if not os.path.exists(upload_dir):
                return {
                    "success": True,
                    "message": "没有找到需要处理的文件",
                    "processed_documents": 0,
                    "total_chunks": 0
                }
            
            uploaded_files = []
            for filename in os.listdir(upload_dir):
                file_path = os.path.join(upload_dir, filename)
                if os.path.isfile(file_path):
                    uploaded_files.append({
                        'filename': filename,
                        'file_path': file_path,
                        'file_size': os.path.getsize(file_path)
                    })
            
            if not uploaded_files:
                return {
                    "success": True,
                    "message": "没有找到需要处理的文件",
                    "processed_documents": 0,
                    "total_chunks": 0
                }
            
            # 3. 开始处理流程 - 每个文件在独立的子事务中处理
            total_chunks = 0
            processed_documents = 0
            failed_documents = []
            
            chunking_config = knowledge_base.config.get('chunking', {})
            
            for file_info in uploaded_files:
                try:
                    # 解析文档
                    document = await self.document_parser_service.parse_document(
                        file_info['file_path'],
                        file_info['filename'],
                        knowledge_base_id
                    )
                    
                    # 设置文档属性
                    document.original_path = file_info['file_path']
                    document.file_size = file_info['file_size']
                    
                    # 计算文件哈希
                    import hashlib
                    with open(file_info['file_path'], 'rb') as f:
                        content = f.read()
                        document.content_hash = hashlib.sha256(content).hexdigest()
                    
                    # 在同一事务中保存文档和分块
                    saved_document, chunks_count = await self._save_document_and_chunks_in_transaction(
                        knowledge_base_id, document, chunking_config, file_info['file_path']
                    )
                    
                    total_chunks += chunks_count
                    processed_documents += 1
                    
                    # 启动异步embedding处理任务（不阻塞主流程）
                    if saved_document.document_id:
                        asyncio.create_task(self._process_document_embeddings_async(
                            knowledge_base_id, saved_document.document_id, knowledge_base.owner_id or "default_user"
                        ))
                    
                except Exception as e:
                    print(f"处理文件 {file_info['filename']} 失败: {str(e)}")
                    failed_documents.append({
                        "filename": file_info['filename'],
                        "error": str(e)
                    })
                    # 继续处理下一个文件，不中断整个流程
                    continue
            
            # 4. 更新知识库统计信息（在单独的操作中，避免事务冲突）
            try:
                await self.knowledge_base_domain_service.update_knowledge_base_statistics(knowledge_base_id)
            except Exception as stats_error:
                print(f"警告：更新知识库统计失败 - {str(stats_error)}")
                # 统计更新失败不影响主流程
            
            return {
                "success": True,
                "message": f"处理完成，共处理 {processed_documents} 个文档，生成 {total_chunks} 个文本块",
                "processed_documents": processed_documents,
                "total_chunks": total_chunks,
                "failed_documents": failed_documents
            }
            
        except ValueError as ve:
            # 验证错误，直接抛出
            raise ve
        except Exception as e:
            # 其他异常，包装后抛出
            raise Exception(f"处理流程失败: {str(e)}")
    
    async def _process_single_document(
        self, 
        document: Document, 
        config: Dict[str, Any]
    ) -> int:
        """处理单个文档（分块 + embedding + 存储）"""
        try:
            # 1. 获取文档内容
            content = await self._get_document_content(document)
            if not content:
                raise ValueError(f"无法获取文档内容: {document.filename}")
            
            # 2. 文本分块
            chunks = await self._chunk_document_content(
                content, config.get('chunking', {})
            )
            
            if not chunks:
                raise ValueError(f"文档分块失败: {document.filename}")
            
            # 3. 清理旧的分块数据
            await self.document_chunk_repo.delete_by_document_id(document.document_id or "")
            
            # 4. 生成向量并存储分块
            embedding_config = config.get('embedding', {})
            saved_chunks = await self._process_and_store_chunks(
                chunks, document, embedding_config
            )
            
            return len(saved_chunks)
            
        except Exception as e:
            raise Exception(f"处理文档 {document.filename} 失败: {str(e)}")
    
    async def _get_document_content(self, document: Document) -> str:
        """获取文档内容"""
        try:
            # 从文件路径读取内容
            if document.file_path and os.path.exists(document.file_path):
                with open(document.file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                # 如果文件不存在，尝试从数据库中获取
                return document.content or ""
        except Exception as e:
            raise Exception(f"读取文档内容失败: {str(e)}")
    
    async def _chunk_document_content(
        self, 
        content: str, 
        chunking_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """对文档内容进行分块"""
        try:
            # 创建分块配置对象
            config = ChunkingConfig.from_dict(chunking_config)
            
            # 使用分块服务进行分块
            chunks_result = await self.document_chunking_service.chunk_text(content, config)
            
            # 转换为统一格式
            chunks = []
            for i, chunk_text in enumerate(chunks_result.chunks):
                chunks.append({
                    "content": chunk_text,
                    "chunk_index": i,
                    "start_index": 0,  # 简化处理
                    "end_index": len(chunk_text),
                    "metadata": {
                        "chunk_method": config.strategy,
                        "chunk_size": len(chunk_text)
                    }
                })
            
            return chunks
            
        except Exception as e:
            raise Exception(f"文档分块失败: {str(e)}")
    
    async def _process_and_store_chunks(
        self, 
        chunks: List[Dict[str, Any]], 
        document: Document,
        embedding_config: Dict[str, Any],
        knowledge_base: Any = None,
        user_id: str = "default_user"
    ) -> List[DocumentChunk]:
        """处理并存储文本块（包括生成向量）"""
        
        saved_chunks = []
        
        # 初始化embedding服务（如果需要）
        embedding_service = None
        if embedding_config.get('strategy') == 'high_quality':
            # 使用传入的配置创建embedding服务
            embedding_service = await self._create_embedding_service(embedding_config)
        
        for chunk_data in chunks:
            try:
                # 创建文本块实体
                chunk = DocumentChunk(
                    content=chunk_data["content"],
                    chunk_index=chunk_data["chunk_index"],
                    start_offset=chunk_data["start_index"],
                    document_id=document.document_id or "",
                    knowledge_base_id=document.knowledge_base_id,
                    end_offset=chunk_data["end_index"],
                    metadata=chunk_data["metadata"]
                )
                
                # 生成向量（如果需要）
                if embedding_service:
                    try:
                        embedding = await embedding_service.embed_text(chunk_data["content"])
                        chunk.set_vector(embedding)
                    except Exception as e:
                        print(f"警告: 生成向量失败 {str(e)}, 继续保存文本块")
                
                # 保存文本块
                saved_chunk = await self.document_chunk_repo.save(chunk)
                saved_chunks.append(saved_chunk)
                
            except Exception as e:
                print(f"警告: 处理文本块失败 {str(e)}, 跳过该块")
                continue
        
        # 清理embedding服务
        if embedding_service:
            try:
                # 检查embedding服务是否有close方法
                if hasattr(embedding_service, 'close') and callable(getattr(embedding_service, 'close')):
                    close_method = getattr(embedding_service, 'close')
                    if asyncio.iscoroutinefunction(close_method):
                        await close_method()
                    else:
                        close_method()
            except Exception as close_error:
                print(f"警告：关闭embedding服务失败 - {str(close_error)}")
        
        return saved_chunks
    
    async def _create_embedding_service(self, embedding_config: Dict[str, Any]):
        """创建embedding服务"""
        try:
            from ...domain.model.services.embedding.factory import create_embedding
            
            # 获取配置信息
            model_name = embedding_config.get('model_name', 'BAAI/bge-large-zh-v1.5')
            provider = embedding_config.get('provider', 'siliconflow')
            api_key = embedding_config.get('api_key')
            base_url = embedding_config.get('base_url')
            
            # 构建配置
            config = {
                'model_name': model_name,
                'batch_size': embedding_config.get('batch_size', 32),
                'max_tokens': embedding_config.get('max_tokens', 8192),
                'timeout': embedding_config.get('timeout', 30),
            }
            
            # 根据提供商添加特定配置
            if provider == 'local':
                config.update({
                    'model_path': embedding_config.get('model_path', '/opt/embedding/bge-m3'),
                    'normalize_embeddings': embedding_config.get('normalize_embeddings', True)
                })
            else:
                # 远程API提供商
                config.update({
                    'api_key': api_key or os.getenv(f'{provider.upper()}_API_KEY'),
                    'base_url': base_url or self._get_default_base_url(provider)
                })
            
            print(f"创建embedding服务: provider={provider}, model={model_name}")
            embedding_service = create_embedding(provider, config)
            return embedding_service
            
        except Exception as e:
            raise Exception(f"创建embedding服务失败: {str(e)}")
    
    def _get_default_base_url(self, provider: str) -> str:
        """获取提供商的默认base_url"""
        default_urls = {
            'siliconflow': 'https://api.siliconflow.cn/v1',
            'openai': 'https://api.openai.com/v1',
            'anthropic': 'https://api.anthropic.com',
        }
        return default_urls.get(provider, 'https://api.siliconflow.cn/v1')
    
    async def _process_document_embeddings_async(
        self, 
        knowledge_base_id: str, 
        document_id: str,
        user_id: str
    ) -> None:
        """
        异步处理文档的embedding（允许失败）
        
        Args:
            knowledge_base_id: 知识库ID
            document_id: 文档ID
            user_id: 用户ID
        """
        try:
            print(f"开始异步处理文档 {document_id} 的embedding...")
            
            # 使用新的DDD架构的embedding应用服务
            from ...infrastructure.database import get_async_session
            from .embedding_application_service import create_embedding_application_service
            
            async with get_async_session() as session:
                embedding_app_service = await create_embedding_application_service(session)
                result = await embedding_app_service.process_document_embeddings(
                    knowledge_base_id, document_id, user_id
                )
                
                if result.success:
                    print(f"文档 {document_id} embedding处理成功: {result.message}")
                else:
                    print(f"文档 {document_id} embedding处理失败: {result.message}")
                
        except Exception as e:
            print(f"异步embedding处理出错: {str(e)}")
            # 不抛出异常，允许失败
    
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
    
    async def _save_document_and_chunks_in_transaction(
        self, 
        knowledge_base_id: str, 
        document: Document,
        chunking_config: Dict[str, Any],
        file_path: Optional[str] = None
    ) -> tuple[Document, int]:
        """
        在同一事务中保存文档和分块
        
        Args:
            knowledge_base_id: 知识库ID
            document: 文档对象
            chunking_config: 分块配置
            file_path: 文件路径（用于直接读取文件内容）
            
        Returns:
            tuple[Document, int]: 保存的文档和分块数量
        """
        try:
            # 1. 保存文档到数据库
            saved_document = await self.document_repo.save(document)
            
            # 2. 获取文档内容进行分块
            content = ""
            if file_path and os.path.exists(file_path):
                # 从文件读取内容
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    # 如果 UTF-8 解码失败，尝试其他编码
                    try:
                        with open(file_path, 'r', encoding='gbk') as f:
                            content = f.read()
                    except UnicodeDecodeError:
                        with open(file_path, 'r', encoding='latin-1') as f:
                            content = f.read()
            else:
                # 如果没有文件路径，使用文档对象中的内容
                content = saved_document.content or ""
            
            if not content.strip():
                print(f"警告：文档 {document.filename} 内容为空，跳过分块处理")
                return saved_document, 0
            
            # 3. 进行文档分块
            chunks = await self._chunk_document_content(content, chunking_config)
            
            # 4. 保存分块（不包含向量）
            document_chunks = []
            for chunk_data in chunks:
                chunk = DocumentChunk(
                    content=chunk_data["content"],
                    chunk_index=chunk_data["chunk_index"],
                    start_offset=chunk_data["start_index"],
                    document_id=saved_document.document_id or "",
                    knowledge_base_id=knowledge_base_id,
                    end_offset=chunk_data["end_index"],
                    metadata=chunk_data["metadata"]
                )
                document_chunks.append(chunk)
            
            # 5. 批量保存分块
            if document_chunks:
                saved_chunks: List[DocumentChunk] = await self.document_chunk_repo.save_batch(document_chunks)
                chunks_count: int = len(saved_chunks)
            else:
                chunks_count = 0
            
            # 6. 更新文档的分块统计
            saved_document.mark_as_processed(chunk_count=chunks_count)
            await self.document_repo.update(saved_document)
            
            # 7. 注意：事务提交由调用方处理
            
            return saved_document, chunks_count
            
        except Exception as e:
            raise Exception(f"保存文档和分块失败: {str(e)}")
    
    async def _process_unprocessed_documents_async(
        self, 
        knowledge_base_id: str, 
        config: Dict[str, Any]
    ) -> None:
        """
        异步处理未处理的文档（从文件系统读取文件，文档落库+分块在同一事务中）
        
        Args:
            knowledge_base_id: 知识库ID
            config: 完整的工作流配置
        """
        try:
            print(f"开始异步处理知识库 {knowledge_base_id} 的文件...")
            
            # 1. 从文件系统扫描未处理的文件
            upload_dir = f"uploads/{knowledge_base_id}"
            if not os.path.exists(upload_dir):
                print(f"上传目录不存在: {upload_dir}")
                return
            
            # 获取已上传的文件列表
            uploaded_files = []
            for filename in os.listdir(upload_dir):
                file_path = os.path.join(upload_dir, filename)
                if os.path.isfile(file_path):
                    uploaded_files.append({
                        'filename': filename,
                        'file_path': file_path,
                        'file_size': os.path.getsize(file_path)
                    })
            
            if not uploaded_files:
                print(f"知识库 {knowledge_base_id} 没有未处理的文件")
                return
            
            print(f"发现 {len(uploaded_files)} 个未处理的文件")
            
            # 2. 提取分块和嵌入配置
            chunking_config = config.get('chunking', {})
            embedding_config = config.get('embedding', {})
            
            # 3. 处理每个文件（文档落库+分块在同一事务中）
            total_chunks = 0
            processed_count = 0
            failed_count = 0
            
            for file_info in uploaded_files:
                try:
                    print(f"处理文件: {file_info['filename']}")
                    
                    # 解析文档
                    document = await self.document_parser_service.parse_document(
                        file_info['file_path'],
                        file_info['filename'],
                        knowledge_base_id
                    )
                    
                    # 设置文档属性
                    document.original_path = file_info['file_path']
                    document.file_size = file_info['file_size']
                    
                    # 计算文件哈希
                    import hashlib
                    with open(file_info['file_path'], 'rb') as f:
                        content = f.read()
                        document.content_hash = hashlib.sha256(content).hexdigest()
                    
                    # 在同一事务中保存文档和分块
                    saved_document, chunks_count = await self._save_document_and_chunks_in_transaction(
                        knowledge_base_id, document, chunking_config, file_info['file_path']
                    )
                    
                    total_chunks += chunks_count
                    processed_count += 1
                    
                    print(f"文件 {file_info['filename']} 处理完成，生成 {chunks_count} 个分块")
                    
                    # 异步处理嵌入（如果配置了高质量嵌入）
                    if embedding_config.get('strategy') == 'high_quality':
                        import asyncio
                        asyncio.create_task(self._process_embeddings_async(
                            saved_document.document_id or "", knowledge_base_id
                        ))
                    
                except Exception as file_error:
                    print(f"处理文件 {file_info['filename']} 失败: {str(file_error)}")
                    failed_count += 1
                    # 继续处理下一个文件，而不是中断整个流程
                    continue
            
            # 4. 更新知识库统计
            try:
                await self.knowledge_base_domain_service.update_knowledge_base_statistics(knowledge_base_id)
            except Exception as stats_error:
                print(f"警告：更新知识库统计失败 - {str(stats_error)}")
            
            print(f"文档处理完成：成功 {processed_count} 个，失败 {failed_count} 个，总分块数 {total_chunks}")
            
        except Exception as e:
            print(f"异步文档处理失败: {str(e)}")
            # 注意：异步任务中的异常不会影响主流程，但需要确保不会导致事务问题
    
    async def _process_embeddings_async(
        self, 
        document_id: str, 
        knowledge_base_id: str
    ) -> None:
        """
        异步处理文档分块的embedding（允许失败）
        
        Args:
            document_id: 文档ID
            knowledge_base_id: 知识库ID
        """
        try:
            print(f"开始处理文档 {document_id} 的embedding...")
            
            # 1. 获取知识库配置
            knowledge_base = await self.knowledge_base_repo.find_by_id(knowledge_base_id)
            if not knowledge_base or not knowledge_base.config:
                print(f"警告：知识库 {knowledge_base_id} 没有配置，跳过embedding处理")
                return
            
            embedding_config = knowledge_base.config.get('embedding', {})
            if not embedding_config or embedding_config.get('strategy') != 'high_quality':
                print(f"警告：知识库 {knowledge_base_id} 没有启用高质量embedding，跳过处理")
                return
            
            # 2. 获取文档分块
            chunks = await self.document_chunk_repo.find_by_document_id(document_id)
            if not chunks:
                print(f"警告：文档 {document_id} 没有分块数据")
                return
            
            # 3. 创建 embedding 服务
            embedding_service = await self._create_embedding_service(embedding_config)
            if not embedding_service:
                print(f"警告：无法创建 embedding 服务")
                return
            
            # 4. 为每个分块生成向量
            success_count = 0
            failed_count = 0
            
            for chunk in chunks:
                try:
                    if chunk.vector:
                        continue  # 已经有向量了，跳过
                    
                    embedding = await embedding_service.embed_text(chunk.content)
                    chunk.set_vector(embedding)
                    await self.document_chunk_repo.update(chunk)
                    success_count += 1
                    
                except Exception as chunk_error:
                    print(f"警告：处理分块 {chunk.chunk_id} 的embedding失败: {str(chunk_error)}")
                    failed_count += 1
                    continue
            
            print(f"Embedding处理完成：成功 {success_count} 个，失败 {failed_count} 个")
            
            # 5. 清理 embedding 服务
            if embedding_service:
                try:
                    if hasattr(embedding_service, 'close') and callable(getattr(embedding_service, 'close')):
                        close_method = getattr(embedding_service, 'close')
                        if asyncio.iscoroutinefunction(close_method):
                            await close_method()
                        else:
                            close_method()
                except Exception as close_error:
                    print(f"警告：关闭embedding服务失败 - {str(close_error)}")
            
        except Exception as e:
            print(f"警告：Embedding异步处理失败: {str(e)}")
            # 不抛出异常，不影响主流程