import { useEffect } from 'react';
import { 
  Home,
  Briefcase, 
  Bot, 
  Users, 
  CreditCard, 
  Database, 
  Puzzle, 
  Settings, 
  Globe, 
  Languages,
  BookOpen,
  Brain
} from 'lucide-react';
import { useLocation, useNavigate } from 'react-router-dom';
import { ROUTES } from '@/utils/routes';
import { cn } from '../utils/cn';

interface SidebarItem {
  id: string;
  path: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  isActive?: boolean;
}

const mainItems: SidebarItem[] = [
  { id: 'model-knowledge-base', path: ROUTES.MODEL_KNOWLEDGE_BASE, label: '模型知识库', icon: Brain },
  { id: 'dashboard', path: ROUTES.DASHBOARD, label: '仪表板', icon: Home },
  { id: 'model-providers', path: ROUTES.MODEL_PROVIDERS, label: '模型供应商', icon: Bot },
  { id: 'knowledge', path: ROUTES.KNOWLEDGE, label: '知识库', icon: BookOpen },
];

const managementItems: SidebarItem[] = [
  { id: 'workspace', path: ROUTES.WORKSPACE, label: '工作空间', icon: Briefcase },
  { id: 'members', path: ROUTES.MEMBERS, label: '成员', icon: Users },
  { id: 'billing', path: ROUTES.BILLING, label: '账单', icon: CreditCard },
  { id: 'data-sources', path: ROUTES.DATA_SOURCES, label: '数据来源', icon: Database },
  { id: 'api-extensions', path: ROUTES.API_EXTENSIONS, label: 'API扩展', icon: Puzzle },
  { id: 'customization', path: ROUTES.CUSTOMIZATION, label: '定制', icon: Settings },
];

const generalItems: SidebarItem[] = [
  { id: 'general', path: ROUTES.GENERAL, label: '通用', icon: Globe },
  { id: 'language', path: ROUTES.LANGUAGE, label: '语言', icon: Languages },
];

export default function Sidebar() {
  const location = useLocation();
  const navigate = useNavigate();

  const renderSidebarItem = (item: SidebarItem) => {
    const Icon = item.icon;
    const isActive = location.pathname === item.path;
    
    return (
      <button
        key={item.id}
        onClick={() => navigate(item.path)}
        className={cn(
          'w-full flex items-center gap-3 px-3 py-2.5 text-sm font-medium rounded-lg transition-colors',
          isActive 
            ? 'bg-gray-200 text-gray-900' 
            : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
        )}
      >
        <Icon className="w-4 h-4" />
        <span>{item.label}</span>
      </button>
    );
  };

  return (
    <div className="w-64 bg-white border-r border-gray-200 h-full flex flex-col">
      <div className="p-4">
        <h1 className="text-lg font-semibold text-gray-900">EasyAI</h1>
      </div>
      
      <nav className="flex-1 px-4 space-y-1">
        {mainItems.map(renderSidebarItem)}
        
        <div className="pt-6">
          <div className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-3">
            管理
          </div>
          {managementItems.map(renderSidebarItem)}
        </div>
        
        <div className="pt-6">
          <div className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-3">
            设置
          </div>
          {generalItems.map(renderSidebarItem)}
        </div>
      </nav>
    </div>
  );
}