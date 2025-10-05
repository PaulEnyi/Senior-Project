// frontend/src/hooks/useAdmin.js
import { useState, useCallback, useEffect } from 'react';
import { apiService } from '../services/api';

export const useAdmin = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [user, setUser] = useState(null);
  const [error, setError] = useState(null);
  const [systemHealth, setSystemHealth] = useState(null);

  // Check if user is authenticated on hook initialization
  useEffect(() => {
    const checkAuthStatus = () => {
      const isAuth = apiService.isAuthenticated();
      setIsAuthenticated(isAuth);
      
      if (isAuth) {
        // If authenticated, set basic user info
        setUser({
          username: 'admin', // In a real app, decode this from JWT
          role: 'admin',
          isAdmin: true
        });
      }
    };

    checkAuthStatus();
  }, []);

  // Login function
  const login = useCallback(async (credentials) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiService.adminLogin(credentials);
      
      if (response.access_token) {
        setIsAuthenticated(true);
        setUser({
          username: credentials.username,
          role: 'admin',
          isAdmin: true,
          tokenExpiresIn: response.expires_in
        });
        
        return { success: true, data: response };
      } else {
        throw new Error('Login failed - no token received');
      }
    } catch (err) {
      const errorMessage = err.response?.data?.message || err.message || 'Login failed';
      setError(errorMessage);
      setIsAuthenticated(false);
      setUser(null);
      
      return { success: false, error: errorMessage };
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Logout function
  const logout = useCallback(async () => {
    setIsLoading(true);
    
    try {
      await apiService.adminLogout();
    } catch (err) {
      console.warn('Logout request failed, but clearing local state anyway');
    } finally {
      // Clear state regardless of API call success
      setIsAuthenticated(false);
      setUser(null);
      setError(null);
      setIsLoading(false);
    }
  }, []);

  // Get system health
  const getSystemHealth = useCallback(async () => {
    if (!isAuthenticated) {
      setError('Must be authenticated to check system health');
      return null;
    }

    try {
      const health = await apiService.getSystemHealth();
      setSystemHealth(health);
      return health;
    } catch (err) {
      const errorMessage = err.response?.data?.message || 'Failed to get system health';
      setError(errorMessage);
      return null;
    }
  }, [isAuthenticated]);

  // Refresh knowledge base
  const refreshKnowledgeBase = useCallback(async (options = {}) => {
    if (!isAuthenticated) {
      setError('Must be authenticated to refresh knowledge base');
      return { success: false, error: 'Not authenticated' };
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await apiService.refreshKnowledgeBase(options);
      return { success: true, data: response };
    } catch (err) {
      const errorMessage = err.response?.data?.message || 'Failed to refresh knowledge base';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated]);

  // Clear vector database
  const clearVectorDatabase = useCallback(async () => {
    if (!isAuthenticated) {
      setError('Must be authenticated to clear database');
      return { success: false, error: 'Not authenticated' };
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await apiService.clearVectorDatabase();
      return { success: true, data: response };
    } catch (err) {
      const errorMessage = err.response?.data?.message || 'Failed to clear database';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated]);

  // Create backup
  const createBackup = useCallback(async (options = {}) => {
    if (!isAuthenticated) {
      setError('Must be authenticated to create backup');
      return { success: false, error: 'Not authenticated' };
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await apiService.createBackup(options);
      return { success: true, data: response };
    } catch (err) {
      const errorMessage = err.response?.data?.message || 'Failed to create backup';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated]);

  // List backups
  const listBackups = useCallback(async () => {
    if (!isAuthenticated) {
      setError('Must be authenticated to list backups');
      return { success: false, error: 'Not authenticated' };
    }

    try {
      const response = await apiService.listBackups();
      return { success: true, data: response };
    } catch (err) {
      const errorMessage = err.response?.data?.message || 'Failed to list backups';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    }
  }, [isAuthenticated]);

  // Delete backup
  const deleteBackup = useCallback(async (backupName) => {
    if (!isAuthenticated) {
      setError('Must be authenticated to delete backup');
      return { success: false, error: 'Not authenticated' };
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await apiService.deleteBackup(backupName);
      return { success: true, data: response };
    } catch (err) {
      const errorMessage = err.response?.data?.message || 'Failed to delete backup';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated]);

  // Get usage analytics
  const getAnalytics = useCallback(async (days = 7) => {
    if (!isAuthenticated) {
      setError('Must be authenticated to get analytics');
      return { success: false, error: 'Not authenticated' };
    }

    try {
      const response = await apiService.getUsageAnalytics({ days });
      return { success: true, data: response };
    } catch (err) {
      const errorMessage = err.response?.data?.message || 'Failed to get analytics';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    }
  }, [isAuthenticated]);

  // Clear error
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Check if token is expiring soon
  const isTokenExpiringSoon = useCallback(() => {
    if (!isAuthenticated || !user?.tokenExpiresIn) return false;
    
    // Check if token expires in less than 5 minutes
    const expirationTime = user.tokenExpiresIn * 1000; // Convert to milliseconds
    const timeUntilExpiration = expirationTime - Date.now();
    return timeUntilExpiration < 5 * 60 * 1000; // 5 minutes
  }, [isAuthenticated, user]);

  // Auto-logout when token expires
  useEffect(() => {
    if (!isAuthenticated || !user?.tokenExpiresIn) return;

    const expirationTime = user.tokenExpiresIn * 1000;
    const timeUntilExpiration = expirationTime - Date.now();

    if (timeUntilExpiration <= 0) {
      logout();
      return;
    }

    const timer = setTimeout(() => {
      logout();
      setError('Session expired. Please login again.');
    }, timeUntilExpiration);

    return () => clearTimeout(timer);
  }, [isAuthenticated, user, logout]);

  return {
    // State
    isAuthenticated,
    isLoading,
    user,
    error,
    systemHealth,

    // Actions
    login,
    logout,
    clearError,

    // Admin functions
    getSystemHealth,
    refreshKnowledgeBase,
    clearVectorDatabase,
    createBackup,
    listBackups,
    deleteBackup,
    getAnalytics,

    // Computed values
    isAdmin: isAuthenticated && user?.isAdmin,
    username: user?.username,
    isTokenExpiringSoon: isTokenExpiringSoon()
  };
};