-- 知识库模块数据库表创建脚本 - 与代码匹配版本
-- 数据库: esayai
-- 用户: twenty
-- 服务器: localhost:5432

-- 创建知识库表（与KnowledgeBase实体匹配）
CREATE TABLE IF NOT EXISTS knowledge_bases (
    knowledge_base_id VARCHAR(255) PRIMARY KEY, -- 知识库唯一标识符
    name VARCHAR(255) NOT NULL, -- 知识库名称
    description TEXT, -- 知识库描述
    owner_id VARCHAR(255) NOT NULL, -- 所有者用户ID
    config JSONB, -- 工作流配置（分块、嵌入、检索等）
    is_active BOOLEAN DEFAULT TRUE NOT NULL, -- 是否激活
    document_count INTEGER DEFAULT 0 NOT NULL, -- 文档数量
    chunk_count INTEGER DEFAULT 0 NOT NULL, -- 分块数量
    is_deleted BOOLEAN DEFAULT FALSE NOT NULL, -- 软删除标志
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL, -- 创建时间
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL -- 最后更新时间
);

COMMENT ON TABLE knowledge_bases IS '存储知识库元数据信息';
COMMENT ON COLUMN knowledge_bases.knowledge_base_id IS '知识库唯一标识符';
COMMENT ON COLUMN knowledge_bases.name IS '知识库名称';
COMMENT ON COLUMN knowledge_bases.description IS '知识库描述';
COMMENT ON COLUMN knowledge_bases.owner_id IS '所有者用户ID';
COMMENT ON COLUMN knowledge_bases.config IS '工作流配置（分块、嵌入、检索等）';
COMMENT ON COLUMN knowledge_bases.is_active IS '是否激活';
COMMENT ON COLUMN knowledge_bases.document_count IS '文档数量';
COMMENT ON COLUMN knowledge_bases.chunk_count IS '分块数量';
COMMENT ON COLUMN knowledge_bases.is_deleted IS '软删除标志';
COMMENT ON COLUMN knowledge_bases.created_at IS '创建时间';
COMMENT ON COLUMN knowledge_bases.updated_at IS '最后更新时间';

-- 创建文档表（与Document实体匹配）
CREATE TABLE IF NOT EXISTS documents (
    document_id VARCHAR(255) PRIMARY KEY, -- 文档唯一标识符
    filename VARCHAR(255) NOT NULL, -- 文件名
    content TEXT, -- 文档内容
    file_type VARCHAR(50) NOT NULL, -- 文件类型
    file_size INTEGER NOT NULL, -- 文件大小
    knowledge_base_id VARCHAR(255) NOT NULL REFERENCES knowledge_bases(knowledge_base_id) ON DELETE CASCADE, -- 所属知识库ID
    file_path VARCHAR(500), -- 文件存储路径
    original_path VARCHAR(500), -- 原始路径
    content_hash VARCHAR(64), -- 内容哈希值
    metadata JSONB, -- 元数据
    is_processed BOOLEAN DEFAULT FALSE NOT NULL, -- 是否已处理
    chunk_count INTEGER DEFAULT 0 NOT NULL, -- 分块数量
    is_deleted BOOLEAN DEFAULT FALSE NOT NULL, -- 软删除标志
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL, -- 创建时间
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL, -- 最后更新时间
    processed_at TIMESTAMPTZ -- 处理完成时间
);

COMMENT ON TABLE documents IS '存储文档信息';
COMMENT ON COLUMN documents.document_id IS '文档唯一标识符';
COMMENT ON COLUMN documents.filename IS '文件名';
COMMENT ON COLUMN documents.content IS '文档内容';
COMMENT ON COLUMN documents.file_type IS '文件类型';
COMMENT ON COLUMN documents.file_size IS '文件大小';
COMMENT ON COLUMN documents.knowledge_base_id IS '所属知识库ID';
COMMENT ON COLUMN documents.file_path IS '文件存储路径';
COMMENT ON COLUMN documents.original_path IS '原始路径';
COMMENT ON COLUMN documents.content_hash IS '内容哈希值';
COMMENT ON COLUMN documents.metadata IS '元数据';
COMMENT ON COLUMN documents.is_processed IS '是否已处理';
COMMENT ON COLUMN documents.chunk_count IS '分块数量';
COMMENT ON COLUMN documents.is_deleted IS '软删除标志';
COMMENT ON COLUMN documents.created_at IS '创建时间';
COMMENT ON COLUMN documents.updated_at IS '最后更新时间';
COMMENT ON COLUMN documents.processed_at IS '处理完成时间';

-- 创建分块表（与DocumentChunk实体匹配）
CREATE TABLE IF NOT EXISTS chunks (
    chunk_id VARCHAR(255) PRIMARY KEY, -- 分块唯一标识符
    content TEXT NOT NULL, -- 分块内容
    chunk_index INTEGER NOT NULL, -- 分块索引
    start_offset INTEGER, -- 开始位置
    end_offset INTEGER, -- 结束位置
    document_id VARCHAR(255) NOT NULL REFERENCES documents(document_id) ON DELETE CASCADE, -- 所属文档ID
    knowledge_base_id VARCHAR(255) NOT NULL REFERENCES knowledge_bases(knowledge_base_id) ON DELETE CASCADE, -- 所属知识库ID
    vector TEXT, -- 向量数据（JSON字符串格式）
    metadata JSONB, -- 元数据
    is_deleted BOOLEAN DEFAULT FALSE NOT NULL, -- 软删除标志
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL, -- 创建时间
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL -- 最后更新时间
);

COMMENT ON TABLE chunks IS '存储文档分块信息';
COMMENT ON COLUMN chunks.chunk_id IS '分块唯一标识符';
COMMENT ON COLUMN chunks.content IS '分块内容';
COMMENT ON COLUMN chunks.chunk_index IS '分块索引';
COMMENT ON COLUMN chunks.start_offset IS '开始位置';
COMMENT ON COLUMN chunks.end_offset IS '结束位置';
COMMENT ON COLUMN chunks.document_id IS '所属文档ID';
COMMENT ON COLUMN chunks.knowledge_base_id IS '所属知识库ID';
COMMENT ON COLUMN chunks.vector IS '向量数据（JSON字符串格式）';
COMMENT ON COLUMN chunks.metadata IS '元数据';
COMMENT ON COLUMN chunks.is_deleted IS '软删除标志';
COMMENT ON COLUMN chunks.created_at IS '创建时间';
COMMENT ON COLUMN chunks.updated_at IS '最后更新时间';

-- 创建嵌入表（可选，用于存储向量相关信息）
CREATE TABLE IF NOT EXISTS embeddings (
    embedding_id VARCHAR(255) PRIMARY KEY, -- 嵌入唯一标识符
    chunk_id VARCHAR(255) NOT NULL UNIQUE REFERENCES chunks(chunk_id) ON DELETE CASCADE, -- 关联的分块ID
    model_name VARCHAR(255) NOT NULL, -- 使用的模型名称
    vector_data TEXT, -- 向量数据（JSON格式）
    vector_dimension INTEGER, -- 向量维度
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL -- 创建时间
);

COMMENT ON TABLE embeddings IS '存储向量嵌入信息';
COMMENT ON COLUMN embeddings.embedding_id IS '嵌入唯一标识符';
COMMENT ON COLUMN embeddings.chunk_id IS '关联的分块ID';
COMMENT ON COLUMN embeddings.model_name IS '使用的模型名称';
COMMENT ON COLUMN embeddings.vector_data IS '向量数据（JSON格式）';
COMMENT ON COLUMN embeddings.vector_dimension IS '向量维度';
COMMENT ON COLUMN embeddings.created_at IS '创建时间';

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_knowledge_bases_owner_id ON knowledge_bases(owner_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_bases_is_deleted ON knowledge_bases(is_deleted);
CREATE INDEX IF NOT EXISTS idx_documents_knowledge_base_id ON documents(knowledge_base_id);
CREATE INDEX IF NOT EXISTS idx_documents_content_hash ON documents(content_hash);
CREATE INDEX IF NOT EXISTS idx_documents_is_deleted ON documents(is_deleted);
CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_chunks_knowledge_base_id ON chunks(knowledge_base_id);
CREATE INDEX IF NOT EXISTS idx_chunks_is_deleted ON chunks(is_deleted);
CREATE INDEX IF NOT EXISTS idx_embeddings_chunk_id ON embeddings(chunk_id);

-- 创建触发器以自动更新updated_at字段
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 创建触发器（如果不存在）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_knowledge_bases_updated_at') THEN
        CREATE TRIGGER update_knowledge_bases_updated_at 
            BEFORE UPDATE ON knowledge_bases 
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;
END
$$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_documents_updated_at') THEN
        CREATE TRIGGER update_documents_updated_at 
            BEFORE UPDATE ON documents 
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;
END
$$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_chunks_updated_at') THEN
        CREATE TRIGGER update_chunks_updated_at 
            BEFORE UPDATE ON chunks 
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;
END
$$;

-- 输出表创建完成信息
SELECT 'Knowledge base tables (code-matching version) created successfully!' as result;