import { useState, useEffect } from 'react';
import { ArrowLeft, Plus, Database, FileText, Settings, Search } from 'lucide-react';
import { cn } from '../utils/cn';
import { useToast } from '../hooks/useToast';
import { knowledgeService, KnowledgeBase, CreateKnowledgeBaseRequest } from '../services/knowledgeService';
import { KnowledgeWorkflowWizard } from '../components/knowledge/KnowledgeWorkflowWizard';

type ViewMode = 'list' | 'create' | 'workflow';

interface CreateKnowledgeBaseModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (request: CreateKnowledgeBaseRequest) => Promise<void>;
  isLoading: boolean;
}

function CreateKnowledgeBaseModal({ isOpen, onClose, onSubmit, isLoading }: CreateKnowledgeBaseModalProps) {
  const [formData, setFormData] = useState({
    name: '',
    description: ''
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name.trim()) return;
    
    await onSubmit(formData);
    setFormData({ name: '', description: '' });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 className="text-lg font-medium text-gray-900 mb-4">创建知识库</h3>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              知识库名称 *
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="输入知识库名称"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              描述
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="输入知识库描述（可选）"
              rows={3}
            />
          </div>
          
          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              disabled={isLoading}
              className="px-4 py-2 text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
            >
              取消
            </button>
            <button
              type="submit"
              disabled={isLoading || !formData.name.trim()}
              className={cn(
                "px-4 py-2 rounded-md font-medium transition-colors",
                isLoading || !formData.name.trim()
                  ? "bg-gray-300 text-gray-500 cursor-not-allowed"
                  : "bg-blue-600 text-white hover:bg-blue-700"
              )}
            >
              {isLoading ? '创建中...' : '创建'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

interface KnowledgeBaseCardProps {
  knowledgeBase: KnowledgeBase;
  onSelect: (knowledgeBase: KnowledgeBase) => void;
}

function KnowledgeBaseCard({ knowledgeBase, onSelect }: KnowledgeBaseCardProps) {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow cursor-pointer"
         onClick={() => onSelect(knowledgeBase)}>
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
            <Database className="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <h3 className="text-lg font-medium text-gray-900">{knowledgeBase.name}</h3>
            <p className="text-sm text-gray-600">{knowledgeBase.description || '暂无描述'}</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <button className="p-2 text-gray-400 hover:text-gray-600 transition-colors">
            <Settings className="w-4 h-4" />
          </button>
        </div>
      </div>
      
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <span className="text-gray-500">文档数量:</span>
          <span className="ml-2 font-medium">{knowledgeBase.document_count}</span>
        </div>
        <div>
          <span className="text-gray-500">文本块:</span>
          <span className="ml-2 font-medium">{knowledgeBase.chunk_count}</span>
        </div>
      </div>
      
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>创建时间: {new Date(knowledgeBase.created_at).toLocaleDateString()}</span>
          <span className={cn(
            "px-2 py-1 rounded-full",
            knowledgeBase.is_active 
              ? "bg-green-100 text-green-800" 
              : "bg-gray-100 text-gray-800"
          )}>
            {knowledgeBase.is_active ? '活跃' : '非活跃'}
          </span>
        </div>
      </div>
    </div>
  );
}

export default function Knowledge() {
  const [viewMode, setViewMode] = useState<ViewMode>('list');
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([]);
  const [selectedKnowledgeBase, setSelectedKnowledgeBase] = useState<KnowledgeBase | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const { addToast } = useToast();

  // 加载知识库列表
  const loadKnowledgeBases = async () => {
    try {
      setIsLoading(true);
      const response = await knowledgeService.getKnowledgeBases();
      setKnowledgeBases(response.knowledge_bases);
    } catch (error) {
      addToast('加载知识库列表失败', 'error');
      console.error('加载知识库列表失败:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // 创建知识库
  const handleCreateKnowledgeBase = async (request: CreateKnowledgeBaseRequest) => {
    try {
      setIsLoading(true);
      const newKnowledgeBase = await knowledgeService.createKnowledgeBase(request);
      setKnowledgeBases(prev => [newKnowledgeBase, ...prev]);
      setIsCreateModalOpen(false);
      addToast('知识库创建成功', 'success');
    } catch (error) {
      addToast(`创建失败: ${error instanceof Error ? error.message : '未知错误'}`, 'error');
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  // 选择知识库并进入工作流
  const handleSelectKnowledgeBase = (knowledgeBase: KnowledgeBase) => {
    setSelectedKnowledgeBase(knowledgeBase);
    setViewMode('workflow');
  };

  // 完成工作流
  const handleWorkflowComplete = () => {
    setViewMode('list');
    setSelectedKnowledgeBase(null);
    loadKnowledgeBases(); // 重新加载列表
  };

  // 取消工作流
  const handleWorkflowCancel = () => {
    setViewMode('list');
    setSelectedKnowledgeBase(null);
  };

  // 过滤知识库
  const filteredKnowledgeBases = knowledgeBases.filter(kb =>
    kb.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (kb.description && kb.description.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  useEffect(() => {
    if (viewMode === 'list') {
      loadKnowledgeBases();
    }
  }, [viewMode]);

  // 工作流视图
  if (viewMode === 'workflow' && selectedKnowledgeBase) {
    return (
      <KnowledgeWorkflowWizard
        knowledgeBaseId={selectedKnowledgeBase.knowledge_base_id}
        onComplete={handleWorkflowComplete}
        onCancel={handleWorkflowCancel}
      />
    );
  }

  // 知识库列表视图
  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* 页面标题 */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">知识库</h1>
          <p className="text-gray-600 mt-1">管理和构建您的知识库，支持文档上传和智能问答</p>
        </div>
        <button
          onClick={() => setIsCreateModalOpen(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors flex items-center space-x-2"
        >
          <Plus className="w-4 h-4" />
          <span>新建知识库</span>
        </button>
      </div>

      {/* 搜索栏 */}
      <div className="relative mb-6">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input
          type="text"
          placeholder="搜索知识库..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* 知识库列表 */}
      {isLoading ? (
        <div className="text-center py-12">
          <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">加载中...</p>
        </div>
      ) : filteredKnowledgeBases.length === 0 ? (
        <div className="text-center py-12">
          <Database className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            {searchQuery ? '未找到匹配的知识库' : '还没有知识库'}
          </h3>
          <p className="text-gray-600 mb-6">
            {searchQuery ? '尝试使用不同的关键词搜索' : '创建您的第一个知识库开始使用'}
          </p>
          {!searchQuery && (
            <button
              onClick={() => setIsCreateModalOpen(true)}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
            >
              创建知识库
            </button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredKnowledgeBases.map((kb) => (
            <KnowledgeBaseCard
              key={kb.knowledge_base_id}
              knowledgeBase={kb}
              onSelect={handleSelectKnowledgeBase}
            />
          ))}
        </div>
      )}

      {/* 创建知识库模态框 */}
      <CreateKnowledgeBaseModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSubmit={handleCreateKnowledgeBase}
        isLoading={isLoading}
      />
    </div>
  );
}