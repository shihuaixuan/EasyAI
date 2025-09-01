import { useEffect } from 'react';
import Sidebar from './Sidebar';
import Header from './Header';
import ProviderList from './ProviderList';
import Knowledge from '../pages/Knowledge';
import { useNavigation } from '@/hooks/useNavigation';

export default function Layout() {
  const { currentPage } = useNavigation();

  const renderCurrentPage = () => {
    switch (currentPage) {
      case 'knowledge':
        return <Knowledge />;
      case 'model-providers':
        return <ProviderList />;
      default:
        return <ProviderList />;
    }
  };

  return (
    <div className="h-screen flex bg-gray-50">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto">
          {renderCurrentPage()}
        </main>
      </div>
    </div>
  );
}