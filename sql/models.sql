-- 创建providers表
CREATE TABLE providers (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    provider VARCHAR(255) NOT NULL,
    api_key VARCHAR(255) NOT NULL,
    base_url VARCHAR(255),
    CONSTRAINT unique_user_provider UNIQUE (user_id, provider)
);

-- 创建models表
CREATE TABLE models (
    id SERIAL PRIMARY KEY,
    provider_id INTEGER NOT NULL,
    model_name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    subtype VARCHAR(50),
    metadata JSONB,
    CONSTRAINT fk_provider FOREIGN KEY (provider_id) REFERENCES providers(id) ON DELETE CASCADE,
    CONSTRAINT unique_provider_model UNIQUE (provider_id, model_name)
);

-- 创建索引以提高查询性能
CREATE INDEX idx_providers_user_id ON providers(user_id);
CREATE INDEX idx_models_provider_id ON models(provider_id);
CREATE INDEX idx_models_type ON models(type);

-- 添加注释
COMMENT ON TABLE providers IS '提供商配置表，存储用户的API提供商信息';
COMMENT ON TABLE models IS '模型表，存储各提供商的模型信息';
COMMENT ON COLUMN providers.user_id IS '用户ID';
COMMENT ON COLUMN providers.provider IS '提供商名称';
COMMENT ON COLUMN providers.api_key IS 'API密钥';
COMMENT ON COLUMN providers.base_url IS 'API基础URL';
COMMENT ON COLUMN models.provider_id IS '关联的提供商ID';
COMMENT ON COLUMN models.model_name IS '模型名称';
COMMENT ON COLUMN models.type IS '模型类型';
COMMENT ON COLUMN models.subtype IS '模型子类型';
COMMENT ON COLUMN models.metadata IS '模型元数据，JSON格式';