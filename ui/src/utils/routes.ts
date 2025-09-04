/**
 * 应用路由常量
 */
export const ROUTES = {
  // 公开路由
  LOGIN: '/login',
  REGISTER: '/register',
  
  // 受保护的路由
  ROOT: '/',
  DASHBOARD: '/dashboard',
  KNOWLEDGE: '/knowledge',
  MODEL_KNOWLEDGE_BASE: '/model-knowledge-base',
  MODEL_PROVIDERS: '/model-providers',
  
  // 管理路由
  WORKSPACE: '/workspace',
  MEMBERS: '/members',
  BILLING: '/billing',
  DATA_SOURCES: '/data-sources',
  API_EXTENSIONS: '/api-extensions',
  CUSTOMIZATION: '/customization',
  
  // 设置路由
  GENERAL: '/general',
  LANGUAGE: '/language',
} as const;

/**
 * 检查路径是否为公开路由
 */
export function isPublicRoute(pathname: string): boolean {
  return [ROUTES.LOGIN, ROUTES.REGISTER].includes(pathname as any);
}

/**
 * 检查路径是否为受保护的路由
 */
export function isProtectedRoute(pathname: string): boolean {
  return !isPublicRoute(pathname);
}

/**
 * 获取默认的登录后跳转路径
 */
export function getDefaultRedirectPath(): string {
  return ROUTES.DASHBOARD;
}
