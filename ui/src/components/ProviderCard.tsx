import { useState } from 'react';
import { Settings, ChevronRight, HelpCircle } from 'lucide-react';
import { cn } from '../utils/cn';
import ProviderModal from './ProviderModal';
import ModelList from './ModelList';
import { useToast } from '../hooks/useToast';
import Toast from './Toast';

interface Capability {
  name: string;
  color?: string;
}

interface Provider {
  id: string;
  name: string;
  logo?: string;
  capabilities: Capability[];
  tokenLimit?: number;
  tokenUsed?: number;
  status: 'connected' | 'disconnected';
  hasApiKey: boolean;
}

interface ProviderCardProps {
  provider: Provider;
  onSave?: () => void;
}

const getCapabilityStyle = (capability: string) => {
  const styles: Record<string, string> = {
    'LLM': 'bg-blue-100 text-blue-800',
    'TEXT EMBEDDING': 'bg-green-100 text-green-800',
    'SPEECH2TEXT': 'bg-purple-100 text-purple-800',
    'MODERATION': 'bg-orange-100 text-orange-800',
    'TTS': 'bg-pink-100 text-pink-800',
    'RERANK': 'bg-indigo-100 text-indigo-800',
  };
  return styles[capability] || 'bg-gray-100 text-gray-800';
};

export default function ProviderCard({ provider, onSave }: ProviderCardProps) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isModelListExpanded, setIsModelListExpanded] = useState(false);
  const { showSuccess, showError, toasts, removeToast } = useToast();
  const statusColor = provider.status === 'connected' ? 'bg-green-500' : 'bg-red-500';
  
  const handleSettingsClick = () => {
    setIsModalOpen(true);
  };
  
  const handleSave = (success: boolean, message: string) => {
    if (success) {
      showSuccess(message);
      // 刷新父组件数据
      onSave?.();
    } else {
      showError(message);
    }
  };
  
  return (
    <>
      <div className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          {provider.logo ? (
            <img 
              src={provider.logo} 
              alt={provider.name} 
              className="w-8 h-8 object-contain"
              onError={(e) => {
                // 如果图片加载失败，显示默认头像
                const target = e.target as HTMLImageElement;
                target.style.display = 'none';
                const fallback = target.nextElementSibling as HTMLElement;
                if (fallback) fallback.style.display = 'flex';
              }}
            />
          ) : null}
          {/* 默认头像（作为备用） */}
          <div 
            className={`w-8 h-8 bg-gray-200 rounded flex items-center justify-center ${
              provider.logo ? 'hidden' : ''
            }`}
          >
            <span className="text-sm font-medium text-gray-600">
              {provider.name.charAt(0)}
            </span>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">{provider.name}</h3>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500">额度</span>
            <HelpCircle className="w-4 h-4 text-gray-400" />
          </div>
          <div className="text-right">
            <div className="text-sm font-medium text-gray-900">
              {provider.tokenLimit ? `${provider.tokenUsed || 0}消费额度` : '0 Tokens'}
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500">API-KEY</span>
            <div className={cn('w-2 h-2 rounded-full', statusColor)} />
          </div>
          <button 
            onClick={handleSettingsClick}
            className="flex items-center gap-1 px-3 py-1.5 text-sm font-medium text-gray-700 bg-gray-100 rounded hover:bg-gray-200 transition-colors"
          >
            <Settings className="w-4 h-4" />
            设置
          </button>
        </div>
      </div>
      
      <div className="flex flex-wrap gap-2 mb-4">
        {provider.capabilities.map((capability, index) => (
          <span
            key={index}
            className={cn(
              'px-2 py-1 text-xs font-medium rounded',
              getCapabilityStyle(capability.name)
            )}
          >
            {capability.name}
          </span>
        ))}
      </div>
      
      <div className="flex items-center justify-between">
        <ModelList
          provider={{
            id: provider.id,
            name: provider.name,
            hasApiKey: provider.hasApiKey
          }}
          isExpanded={isModelListExpanded}
          onToggle={() => setIsModelListExpanded(!isModelListExpanded)}
        />
        
        <div className="flex items-center gap-2">
          <button className="text-sm text-gray-500 hover:text-gray-700">
            添加模型
          </button>
        </div>
      </div>
      </div>
      
      {/* Toast 通知 */}
      {toasts.map((toast) => (
        <Toast
          key={toast.id}
          message={toast.message}
          type={toast.type}
          isVisible={true}
          onClose={() => removeToast(toast.id)}
        />
      ))}
      
      {/* 模态对话框 */}
      <ProviderModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSave={handleSave}
        provider={provider}
      />
    </>
  );
}