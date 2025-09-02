-- 知识库模块数据库表创建脚本
-- 数据库: esayai
-- 用户: twenty
-- 服务器: localhost:5432

-- 启用PGVector扩展（如果需要向量搜索功能）
-- CREATE EXTENSION IF NOT EXISTS vector;

-- 创建知识库表
CREATE TABLE IF NOT EXISTS datasets (
    id BIGSERIAL PRIMARY KEY, -- 知识库唯一标识符，自增主键
    name VARCHAR(255) NOT NULL, -- 知识库名称
    user_id VARCHAR(255) NOT NULL, -- 所有者用户ID
    description TEXT, -- 知识库描述
    embedding_model_id VARCHAR(255) NOT NULL, -- 使用的嵌入模型标识
    embedding_model_config JSONB, -- 嵌入模型配置（维度、参数等）
    parser_config JSONB, -- 文本解析器配置（分块大小、重叠等）
    meta JSONB, -- 自定义元数据（标签、分类等）
    is_public BOOLEAN DEFAULT FALSE NOT NULL, -- 是否公开知识库
    is_deleted BOOLEAN DEFAULT FALSE NOT NULL, -- 软删除标志
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL, -- 创建时间
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL -- 最后更新时间
);

COMMENT ON TABLE datasets IS '存储知识库元数据信息';
COMMENT ON COLUMN datasets.id IS '知识库唯一标识符，自增主键';
COMMENT ON COLUMN datasets.name IS '知识库名称';
COMMENT ON COLUMN datasets.user_id IS '所有者用户ID';
COMMENT ON COLUMN datasets.description IS '知识库描述';
COMMENT ON COLUMN datasets.embedding_model_id IS '使用的嵌入模型标识';
COMMENT ON COLUMN datasets.embedding_model_config IS '嵌入模型配置（维度、参数等）';
COMMENT ON COLUMN datasets.parser_config IS '文本解析器配置（分块大小、重叠等）';
COMMENT ON COLUMN datasets.meta IS '自定义元数据（标签、分类等）';
COMMENT ON COLUMN datasets.is_public IS '是否公开知识库';
COMMENT ON COLUMN datasets.is_deleted IS '软删除标志';
COMMENT ON COLUMN datasets.created_at IS '创建时间';
COMMENT ON COLUMN datasets.updated_at IS '最后更新时间';

-- 创建文档表
CREATE TABLE IF NOT EXISTS documents (
    id BIGSERIAL PRIMARY KEY, -- 文档唯一标识符，自增主键
    dataset_id BIGINT NOT NULL REFERENCES datasets(id) ON DELETE CASCADE, -- 所属知识库ID
    name VARCHAR(255) NOT NULL, -- 原始文档名称
    original_document_id VARCHAR(255), -- 原始文档在对象存储中的标识或路径
    hash VARCHAR(64) NOT NULL, -- 文档内容哈希值（用于去重）
    char_size INTEGER DEFAULT 0 NOT NULL CHECK (char_size >= 0), -- 文档字符数
    token_size INTEGER CHECK (token_size >= 0), -- 文档Token数（适用于LLM）
    meta JSONB, -- 文档级元数据（作者、发布日期、来源URL等）
    process_status VARCHAR(20) DEFAULT 'pending' NOT NULL CHECK (
        process_status IN ('pending', 'processing', 'completed', 'failed')
    ), -- 文档处理状态
    error_message TEXT, -- 处理失败时的错误信息
    is_active BOOLEAN DEFAULT TRUE NOT NULL, -- 是否激活
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL, -- 创建时间
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL -- 最后更新时间
);

COMMENT ON TABLE documents IS '存储文档元数据信息';
COMMENT ON COLUMN documents.id IS '文档唯一标识符，自增主键';
COMMENT ON COLUMN documents.dataset_id IS '所属知识库ID';
COMMENT ON COLUMN documents.name IS '原始文档名称';
COMMENT ON COLUMN documents.original_document_id IS '原始文档在对象存储中的标识或路径';
COMMENT ON COLUMN documents.hash IS '文档内容哈希值（用于去重）';
COMMENT ON COLUMN documents.char_size IS '文档字符数';
COMMENT ON COLUMN documents.token_size IS '文档Token数（适用于LLM）';
COMMENT ON COLUMN documents.meta IS '文档级元数据（作者、发布日期、来源URL等）';
COMMENT ON COLUMN documents.process_status IS '文档处理状态';
COMMENT ON COLUMN documents.error_message IS '处理失败时的错误信息';
COMMENT ON COLUMN documents.is_active IS '是否激活';
COMMENT ON COLUMN documents.created_at IS '创建时间';
COMMENT ON COLUMN documents.updated_at IS '最后更新时间';

-- 创建分块表（支持分子分块策略）
CREATE TABLE IF NOT EXISTS chunks (
    id BIGSERIAL PRIMARY KEY, -- 分块唯一标识符，自增主键
    document_id BIGINT NOT NULL REFERENCES documents(id) ON DELETE CASCADE, -- 所属文档ID
    dataset_id BIGINT NOT NULL REFERENCES datasets(id) ON DELETE CASCADE, -- 所属知识库ID（冗余存储，提高查询性能）
    parent_chunk_id BIGINT REFERENCES chunks(id) ON DELETE CASCADE, -- 父分块ID（用于构建层次结构）
    chunk_type VARCHAR(10) DEFAULT 'flat' NOT NULL CHECK (
        chunk_type IN ('parent', 'child', 'flat')
    ), -- 分块类型：parent(父块)/child(子块)/flat(普通平级块)
    chunk_level INTEGER DEFAULT 0 NOT NULL CHECK (chunk_level >= 0), -- 分块层级（0表示顶级）
    content TEXT NOT NULL, -- 分块文本内容
    char_size INTEGER NOT NULL CHECK (char_size >= 0), -- 分块字符数
    token_size INTEGER CHECK (token_size >= 0), -- 分块Token数
    index_in_doc INTEGER DEFAULT 0 NOT NULL CHECK (index_in_doc >= 0), -- 在原文中的序号
    meta JSONB, -- 分块级元数据（页码、章节标题等）
    is_active BOOLEAN DEFAULT TRUE NOT NULL, -- 是否激活
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL -- 创建时间
);

COMMENT ON TABLE chunks IS '存储文档分块信息，支持普通分块和分子分块策略';
COMMENT ON COLUMN chunks.id IS '分块唯一标识符，自增主键';
COMMENT ON COLUMN chunks.document_id IS '所属文档ID';
COMMENT ON COLUMN chunks.dataset_id IS '所属知识库ID（冗余存储，提高查询性能）';
COMMENT ON COLUMN chunks.parent_chunk_id IS '父分块ID（用于构建层次结构）';
COMMENT ON COLUMN chunks.chunk_type IS '分块类型：parent(父块)/child(子块)/flat(普通平级块)';
COMMENT ON COLUMN chunks.chunk_level IS '分块层级（0表示顶级）';
COMMENT ON COLUMN chunks.content IS '分块文本内容';
COMMENT ON COLUMN chunks.char_size IS '分块字符数';
COMMENT ON COLUMN chunks.token_size IS '分块Token数';
COMMENT ON COLUMN chunks.index_in_doc IS '在原文中的序号';
COMMENT ON COLUMN chunks.meta IS '分块级元数据（页码、章节标题等）';
COMMENT ON COLUMN chunks.is_active IS '是否激活';
COMMENT ON COLUMN chunks.created_at IS '创建时间';

-- 创建向量表（预留，需要PGVector扩展）
-- 注意：如果没有安装PGVector扩展，此表创建会失败
-- 可以先注释掉vector列，后续安装扩展后再添加
CREATE TABLE IF NOT EXISTS embeddings (
    id BIGSERIAL PRIMARY KEY, -- 向量记录唯一标识符，自增主键
    chunk_id BIGINT NOT NULL UNIQUE REFERENCES chunks(id) ON DELETE CASCADE, -- 关联的分块ID
    -- embedding vector(1536), -- 向量数据（1536维，适用于OpenAI text-embedding-ada-002）
    embedding_data TEXT, -- 临时存储向量数据的文本格式，待PGVector扩展安装后可转换
    embedding_model_id VARCHAR(255) NOT NULL, -- 生成此向量所用的模型ID
    version INTEGER DEFAULT 1 NOT NULL CHECK (version >= 1), -- 向量版本号（支持模型升级）
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL -- 创建时间
);

COMMENT ON TABLE embeddings IS '存储文本分块的向量表示';
COMMENT ON COLUMN embeddings.id IS '向量记录唯一标识符，自增主键';
COMMENT ON COLUMN embeddings.chunk_id IS '关联的分块ID';
-- COMMENT ON COLUMN embeddings.embedding IS '向量数据（1536维，适用于OpenAI text-embedding-ada-002）';
COMMENT ON COLUMN embeddings.embedding_data IS '临时存储向量数据的文本格式';
COMMENT ON COLUMN embeddings.embedding_model_id IS '生成此向量所用的模型ID';
COMMENT ON COLUMN embeddings.version IS '向量版本号（支持模型升级）';
COMMENT ON COLUMN embeddings.created_at IS '创建时间';

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_datasets_user_id ON datasets(user_id); -- 按用户ID查询知识库
CREATE INDEX IF NOT EXISTS idx_datasets_is_deleted ON datasets(is_deleted); -- 过滤已删除知识库
CREATE INDEX IF NOT EXISTS idx_documents_dataset_id ON documents(dataset_id); -- 按知识库ID查询文档
CREATE INDEX IF NOT EXISTS idx_documents_hash ON documents(hash); -- 按哈希值查询文档（用于去重）
CREATE INDEX IF NOT EXISTS idx_documents_process_status ON documents(process_status); -- 按处理状态查询文档
CREATE INDEX IF NOT EXISTS idx_chunks_dataset_id ON chunks(dataset_id); -- 按知识库ID查询分块
CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON chunks(document_id); -- 按文档ID查询分块
CREATE INDEX IF NOT EXISTS idx_chunks_parent_chunk_id ON chunks(parent_chunk_id); -- 按父分块ID查询子分块
CREATE INDEX IF NOT EXISTS idx_chunks_chunk_type ON chunks(chunk_type); -- 按分块类型查询
CREATE INDEX IF NOT EXISTS idx_chunks_chunk_level ON chunks(chunk_level); -- 按分块层级查询
CREATE INDEX IF NOT EXISTS idx_embeddings_chunk_id ON embeddings(chunk_id); -- 按分块ID查询向量
CREATE INDEX IF NOT EXISTS idx_embeddings_model_version ON embeddings(embedding_model_id, version); -- 按模型和版本查询向量

-- 创建向量相似性搜索索引（根据实际查询模式选择合适索引）
-- 注意：需要先安装PGVector扩展，创建向量索引可能需要较长时间和大量资源
-- CREATE INDEX IF NOT EXISTS idx_embeddings_vector ON embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
-- 或者使用HNSW索引（PgVector 0.5.0+）
-- CREATE INDEX IF NOT EXISTS idx_embeddings_vector ON embeddings USING hnsw (embedding vector_cosine_ops);

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
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_datasets_updated_at') THEN
        CREATE TRIGGER update_datasets_updated_at 
            BEFORE UPDATE ON datasets 
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

COMMENT ON FUNCTION update_updated_at_column() IS '自动更新updated_at字段的触发器函数';

-- 输出表创建完成信息
SELECT 'Knowledge base tables created successfully!' as result;