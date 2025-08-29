import { useState } from 'react';
import { 
  Briefcase, 
  Bot, 
  Users, 
  CreditCard, 
  Database, 
  Puzzle, 
  Settings, 
  Globe, 
  Languages 
} from 'lucide-react';
import { cn } from '../utils/cn';

interface SidebarItem {
  id: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  isActive?: boolean;
}

const sidebarItems: SidebarItem[] = [
  { id: 'workspace', label: '工作空间', icon: Briefcase },
  { id: 'model-providers', label: '模型供应商', icon: Bot, isActive: true },
  { id: 'members', label: '成员', icon: Users },
  { id: 'billing', label: '账单', icon: CreditCard },
  { id: 'data-sources', label: '数据来源', icon: Database },
  { id: 'api-extensions', label: 'API扩展', icon: Puzzle },
  { id: 'customization', label: '定制', icon: Settings },
];

const generalItems: SidebarItem[] = [
  { id: 'general', label: '通用', icon: Globe },
  { id: 'language', label: '语言', icon: Languages },
];

export default function Sidebar() {
  const [activeItem, setActiveItem] = useState('model-providers');

  const renderSidebarItem = (item: SidebarItem) => {
    const Icon = item.icon;
    const isActive = activeItem === item.id;
    
    return (
      <button
        key={item.id}
        onClick={() => setActiveItem(item.id)}
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
        <h1 className="text-lg font-semibold text-gray-900">设置</h1>
      </div>
      
      <nav className="flex-1 px-4 space-y-1">
        {sidebarItems.map(renderSidebarItem)}
        
        <div className="pt-6">
          <div className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-3">
            通用
          </div>
          {generalItems.map(renderSidebarItem)}
        </div>
      </nav>
    </div>
  );
}