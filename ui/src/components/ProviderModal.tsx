import { useState, useEffect } from 'react';
import { X, ExternalLink } from 'lucide-react';
import { cn } from '../utils/cn';
import { saveProvider, SaveProviderRequest, getProviderConfig, ProviderResponse } from '../services/providerService';
import { useAuthStore } from '../stores/authStore';

interface ProviderModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave?: (success: boolean, message: string) => void;
  provider: {
    id: string;
    name: string;
  };
}

export default function ProviderModal({ isOpen, onClose, onSave, provider }: ProviderModalProps) {
  const [formData, setFormData] = useState({
    apiKey: '',
    organizationId: '',
    apiBase: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isExistingConfig, setIsExistingConfig] = useState(false); // 标记是否为已存在配置
  const { user } = useAuthStore();
  
  // 获取访问令牌
  const getAccessToken = () => {
    return localStorage.getItem('auth_token');
  };

  // 当模态框打开时，初始化配置和加载已保存的数据
  useEffect(() => {
    if (isOpen) {
      const loadProviderConfig = async () => {
        const config = getProviderConfigLocal();
        
        // 加载已保存的配置
        try {
          const token = getAccessToken();
          if (!token) {
            console.warn('未找到访问令牌，跳过加载已保存配置');
            return;
          }
          
          const existingConfig: ProviderResponse | null = await getProviderConfig(token, provider.id);
          
          if (existingConfig) {
            setFormData({
              apiKey: existingConfig.api_key_masked || '',  // 显示掉码API Key
              organizationId: '', // 组织ID不在后端存储，保持为空
              apiBase: existingConfig.base_url || config.apiBaseDefault
            });
            setIsExistingConfig(true);
          } else {
            // 新配置，使用默认值
            setFormData(prev => ({
              ...prev,
              apiBase: prev.apiBase || config.apiBaseDefault
            }));
            setIsExistingConfig(false);
          }
        } catch (error) {
          console.error('加载提供商配置失败:', error);
          // 加载失败时使用默认配置
          const config = getProviderConfigLocal();
          setFormData(prev => ({
            ...prev,
            apiBase: prev.apiBase || config.apiBaseDefault
          }));
          setIsExistingConfig(false);
        }
      };
      
      loadProviderConfig();
    }
  }, [isOpen, provider.id]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    
    try {
      const config = getProviderConfigLocal();
      
      // 构建请求数据
      if (!user?.id) {
        throw new Error('请先登录');
      }
      
      const request: SaveProviderRequest = {
        user_id: user.id, // 直接使用字符串ID（UUID格式）
        provider: provider.id,
        api_key: formData.apiKey,
        base_url: formData.apiBase || config.apiBaseDefault
      };
      
      // 调用API保存
      const result = await saveProvider(request);
      
      if (result.success) {
        // 成功回调
        onSave?.(true, result.message);
        // 重置表单
        setFormData({
          apiKey: '',
          organizationId: '',
          apiBase: ''
        });
        onClose();
      } else {
        setError(result.message);
        onSave?.(false, result.message);
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '保存失败';
      setError(errorMessage);
      onSave?.(false, errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    setFormData({
      apiKey: '',
      organizationId: '',
      apiBase: ''
    });
    setError(null);
    onClose();
  };

  const getProviderConfigLocal = () => {
    switch (provider.id) {
      case 'openai':
        return {
          name: 'OpenAI',
          showOrgId: true,
          apiKeyHint: '在此输入您的 OpenAI API Key',
          apiBaseDefault: 'https://api.openai.com',
          helpLink: 'https://platform.openai.com/api-keys'
        };
      case 'deepseek':
        return {
          name: '深度求索',
          showOrgId: false,
          apiKeyHint: '在此输入您的 DeepSeek API Key',
          apiBaseDefault: 'https://api.deepseek.com',
          helpLink: 'https://platform.deepseek.com/api-keys'
        };
      case 'siliconflow':
        return {
          name: '硅基流动',
          showOrgId: false,
          apiKeyHint: '在此输入您的 SiliconFlow API Key',
          apiBaseDefault: 'https://api.siliconflow.cn',
          helpLink: 'https://cloud.siliconflow.cn/account/ak'
        };
      case 'anthropic':
        return {
          name: 'Anthropic',
          showOrgId: false,
          apiKeyHint: '在此输入您的 Anthropic API Key',
          apiBaseDefault: 'https://api.anthropic.com',
          helpLink: 'https://console.anthropic.com/'
        };
      default:
        return {
          name: provider.name,
          showOrgId: false,
          apiKeyHint: '在此输入您的 API Key',
          apiBaseDefault: '',
          helpLink: '#'
        };
    }
  };

  if (!isOpen) return null;

  const config = getProviderConfigLocal();

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900">
            添加 {config.name}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* 错误信息显示 */}
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-md">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}
          {/* API Key 字段 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              API Key <span className="text-red-500">*</span>
            </label>
            <input
              type="password"
              value={formData.apiKey}
              onChange={(e) => setFormData({ ...formData, apiKey: e.target.value })}
              placeholder={isExistingConfig ? '已保存的API Key，输入新值可更新' : config.apiKeyHint}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required={!isExistingConfig} // 已存在配置时不强制要求
            />
            {isExistingConfig && (
              <p className="mt-1 text-xs text-gray-500">
                当前显示: {formData.apiKey} - 输入新的API Key可更新配置
              </p>
            )}
          </div>

          {/* 组织 ID 字段 (仅对显示组织ID的提供商显示) */}
          {config.showOrgId && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                组织 ID
              </label>
              <input
                type="text"
                value={formData.organizationId}
                onChange={(e) => setFormData({ ...formData, organizationId: e.target.value })}
                placeholder="在此输入您的组织 ID"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          )}

          {/* API Base 字段 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              API Base
            </label>
            <input
              type="url"
              value={formData.apiBase || config.apiBaseDefault}
              onChange={(e) => setFormData({ ...formData, apiBase: e.target.value })}
              placeholder={`在此输入您的 API Base，如：${config.apiBaseDefault}`}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* 帮助链接 */}
          <div className="pt-2">
            <a
              href={config.helpLink}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800"
            >
              从 {config.name} 获取 API Key
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>

          {/* 按钮组 */}
          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={handleCancel}
              disabled={isLoading}
              className="flex-1 px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              取消
            </button>
            <button
              type="submit"
              disabled={isLoading || (!isExistingConfig && !formData.apiKey.trim())}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? '保存中...' : (isExistingConfig ? '更新' : '保存')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}