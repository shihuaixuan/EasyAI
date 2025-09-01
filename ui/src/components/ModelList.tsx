import React, { useState, useEffect } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { cn } from '../utils/cn';

// API 服务
const API_BASE_URL = 'http://localhost:8000/api/v1/models';

interface ModelInfo {
  model: string;
  model_type: string;
  provider: string;
  description?: string;
  capabilities?: string[];
  context_length?: number;
  max_tokens?: number;
  enabled: boolean;
}

interface ProviderModelsResponse {
  provider: string;
  has_api_key: boolean;
  models: ModelInfo[];
}

interface ModelToggleRequest {
  user_id: number;
  provider: string;
  model_name: string;
  enabled: boolean;
}

interface ModelListProps {
  provider: {
    id: string;
    name: string;
    hasApiKey: boolean;
  };
  isExpanded: boolean;
  onToggle: () => void;
}

// API 服务函数
const getProviderModels = async (userId: number, provider: string): Promise<ProviderModelsResponse> => {
  const response = await fetch(`${API_BASE_URL}/provider/${provider}/user/${userId}`);
  if (!response.ok) {
    throw new Error('获取模型列表失败');
  }
  return await response.json();
};

const toggleModel = async (request: ModelToggleRequest): Promise<any> => {
  const response = await fetch(`${API_BASE_URL}/toggle`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });
  
  if (!response.ok) {
    throw new Error('切换模型状态失败');
  }
  
  return await response.json();
};

const ModelList: React.FC<ModelListProps> = ({ provider, isExpanded, onToggle }) => {
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 加载模型列表
  const loadModels = async () => {
    if (!isExpanded) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const userId = 1; // TODO: 从用户上下文获取
      const response = await getProviderModels(userId, provider.id);
      setModels(response.models);
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载失败');
    } finally {
      setLoading(false);
    }
  };

  // 切换模型状态
  const handleModelToggle = async (model: ModelInfo, enabled: boolean) => {
    if (!provider.hasApiKey) {
      alert('请先配置API Key');
      return;
    }

    try {
      const userId = 1; // TODO: 从用户上下文获取
      const request: ModelToggleRequest = {
        user_id: userId,
        provider: provider.id,
        model_name: model.model,
        enabled
      };

      const result = await toggleModel(request);
      
      if (result.success) {
        // 更新本地状态
        setModels(prevModels => 
          prevModels.map(m => 
            m.model === model.model 
              ? { ...m, enabled }
              : m
          )
        );
      } else {
        alert(result.message || '操作失败');
      }
    } catch (err) {
      alert(err instanceof Error ? err.message : '操作失败');
    }
  };

  // 当展开状态改变时加载数据
  useEffect(() => {
    loadModels();
  }, [isExpanded]);

  // 获取能力标签样式
  const getCapabilityStyle = (capability: string) => {
    const styles: Record<string, string> = {
      'LLM': 'bg-blue-100 text-blue-800',
      'CHAT': 'bg-green-100 text-green-800',
      '128K': 'bg-purple-100 text-purple-800',
    };
    return styles[capability] || 'bg-gray-100 text-gray-800';
  };

  if (!isExpanded) {
    return (
      <button
        onClick={onToggle}
        className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-800 transition-colors"
      >
        <span>显示模型</span>
        <ChevronDown className="w-4 h-4" />
      </button>
    );
  }

  return (
    <div className="mt-4">
      {/* 收起按钮 */}
      <button
        onClick={onToggle}
        className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-800 transition-colors mb-4"
      >
        <span>收起模型</span>
        <ChevronUp className="w-4 h-4" />
      </button>

      {/* 模型计数 */}
      <div className="flex items-center gap-2 mb-4">
        <span className="text-sm text-gray-600">
          {models.length} 个模型
        </span>
        <ChevronDown className="w-4 h-4 text-gray-400" />
      </div>

      {/* 加载状态 */}
      {loading && (
        <div className="text-center py-4">
          <div className="text-sm text-gray-500">加载中...</div>
        </div>
      )}

      {/* 错误状态 */}
      {error && (
        <div className="text-center py-4">
          <div className="text-sm text-red-500">{error}</div>
        </div>
      )}

      {/* 模型列表 */}
      {!loading && !error && (
        <div className="space-y-3">
          {models.map((model) => (
            <div
              key={model.model}
              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
            >
              <div className="flex items-center gap-3">
                {/* 模型图标 */}
                <div className="w-8 h-8 bg-blue-100 rounded flex items-center justify-center">
                  <span className="text-sm font-medium text-blue-600">
                    {provider.name.charAt(0)}
                  </span>
                </div>

                {/* 模型信息 */}
                <div>
                  <div className="flex items-center gap-2">
                    <h4 className="text-sm font-medium text-gray-900">
                      {model.model}
                    </h4>
                    
                    {/* 能力标签 */}
                    <div className="flex gap-1">
                      <span className={cn(
                        'px-2 py-0.5 text-xs font-medium rounded',
                        getCapabilityStyle('LLM')
                      )}>
                        LLM
                      </span>
                      <span className={cn(
                        'px-2 py-0.5 text-xs font-medium rounded',
                        getCapabilityStyle('CHAT')
                      )}>
                        CHAT
                      </span>
                      <span className={cn(
                        'px-2 py-0.5 text-xs font-medium rounded',
                        getCapabilityStyle('128K')
                      )}>
                        128K
                      </span>
                    </div>
                  </div>
                  
                  {model.description && (
                    <p className="text-xs text-gray-500 mt-1">
                      {model.description}
                    </p>
                  )}
                </div>
              </div>

              {/* 开关 */}
              <div className="flex items-center">
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={model.enabled}
                    onChange={(e) => handleModelToggle(model, e.target.checked)}
                    disabled={!provider.hasApiKey}
                    className="sr-only peer"
                  />
                  <div className={cn(
                    "relative w-11 h-6 rounded-full transition-colors",
                    "after:content-[''] after:absolute after:top-[2px] after:left-[2px]",
                    "after:bg-white after:border-gray-300 after:border after:rounded-full",
                    "after:h-5 after:w-5 after:transition-all",
                    "peer-focus:ring-4 peer-focus:ring-blue-300",
                    model.enabled 
                      ? "bg-blue-600 after:translate-x-full after:border-white" 
                      : "bg-gray-200",
                    !provider.hasApiKey && "opacity-50 cursor-not-allowed"
                  )}>
                  </div>
                </label>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ModelList;