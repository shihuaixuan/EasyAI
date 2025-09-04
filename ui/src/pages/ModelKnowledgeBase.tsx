import React, { useState } from 'react';
import { Brain, Database, Plus, Search, Settings, Trash2, Edit, Upload, Download } from 'lucide-react';
import { cn } from '@/utils/cn';

interface Model {
  id: string;
  name: string;
  type: string;
  status: 'active' | 'inactive';
  description: string;
  createdAt: string;
}

interface KnowledgeBase {
  id: string;
  name: string;
  type: string;
  documentsCount: number;
  status: 'ready' | 'processing';
}

// 模拟数据
const mockModels: Model[] = [
  {
    id: '1',
    name: 'GPT-4',
    type: 'OpenAI',
    status: 'active',
    description: '最新的GPT-4模型，支持多模态输入',
    createdAt: '2024-01-15'
  },
  {
    id: '2',
    name: 'Claude-3',
    type: 'Anthropic',
    status: 'inactive',
    description: 'Claude-3 Sonnet模型，擅长推理和分析',
    createdAt: '2024-01-10'
  }
];

const mockKnowledgeBases: KnowledgeBase[] = [
  {
    id: '1',
    name: '技术文档库',
    type: 'PDF',
    documentsCount: 25,
    status: 'ready'
  },
  {
    id: '2',
    name: '产品手册',
    type: 'Word',
    documentsCount: 12,
    status: 'processing'
  }
];

export default function ModelKnowledgeBase() {
  const [activeTab, setActiveTab] = useState<'models' | 'knowledge'>('models');
  const [models, setModels] = useState<Model[]>(mockModels);
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>(mockKnowledgeBases);
  const [searchTerm, setSearchTerm] = useState('');

  const filteredModels = models.filter(model => 
    model.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    model.type.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filteredKnowledgeBases = knowledgeBases.filter(kb => 
    kb.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    kb.type.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleDeleteModel = (id: string) => {
    setModels(models.filter(model => model.id !== id));
  };

  const handleDeleteKnowledgeBase = (id: string) => {
    setKnowledgeBases(knowledgeBases.filter(kb => kb.id !== id));
  };

  const toggleModelStatus = (id: string) => {
    setModels(models.map(model => 
      model.id === id 
        ? { ...model, status: model.status === 'active' ? 'inactive' : 'active' }
        : model
    ));
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* 页面标题 */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">模型与知识库管理</h1>
        <p className="text-gray-600">管理您的AI模型和知识库资源</p>
      </div>

      {/* 标签页切换 */}
      <div className="mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('models')}
              className={cn(
                'py-2 px-1 border-b-2 font-medium text-sm',
                activeTab === 'models'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              )}
            >
              <Brain className="w-4 h-4 inline mr-2" />
              AI模型
            </button>
            <button
              onClick={() => setActiveTab('knowledge')}
              className={cn(
                'py-2 px-1 border-b-2 font-medium text-sm',
                activeTab === 'knowledge'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              )}
            >
              <Database className="w-4 h-4 inline mr-2" />
              知识库
            </button>
          </nav>
        </div>
      </div>

      {/* 搜索和操作栏 */}
      <div className="mb-6 flex justify-between items-center">
        <div className="relative">
          <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder={`搜索${activeTab === 'models' ? '模型' : '知识库'}...`}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center">
          <Plus className="w-4 h-4 mr-2" />
          添加{activeTab === 'models' ? '模型' : '知识库'}
        </button>
      </div>

      {/* 内容区域 */}
      {activeTab === 'models' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredModels.map((model) => (
            <div key={model.id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center">
                  <Brain className="w-8 h-8 text-blue-600 mr-3" />
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">{model.name}</h3>
                    <p className="text-sm text-gray-500">{model.type}</p>
                  </div>
                </div>
                <div className="flex space-x-2">
                  <button 
                    onClick={() => toggleModelStatus(model.id)}
                    className={cn(
                      'px-2 py-1 rounded-full text-xs font-medium',
                      model.status === 'active'
                        ? 'bg-green-100 text-green-800'
                        : 'bg-gray-100 text-gray-800'
                    )}
                  >
                    {model.status === 'active' ? '活跃' : '停用'}
                  </button>
                </div>
              </div>
              <p className="text-gray-600 text-sm mb-4">{model.description}</p>
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-500">创建于 {model.createdAt}</span>
                <div className="flex space-x-2">
                  <button className="p-1 text-gray-400 hover:text-blue-600">
                    <Edit className="w-4 h-4" />
                  </button>
                  <button className="p-1 text-gray-400 hover:text-gray-600">
                    <Settings className="w-4 h-4" />
                  </button>
                  <button 
                    onClick={() => handleDeleteModel(model.id)}
                    className="p-1 text-gray-400 hover:text-red-600"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredKnowledgeBases.map((kb) => (
            <div key={kb.id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center">
                  <Database className="w-8 h-8 text-green-600 mr-3" />
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">{kb.name}</h3>
                    <p className="text-sm text-gray-500">{kb.type}</p>
                  </div>
                </div>
                <span className={cn(
                  'px-2 py-1 rounded-full text-xs font-medium',
                  kb.status === 'ready'
                    ? 'bg-green-100 text-green-800'
                    : 'bg-yellow-100 text-yellow-800'
                )}>
                  {kb.status === 'ready' ? '就绪' : '处理中'}
                </span>
              </div>
              <div className="mb-4">
                <p className="text-sm text-gray-600 mb-2">
                  文档数量: <span className="font-medium">{kb.documentsCount}</span>
                </p>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex space-x-2">
                  <button className="p-1 text-gray-400 hover:text-blue-600">
                    <Upload className="w-4 h-4" />
                  </button>
                  <button className="p-1 text-gray-400 hover:text-green-600">
                    <Download className="w-4 h-4" />
                  </button>
                </div>
                <div className="flex space-x-2">
                  <button className="p-1 text-gray-400 hover:text-blue-600">
                    <Edit className="w-4 h-4" />
                  </button>
                  <button className="p-1 text-gray-400 hover:text-gray-600">
                    <Settings className="w-4 h-4" />
                  </button>
                  <button 
                    onClick={() => handleDeleteKnowledgeBase(kb.id)}
                    className="p-1 text-gray-400 hover:text-red-600"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* 空状态 */}
      {((activeTab === 'models' && filteredModels.length === 0) || 
        (activeTab === 'knowledge' && filteredKnowledgeBases.length === 0)) && (
        <div className="text-center py-12">
          <div className="mx-auto w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mb-4">
            {activeTab === 'models' ? (
              <Brain className="w-12 h-12 text-gray-400" />
            ) : (
              <Database className="w-12 h-12 text-gray-400" />
            )}
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            没有找到{activeTab === 'models' ? '模型' : '知识库'}
          </h3>
          <p className="text-gray-500 mb-4">
            {searchTerm ? '尝试调整搜索条件' : `开始添加您的第一个${activeTab === 'models' ? '模型' : '知识库'}`}
          </p>
          <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
            添加{activeTab === 'models' ? '模型' : '知识库'}
          </button>
        </div>
      )}
    </div>
  );
}