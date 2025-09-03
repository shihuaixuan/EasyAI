"""
文档仓储SQL实现 - 简化版
"""
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ....domain.knowledge.entities.document import Document
from ....domain.knowledge.repositories.document_repository import DocumentRepository


class DocumentSqlRepository(DocumentRepository):
    """文档仓储SQL实现"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def save(self, document: Document) -> Document:
        """保存文档"""
        # 使用实际数据库表字段
        sql = """
        INSERT INTO documents (dataset_id, name, original_document_id, hash, char_size, meta, process_status, is_active, created_at, updated_at)
        VALUES (:dataset_id, :name, :original_document_id, :hash, :char_size, :meta, :process_status, :is_active, :created_at, :updated_at)
        RETURNING id
        """
        
        # 转换字段名映射
        params = {
            'dataset_id': int(document.knowledge_base_id) if document.knowledge_base_id else None,
            'name': document.filename,
            'original_document_id': document.document_id,
            'hash': document.content_hash,
            'char_size': document.file_size,
            'meta': json.dumps(document.metadata),
            'process_status': 'completed' if document.is_processed else 'pending',
            'is_active': True,
            'created_at': document.created_at,
            'updated_at': document.updated_at
        }
        
        result = await self.session.execute(text(sql), params)
        new_id = result.scalar()
        
        # 更新实体的ID
        if new_id:
            document.document_id = str(new_id)
        
        return document
    
    async def save_batch(self, documents: List[Document]) -> List[Document]:
        """批量保存文档"""
        if not documents:
            return []
        
        # 转换为数据库模型列表
        for doc in documents:
            await self.save(doc)
        
        return documents
    
    async def find_by_id(self, document_id: str) -> Optional[Document]:
        """根据ID查找文档"""
        sql = """
        SELECT * FROM documents 
        WHERE id = :id AND is_active = true
        """
        
        result = await self.session.execute(text(sql), {"id": int(document_id)})
        row = result.fetchone()
        
        if row:
            return self._from_dict(dict(row._mapping))
        return None
    
    async def find_by_knowledge_base_id(self, knowledge_base_id: str) -> List[Document]:
        """根据知识库ID查找文档列表"""
        sql = """
        SELECT * FROM documents 
        WHERE dataset_id = :dataset_id AND is_active = true
        ORDER BY created_at DESC
        """
        
        result = await self.session.execute(text(sql), {"dataset_id": int(knowledge_base_id)})
        rows = result.fetchall()
        
        return [self._from_dict(dict(row._mapping)) for row in rows]
    
    async def update(self, document: Document) -> Document:
        """更新文档"""
        if document.document_id is None:
            raise ValueError("文档ID不能为空")
        
        document.updated_at = datetime.now()
        
        sql = """
        UPDATE documents 
        SET name = :name,
            hash = :hash,
            char_size = :char_size,
            meta = :meta,
            process_status = :process_status,
            updated_at = :updated_at
        WHERE id = :id
        """
        
        params = {
            'id': int(document.document_id),
            'name': document.filename,
            'hash': document.content_hash,
            'char_size': document.file_size,
            'meta': json.dumps(document.metadata),
            'process_status': 'completed' if document.is_processed else 'pending',
            'updated_at': document.updated_at
        }
        
        await self.session.execute(text(sql), params)
        return document
    
    async def delete_by_id(self, document_id: str) -> bool:
        """根据ID删除文档（硬删除）"""
        sql = """
        DELETE FROM documents 
        WHERE id = :id
        """
        
        result = await self.session.execute(text(sql), {
            "id": int(document_id)
        })
        # 注意：事务提交由调用方处理，不在这里提交
        return result.rowcount > 0
    
    async def delete_by_knowledge_base_id(self, knowledge_base_id: str) -> int:
        """根据知识库ID删除所有文档（软删除），返回删除数量"""
        sql = """
        UPDATE documents 
        SET is_active = false, updated_at = :updated_at
        WHERE dataset_id = :dataset_id AND is_active = true
        """
        
        result = await self.session.execute(text(sql), {
            "dataset_id": int(knowledge_base_id),
            "updated_at": datetime.now()
        })
        # 注意：事务提交由调用方处理，不在这里提交
        return result.rowcount
    
    async def count_by_knowledge_base_id(self, knowledge_base_id: str) -> int:
        """统计知识库中的文档数量"""
        sql = """
        SELECT COUNT(*) FROM documents
        WHERE dataset_id = :dataset_id AND is_active = true
        """
        
        result = await self.session.execute(text(sql), {"dataset_id": int(knowledge_base_id)})
        return result.scalar() or 0
    
    async def find_unprocessed_documents(self, knowledge_base_id: str) -> List[Document]:
        """查找未处理的文档"""
        sql = """
        SELECT * FROM documents 
        WHERE dataset_id = :dataset_id 
            AND process_status = 'pending' 
            AND is_active = true
        ORDER BY created_at ASC
        """
        
        result = await self.session.execute(text(sql), {"dataset_id": int(knowledge_base_id)})
        rows = result.fetchall()
        
        return [self._from_dict(dict(row._mapping)) for row in rows]
    
    async def find_unprocessed_by_knowledge_base_id(self, knowledge_base_id: str) -> List[Document]:
        """根据知识库ID查找未处理的文档列表"""
        return await self.find_unprocessed_documents(knowledge_base_id)
    
    async def find_by_content_hash(self, content_hash: str, knowledge_base_id: str) -> Optional[Document]:
        """根据内容哈希查找文档（用于去重）"""
        sql = """
        SELECT * FROM documents
        WHERE hash = :hash 
            AND dataset_id = :dataset_id 
            AND is_active = true
        """
        
        result = await self.session.execute(text(sql), {
            "hash": content_hash,
            "dataset_id": int(knowledge_base_id)
        })
        row = result.fetchone()
        
        if row:
            return self._from_dict(dict(row._mapping))
        return None
    
    async def find_by_filename_pattern(self, knowledge_base_id: str, pattern: str) -> List[Document]:
        """根据文件名模式查找文档"""
        sql = """
        SELECT * FROM documents
        WHERE dataset_id = :dataset_id 
            AND name LIKE :pattern 
            AND is_active = true
        ORDER BY created_at DESC
        """
        
        result = await self.session.execute(text(sql), {
            "dataset_id": int(knowledge_base_id),
            "pattern": f"%{pattern}%"
        })
        rows = result.fetchall()
        
        return [self._from_dict(dict(row._mapping)) for row in rows]
    

    def _from_dict(self, data: Dict[str, Any]) -> Document:
        """从字典转换为文档实体"""
        # 处理meta字段，可能是JSON字符串也可能是字典
        meta_data = data.get('meta')
        if isinstance(meta_data, str):
            import json
            try:
                meta_data = json.loads(meta_data)
            except json.JSONDecodeError:
                meta_data = {}
        elif not isinstance(meta_data, dict):
            meta_data = {}
        
        return Document(
            document_id=str(data.get('id')) if data.get('id') else None,
            filename=data.get('name', ''),
            content="",  # 实际表中没有content字段
            file_type="",  # 实际表中没有file_type字段
            file_size=data.get('char_size', 0),
            knowledge_base_id=str(data.get('dataset_id')) if data.get('dataset_id') else "",
            file_path=None,  # 实际表中没有file_path字段
            original_path=None,  # 实际表中没有original_path字段
            content_hash=data.get('hash'),
            metadata=meta_data,
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            processed_at=None,  # 实际表中没有processed_at字段
            is_processed=data.get('process_status') == 'completed',
            chunk_count=0  # 实际表中没有chunk_count字段
        )