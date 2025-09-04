import { create } from 'zustand';
import { authService, User, LoginRequest } from '@/services/authService';

interface AuthState {
  // 状态
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  // 动作
  login: (credentials: LoginRequest) => Promise<void>;
  logout: () => void;
  checkAuth: () => void;
  clearError: () => void;
  setLoading: (loading: boolean) => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  // 初始状态
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  // 登录
  login: async (credentials: LoginRequest) => {
    set({ isLoading: true, error: null });
    
    try {
      const response = await authService.login(credentials);
      set({ 
        user: response.user, 
        isAuthenticated: true, 
        isLoading: false,
        error: null 
      });
    } catch (error) {
      console.log('AuthStore login error:', error);
      let errorMessage = '登录失败';
      
      if (error instanceof Error) {
        errorMessage = error.message;
      } else if (typeof error === 'string') {
        errorMessage = error;
      } else if (error && typeof error === 'object') {
        // 如果是对象，尝试提取错误信息
        errorMessage = JSON.stringify(error);
      }
      
      console.log('Processed error message:', errorMessage);
      
      set({ 
        user: null, 
        isAuthenticated: false, 
        isLoading: false,
        error: errorMessage 
      });
      throw error;
    }
  },

  // 登出
  logout: () => {
    authService.logout();
    set({ 
      user: null, 
      isAuthenticated: false, 
      isLoading: false,
      error: null 
    });
  },

  // 检查认证状态
  checkAuth: () => {
    const isAuth = authService.isAuthenticated();
    const currentUser = authService.getCurrentUser();
    
    set({ 
      user: currentUser, 
      isAuthenticated: isAuth,
      isLoading: false 
    });
  },

  // 清除错误
  clearError: () => {
    set({ error: null });
  },

  // 设置加载状态
  setLoading: (loading: boolean) => {
    set({ isLoading: loading });
  },
}));

// 初始化认证状态检查
if (typeof window !== 'undefined') {
  useAuthStore.getState().checkAuth();
}