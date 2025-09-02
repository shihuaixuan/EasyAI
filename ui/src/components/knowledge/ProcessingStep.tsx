/**
 * 处理步骤组件
 */

import React from 'react';
import { CheckCircle, Loader, AlertCircle, Play, Settings } from 'lucide-react';
import { cn } from '../../utils/cn';
import { FileUploadResponse } from '../../services/knowledgeService';
import { ChunkingConfigStep, EmbeddingConfigStep, RetrievalConfigStep } from '../../hooks/useKnowledgeWorkflow';

interface ProcessingStepProps {
  uploadResults: FileUploadResponse[];
  chunkingConfig: ChunkingConfigStep;
  embeddingConfig: EmbeddingConfigStep;
  retrievalConfig: RetrievalConfigStep;
  isProcessing: boolean;
  processingResults?: any;
  onStartProcessing: () => Promise<void>;
}

export const ProcessingStep: React.FC<ProcessingStepProps> = ({
  uploadResults,
  chunkingConfig,
  embeddingConfig,
  retrievalConfig,
  isProcessing,
  processingResults,
  onStartProcessing,
}) => {
  const successfulUploads = uploadResults.filter(result => result.success);
  const hasProcessingCompleted = processingResults && !isProcessing;

  const getStrategyDisplayName = (strategy: string, type: 'chunking' | 'embedding' | 'retrieval') => {
    const strategies = {
      chunking: {
        parent_child: '父子分段',
        general: '通用分段'
      },
      embedding: {
        high_quality: '高质量嵌入',
        economic: '经济模式'
      },
      retrieval: {
        vector_search: '向量检索',
        fulltext_search: '全文检索',
        hybrid_search: '混合检索'
      }
    };
    return strategies[type][strategy] || strategy;
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">处理并完成</h3>
        <p className="text-sm text-gray-600 mb-6">
          确认配置信息并开始处理文档。处理完成后，您可以开始使用知识库进行问答。
        </p>
      </div>

      {/* 文件信息概览 */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <h4 className="text-sm font-medium text-gray-900 mb-3">文件信息</h4>
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">上传成功的文件:</span>
            <span className="font-medium">{successfulUploads.length} 个</span>
          </div>
          {successfulUploads.length > 0 && (
            <div className="text-xs text-gray-500">
              {successfulUploads.map(result => result.filename).join(', ')}
            </div>
          )}
        </div>
      </div>

      {/* 配置信息概览 */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <h4 className="text-sm font-medium text-gray-900 mb-3">配置信息</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <div className="text-xs text-gray-500 mb-1">分块策略</div>
            <div className="text-sm font-medium text-gray-900">
              {getStrategyDisplayName(chunkingConfig.strategy, 'chunking')}
            </div>
            <div className="text-xs text-gray-600">
              最大长度: {chunkingConfig.maxLength} 字符
            </div>
          </div>
          
          <div>
            <div className="text-xs text-gray-500 mb-1">嵌入策略</div>
            <div className="text-sm font-medium text-gray-900">
              {getStrategyDisplayName(embeddingConfig.strategy, 'embedding')}
            </div>
            {embeddingConfig.modelName && (
              <div className="text-xs text-gray-600">
                模型: {embeddingConfig.modelName}
              </div>
            )}
          </div>
          
          <div>
            <div className="text-xs text-gray-500 mb-1">检索策略</div>
            <div className="text-sm font-medium text-gray-900">
              {getStrategyDisplayName(retrievalConfig.strategy, 'retrieval')}
            </div>
            <div className="text-xs text-gray-600">
              Top K: {retrievalConfig.topK}
            </div>
          </div>
        </div>
      </div>

      {/* 处理状态 */}
      {!isProcessing && !hasProcessingCompleted && (
        <div className="text-center py-8">
          <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Play className="w-8 h-8 text-blue-600" />
          </div>
          <h4 className="text-lg font-medium text-gray-900 mb-2">准备开始处理</h4>
          <p className="text-sm text-gray-600 mb-6">
            点击下方按钮开始处理文档。根据文件大小和数量，处理时间可能需要几分钟。
          </p>
          <button
            onClick={onStartProcessing}
            disabled={successfulUploads.length === 0}
            className={cn(
              "px-6 py-3 rounded-lg font-medium transition-colors",
              successfulUploads.length === 0
                ? "bg-gray-300 text-gray-500 cursor-not-allowed"
                : "bg-blue-600 text-white hover:bg-blue-700"
            )}
          >
            开始处理文档
          </button>
        </div>
      )}

      {/* 处理中状态 */}
      {isProcessing && (
        <div className="text-center py-8">
          <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Loader className="w-8 h-8 text-blue-600 animate-spin" />
          </div>
          <h4 className="text-lg font-medium text-gray-900 mb-2">正在处理文档</h4>
          <p className="text-sm text-gray-600 mb-4">
            系统正在分析和处理您的文档，请稍等...
          </p>
          
          {/* 处理步骤指示器 */}
          <div className="max-w-md mx-auto">
            <div className="space-y-3">
              <div className="flex items-center justify-between text-sm">
                <span className="flex items-center">
                  <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                  文档解析
                </span>
                <span className="text-green-600">完成</span>
              </div>
              
              <div className="flex items-center justify-between text-sm">
                <span className="flex items-center">
                  <Loader className="w-4 h-4 text-blue-500 mr-2 animate-spin" />
                  文本分块
                </span>
                <span className="text-blue-600">进行中</span>
              </div>
              
              <div className="flex items-center justify-between text-sm">
                <span className="flex items-center">
                  <div className="w-4 h-4 border-2 border-gray-300 rounded-full mr-2" />
                  向量化处理
                </span>
                <span className="text-gray-500">等待中</span>
              </div>
              
              <div className="flex items-center justify-between text-sm">
                <span className="flex items-center">
                  <div className="w-4 h-4 border-2 border-gray-300 rounded-full mr-2" />
                  索引构建
                </span>
                <span className="text-gray-500">等待中</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 处理完成状态 */}
      {hasProcessingCompleted && (
        <div className="text-center py-8">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <CheckCircle className="w-8 h-8 text-green-600" />
          </div>
          <h4 className="text-lg font-medium text-gray-900 mb-2">处理完成！</h4>
          <p className="text-sm text-gray-600 mb-6">
            您的知识库已经准备就绪，现在可以开始使用了。
          </p>
          
          {/* 处理结果摘要 */}
          {processingResults && (
            <div className="max-w-md mx-auto mb-6">
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">处理文档数:</span>
                    <span className="font-medium">{successfulUploads.length}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">生成文本块:</span>
                    <span className="font-medium">-</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">处理时间:</span>
                    <span className="font-medium">-</span>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          <div className="space-y-3">
            <button className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors">
              开始问答测试
            </button>
            <button className="w-full px-6 py-3 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors">
              返回知识库列表
            </button>
          </div>
        </div>
      )}

      {/* 错误状态 */}
      {!isProcessing && !hasProcessingCompleted && successfulUploads.length === 0 && (
        <div className="text-center py-8">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <AlertCircle className="w-8 h-8 text-red-600" />
          </div>
          <h4 className="text-lg font-medium text-gray-900 mb-2">无法开始处理</h4>
          <p className="text-sm text-gray-600 mb-4">
            请先上传至少一个文件才能开始处理。
          </p>
          <button
            onClick={() => window.history.back()}
            className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors"
          >
            返回上一步
          </button>
        </div>
      )}
    </div>
  );
};