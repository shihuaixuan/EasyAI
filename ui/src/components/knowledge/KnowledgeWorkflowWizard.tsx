/**
 * 知识库工作流向导组件
 */

import React from 'react';
import { ArrowLeft, ArrowRight } from 'lucide-react';
import { cn } from '../../utils/cn';
import { useKnowledgeWorkflow } from '../../hooks/useKnowledgeWorkflow';
import { FileUploadStep } from './FileUploadStep';
import { ConfigurationStep } from './ConfigurationStep';
import { ProcessingStep } from './ProcessingStep';

interface StepIndicatorProps {
  currentStep: number;
  steps: { label: string; step: number }[];
}

const StepIndicator: React.FC<StepIndicatorProps> = ({ currentStep, steps }) => {
  return (
    <div className="flex items-center justify-center mb-8">
      {steps.map((step, index) => (
        <div key={step.step} className="flex items-center">
          <div className="flex flex-col items-center">
            <div className={cn(
              "w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-colors",
              step.step === currentStep 
                ? "bg-blue-500 text-white" 
                : step.step < currentStep 
                ? "bg-green-500 text-white"
                : "bg-gray-200 text-gray-500"
            )}>
              {step.step}
            </div>
            <span className={cn(
              "text-xs font-medium mt-2 text-center",
              step.step === currentStep ? "text-blue-600" : "text-gray-600"
            )}>
              {step.label}
            </span>
          </div>
          {index < steps.length - 1 && (
            <div className={cn(
              "w-16 h-px mx-4 transition-colors",
              step.step < currentStep ? "bg-green-500" : "bg-gray-300"
            )} />
          )}
        </div>
      ))}
    </div>
  );
};

interface KnowledgeWorkflowWizardProps {
  knowledgeBaseId: string;
  onComplete?: () => void;
  onCancel?: () => void;
  initialStep?: number;
  initialConfig?: any;
  mode?: 'upload' | 'settings'; // 新增模式属性
}

export const KnowledgeWorkflowWizard: React.FC<KnowledgeWorkflowWizardProps> = ({
  knowledgeBaseId,
  onComplete,
  onCancel,
  initialStep = 1,
  initialConfig,
  mode = 'upload', // 默认为上传模式
}) => {
  const {
    state,
    updateFileUpload,
    updateChunkingConfig,
    updateEmbeddingConfig,
    updateRetrievalConfig,
    nextStep,
    prevStep,
    handleFileSelect,
    uploadFiles,
    startProcessing,
    canProceedToNextStep,
  } = useKnowledgeWorkflow(knowledgeBaseId, initialStep, initialConfig);

  // 根据模式调整步骤
  const steps = mode === 'settings' 
    ? [
        { label: '配置参数', step: 2 },
        { label: '处理完成', step: 3 },
      ]
    : [
        { label: '上传文件', step: 1 },
        { label: '配置参数', step: 2 },
        { label: '处理完成', step: 3 },
      ];

  const handleRemoveFile = (index: number) => {
    const newFiles = state.fileUpload.uploadedFiles.filter((_, i) => i !== index);
    const newResults = state.fileUpload.uploadResults.filter(result => 
      newFiles.some(file => file.name === result.filename)
    );
    updateFileUpload({ 
      uploadedFiles: newFiles, 
      uploadResults: newResults 
    });
  };

  const handleUpload = async () => {
    await uploadFiles();
  };

  const handleNext = async () => {
    if (state.currentStep === 1) {
      // 第一步：确保文件已上传
      if (state.fileUpload.uploadResults.length === 0 && state.fileUpload.uploadedFiles.length > 0) {
        await uploadFiles();
      }
      if (canProceedToNextStep()) {
        nextStep();
      }
    } else if (state.currentStep === 2) {
      // 第二步：进入处理步骤
      nextStep();
    }
  };

  const handleStartProcessing = async () => {
    try {
      await startProcessing();
      if (onComplete) {
        onComplete();
      }
    } catch (error) {
      console.error('处理失败:', error);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* 标题和面包屑 */}
      <div className="flex items-center space-x-4 mb-8">
        <button
          onClick={onCancel}
          className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            {mode === 'settings' ? '修改知识库配置' : '创建知识库'}
          </h1>
          <p className="text-gray-600 mt-1">
            {mode === 'settings' 
              ? '调整知识库的分块配置参数，索引方式和检索设置为只读状态' 
              : '上传文档并配置处理参数，构建您的专属知识库'
            }
          </p>
        </div>
      </div>

      {/* 步骤指示器 */}
      <StepIndicator currentStep={state.currentStep} steps={steps} />

      {/* 步骤内容 */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        {/* 只在上传模式下显示文件上传步骤 */}
        {mode === 'upload' && state.currentStep === 1 && (
          <FileUploadStep
            uploadedFiles={state.fileUpload.uploadedFiles}
            uploadResults={state.fileUpload.uploadResults}
            isUploading={state.fileUpload.isUploading}
            onFileSelect={handleFileSelect}
            onUpload={handleUpload}
            onRemoveFile={handleRemoveFile}
          />
        )}

        {state.currentStep === 2 && (
          <ConfigurationStep
            chunkingConfig={state.chunkingConfig}
            embeddingConfig={state.embeddingConfig}
            retrievalConfig={state.retrievalConfig}
            onChunkingConfigChange={updateChunkingConfig}
            onEmbeddingConfigChange={updateEmbeddingConfig}
            onRetrievalConfigChange={updateRetrievalConfig}
            mode={mode} // 传递模式给配置步骤
          />
        )}

        {state.currentStep === 3 && (
          <ProcessingStep
            uploadResults={state.fileUpload.uploadResults}
            chunkingConfig={state.chunkingConfig}
            embeddingConfig={state.embeddingConfig}
            retrievalConfig={state.retrievalConfig}
            isProcessing={state.isProcessing}
            processingResults={state.processingResults}
            onStartProcessing={handleStartProcessing}
          />
        )}
      </div>

      {/* 导航按钮 */}
      <div className="flex justify-between">
        <button
          onClick={prevStep}
          disabled={(mode === 'upload' && state.currentStep === 1) || (mode === 'settings' && state.currentStep === 2) || state.isProcessing}
          className={cn(
            "px-6 py-2 rounded-lg font-medium transition-colors flex items-center",
            (mode === 'upload' && state.currentStep === 1) || (mode === 'settings' && state.currentStep === 2) || state.isProcessing
              ? "bg-gray-100 text-gray-400 cursor-not-allowed"
              : "bg-gray-200 text-gray-700 hover:bg-gray-300"
          )}
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          上一步
        </button>

        {state.currentStep < 3 && (
          <button
            onClick={handleNext}
            disabled={!canProceedToNextStep() || state.isProcessing}
            className={cn(
              "px-6 py-2 rounded-lg font-medium transition-colors flex items-center",
              !canProceedToNextStep() || state.isProcessing
                ? "bg-gray-300 text-gray-500 cursor-not-allowed"
                : "bg-blue-600 text-white hover:bg-blue-700"
            )}
          >
            下一步
            <ArrowRight className="w-4 h-4 ml-2" />
          </button>
        )}

        {state.currentStep === 3 && state.processingResults && (
          <button
            onClick={onComplete}
            className="px-6 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition-colors"
          >
            完成
          </button>
        )}
      </div>
    </div>
  );
};