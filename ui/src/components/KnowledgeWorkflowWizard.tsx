import React from 'react';
import { ArrowLeft } from 'lucide-react';

interface KnowledgeWorkflowWizardProps {
  knowledgeBaseId: string;
  onComplete: () => void;
  onCancel: () => void;
}

export function KnowledgeWorkflowWizard({ 
  knowledgeBaseId, 
  onComplete, 
  onCancel 
}: KnowledgeWorkflowWizardProps) {
  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-4">
          <button
            onClick={onCancel}
            className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">知识库工作流</h1>
            <p className="text-gray-600 mt-1">配置和上传文件到知识库</p>
          </div>
        </div>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-8">
        <div className="text-center">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            工作流组件开发中
          </h3>
          <p className="text-gray-600 mb-6">
            知识库ID: {knowledgeBaseId}
          </p>
          <div className="flex justify-center space-x-4">
            <button
              onClick={onCancel}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
            >
              返回
            </button>
            <button
              onClick={onComplete}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              完成
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}