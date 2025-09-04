/**
 * 分块配置步骤组件
 */

import React, { useState, useEffect } from 'react';
import { FileText, Database, Settings, HelpCircle, ChevronDown, ChevronRight } from 'lucide-react';
import { cn } from '../../utils/cn';
import { ChunkingConfigStep, EmbeddingConfigStep, RetrievalConfigStep } from '../../hooks/useKnowledgeWorkflow';

interface ConfigurationStepProps {
  chunkingConfig: ChunkingConfigStep;
  embeddingConfig: EmbeddingConfigStep;
  retrievalConfig: RetrievalConfigStep;
  onChunkingConfigChange: (config: Partial<ChunkingConfigStep>) => void;
  onEmbeddingConfigChange: (config: Partial<EmbeddingConfigStep>) => void;
  onRetrievalConfigChange: (config: Partial<RetrievalConfigStep>) => void;
  mode?: 'upload' | 'settings'; // 新增模式属性
}

type ChunkingStrategy = 'parent_child' | 'general';

// Embedding模型接口定义
interface EmbeddingModel {
  model_name: string;
  provider: string;
  description?: string;
  capabilities?: string[];
  context_length?: number;
}

interface EmbeddingModelsResponse {
  models: EmbeddingModel[];
  user_providers: string[];
}

// API调用函数
const getAvailableEmbeddingModels = async (): Promise<EmbeddingModelsResponse> => {
  const token = localStorage.getItem('auth_token');
  const response = await fetch('http://localhost:8000/api/knowledge/embedding-models', {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });
  if (!response.ok) {
    throw new Error('获取embedding模型列表失败');
  }
  return await response.json();
};

export const ConfigurationStep: React.FC<ConfigurationStepProps> = ({
  chunkingConfig,
  embeddingConfig,
  retrievalConfig,
  onChunkingConfigChange,
  onEmbeddingConfigChange,
  onRetrievalConfigChange,
  mode = 'upload', // 默认为上传模式
}) => {
  const [embeddingModels, setEmbeddingModels] = useState<EmbeddingModel[]>([]);
  const [loadingModels, setLoadingModels] = useState(false);
  const [modelError, setModelError] = useState<string | null>(null);

  // 获取可用的embedding模型
  useEffect(() => {
    const fetchEmbeddingModels = async () => {
      if (mode === 'settings') {
        // 在settings模式下，不获取所有可用模型，而是基于当前配置创建模型列表
        console.log('settings模式，使用当前配置的模型，modelName:', embeddingConfig.modelName);
        if (embeddingConfig.modelName) {
          setEmbeddingModels([{
            model_name: embeddingConfig.modelName,
            provider: 'current', // 标识为当前配置的模型
            description: '当前配置的embedding模型'
          }]);
        } else {
          // 如果model_name为null，清空模型列表
          setEmbeddingModels([]);
        }
        return;
      }
      
      // 在upload模式下，只有strategy为high_quality时才获取模型列表
      if (embeddingConfig.strategy === 'high_quality') {
        console.log('开始获取所有可用模型...');
        setLoadingModels(true);
        setModelError(null);
        try {
          console.log('开始获取embedding模型列表...');
          const response = await getAvailableEmbeddingModels();
          console.log('API响应:', response);
          setEmbeddingModels(response.models);
          console.log('设置的模型列表:', response.models);
          // 如果当前没有选择模型，默认选择第一个
          if (!embeddingConfig.modelName && response.models.length > 0) {
            onEmbeddingConfigChange({ modelName: response.models[0].model_name });
          }
        } catch (error) {
          console.error('获取embedding模型失败:', error);
          setModelError('获取模型列表失败，请稍后重试');
          // 如果API调用失败，使用默认模型（仅在upload模式下）
          if (mode === 'upload') {
            setEmbeddingModels([{
              model_name: 'netease-youdao/bce-embedding-base_v1',
              provider: 'netease-youdao',
              description: '默认embedding模型'
            }]);
          }
        } finally {
          setLoadingModels(false);
        }
      }
    };

    fetchEmbeddingModels();
  }, [embeddingConfig.strategy, embeddingConfig.modelName, onEmbeddingConfigChange, mode]);
  const [expandedStrategy, setExpandedStrategy] = useState<ChunkingStrategy | null>(chunkingConfig.strategy);

  const handleStrategyClick = (strategy: ChunkingStrategy) => {
    if (expandedStrategy === strategy) {
      setExpandedStrategy(null);
    } else {
      setExpandedStrategy(strategy);
      // 在设置模式下不允许修改策略
      if (mode !== 'settings') {
        onChunkingConfigChange({ strategy });
      }
    }
  };

  const renderTextPreprocessingOptions = () => (
    <div className="border-t pt-4">
      <h5 className="text-sm font-medium text-gray-900 mb-3">文本预处理规则</h5>
      <div className="space-y-2">
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={chunkingConfig.removeExtraWhitespace}
            onChange={(e) => onChunkingConfigChange({ removeExtraWhitespace: e.target.checked })}
            className="mr-2"
          />
          <span className="text-sm text-gray-700">替换掉连续的空格、换行符和制表符</span>
        </label>
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={chunkingConfig.removeUrls}
            onChange={(e) => onChunkingConfigChange({ removeUrls: e.target.checked })}
            className="mr-2"
          />
          <span className="text-sm text-gray-700">删除所有 URL</span>
        </label>
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={chunkingConfig.removeEmails}
            onChange={(e) => onChunkingConfigChange({ removeEmails: e.target.checked })}
            className="mr-2"
          />
          <span className="text-sm text-gray-700">删除所有电子邮件地址</span>
        </label>
      </div>
    </div>
  );

  return (
    <div className="space-y-8">
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-6">配置处理参数</h3>
        {mode === 'settings' && (
          <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm text-blue-800">
              ℹ️ 在设置模式下，索引方式和向量检索设置为只读状态，仅可修改分块配置参数。
            </p>
          </div>
        )}
      </div>

      {/* 分块策略配置 */}
      <div className="space-y-4">
        {/* 父子分块 */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg">
          <div 
            className="p-4 cursor-pointer"
            onClick={() => handleStrategyClick('parent_child')}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="flex items-center space-x-2">
                  <input
                    type="radio"
                    name="chunkingStrategy"
                    value="parent_child"
                    checked={chunkingConfig.strategy === 'parent_child'}
                    onChange={() => {}}
                    className="mr-2"
                  />
                  <FileText className="w-5 h-5 text-blue-600" />
                  <h4 className="text-md font-medium text-gray-900">父子分块</h4>
                </div>
              </div>
              {expandedStrategy === 'parent_child' ? 
                <ChevronDown className="w-5 h-5 text-gray-400" /> : 
                <ChevronRight className="w-5 h-5 text-gray-400" />
              }
            </div>
            <p className="text-sm text-gray-600 mt-2 ml-7">
              使用父子模式时，子块用于检索，父块用作上下文
            </p>
          </div>
          
          {expandedStrategy === 'parent_child' && (
            <div className="px-4 pb-4 space-y-4">
              {/* 父块配置 */}
              <div className="border-t pt-4">
                <h5 className="text-sm font-medium text-gray-900 mb-3">父块用作上下文</h5>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      分段标识符
                      <HelpCircle className="inline w-3 h-3 ml-1 text-gray-400" />
                    </label>
                    <input
                      type="text"
                      value={chunkingConfig.parentSeparator || '\n\n'}
                      onChange={(e) => onChunkingConfigChange({ parentSeparator: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                      placeholder="\n\n"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">分段最大长度</label>
                    <div className="flex items-center space-x-2">
                      <input
                        type="number"
                        value={chunkingConfig.parentMaxLength || 1024}
                        onChange={(e) => onChunkingConfigChange({ parentMaxLength: parseInt(e.target.value) })}
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm"
                        min="1"
                        max="10000"
                      />
                      <span className="text-sm text-gray-500">characters</span>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* 子块配置 */}
              <div className="border-t pt-4">
                <h5 className="text-sm font-medium text-gray-900 mb-3">子块用于检索</h5>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      分段标识符
                      <HelpCircle className="inline w-3 h-3 ml-1 text-gray-400" />
                    </label>
                    <input
                      type="text"
                      value={chunkingConfig.childSeparator || '\n'}
                      onChange={(e) => onChunkingConfigChange({ childSeparator: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                      placeholder="\n"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">分段最大长度</label>
                    <div className="flex items-center space-x-2">
                      <input
                        type="number"
                        value={chunkingConfig.childMaxLength || 512}
                        onChange={(e) => onChunkingConfigChange({ childMaxLength: parseInt(e.target.value) })}
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm"
                        min="1"
                        max="5000"
                      />
                      <span className="text-sm text-gray-500">characters</span>
                    </div>
                  </div>
                </div>
              </div>

              {renderTextPreprocessingOptions()}
            </div>
          )}
        </div>

        {/* 普通分块 */}
        <div className="bg-gray-50 border border-gray-200 rounded-lg">
          <div 
            className="p-4 cursor-pointer"
            onClick={() => handleStrategyClick('general')}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="flex items-center space-x-2">
                  <input
                    type="radio"
                    name="chunkingStrategy"
                    value="general"
                    checked={chunkingConfig.strategy === 'general'}
                    onChange={() => {}}
                    className="mr-2"
                  />
                  <FileText className="w-5 h-5 text-gray-600" />
                  <h4 className="text-md font-medium text-gray-900">普通分块</h4>
                </div>
              </div>
              {expandedStrategy === 'general' ? 
                <ChevronDown className="w-5 h-5 text-gray-400" /> : 
                <ChevronRight className="w-5 h-5 text-gray-400" />
              }
            </div>
            <p className="text-sm text-gray-600 mt-2 ml-7">
              按照指定的分隔符和最大块长度将文本拆分为常规块
            </p>
          </div>
          
          {expandedStrategy === 'general' && (
            <div className="px-4 pb-4 space-y-4">
              {/* 普通分块配置 */}
              <div className="border-t pt-4">
                <h5 className="text-sm font-medium text-gray-900 mb-3">分块设置</h5>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      分段标识符
                      <HelpCircle className="inline w-3 h-3 ml-1 text-gray-400" />
                    </label>
                    <input
                      type="text"
                      value={chunkingConfig.separator}
                      onChange={(e) => onChunkingConfigChange({ separator: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                      placeholder="\n\n"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">分段最大长度</label>
                    <div className="flex items-center space-x-2">
                      <input
                        type="number"
                        value={chunkingConfig.maxLength}
                        onChange={(e) => onChunkingConfigChange({ maxLength: parseInt(e.target.value) })}
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm"
                        min="1"
                        max="10000"
                      />
                      <span className="text-sm text-gray-500">characters</span>
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      分段重叠长度
                      <HelpCircle className="inline w-3 h-3 ml-1 text-gray-400" />
                    </label>
                    <div className="flex items-center space-x-2">
                      <input
                        type="number"
                        value={chunkingConfig.overlapLength}
                        onChange={(e) => onChunkingConfigChange({ overlapLength: parseInt(e.target.value) })}
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm"
                        min="0"
                        max="1000"
                      />
                      <span className="text-sm text-gray-500">characters</span>
                    </div>
                  </div>
                </div>
              </div>

              {renderTextPreprocessingOptions()}
            </div>
          )}
        </div>
      </div>

      {/* 索引方式配置 */}
      <div className={cn(
        "border border-gray-200 rounded-lg p-6",
        mode === 'settings' ? "bg-gray-100" : "bg-gray-50"
      )}>
        <div className="flex items-center space-x-2 mb-4">
          <Database className="w-5 h-5 text-gray-600" />
          <h4 className="text-md font-medium text-gray-900">索引方式</h4>
          {mode === 'settings' && (
            <span className="text-xs bg-gray-200 text-gray-600 px-2 py-1 rounded">只读</span>
          )}
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <label className={cn(
            "flex items-start p-4 border rounded-lg transition-colors",
            mode === 'settings' ? "cursor-not-allowed" : "cursor-pointer",
            embeddingConfig.strategy === 'high_quality' 
              ? "border-blue-500 bg-blue-50" 
              : "border-gray-300 bg-white hover:border-gray-400"
          )}>
            <input
              type="radio"
              name="embeddingStrategy"
              value="high_quality"
              checked={embeddingConfig.strategy === 'high_quality'}
              onChange={(e) => mode !== 'settings' && onEmbeddingConfigChange({ strategy: e.target.value as 'high_quality' })}
              disabled={mode === 'settings'}
              className="mr-3 mt-1"
            />
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-medium text-gray-900">高质量</span>
                <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">推荐</span>
              </div>
              <div className="text-sm text-gray-600 mt-1">
                调用嵌入模型处理文档以实现更精确的检索，可以帮助 LLM 生成高质量的答案。
              </div>
            </div>
          </label>
          
          <label className={cn(
            "flex items-start p-4 border rounded-lg transition-colors",
            mode === 'settings' ? "cursor-not-allowed" : "cursor-pointer",
            embeddingConfig.strategy === 'economic' 
              ? "border-blue-500 bg-blue-50" 
              : "border-gray-300 bg-white hover:border-gray-400"
          )}>
            <input
              type="radio"
              name="embeddingStrategy"
              value="economic"
              checked={embeddingConfig.strategy === 'economic'}
              onChange={(e) => mode !== 'settings' && onEmbeddingConfigChange({ strategy: e.target.value as 'economic' })}
              disabled={mode === 'settings'}
              className="mr-3 mt-1"
            />
            <div>
              <div className="font-medium text-gray-900">经济</div>
              <div className="text-sm text-gray-600 mt-1">
                每个数据块使用 10 个关键词进行检索，不会消耗任何 tokens，但会以降低检索准确性为代价。
              </div>
            </div>
          </label>
        </div>

        {embeddingConfig.strategy === 'high_quality' && (
          <div className="mt-4 p-3 bg-orange-50 border border-orange-200 rounded-lg">
            <p className="text-sm text-orange-800">
              ⚠️ 使用高质量模式进行嵌入后，无法切换回经济模式。
            </p>
          </div>
        )}

        {embeddingConfig.strategy === 'high_quality' && (
          <div className="mt-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">Embedding 模型</label>
            {modelError && (
              <div className="mb-2 p-2 bg-red-50 border border-red-200 rounded-md">
                <p className="text-sm text-red-600">{modelError}</p>
              </div>
            )}
            <select
              value={embeddingConfig.modelName || ''}
              onChange={(e) => mode !== 'settings' && onEmbeddingConfigChange({ modelName: e.target.value })}
              disabled={mode === 'settings' || loadingModels}
              className={cn(
                "w-full px-3 py-2 border border-gray-300 rounded-md text-sm",
                mode === 'settings' || loadingModels ? "bg-gray-100 cursor-not-allowed" : ""
              )}
            >
              {(mode !== 'settings' || embeddingModels.length > 0) && (
                <option value="" disabled>
                  {loadingModels ? "加载中..." : "选择embedding模型"}
                </option>
              )}
              {embeddingModels.length > 0 && embeddingModels.map((model) => (
                <option key={model.model_name} value={model.model_name}>
                  {model.model_name}
                </option>
              ))}
            </select>
            {embeddingConfig.modelName && embeddingModels.length > 0 && (
              <div className="mt-2 text-xs text-gray-500">
                {(() => {
                  const selectedModel = embeddingModels.find(m => m.model_name === embeddingConfig.modelName);
                  if (selectedModel) {
                    return (
                      <div>
                        <div>提供商: {selectedModel.provider}</div>
                        {selectedModel.context_length && (
                          <div>上下文长度: {selectedModel.context_length.toLocaleString()}</div>
                        )}
                        {selectedModel.capabilities && selectedModel.capabilities.length > 0 && (
                          <div>功能: {selectedModel.capabilities.join(', ')}</div>
                        )}
                      </div>
                    );
                  }
                  return null;
                })()} 
              </div>
            )}
          </div>
        )}
      </div>

      {/* 检索设置配置 */}
      <div className={cn(
        "border border-gray-200 rounded-lg p-6",
        mode === 'settings' ? "bg-gray-100" : "bg-gray-50"
      )}>
        <div className="flex items-center space-x-2 mb-4">
          <Settings className="w-5 h-5 text-gray-600" />
          <h4 className="text-md font-medium text-gray-900">检索设置</h4>
          {mode === 'settings' && (
            <span className="text-xs bg-gray-200 text-gray-600 px-2 py-1 rounded">只读</span>
          )}
        </div>
        <p className="text-sm text-gray-600 mb-4">
          了解更多关于检索方法，您可以随时在知识库设置中更改此设置。
        </p>
        
        <div className="space-y-4">
          <label className={cn(
            "flex items-start p-4 border rounded-lg cursor-pointer transition-colors",
            retrievalConfig.strategy === 'vector_search' 
              ? "border-blue-500 bg-blue-50" 
              : "border-gray-300 bg-white hover:border-gray-400"
          )}>
            <input
              type="radio"
              name="retrievalStrategy"
              value="vector_search"
              checked={retrievalConfig.strategy === 'vector_search'}
              onChange={(e) => mode !== 'settings' && onRetrievalConfigChange({ strategy: e.target.value as 'vector_search' })}
              disabled={mode === 'settings'}
              className="mr-3 mt-1"
            />
            <div className="flex-1">
              <div className="font-medium text-gray-900">向量检索</div>
              <div className="text-sm text-gray-600 mt-1">
                通过生成查询嵌入并查询与其向量表示最相似的文本分段
              </div>
              
              {retrievalConfig.strategy === 'vector_search' && (
                <div className="mt-4 space-y-4">
                  <div className="flex items-center space-x-4">
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={retrievalConfig.enableRerank}
                        onChange={(e) => mode !== 'settings' && onRetrievalConfigChange({ enableRerank: e.target.checked })}
                        disabled={mode === 'settings'}
                        className="mr-2"
                      />
                      <span className="text-sm font-medium text-gray-700">Rerank 模型</span>
                      <HelpCircle className="w-3 h-3 ml-1 text-gray-400" />
                    </label>
                  </div>
                  
                  {retrievalConfig.enableRerank && (
                    <div>
                      <select
                        value={retrievalConfig.rerankModel || 'netease-youdao/bce-reranker-base_v1'}
                        onChange={(e) => mode !== 'settings' && onRetrievalConfigChange({ rerankModel: e.target.value })}
                        disabled={mode === 'settings'}
                        className={cn(
                          "w-full px-3 py-2 border border-gray-300 rounded-md text-sm",
                          mode === 'settings' ? "bg-gray-100 cursor-not-allowed" : ""
                        )}
                      >
                        <option value="netease-youdao/bce-reranker-base_v1">netease-youdao/bce-reranker-base_v1</option>
                      </select>
                    </div>
                  )}
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Top K
                        <HelpCircle className="inline w-3 h-3 ml-1 text-gray-400" />
                      </label>
                      <div className="flex items-center space-x-2">
                        <input
                          type="number"
                          value={retrievalConfig.topK}
                          onChange={(e) => mode !== 'settings' && onRetrievalConfigChange({ topK: parseInt(e.target.value) })}
                          disabled={mode === 'settings'}
                          className={cn(
                            "flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm",
                            mode === 'settings' ? "bg-gray-100 cursor-not-allowed" : ""
                          )}
                          min="1"
                          max="100"
                        />
                        <div className="w-20 h-2 bg-gray-200 rounded">
                          <div 
                            className="h-full bg-blue-500 rounded" 
                            style={{ width: `${(retrievalConfig.topK / 100) * 100}%` }}
                          />
                        </div>
                      </div>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Score 阈值
                        <HelpCircle className="inline w-3 h-3 ml-1 text-gray-400" />
                      </label>
                      <div className="flex items-center space-x-2">
                        <input
                          type="number"
                          step="0.1"
                          value={retrievalConfig.scoreThreshold}
                          onChange={(e) => mode !== 'settings' && onRetrievalConfigChange({ scoreThreshold: parseFloat(e.target.value) })}
                          disabled={mode === 'settings'}
                          className={cn(
                            "flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm",
                            mode === 'settings' ? "bg-gray-100 cursor-not-allowed" : ""
                          )}
                          min="0"
                          max="1"
                        />
                        <div className="w-20 h-2 bg-gray-200 rounded">
                          <div 
                            className="h-full bg-blue-500 rounded" 
                            style={{ width: `${retrievalConfig.scoreThreshold * 100}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </label>

          <label className={cn(
            "flex items-start p-4 border rounded-lg cursor-pointer transition-colors",
            retrievalConfig.strategy === 'fulltext_search' 
              ? "border-blue-500 bg-blue-50" 
              : "border-gray-300 bg-white hover:border-gray-400"
          )}>
            <input
              type="radio"
              name="retrievalStrategy"
              value="fulltext_search"
              checked={retrievalConfig.strategy === 'fulltext_search'}
              onChange={(e) => mode !== 'settings' && onRetrievalConfigChange({ strategy: e.target.value as 'fulltext_search' })}
              disabled={mode === 'settings'}
              className="mr-3 mt-1"
            />
            <div>
              <div className="font-medium text-gray-900">全文检索</div>
              <div className="text-sm text-gray-600 mt-1">
                索引文档中的所有词汇，从而允许用户查询任意词汇，并返回包含这些词汇的文本片段
              </div>
            </div>
          </label>

          <label className={cn(
            "flex items-start p-4 border rounded-lg cursor-pointer transition-colors",
            retrievalConfig.strategy === 'hybrid_search' 
              ? "border-blue-500 bg-blue-50" 
              : "border-gray-300 bg-white hover:border-gray-400"
          )}>
            <input
              type="radio"
              name="retrievalStrategy"
              value="hybrid_search"
              checked={retrievalConfig.strategy === 'hybrid_search'}
              onChange={(e) => mode !== 'settings' && onRetrievalConfigChange({ strategy: e.target.value as 'hybrid_search' })}
              disabled={mode === 'settings'}
              className="mr-3 mt-1"
            />
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-medium text-gray-900">混合检索</span>
                <span className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded">推荐</span>
              </div>
              <div className="text-sm text-gray-600 mt-1">
                同时执行全文检索和向量检索，并应用重排序步骤，从两类查询结果中选择匹配用户问题的最佳结果，用户可以选择设置权重或配置重新排序模型。
              </div>
            </div>
          </label>
        </div>
      </div>
    </div>
  );
};