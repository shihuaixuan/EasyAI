/**
 * 分块配置步骤组件
 */

import React from 'react';
import { FileText, Database, Settings, HelpCircle } from 'lucide-react';
import { cn } from '../../utils/cn';
import { ChunkingConfigStep, EmbeddingConfigStep, RetrievalConfigStep } from '../../hooks/useKnowledgeWorkflow';

interface ConfigurationStepProps {
  chunkingConfig: ChunkingConfigStep;
  embeddingConfig: EmbeddingConfigStep;
  retrievalConfig: RetrievalConfigStep;
  onChunkingConfigChange: (config: Partial<ChunkingConfigStep>) => void;
  onEmbeddingConfigChange: (config: Partial<EmbeddingConfigStep>) => void;
  onRetrievalConfigChange: (config: Partial<RetrievalConfigStep>) => void;
}

export const ConfigurationStep: React.FC<ConfigurationStepProps> = ({
  chunkingConfig,
  embeddingConfig,
  retrievalConfig,
  onChunkingConfigChange,
  onEmbeddingConfigChange,
  onRetrievalConfigChange,
}) => {
  return (
    <div className="space-y-8">
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-6">配置处理参数</h3>
      </div>

      {/* 分块策略配置 */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <div className="flex items-center space-x-2 mb-4">
          <FileText className="w-5 h-5 text-blue-600" />
          <h4 className="text-md font-medium text-gray-900">父子分段</h4>
        </div>
        <p className="text-sm text-gray-600 mb-4">
          使用父子模式时，子块用于检索，父块用作上下文
        </p>
        
        <div className="space-y-4">
          {/* 策略选择 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <label className={cn(
              "flex items-center p-4 border rounded-lg cursor-pointer transition-colors",
              chunkingConfig.strategy === 'parent_child' 
                ? "border-blue-500 bg-blue-50" 
                : "border-gray-300 bg-white hover:border-gray-400"
            )}>
              <input
                type="radio"
                name="chunkingStrategy"
                value="parent_child"
                checked={chunkingConfig.strategy === 'parent_child'}
                onChange={(e) => onChunkingConfigChange({ strategy: e.target.value as 'parent_child' })}
                className="mr-3"
              />
              <div>
                <div className="font-medium text-gray-900">段落</div>
                <div className="text-sm text-gray-600">
                  此模式根据分隔符和最大块长度将文本拆分为段落，使用拆分文本作为检索的父块
                </div>
              </div>
            </label>
            
            <label className={cn(
              "flex items-center p-4 border rounded-lg cursor-pointer transition-colors",
              chunkingConfig.strategy === 'general' 
                ? "border-blue-500 bg-blue-50" 
                : "border-gray-300 bg-white hover:border-gray-400"
            )}>
              <input
                type="radio"
                name="chunkingStrategy"
                value="general"
                checked={chunkingConfig.strategy === 'general'}
                onChange={(e) => onChunkingConfigChange({ strategy: e.target.value as 'general' })}
                className="mr-3"
              />
              <div>
                <div className="font-medium text-gray-900">全文</div>
                <div className="text-sm text-gray-600">
                  整个文档用作父块并直接检索。请注意，出于性能原因，超过 10000 个标记的文本将被自动截断。
                </div>
              </div>
            </label>
          </div>

          {/* 父块配置 - 仅在父子模式下显示 */}
          {chunkingConfig.strategy === 'parent_child' && (
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
          )}

          {/* 子块配置 - 仅在父子模式下显示 */}
          {chunkingConfig.strategy === 'parent_child' && (
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
          )}

          {/* 通用配置 */}
          <div className="border-t pt-4">
            <h5 className="text-sm font-medium text-gray-900 mb-3">分段设置</h5>
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

          {/* 文本预处理规则 */}
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
                <span className="text-sm text-gray-700">替换填连续的空格、换行符和制表符</span>
              </label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={chunkingConfig.removeUrls}
                  onChange={(e) => onChunkingConfigChange({ removeUrls: e.target.checked })}
                  className="mr-2"
                />
                <span className="text-sm text-gray-700">删除所有 URL 和电子邮件地址</span>
              </label>
            </div>
          </div>
        </div>
      </div>

      {/* 索引方式配置 */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
        <div className="flex items-center space-x-2 mb-4">
          <Database className="w-5 h-5 text-gray-600" />
          <h4 className="text-md font-medium text-gray-900">索引方式</h4>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <label className={cn(
            "flex items-start p-4 border rounded-lg cursor-pointer transition-colors",
            embeddingConfig.strategy === 'high_quality' 
              ? "border-blue-500 bg-blue-50" 
              : "border-gray-300 bg-white hover:border-gray-400"
          )}>
            <input
              type="radio"
              name="embeddingStrategy"
              value="high_quality"
              checked={embeddingConfig.strategy === 'high_quality'}
              onChange={(e) => onEmbeddingConfigChange({ strategy: e.target.value as 'high_quality' })}
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
            "flex items-start p-4 border rounded-lg cursor-pointer transition-colors",
            embeddingConfig.strategy === 'economic' 
              ? "border-blue-500 bg-blue-50" 
              : "border-gray-300 bg-white hover:border-gray-400"
          )}>
            <input
              type="radio"
              name="embeddingStrategy"
              value="economic"
              checked={embeddingConfig.strategy === 'economic'}
              onChange={(e) => onEmbeddingConfigChange({ strategy: e.target.value as 'economic' })}
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
            <select
              value={embeddingConfig.modelName || 'netease-youdao/bce-embedding-base_v1'}
              onChange={(e) => onEmbeddingConfigChange({ modelName: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
            >
              <option value="netease-youdao/bce-embedding-base_v1">netease-youdao/bce-embedding-base_v1</option>
            </select>
          </div>
        )}
      </div>

      {/* 检索设置配置 */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
        <div className="flex items-center space-x-2 mb-4">
          <Settings className="w-5 h-5 text-gray-600" />
          <h4 className="text-md font-medium text-gray-900">检索设置</h4>
        </div>
        <p className="text-sm text-gray-600 mb-4">
          了解更多关于检索方法，您可以随时在知识库设置中更改此设置。
        </p>
        
        <div className="space-y-4">
          {/* 向量检索 */}
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
              onChange={(e) => onRetrievalConfigChange({ strategy: e.target.value as 'vector_search' })}
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
                        onChange={(e) => onRetrievalConfigChange({ enableRerank: e.target.checked })}
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
                        onChange={(e) => onRetrievalConfigChange({ rerankModel: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
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
                          onChange={(e) => onRetrievalConfigChange({ topK: parseInt(e.target.value) })}
                          className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm"
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
                          onChange={(e) => onRetrievalConfigChange({ scoreThreshold: parseFloat(e.target.value) })}
                          className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm"
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

          {/* 全文检索 */}
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
              onChange={(e) => onRetrievalConfigChange({ strategy: e.target.value as 'fulltext_search' })}
              className="mr-3 mt-1"
            />
            <div>
              <div className="font-medium text-gray-900">全文检索</div>
              <div className="text-sm text-gray-600 mt-1">
                索引文档中的所有词汇，从而允许用户查询任意词汇，并返回包含这些词汇的文本片段
              </div>
            </div>
          </label>

          {/* 混合检索 */}
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
              onChange={(e) => onRetrievalConfigChange({ strategy: e.target.value as 'hybrid_search' })}
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