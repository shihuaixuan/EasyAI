/**
 * 文件上传步骤组件
 */

import React, { useState } from 'react';
import { Upload, File, X, CheckCircle, AlertCircle, Loader } from 'lucide-react';
import { cn } from '../../utils/cn';
import { FileUploadResponse } from '../../services/knowledgeService';

interface FileUploadStepProps {
  uploadedFiles: File[];
  uploadResults: FileUploadResponse[];
  isUploading: boolean;
  onFileSelect: (files: FileList) => void;
  onUpload: () => Promise<void>;
  onRemoveFile: (index: number) => void;
}

export const FileUploadStep: React.FC<FileUploadStepProps> = ({
  uploadedFiles,
  uploadResults,
  isUploading,
  onFileSelect,
  onUpload,
  onRemoveFile,
}) => {
  const [isDragging, setIsDragging] = useState(false);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      onFileSelect(files);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      onFileSelect(files);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getUploadResult = (filename: string) => {
    return uploadResults.find(result => result.filename === filename);
  };

  const hasSuccessfulUploads = uploadResults.some(result => result.success);

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">上传文档文件</h3>
        
        {/* 文件拖拽上传区域 */}
        <div
          className={cn(
            "border-2 border-dashed rounded-lg p-8 text-center transition-colors",
            isDragging 
              ? "border-blue-500 bg-blue-50" 
              : "border-gray-300 bg-gray-50 hover:border-gray-400"
          )}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
        >
          <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <div className="text-gray-600 mb-2">
            <span className="font-medium">拖拽文件至此</span>
            <span className="mx-2">，或者</span>
            <label className="text-blue-600 font-medium cursor-pointer hover:text-blue-700">
              选择文件
              <input
                type="file"
                className="hidden"
                multiple
                accept=".txt,.md,.mdx,.pdf,.html,.xlsx,.xls,.vtt,.properties,.doc,.docx,.csv,.eml,.msg,.pptx,.xml,.epub,.ppt,.htm"
                onChange={handleFileInput}
                disabled={isUploading}
              />
            </label>
          </div>
          <p className="text-sm text-gray-500">
            支持 TXT、MARKDOWN、PDF、WORD、EXCEL、PPT 等格式，每个文件不超过 15MB
          </p>
        </div>
      </div>

      {/* 已选择的文件列表 */}
      {uploadedFiles.length > 0 && (
        <div className="space-y-4">
          <h4 className="text-sm font-medium text-gray-900">已选择的文件 ({uploadedFiles.length})</h4>
          <div className="space-y-2">
            {uploadedFiles.map((file, index) => {
              const result = getUploadResult(file.name);
              return (
                <div
                  key={index}
                  className="flex items-center justify-between p-3 bg-white border border-gray-200 rounded-lg"
                >
                  <div className="flex items-center space-x-3">
                    <File className="w-5 h-5 text-gray-400" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">{file.name}</p>
                      <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    {/* 上传状态指示器 */}
                    {isUploading && !result && (
                      <Loader className="w-4 h-4 text-blue-500 animate-spin" />
                    )}
                    
                    {result && result.success && (
                      <CheckCircle className="w-4 h-4 text-green-500" />
                    )}
                    
                    {result && !result.success && (
                      <div title={result.error_message || '上传失败'}>
                        <AlertCircle className="w-4 h-4 text-red-500" />
                      </div>
                    )}
                    
                    {!isUploading && (
                      <button
                        onClick={() => onRemoveFile(index)}
                        className="p-1 text-gray-400 hover:text-red-500 transition-colors"
                        title="移除文件"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* 上传按钮和状态 */}
      {uploadedFiles.length > 0 && (
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-600">
            {uploadResults.length > 0 && (
              <span>
                已处理: {uploadResults.filter(r => r.success).length} 成功, {uploadResults.filter(r => !r.success).length} 失败
              </span>
            )}
          </div>
          
          <button
            onClick={onUpload}
            disabled={isUploading || uploadResults.length === uploadedFiles.length}
            className={cn(
              "px-6 py-2 rounded-lg font-medium transition-colors",
              isUploading || uploadResults.length === uploadedFiles.length
                ? "bg-gray-300 text-gray-500 cursor-not-allowed"
                : "bg-blue-600 text-white hover:bg-blue-700"
            )}
          >
            {isUploading ? (
              <span className="flex items-center space-x-2">
                <Loader className="w-4 h-4 animate-spin" />
                <span>上传中...</span>
              </span>
            ) : uploadResults.length === uploadedFiles.length ? (
              "上传完成"
            ) : (
              "开始上传"
            )}
          </button>
        </div>
      )}

      {/* 上传错误信息 */}
      {uploadResults.some(result => !result.success) && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h5 className="text-sm font-medium text-red-800 mb-2">上传失败的文件:</h5>
          <div className="space-y-1">
            {uploadResults
              .filter(result => !result.success)
              .map((result, index) => (
                <p key={index} className="text-xs text-red-700">
                  {result.filename}: {result.error_message}
                </p>
              ))}
          </div>
        </div>
      )}

      {/* 成功提示 */}
      {hasSuccessfulUploads && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <p className="text-sm text-green-800">
            文件上传成功！您可以继续进行下一步配置。
          </p>
        </div>
      )}
    </div>
  );
};