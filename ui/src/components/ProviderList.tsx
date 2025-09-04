import { useState, useEffect } from 'react';
import ProviderCard from './ProviderCard';
import { getUserProviders, ProviderResponse } from '../services/providerService';
import { useAuthStore } from '../stores/authStore';

// 基础提供商配置模板
const baseProviders = [
  {
    id: 'openai',
    name: 'OpenAI',
    logo: '/openai.svg',
    capabilities: [
      { name: 'LLM' },
      { name: 'TEXT EMBEDDING' },
      { name: 'SPEECH2TEXT' },
      { name: 'MODERATION' },
      { name: 'TTS' }
    ],
    tokenLimit: 200,
    tokenUsed: 200,
  },
  {
    id: 'anthropic',
    name: 'ANTHROPIC',
    logo: '/claude.ico',
    capabilities: [
      { name: 'LLM' }
    ],
    tokenLimit: 0,
    tokenUsed: 0,
  },
  {
    id: 'siliconflow',
    name: '硅基流动',
    logo: '/sillconFlow.ico',
    capabilities: [
      { name: 'LLM' },
      { name: 'TEXT EMBEDDING' },
      { name: 'RERANK' },
      { name: 'SPEECH2TEXT' },
      { name: 'TTS' }
    ],
  },
  {
    id: 'deepseek',
    name: '深度求索',
    logo: '/deepseek.ico',
    capabilities: [
      { name: 'LLM' }
    ],
  }
];

export default function ProviderList() {
  const [providers, setProviders] = useState<any[]>([]);
  const [savedProviders, setSavedProviders] = useState<ProviderResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuthStore();
  
  // 获取访问令牌
  const getAccessToken = () => {
    return localStorage.getItem('auth_token');
  };
  
  // 获取已保存的提供商配置
  const fetchSavedProviders = async () => {
    try {
      console.log('开始获取已保存的提供商配置...');
      const token = getAccessToken();
      if (!token) {
        setError('请先登录');
        return;
      }
      
      const saved = await getUserProviders(token);
      console.log('获取到的提供商配置:', saved);
      setSavedProviders(saved);
    } catch (err) {
      console.error('获取已保存的提供商失败:', err);
      setError('获取配置失败');
    }
  };
  
  // 初始化加载
  useEffect(() => {
    const initializeProviders = async () => {
      setLoading(true);
      await fetchSavedProviders();
      setLoading(false);
    };
    
    initializeProviders();
  }, []);
  
  // 合并基础配置和已保存的配置
  useEffect(() => {
    const mergedProviders = baseProviders.map(baseProvider => {
      const savedProvider = savedProviders.find(sp => sp.provider === baseProvider.id);
      return {
        ...baseProvider,
        status: savedProvider ? 'connected' as const : 'disconnected' as const,
        hasApiKey: !!savedProvider,
        base_url: savedProvider?.base_url,
        saved_id: savedProvider?.id
      };
    });
    setProviders(mergedProviders);
  }, [savedProviders]);
  
  // 刷新提供商列表的函数
  const refreshProviders = () => {
    fetchSavedProviders();
  };
  
  if (loading) {
    return (
      <div className="p-6">
        <div className="flex justify-center items-center h-64">
          <div className="text-gray-500">加载中...</div>
        </div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="p-6">
        <div className="flex justify-center items-center h-64">
          <div className="text-red-500">{error}</div>
        </div>
      </div>
    );
  }
  return (
    <div className="p-6">
      <div className="space-y-4">
        {providers.map((provider) => (
          <ProviderCard 
            key={provider.id} 
            provider={provider} 
            onSave={refreshProviders} // 传递刷新函数
          />
        ))}
      </div>
    </div>
  );
}