import { useEffect, ReactNode } from 'react';
import { Loader2, Shield } from 'lucide-react';
import { useAuthStore } from '@/stores/authStore';
import { useNavigation } from '@/hooks/useNavigation';
import Login from '@/pages/Login';

interface AuthGuardProps {
  children: ReactNode;
  fallback?: ReactNode;
}

/**
 * 认证守卫组件
 * 用于保护需要登录才能访问的页面
 */
export default function AuthGuard({ children, fallback }: AuthGuardProps) {
  const { isAuthenticated, isLoading, checkAuth } = useAuthStore();
  const { currentPage } = useNavigation();

  // 组件挂载时检查认证状态
  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  // 如果正在加载，显示加载状态
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-purple-50">
        <div className="text-center">
          <div className="mx-auto h-16 w-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center mb-6">
            <Shield className="h-8 w-8 text-white" />
          </div>
          <div className="flex items-center justify-center mb-4">
            <Loader2 className="h-8 w-8 text-blue-600 animate-spin" />
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">EasyAI</h2>
          <p className="text-gray-600">正在验证身份...</p>
        </div>
      </div>
    );
  }

  // 如果未认证，显示登录页面或自定义fallback
  if (!isAuthenticated) {
    return fallback || <Login />;
  }

  // 已认证，显示受保护的内容
  return <>{children}</>;
}

/**
 * 高阶组件：为页面添加认证保护
 */
export function withAuthGuard<P extends object>(
  Component: React.ComponentType<P>,
  fallback?: ReactNode
) {
  return function AuthGuardedComponent(props: P) {
    return (
      <AuthGuard fallback={fallback}>
        <Component {...props} />
      </AuthGuard>
    );
  };
}