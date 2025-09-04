import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from "@/components/Layout";
import Login from "@/pages/Login";
import Register from "@/pages/Register";
import Dashboard from "@/pages/Dashboard";
import Knowledge from "@/pages/Knowledge";
import ModelKnowledgeBase from "@/pages/ModelKnowledgeBase";
import ProviderList from "@/components/ProviderList";
import { useAuthStore } from '@/stores/authStore';
import { ROUTES } from '@/utils/routes';
import { useEffect } from 'react';

export default function App() {
  const { isAuthenticated, checkAuth } = useAuthStore();

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  return (
    <Router>
      <Routes>
        {/* 公开路由 */}
        <Route 
          path={ROUTES.LOGIN} 
          element={
            isAuthenticated ? <Navigate to={ROUTES.DASHBOARD} replace /> : <Login />
          } 
        />
        <Route 
          path={ROUTES.REGISTER} 
          element={
            isAuthenticated ? <Navigate to={ROUTES.DASHBOARD} replace /> : <Register />
          } 
        />
        
        {/* 受保护的路由 */}
        {isAuthenticated ? (
          <>
            <Route path={ROUTES.ROOT} element={<Layout />}>
              <Route index element={<Navigate to={ROUTES.DASHBOARD} replace />} />
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="knowledge" element={<Knowledge />} />
              <Route path="model-knowledge-base" element={<ModelKnowledgeBase />} />
              <Route path="model-providers" element={<ProviderList />} />
            </Route>
          </>
        ) : (
          <>
            {/* 未认证时，所有受保护路由都重定向到登录页 */}
            <Route path={ROUTES.DASHBOARD} element={<Navigate to={ROUTES.LOGIN} replace />} />
            <Route path={ROUTES.KNOWLEDGE} element={<Navigate to={ROUTES.LOGIN} replace />} />
            <Route path={ROUTES.MODEL_KNOWLEDGE_BASE} element={<Navigate to={ROUTES.LOGIN} replace />} />
            <Route path={ROUTES.MODEL_PROVIDERS} element={<Navigate to={ROUTES.LOGIN} replace />} />
            <Route path={ROUTES.ROOT} element={<Navigate to={ROUTES.LOGIN} replace />} />
          </>
        )}
        
        {/* 404 重定向 */}
        <Route path="*" element={<Navigate to={isAuthenticated ? ROUTES.DASHBOARD : ROUTES.LOGIN} replace />} />
      </Routes>
    </Router>
  );
}
