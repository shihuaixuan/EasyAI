#!/usr/bin/env python3
"""
检查数据库表结构的脚本
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from sqlalchemy import text
from src.infrastructure.database import get_async_session


async def check_table_structure():
    """检查数据库表结构"""
    async with get_async_session() as session:
        try:
            print("=== 检查数据库表结构 ===\n")
            
            # 检查documents表结构
            print("1. documents表结构:")
            result = await session.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'documents' 
                ORDER BY ordinal_position
            """))
            
            documents_columns = result.fetchall()
            if documents_columns:
                for row in documents_columns:
                    print(f"  {row[0]:25} {row[1]:15} nullable:{row[2]:3} default:{row[3]}")
            else:
                print("  表不存在或没有字段")
            
            print("\n2. chunks表结构:")
            result = await session.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'chunks' 
                ORDER BY ordinal_position
            """))
            
            chunks_columns = result.fetchall()
            if chunks_columns:
                for row in chunks_columns:
                    print(f"  {row[0]:25} {row[1]:15} nullable:{row[2]:3} default:{row[3]}")
            else:
                print("  表不存在或没有字段")
            
            print("\n3. datasets表结构:")
            result = await session.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'datasets' 
                ORDER BY ordinal_position
            """))
            
            datasets_columns = result.fetchall()
            if datasets_columns:
                for row in datasets_columns:
                    print(f"  {row[0]:25} {row[1]:15} nullable:{row[2]:3} default:{row[3]}")
            else:
                print("  表不存在或没有字段")
            
            print("\n4. 检查是否有其他knowledge相关表:")
            result = await session.execute(text("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND (table_name LIKE '%knowledge%' OR table_name LIKE '%document%' OR table_name LIKE '%chunk%')
                ORDER BY table_name
            """))
            
            tables = result.fetchall()
            if tables:
                print("  发现的相关表:")
                for table in tables:
                    print(f"    - {table[0]}")
            else:
                print("  没有发现相关表")
                
        except Exception as e:
            print(f"检查表结构出错: {str(e)}")


if __name__ == "__main__":
    asyncio.run(check_table_structure())