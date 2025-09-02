"""
文档仓储内存实现（测试用）
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from ...domain.knowledge.entities.document import Document
from ...domain.knowledge.repositories.document_repository import DocumentRepository


class DocumentRepositoryImpl(DocumentRepository):
    """文档仓储内存实现"""
    
    def __init__(self, session=None):
        self.session = session
        self._storage: Dict[str, Document] = {}
    
    async def save(self, document: Document) -> Document:
        """保存文档"""
        if document.document_id is None:
            document.document_id = str(uuid.uuid4())
        
        self._storage[document.document_id] = document
        return document
    
    async def save_batch(self, documents: List[Document]) -> List[Document]:
        """批量保存文档"""
        results = []
        for doc in documents:
            result = await self.save(doc)
            results.append(result)
        return results
    
    async def find_by_id(self, document_id: str) -> Optional[Document]:
        """根据ID查找文档"""
        return self._storage.get(document_id)
    
    async def find_by_knowledge_base_id(self, knowledge_base_id: str) -> List[Document]:
        """根据知识库ID查找文档列表"""
        return [doc for doc in self._storage.values() 
                if doc.knowledge_base_id == knowledge_base_id]
    
    async def update(self, document: Document) -> Document:
        """更新文档"""
        if document.document_id is None:
            raise ValueError("文档ID不能为空")
        document.updated_at = datetime.now()
        self._storage[document.document_id] = document
        return document
    
    async def delete_by_id(self, document_id: str) -> bool:
        """根据ID删除文档"""
        if document_id in self._storage:
            del self._storage[document_id]
            return True
        return False
    
    async def delete_by_knowledge_base_id(self, knowledge_base_id: str) -> int:
        """根据知识库ID删除所有文档，返回删除数量"""
        docs_to_delete = [doc_id for doc_id, doc in self._storage.items() 
                         if doc.knowledge_base_id == knowledge_base_id]
        
        for doc_id in docs_to_delete:
            del self._storage[doc_id]
        
        return len(docs_to_delete)
    
    async def count_by_knowledge_base_id(self, knowledge_base_id: str) -> int:
        """统计知识库中的文档数量"""
        return len([doc for doc in self._storage.values() 
                   if doc.knowledge_base_id == knowledge_base_id])
    
    async def find_unprocessed_documents(self, knowledge_base_id: str) -> List[Document]:
        """查找未处理的文档"""
        return [doc for doc in self._storage.values()
                if doc.knowledge_base_id == knowledge_base_id and not doc.is_processed]
    
    async def find_unprocessed_by_knowledge_base_id(self, knowledge_base_id: str) -> List[Document]:
        """根据知识库ID查找未处理的文档列表"""
        return [doc for doc in self._storage.values()
                if doc.knowledge_base_id == knowledge_base_id and not doc.is_processed]
    
    async def find_by_content_hash(self, content_hash: str, knowledge_base_id: str) -> Optional[Document]:
        """根据内容哈希查找文档（用于去重）"""
        for doc in self._storage.values():
            if (doc.content_hash == content_hash and 
                doc.knowledge_base_id == knowledge_base_id):
                return doc
        return None
    
    async def find_by_filename_pattern(self, knowledge_base_id: str, pattern: str) -> List[Document]:
        """根据文件名模式查找文档"""
        import re
        compiled_pattern = re.compile(pattern)
        return [doc for doc in self._storage.values()
                if doc.knowledge_base_id == knowledge_base_id and 
                compiled_pattern.search(doc.filename)]