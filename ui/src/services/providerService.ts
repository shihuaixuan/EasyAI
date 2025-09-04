/**
 * Provider API 服务
 */

const API_BASE_URL = 'http://localhost:8000/api/v1/providers';

export interface SaveProviderRequest {
  user_id: string;  // 改为字符串类型（UUID格式）
  provider: string;
  api_key: string;
  base_url?: string;
}

export interface ProviderResponse {
  id: string;  // 改为字符串类型（UUID格式）
  user_id: string;  // 改为字符串类型（UUID格式）
  provider: string;
  api_key_masked?: string;  // 添加掉码API Key字段
  base_url?: string;
  created_at: string;
  updated_at: string;
}

export interface SaveProviderResponse {
  success: boolean;
  message: string;
  data?: ProviderResponse;
}

/**
 * 保存提供商配置
 */
export const saveProvider = async (request: SaveProviderRequest): Promise<SaveProviderResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/save`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || '保存失败');
    }

    return await response.json();
  } catch (error) {
    console.error('保存提供商配置失败:', error);
    throw error;
  }
};

/**
 * 获取当前用户的提供商配置
 */
export const getUserProviders = async (token: string): Promise<ProviderResponse[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || '获取配置失败');
    }

    return await response.json();
  } catch (error) {
    console.error('获取用户提供商配置失败:', error);
    throw error;
  }
};

/**
 * 获取单个提供商配置
 */
export const getProviderConfig = async (token: string, provider: string): Promise<ProviderResponse | null> => {
  try {
    const providers = await getUserProviders(token);
    return providers.find(p => p.provider === provider) || null;
  } catch (error) {
    console.error('获取提供商配置失败:', error);
    return null;
  }
};

/**
 * 检查API健康状态
 */
export const checkHealth = async (): Promise<{ status: string }> => {
  try {
    const response = await fetch('http://localhost:8000/health');
    return await response.json();
  } catch (error) {
    console.error('健康检查失败:', error);
    throw error;
  }
};