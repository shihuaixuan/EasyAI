import { useState, useEffect, useCallback } from 'react';

export type PageType = 'model-providers' | 'knowledge' | 'workspace' | 'members' | 'billing' | 'data-sources' | 'api-extensions' | 'customization' | 'general' | 'language';

// 全局状态管理
class NavigationStore {
  private currentPage: PageType = 'knowledge';
  private listeners: Array<(page: PageType) => void> = [];

  getCurrentPage(): PageType {
    return this.currentPage;
  }

  setPage(page: PageType): void {
    this.currentPage = page;
    this.notifyListeners();
  }

  addListener(listener: (page: PageType) => void): void {
    this.listeners.push(listener);
    // 立即通知当前状态
    listener(this.currentPage);
  }

  removeListener(listener: (page: PageType) => void): void {
    const index = this.listeners.indexOf(listener);
    if (index > -1) {
      this.listeners.splice(index, 1);
    }
  }

  private notifyListeners(): void {
    this.listeners.forEach(listener => {
      try {
        listener(this.currentPage);
      } catch (error) {
        console.error('Error in navigation listener:', error);
      }
    });
  }
}

const navigationStore = new NavigationStore();

export function useNavigation() {
  const [currentPage, setCurrentPage] = useState<PageType>(navigationStore.getCurrentPage());

  useEffect(() => {
    const handlePageChange = (page: PageType) => {
      setCurrentPage(page);
    };

    navigationStore.addListener(handlePageChange);

    return () => {
      navigationStore.removeListener(handlePageChange);
    };
  }, []);

  const changePage = useCallback((page: PageType) => {
    navigationStore.setPage(page);
  }, []);

  return {
    currentPage,
    setCurrentPage: changePage
  };
}