/**
 * 知识库详情组件
 */

import React, { useState, useEffect } from 'react';
import { ArrowLeft, FileText, Upload, Trash2, Settings, Download, Calendar, HardDrive } from 'lucide-react';
import { cn } from '../../utils/cn';
import { knowledgeService, KnowledgeBase } from '../../services/knowledgeService';
import { useToast } from '../../hooks/useToast';

interface FileInfo {
  document_id: string;
  filename: string;
  file_size: number;
  file_type: string;
  created_at: string;
  is_processed: boolean;
  chunk_count: number;
  processed_at: string | null;
}

interface KnowledgeBaseDetailProps {
  knowledgeBaseId: string;
  onBack: () => void;
  onUploadMore: () => void;
  onConfigureWorkflow: (knowledgeBaseId: string) => void;
}

export const KnowledgeBaseDetail: React.FC<KnowledgeBaseDetailProps> = ({
  knowledgeBaseId,
  onBack,
  onUploadMore,
  onConfigureWorkflow,
}) => {
  const [knowledgeBase, setKnowledgeBase] = useState<KnowledgeBase | null>(null);
  const [files, setFiles] = useState<FileInfo[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isDeleting, setIsDeleting] = useState<string | null>(null);
  const { addToast } = useToast();

  // 加载知识库详情
  const loadKnowledgeBaseDetail = async () => {
    try {
      setIsLoading(true);
      const [kbDetail, fileList] = await Promise.all([
        knowledgeService.getKnowledgeBase(knowledgeBaseId),
        knowledgeService.getFiles(knowledgeBaseId)
      ]);
      setKnowledgeBase(kbDetail);
      setFiles(fileList.files || []);
    } catch (error) {
      addToast('加载知识库详情失败', 'error');
      console.error('加载知识库详情失败:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // 删除文件
  const handleDeleteFile = async (fileId: string, filename: string) => {
    if (!confirm(`确定要删除文件 "${filename}" 吗？`)) {
      return;
    }

    try {
      setIsDeleting(fileId);
      await knowledgeService.deleteFile(knowledgeBaseId, fileId);
      setFiles(prev => prev.filter(file => file.document_id !== fileId));
      addToast('文件删除成功', 'success');
      // 重新加载知识库详情以更新统计信息
      loadKnowledgeBaseDetail();
    } catch (error) {
      addToast('删除文件失败', 'error');
      console.error('删除文件失败:', error);
    } finally {
      setIsDeleting(null);
    }
  };

  // 配置工作流
  const handleConfigureWorkflow = () => {
    onConfigureWorkflow(knowledgeBaseId);
  };

  // 格式化文件大小
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // 格式化日期时间
  const formatDateTime = (dateString: string): string => {
    const date = new Date(dateString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day} ${hours}:${minutes}`;
  };

  // 获取文件类型图标
  const getFileTypeIcon = (fileType: string) => {
    const type = fileType.toLowerCase();
    if (type.includes('pdf')) return '📄';
    if (type.includes('word') || type.includes('doc')) return '📝';
    if (type.includes('excel') || type.includes('sheet')) return '📊';
    if (type.includes('powerpoint') || type.includes('presentation')) return '📈';
    if (type.includes('text') || type.includes('markdown')) return '📃';
    return '📄';
  };

  useEffect(() => {
    loadKnowledgeBaseDetail();
  }, [knowledgeBaseId]);

  if (isLoading) {
    return (
      <div className="max-w-6xl mx-auto p-6">
        <div className="text-center py-12">
          <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">加载中...</p>
        </div>
      </div>
    );
  }

  if (!knowledgeBase) {
    return (
      <div className="max-w-6xl mx-auto p-6">
        <div className="text-center py-12">
          <p className="text-gray-600">知识库不存在</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* 标题和返回按钮 */}
      <div className="flex items-center gap-2 mb-6">
        <button 
          onClick={onBack}
          className="flex items-center text-gray-600 hover:text-gray-900 transition-colors"
        >
          <ArrowLeft className="w-4 h-4 mr-1" />
          <span>返回</span>
        </button>
      </div>

      {/* 知识库信息卡片 */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center space-x-4">
            <div className="w-16 h-16 bg-blue-100 rounded-lg flex items-center justify-center">
              <FileText className="w-8 h-8 text-blue-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{knowledgeBase.name}</h1>
              <p className="text-gray-600 mt-1">{knowledgeBase.description || '暂无描述'}</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button 
              onClick={onUploadMore}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors flex items-center space-x-2"
            >
              <Upload className="w-4 h-4" />
              <span>上传文件</span>
            </button>
            <button 
              onClick={handleConfigureWorkflow}
              className="p-2 text-gray-400 hover:text-blue-600 transition-colors"
              title="配置工作流"
            >
              <Settings className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* 统计信息 */}
        <div className="grid grid-cols-3 gap-4 pt-4 border-t border-gray-200">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{knowledgeBase.document_count}</div>
            <div className="text-sm text-gray-500">文档数量</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">{files.length}</div>
            <div className="text-sm text-gray-500">文件总数</div>
          </div>
          <div className="text-center">
            <div className={cn(
              "text-2xl font-bold",
              knowledgeBase.is_active ? "text-green-600" : "text-gray-400"
            )}>
              {knowledgeBase.is_active ? '活跃' : '非活跃'}
            </div>
            <div className="text-sm text-gray-500">状态</div>
          </div>
        </div>
      </div>

      {/* 文件列表 */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">文件列表</h2>
          <p className="text-sm text-gray-600 mt-1">管理知识库中的所有文件</p>
        </div>

        {files.length === 0 ? (
          <div className="text-center py-12">
            <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">暂无文件</h3>
            <p className="text-gray-600 mb-6">开始上传文件来构建您的知识库</p>
            <button
              onClick={onUploadMore}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
            >
              上传文件
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-200">
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    文件名
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    大小
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    上传时间
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    状态
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    操作
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {files.map((file) => (
                  <tr key={file.document_id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap text-left">
                      <div className="flex items-center space-x-3">
                        <div className="text-xl">{getFileTypeIcon(file.file_type)}</div>
                        <div className="text-sm font-medium text-gray-900">{file.filename}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-center">
                      <div className="text-sm text-gray-500">
                        {formatFileSize(file.file_size)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-center">
                      <div className="text-sm text-gray-500">
                        {formatDateTime(file.created_at)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-center">
                      <span className={cn(
                        "inline-flex px-2 py-1 rounded-full text-xs font-medium",
                        file.is_processed 
                          ? "bg-green-100 text-green-800" 
                          : "bg-gray-100 text-gray-800"
                      )}>
                        {file.is_processed ? '已处理' : '待处理'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-center">
                      <div className="flex items-center justify-center space-x-2">
                        <button 
                          className="p-2 text-gray-400 hover:text-blue-600 transition-colors"
                          title="下载文件"
                        >
                          <Download className="w-4 h-4" />
                        </button>
                        <button 
                          onClick={handleConfigureWorkflow}
                          className="p-2 text-gray-400 hover:text-green-600 transition-colors"
                          title="配置工作流"
                        >
                          <Settings className="w-4 h-4" />
                        </button>
                        <button 
                          onClick={() => handleDeleteFile(file.document_id, file.filename)}
                          disabled={isDeleting === file.document_id}
                          className="p-2 text-gray-400 hover:text-red-600 transition-colors disabled:opacity-50"
                          title="删除文件"
                        >
                          {isDeleting === file.document_id ? (
                            <div className="w-4 h-4 border border-red-600 border-t-transparent rounded-full animate-spin"></div>
                          ) : (
                            <Trash2 className="w-4 h-4" />
                          )}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};