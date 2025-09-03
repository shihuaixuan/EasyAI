#!/usr/bin/env python3
"""
测试文档上传事务管理的脚本
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.infrastructure.database import get_async_session
from src.infrastructure.repositories.document_sql_repository import DocumentSqlRepository
from src.infrastructure.repositories.document_chunk_sql_repository import DocumentChunkSqlRepository
from src.infrastructure.repositories.knowledge_base_database_repository_impl import KnowledgeBaseDatabaseRepositoryImpl
from src.domain.knowledge.entities.document import Document
from src.domain.knowledge.entities.document_chunk import DocumentChunk
from src.domain.knowledge.entities.knowledge_base import KnowledgeBase


async def test_transaction_management():
    """测试事务管理"""
    async with get_async_session() as session:
        try:
            # 创建仓储实例
            kb_repo = KnowledgeBaseDatabaseRepositoryImpl(session)
            doc_repo = DocumentSqlRepository(session)
            chunk_repo = DocumentChunkSqlRepository(session)
            
            print("1. 创建测试知识库...")
            kb = KnowledgeBase(
                name="测试知识库",
                description="用于测试事务管理",
                owner_id="test_user",
                config={
                    "chunking": {
                        "strategy": "general",
                        "chunk_size": 500,
                        "chunk_overlap": 50
                    }
                }
            )
            
            saved_kb = await kb_repo.save(kb)
            print(f"知识库创建成功: {saved_kb.knowledge_base_id}")
            
            print("2. 创建测试文档...")
            doc = Document(
                filename="test.txt",
                content="这是一个测试文档，用于验证事务管理功能。" * 100,  # 生成足够长的内容
                file_type="text/plain",
                file_size=1000,
                knowledge_base_id=saved_kb.knowledge_base_id or ""
            )
            
            saved_doc = await doc_repo.save(doc)
            print(f"文档创建成功: {saved_doc.document_id}")
            
            print("3. 创建测试分块...")
            chunks = []
            for i in range(3):
                chunk = DocumentChunk(
                    content=f"这是第{i+1}个测试分块的内容...",
                    chunk_index=i,
                    start_offset=i * 100,
                    end_offset=(i + 1) * 100,
                    document_id=saved_doc.document_id or "",
                    knowledge_base_id=saved_kb.knowledge_base_id or "",
                    metadata={"test": True}
                )
                chunks.append(chunk)
            
            saved_chunks = await chunk_repo.save_batch(chunks)
            print(f"分块创建成功: {len(saved_chunks)} 个")
            
            print("4. 更新文档处理状态...")
            saved_doc.mark_as_processed(len(saved_chunks))
            await doc_repo.update(saved_doc)
            print(f"文档处理状态更新完成: {saved_doc.is_processed}")
            
            print("5. 验证数据完整性...")
            # 查询文档
            found_doc = await doc_repo.find_by_id(saved_doc.document_id or "")
            assert found_doc is not None, "文档查询失败"
            assert found_doc.is_processed == True, "文档处理状态不正确"
            
            # 查询分块
            found_chunks = await chunk_repo.find_by_document_id(saved_doc.document_id or "")
            assert len(found_chunks) == 3, f"分块数量不正确: {len(found_chunks)}"
            
            print("✅ 事务管理测试通过！")
            
            # 清理测试数据
            await chunk_repo.delete_by_document_id(saved_doc.document_id or "")
            await doc_repo.delete_by_id(saved_doc.document_id or "")
            await kb_repo.delete_by_id(saved_kb.knowledge_base_id or "")
            
            print("测试数据清理完成")
            
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
            raise


if __name__ == "__main__":
    asyncio.run(test_transaction_management())