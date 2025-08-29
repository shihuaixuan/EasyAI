import Sidebar from './Sidebar';
import Header from './Header';
import ProviderList from './ProviderList';

export default function Layout() {
  return (
    <div className="h-screen flex bg-gray-50">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto">
          <ProviderList />
        </main>
      </div>
    </div>
  );
}