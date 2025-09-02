/**
 * 知识库工作流管理Hook
 */

import { useState, useCallback } from 'react';
import { knowledgeService, WorkflowConfig, FileUploadResponse } from '../services/knowledgeService';
import { useToast } from './useToast';

export interface FileUploadStep {
  uploadedFiles: File[];
  uploadResults: FileUploadResponse[];
  isUploading: boolean;
  uploadProgress: Record<string, number>;
}

export interface ChunkingConfigStep {
  strategy: 'parent_child' | 'general';
  separator: string;
  maxLength: number;
  overlapLength: number;
  removeExtraWhitespace: boolean;
  removeUrls: boolean;
  removeEmails: boolean;  // 新增独立的邮箱删除选项
  // 父子分段特有配置
  parentSeparator?: string;
  parentMaxLength?: number;
  childSeparator?: string;
  childMaxLength?: number;
}

export interface EmbeddingConfigStep {
  strategy: 'high_quality' | 'economic';
  modelName?: string;
}

export interface RetrievalConfigStep {
  strategy: 'vector_search' | 'fulltext_search' | 'hybrid_search';
  topK: number;
  scoreThreshold: number;
  enableRerank: boolean;
  rerankModel?: string;
}

export interface KnowledgeWorkflowState {
  currentStep: number;
  knowledgeBaseId?: string;
  fileUpload: FileUploadStep;
  chunkingConfig: ChunkingConfigStep;
  embeddingConfig: EmbeddingConfigStep;
  retrievalConfig: RetrievalConfigStep;
  isProcessing: boolean;
  processingResults?: any;
}

const defaultChunkingConfig: ChunkingConfigStep = {
  strategy: 'general',
  separator: '\n\n',
  maxLength: 1024,
  overlapLength: 50,
  removeExtraWhitespace: false,
  removeUrls: false,
  removeEmails: false,  // 新增默认值
};

const defaultEmbeddingConfig: EmbeddingConfigStep = {
  strategy: 'high_quality',
};

const defaultRetrievalConfig: RetrievalConfigStep = {
  strategy: 'vector_search',
  topK: 10,
  scoreThreshold: 0.0,
  enableRerank: false,
};

export const useKnowledgeWorkflow = (initialKnowledgeBaseId?: string) => {
  const { addToast } = useToast();
  
  const [state, setState] = useState<KnowledgeWorkflowState>({
    currentStep: 1,
    knowledgeBaseId: initialKnowledgeBaseId,
    fileUpload: {
      uploadedFiles: [],
      uploadResults: [],
      isUploading: false,
      uploadProgress: {},
    },
    chunkingConfig: defaultChunkingConfig,
    embeddingConfig: defaultEmbeddingConfig,
    retrievalConfig: defaultRetrievalConfig,
    isProcessing: false,
  });

  // 更新文件上传状态
  const updateFileUpload = useCallback((fileUpload: Partial<FileUploadStep>) => {
    setState(prev => ({
      ...prev,
      fileUpload: { ...prev.fileUpload, ...fileUpload },
    }));
  }, []);

  // 更新分块配置
  const updateChunkingConfig = useCallback((chunkingConfig: Partial<ChunkingConfigStep>) => {
    setState(prev => ({
      ...prev,
      chunkingConfig: { ...prev.chunkingConfig, ...chunkingConfig },
    }));
  }, []);

  // 更新嵌入配置
  const updateEmbeddingConfig = useCallback((embeddingConfig: Partial<EmbeddingConfigStep>) => {
    setState(prev => ({
      ...prev,
      embeddingConfig: { ...prev.embeddingConfig, ...embeddingConfig },
    }));
  }, []);

  // 更新检索配置
  const updateRetrievalConfig = useCallback((retrievalConfig: Partial<RetrievalConfigStep>) => {
    setState(prev => ({
      ...prev,
      retrievalConfig: { ...prev.retrievalConfig, ...retrievalConfig },
    }));
  }, []);

  // 设置知识库ID
  const setKnowledgeBaseId = useCallback((knowledgeBaseId: string) => {
    setState(prev => ({ ...prev, knowledgeBaseId }));
  }, []);

  // 下一步
  const nextStep = useCallback(() => {
    setState(prev => ({
      ...prev,
      currentStep: Math.min(prev.currentStep + 1, 3),
    }));
  }, []);

  // 上一步
  const prevStep = useCallback(() => {
    setState(prev => ({
      ...prev,
      currentStep: Math.max(prev.currentStep - 1, 1),
    }));
  }, []);

  // 重置工作流
  const resetWorkflow = useCallback(() => {
    setState(prev => ({
      ...prev,
      currentStep: 1,
      fileUpload: {
        uploadedFiles: [],
        uploadResults: [],
        isUploading: false,
        uploadProgress: {},
      },
      chunkingConfig: defaultChunkingConfig,
      embeddingConfig: defaultEmbeddingConfig,
      retrievalConfig: defaultRetrievalConfig,
      isProcessing: false,
      processingResults: undefined,
    }));
  }, []);

  // 处理文件选择
  const handleFileSelect = useCallback((files: FileList) => {
    const fileArray = Array.from(files);
    updateFileUpload({ uploadedFiles: fileArray });
  }, [updateFileUpload]);

  // 上传文件
  const uploadFiles = useCallback(async () => {
    if (!state.knowledgeBaseId || state.fileUpload.uploadedFiles.length === 0) {
      addToast('请先选择文件', 'error');
      return;
    }

    updateFileUpload({ isUploading: true, uploadProgress: {} });

    try {
      const result = await knowledgeService.uploadFiles(
        state.knowledgeBaseId,
        state.fileUpload.uploadedFiles
      );

      updateFileUpload({
        isUploading: false,
        uploadResults: [...result.successful_uploads, ...result.failed_uploads],
      });

      if (result.success_count > 0) {
        addToast(`成功上传 ${result.success_count} 个文件`, 'success');
      }

      if (result.error_count > 0) {
        addToast(`${result.error_count} 个文件上传失败`, 'error');
      }

      return result;
    } catch (error) {
      updateFileUpload({ isUploading: false });
      addToast(`文件上传失败: ${error instanceof Error ? error.message : '未知错误'}`, 'error');
      throw error;
    }
  }, [state.knowledgeBaseId, state.fileUpload.uploadedFiles, updateFileUpload, addToast]);

  // 保存配置并开始处理
  const startProcessing = useCallback(async () => {
    if (!state.knowledgeBaseId) {
      addToast('请先选择知识库', 'error');
      return;
    }

    setState(prev => ({ ...prev, isProcessing: true }));

    try {
      // 构建配置对象
      const config: WorkflowConfig = {
        chunking: {
          strategy: state.chunkingConfig.strategy,
          separator: state.chunkingConfig.separator,
          max_length: state.chunkingConfig.maxLength,
          overlap_length: state.chunkingConfig.overlapLength,
          remove_extra_whitespace: state.chunkingConfig.removeExtraWhitespace,
          remove_urls: state.chunkingConfig.removeUrls,
          remove_emails: state.chunkingConfig.removeEmails,  // 新增字段
        },
        embedding: {
          strategy: state.embeddingConfig.strategy,
          model_name: state.embeddingConfig.modelName,
        },
        retrieval: {
          strategy: state.retrievalConfig.strategy,
          top_k: state.retrievalConfig.topK,
          score_threshold: state.retrievalConfig.scoreThreshold,
          enable_rerank: state.retrievalConfig.enableRerank,
          rerank_model: state.retrievalConfig.rerankModel,
        },
      };

      // 添加父子分段特有配置
      if (state.chunkingConfig.strategy === 'parent_child') {
        config.chunking.parent_separator = state.chunkingConfig.parentSeparator;
        config.chunking.parent_max_length = state.chunkingConfig.parentMaxLength;
        config.chunking.child_separator = state.chunkingConfig.childSeparator;
        config.chunking.child_max_length = state.chunkingConfig.childMaxLength;
      }

      // 保存配置
      const result = await knowledgeService.updateWorkflowConfig(state.knowledgeBaseId, config);

      setState(prev => ({
        ...prev,
        isProcessing: false,
        processingResults: result,
      }));

      addToast('配置保存成功，开始处理文档...', 'success');
      return result;
    } catch (error) {
      setState(prev => ({ ...prev, isProcessing: false }));
      addToast(`处理失败: ${error instanceof Error ? error.message : '未知错误'}`, 'error');
      throw error;
    }
  }, [
    state.knowledgeBaseId,
    state.chunkingConfig,
    state.embeddingConfig,
    state.retrievalConfig,
    addToast,
  ]);

  // 验证当前步骤是否可以继续
  const canProceedToNextStep = useCallback(() => {
    switch (state.currentStep) {
      case 1: // 文件上传步骤
        return state.fileUpload.uploadResults.some(result => result.success);
      case 2: // 配置步骤
        return true; // 配置步骤始终可以继续
      case 3: // 处理步骤
        return false; // 处理步骤是最后一步
      default:
        return false;
    }
  }, [state.currentStep, state.fileUpload.uploadResults]);

  return {
    state,
    updateFileUpload,
    updateChunkingConfig,
    updateEmbeddingConfig,
    updateRetrievalConfig,
    setKnowledgeBaseId,
    nextStep,
    prevStep,
    resetWorkflow,
    handleFileSelect,
    uploadFiles,
    startProcessing,
    canProceedToNextStep,
  };
};