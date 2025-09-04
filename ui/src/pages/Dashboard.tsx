import { BarChart3, Users, Database, Settings, Plus, TrendingUp } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';
import { ROUTES } from '@/utils/routes';

export default function Dashboard() {
  const { user } = useAuthStore();
  const navigate = useNavigate();

  const stats = [
    {
      title: '模型供应商',
      value: '5',
      change: '+2',
      changeType: 'positive' as const,
      icon: Database,
      color: 'bg-blue-500'
    },
    {
      title: '知识库',
      value: '12',
      change: '+3',
      changeType: 'positive' as const,
      icon: BarChart3,
      color: 'bg-green-500'
    },
    {
      title: '活跃用户',
      value: '8',
      change: '+1',
      changeType: 'positive' as const,
      icon: Users,
      color: 'bg-purple-500'
    },
    {
      title: '系统状态',
      value: '正常',
      change: '99.9%',
      changeType: 'positive' as const,
      icon: TrendingUp,
      color: 'bg-orange-500'
    }
  ];

  const quickActions = [
    {
      title: '添加模型供应商',
      description: '配置新的AI模型供应商',
      icon: Plus,
      action: () => navigate(ROUTES.MODEL_PROVIDERS),
      color: 'bg-blue-500'
    },
    {
      title: '创建知识库',
      description: '构建新的知识库',
      icon: Database,
      action: () => navigate(ROUTES.KNOWLEDGE),
      color: 'bg-green-500'
    },
    {
      title: '系统设置',
      description: '管理系统配置',
      icon: Settings,
      action: () => navigate(ROUTES.GENERAL),
      color: 'bg-purple-500'
    }
  ];

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* 欢迎区域 */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          欢迎回来，{user?.username}！
        </h1>
        <p className="text-gray-600">
          这里是您的EasyAI控制台，管理您的AI模型和知识库。
        </p>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <div key={index} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <div className={`w-12 h-12 ${stat.color} rounded-lg flex items-center justify-center`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
                <span className={`text-sm font-medium px-2 py-1 rounded-full ${
                  stat.changeType === 'positive' 
                    ? 'text-green-700 bg-green-100' 
                    : 'text-red-700 bg-red-100'
                }`}>
                  {stat.change}
                </span>
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-1">{stat.value}</h3>
              <p className="text-gray-600 text-sm">{stat.title}</p>
            </div>
          );
        })}
      </div>

      {/* 快速操作 */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">快速操作</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {quickActions.map((action, index) => {
            const Icon = action.icon;
            return (
              <button
                key={index}
                onClick={action.action}
                className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 text-left hover:shadow-md transition-shadow group"
              >
                <div className={`w-12 h-12 ${action.color} rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{action.title}</h3>
                <p className="text-gray-600 text-sm">{action.description}</p>
              </button>
            );
          })}
        </div>
      </div>

      {/* 最近活动 */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">最近活动</h2>
        <div className="space-y-4">
          <div className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg">
            <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center">
              <Database className="w-5 h-5 text-white" />
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900">添加了新的模型供应商</p>
              <p className="text-xs text-gray-500">2小时前</p>
            </div>
          </div>
          
          <div className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg">
            <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center">
              <BarChart3 className="w-5 h-5 text-white" />
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900">创建了新的知识库</p>
              <p className="text-xs text-gray-500">5小时前</p>
            </div>
          </div>
          
          <div className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg">
            <div className="w-10 h-10 bg-purple-500 rounded-full flex items-center justify-center">
              <Settings className="w-5 h-5 text-white" />
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900">更新了系统配置</p>
              <p className="text-xs text-gray-500">1天前</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}