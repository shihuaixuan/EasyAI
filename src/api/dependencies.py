"""
API依赖注入配置
"""

from ..application.services.knowledge_application_service import KnowledgeApplicationService
from ..infrastructure.repositories.knowledge_base_repository_impl import KnowledgeBaseRepositoryImpl
from ..infrastructure.repositories.document_repository_impl import DocumentRepositoryImpl
from ..infrastructure.repositories.document_chunk_repository_impl import DocumentChunkRepositoryImpl
from ..domain.knowledge.services.file_upload_service import FileUploadService
from ..domain.knowledge.services.document_parser_service import DocumentParserService, DocumentParserRegistry
from ..domain.knowledge.services.knowledge_base_domain_service import KnowledgeBaseDomainService
from ..domain.knowledge.vo.workflow_config import FileUploadConfig
from ..infrastructure.database import get_session
from ..infrastructure.parsers.document_parsers import TextDocumentParser, DefaultDocumentParser


# 全局服务实例（简单的单例模式）
_knowledge_service_instance = None


async def get_knowledge_service() -> KnowledgeApplicationService:
    """获取知识库应用服务"""
    global _knowledge_service_instance
    
    if _knowledge_service_instance is None:
        # 创建仓储实例
        session = await get_session()
        knowledge_base_repo = KnowledgeBaseRepositoryImpl(session)
        document_repo = DocumentRepositoryImpl(session)
        document_chunk_repo = DocumentChunkRepositoryImpl(session)
        
        # 创建领域服务实例
        file_upload_config = FileUploadConfig()
        file_upload_service = FileUploadService(file_upload_config)
        
        # 创建文档解析器注册表和服务
        parser_registry = DocumentParserRegistry()
        parser_registry.register(['.txt', '.md', '.mdx', '.csv', '.json', '.xml', '.html', '.htm'], TextDocumentParser)
        parser_registry.register(['.pdf', '.doc', '.docx', '.xlsx', '.xls', '.ppt', '.pptx'], DefaultDocumentParser)
        document_parser_service = DocumentParserService(parser_registry)
        
        # 创建领域服务
        knowledge_base_domain_service = KnowledgeBaseDomainService(
            knowledge_base_repo=knowledge_base_repo,
            document_repo=document_repo,
            chunk_repo=document_chunk_repo
        )
        
        # 创建应用服务实例
        _knowledge_service_instance = KnowledgeApplicationService(
            knowledge_base_domain_service=knowledge_base_domain_service,
            file_upload_service=file_upload_service,
            document_parser_service=document_parser_service,
            knowledge_base_repo=knowledge_base_repo,
            document_repo=document_repo
        )
    
    return _knowledge_service_instance


def get_current_user_id() -> str:
    """获取当前用户ID（临时实现）"""
    return "test_user"