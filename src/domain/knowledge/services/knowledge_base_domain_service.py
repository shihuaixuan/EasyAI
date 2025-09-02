"""
知识库领域服务
"""

from typing import List, Optional, Dict, Any
from ..entities.knowledge_base import KnowledgeBase
from ..entities.document import Document
from ..repositories.knowledge_base_repository import KnowledgeBaseRepository
from ..repositories.document_repository import DocumentRepository
from ..repositories.document_chunk_repository import DocumentChunkRepository


class KnowledgeBaseDomainService:
    """知识库领域服务"""
    
    def __init__(
        self,
        knowledge_base_repo: KnowledgeBaseRepository,
        document_repo: DocumentRepository,
        chunk_repo: DocumentChunkRepository
    ):
        self.knowledge_base_repo = knowledge_base_repo
        self.document_repo = document_repo
        self.chunk_repo = chunk_repo
    
    async def create_knowledge_base(
        self, 
        name: str, 
        description: str, 
        owner_id: str,
        config: Optional[Dict[str, Any]] = None
    ) -> KnowledgeBase:
        """创建知识库
        
        Args:
            name: 知识库名称
            description: 知识库描述
            owner_id: 所有者ID
            config: 配置信息
            
        Returns:
            创建的知识库对象
            
        Raises:
            ValueError: 名称重复或其他验证错误
        """
        # 检查名称是否重复
        if await self.knowledge_base_repo.exists_by_name_and_owner(name, owner_id):
            raise ValueError(f"知识库名称 '{name}' 已存在")
        
        # 验证名称
        if not name or not name.strip():
            raise ValueError("知识库名称不能为空")
        
        if len(name.strip()) > 100:
            raise ValueError("知识库名称不能超过100个字符")
        
        # 创建知识库
        knowledge_base = KnowledgeBase(
            name=name.strip(),
            description=description.strip() if description else "",
            owner_id=owner_id,
            config=config or {}
        )
        
        return await self.knowledge_base_repo.save(knowledge_base)
    
    async def update_knowledge_base_config(
        self, 
        knowledge_base_id: str, 
        config: Dict[str, Any]
    ) -> KnowledgeBase:
        """更新知识库配置
        
        Args:
            knowledge_base_id: 知识库ID
            config: 新的配置信息
            
        Returns:
            更新后的知识库对象
            
        Raises:
            ValueError: 知识库不存在
        """
        knowledge_base = await self.knowledge_base_repo.find_by_id(knowledge_base_id)
        if not knowledge_base:
            raise ValueError(f"知识库不存在: {knowledge_base_id}")
        
        knowledge_base.update_config(config)
        return await self.knowledge_base_repo.update(knowledge_base)
    
    async def update_knowledge_base_statistics(self, knowledge_base_id: str) -> KnowledgeBase:
        """更新知识库统计信息
        
        Args:
            knowledge_base_id: 知识库ID
            
        Returns:
            更新后的知识库对象
        """
        knowledge_base = await self.knowledge_base_repo.find_by_id(knowledge_base_id)
        if not knowledge_base:
            raise ValueError(f"知识库不存在: {knowledge_base_id}")
        
        # 统计文档和块的数量
        document_count = await self.document_repo.count_by_knowledge_base_id(knowledge_base_id)
        chunk_count = await self.chunk_repo.count_by_knowledge_base_id(knowledge_base_id)
        
        knowledge_base.update_statistics(document_count, chunk_count)
        return await self.knowledge_base_repo.update(knowledge_base)
    
    async def delete_knowledge_base(self, knowledge_base_id: str) -> bool:
        """删除知识库及其所有相关数据
        
        Args:
            knowledge_base_id: 知识库ID
            
        Returns:
            是否删除成功
        """
        knowledge_base = await self.knowledge_base_repo.find_by_id(knowledge_base_id)
        if not knowledge_base:
            return False
        
        # 删除所有文档块
        await self.chunk_repo.delete_by_knowledge_base_id(knowledge_base_id)
        
        # 删除所有文档
        await self.document_repo.delete_by_knowledge_base_id(knowledge_base_id)
        
        # 删除知识库
        return await self.knowledge_base_repo.delete_by_id(knowledge_base_id)
    
    async def add_document_to_knowledge_base(
        self, 
        knowledge_base_id: str, 
        document: Document
    ) -> Document:
        """添加文档到知识库
        
        Args:
            knowledge_base_id: 知识库ID
            document: 文档对象
            
        Returns:
            保存后的文档对象
            
        Raises:
            ValueError: 知识库不存在或文档重复
        """
        # 检查知识库是否存在
        knowledge_base = await self.knowledge_base_repo.find_by_id(knowledge_base_id)
        if not knowledge_base:
            raise ValueError(f"知识库不存在: {knowledge_base_id}")
        
        # 检查文档是否重复（基于内容哈希）
        if document.content_hash:
            existing_doc = await self.document_repo.find_by_content_hash(
                document.content_hash, knowledge_base_id
            )
            if existing_doc:
                raise ValueError(f"文档内容重复: {document.filename}")
        
        # 设置知识库ID
        document.knowledge_base_id = knowledge_base_id
        
        # 保存文档
        saved_document = await self.document_repo.save(document)
        
        # 更新知识库统计信息
        await self.update_knowledge_base_statistics(knowledge_base_id)
        
        return saved_document
    
    async def get_knowledge_base_overview(self, knowledge_base_id: str) -> Dict[str, Any]:
        """获取知识库概览信息
        
        Args:
            knowledge_base_id: 知识库ID
            
        Returns:
            知识库概览信息
        """
        knowledge_base = await self.knowledge_base_repo.find_by_id(knowledge_base_id)
        if not knowledge_base:
            raise ValueError(f"知识库不存在: {knowledge_base_id}")
        
        documents = await self.document_repo.find_by_knowledge_base_id(knowledge_base_id)
        
        return {
            "knowledge_base": knowledge_base,
            "document_count": len(documents),
            "chunk_count": knowledge_base.chunk_count,
            "recent_documents": documents[:5],  # 最近5个文档
            "file_types": list(set(doc.file_type for doc in documents)),
            "total_size": sum(doc.file_size for doc in documents)
        }