-- 为已存在的表添加is_delete字段（如果不存在）
-- 这个脚本是幂等的，可以安全重复执行

-- 为providers表添加is_delete字段
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'providers' 
        AND column_name = 'is_delete'
    ) THEN
        ALTER TABLE providers ADD COLUMN is_delete SMALLINT DEFAULT 0 NOT NULL;
        COMMENT ON COLUMN providers.is_delete IS '软删除标记，0-未删除，1-已删除';
    END IF;
END $$;

-- 为models表添加is_delete字段
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'models' 
        AND column_name = 'is_delete'
    ) THEN
        ALTER TABLE models ADD COLUMN is_delete SMALLINT DEFAULT 0 NOT NULL;
        COMMENT ON COLUMN models.is_delete IS '软删除标记，0-未删除，1-已删除';
    END IF;
END $$;

-- 为models表添加model_metadata字段（存储JSON格式的模型元数据）
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'models' 
        AND column_name = 'model_metadata'
    ) THEN
        ALTER TABLE models ADD COLUMN model_metadata TEXT;
        COMMENT ON COLUMN models.model_metadata IS '模型元数据，JSON格式';
    END IF;
END $$;

-- 确保表存在created_at和updated_at字段
DO $$ 
BEGIN
    -- 为providers表添加时间戳字段
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'providers' 
        AND column_name = 'created_at'
    ) THEN
        ALTER TABLE providers ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL;
        COMMENT ON COLUMN providers.created_at IS '创建时间';
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'providers' 
        AND column_name = 'updated_at'
    ) THEN
        ALTER TABLE providers ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL;
        COMMENT ON COLUMN providers.updated_at IS '更新时间';
    END IF;
    
    -- 为models表添加时间戳字段
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'models' 
        AND column_name = 'created_at'
    ) THEN
        ALTER TABLE models ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL;
        COMMENT ON COLUMN models.created_at IS '创建时间';
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'models' 
        AND column_name = 'updated_at'
    ) THEN
        ALTER TABLE models ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL;
        COMMENT ON COLUMN models.updated_at IS '更新时间';
    END IF;
END $$;

-- 创建索引以提高查询性能（如果不存在）
CREATE INDEX IF NOT EXISTS idx_providers_user_provider_delete ON providers(user_id, provider, is_delete);
CREATE INDEX IF NOT EXISTS idx_models_provider_delete ON models(provider_id, is_delete);
CREATE INDEX IF NOT EXISTS idx_models_name_delete ON models(model_name, is_delete);