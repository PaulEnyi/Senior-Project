import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const useThemeStore = create(
  persist(
    (set, get) => ({
      theme: 'dark',
      primaryColor: 'morgan',
      
      toggleTheme: () => {
        const newTheme = get().theme === 'dark' ? 'light' : 'dark';
        set({ theme: newTheme });
        document.documentElement.setAttribute('data-theme', newTheme);
      },
      
      setTheme: (theme) => {
        set({ theme });
        document.documentElement.setAttribute('data-theme', theme);
      },
      
      setPrimaryColor: (color) => {
        set({ primaryColor: color });
        document.documentElement.style.setProperty('--primary-color', color);
      },
      
      initTheme: () => {
        const { theme } = get();
        document.documentElement.setAttribute('data-theme', theme);
      }
    }),
    {
      name: 'theme-storage',
      partialize: (state) => ({
        theme: state.theme,
        primaryColor: state.primaryColor
      })
    }
  )
);

export const useTheme = () => {
  const store = useThemeStore();
  
  // Initialize theme on mount
  if (typeof window !== 'undefined') {
    store.initTheme();
  }
  
  return store;
};