import { useState, useEffect, useCallback } from 'react'
import { adminService } from '../services/adminService'
import toast from 'react-hot-toast'

export const useAdmin = () => {
  const [stats, setStats] = useState({
    totalUsers: 0,
    totalMessages: 0,
    activeSessions: 0,
    knowledgeBaseDocuments: 0,
    systemStatus: {
      openai: 'unknown',
      pinecone: 'unknown',
      voiceEnabled: false
    }
  })
  
  const [settings, setSettings] = useState({
    enable_voice: true,
    tts_voice: 'alloy',
    tts_speed: 1.0,
    max_tokens: 2000,
    temperature: 0.7,
    top_k_results: 5
  })
  
  const [users, setUsers] = useState([])
  const [logs, setLogs] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [refreshInterval, setRefreshInterval] = useState(null)

  // Fetch dashboard stats
  const fetchDashboardStats = useCallback(async () => {
    try {
      const data = await adminService.getDashboardStats()
      setStats({
        totalUsers: data.total_users || 0,
        totalMessages: data.total_messages || 0,
        activeSessions: data.active_sessions || 0,
        knowledgeBaseDocuments: data.knowledge_base?.total_documents || 0,
        systemStatus: data.system_status || stats.systemStatus
      })
      return data
    } catch (error) {
      console.error('Failed to fetch dashboard stats:', error)
      toast.error('Failed to load dashboard statistics')
      return null
    }
  }, [])

  // Fetch system settings
  const fetchSettings = useCallback(async () => {
    try {
      const data = await adminService.getSettings()
      setSettings(data)
      return data
    } catch (error) {
      console.error('Failed to fetch settings:', error)
      toast.error('Failed to load system settings')
      return null
    }
  }, [])

  // Update system settings
  const updateSettings = useCallback(async (newSettings) => {
    setIsLoading(true)
    try {
      const data = await adminService.updateSettings(newSettings)
      setSettings(data)
      toast.success('Settings updated successfully')
      return data
    } catch (error) {
      console.error('Failed to update settings:', error)
      toast.error('Failed to update settings')
      return null
    } finally {
      setIsLoading(false)
    }
  }, [])

  // Refresh knowledge base
  const refreshKnowledgeBase = useCallback(async () => {
    setIsLoading(true)
    try {
      const result = await adminService.refreshKnowledgeBase()
      toast.success('Knowledge base refreshed successfully')
      // Refresh stats to show updated document count
      await fetchDashboardStats()
      return result
    } catch (error) {
      console.error('Failed to refresh knowledge base:', error)
      toast.error('Failed to refresh knowledge base')
      return null
    } finally {
      setIsLoading(false)
    }
  }, [fetchDashboardStats])

  // User management
  const fetchUsers = useCallback(async (limit = 50, offset = 0) => {
    try {
      const data = await adminService.getUsers(limit, offset)
      setUsers(data.users || [])
      return data
    } catch (error) {
      console.error('Failed to fetch users:', error)
      toast.error('Failed to load users')
      return null
    }
  }, [])

  const createUser = useCallback(async (userData) => {
    setIsLoading(true)
    try {
      const newUser = await adminService.createUser(userData)
      setUsers(prev => [...prev, newUser])
      toast.success('User created successfully')
      return newUser
    } catch (error) {
      console.error('Failed to create user:', error)
      toast.error('Failed to create user')
      return null
    } finally {
      setIsLoading(false)
    }
  }, [])

  const updateUser = useCallback(async (userId, userData) => {
    setIsLoading(true)
    try {
      const updatedUser = await adminService.updateUser(userId, userData)
      setUsers(prev => prev.map(user => 
        user.id === userId ? updatedUser : user
      ))
      toast.success('User updated successfully')
      return updatedUser
    } catch (error) {
      console.error('Failed to update user:', error)
      toast.error('Failed to update user')
      return null
    } finally {
      setIsLoading(false)
    }
  }, [])

  const deleteUser = useCallback(async (userId) => {
    setIsLoading(true)
    try {
      await adminService.deleteUser(userId)
      setUsers(prev => prev.filter(user => user.id !== userId))
      toast.success('User deleted successfully')
      return true
    } catch (error) {
      console.error('Failed to delete user:', error)
      toast.error('Failed to delete user')
      return false
    } finally {
      setIsLoading(false)
    }
  }, [])

  // Knowledge base management
  const addDocument = useCallback(async (content, metadata) => {
    setIsLoading(true)
    try {
      const result = await adminService.addDocument(content, metadata)
      toast.success('Document added successfully')
      await fetchDashboardStats()
      return result
    } catch (error) {
      console.error('Failed to add document:', error)
      toast.error('Failed to add document')
      return null
    } finally {
      setIsLoading(false)
    }
  }, [fetchDashboardStats])

  const updateDocument = useCallback(async (documentId, content, metadata) => {
    setIsLoading(true)
    try {
      const result = await adminService.updateDocument(documentId, content, metadata)
      toast.success('Document updated successfully')
      return result
    } catch (error) {
      console.error('Failed to update document:', error)
      toast.error('Failed to update document')
      return null
    } finally {
      setIsLoading(false)
    }
  }, [])

  const deleteDocument = useCallback(async (documentId) => {
    setIsLoading(true)
    try {
      await adminService.deleteDocument(documentId)
      toast.success('Document deleted successfully')
      await fetchDashboardStats()
      return true
    } catch (error) {
      console.error('Failed to delete document:', error)
      toast.error('Failed to delete document')
      return false
    } finally {
      setIsLoading(false)
    }
  }, [fetchDashboardStats])

  // Session management
  const terminateSession = useCallback(async (userId) => {
    try {
      await adminService.terminateSession(userId)
      toast.success('Session terminated')
      await fetchDashboardStats()
      return true
    } catch (error) {
      console.error('Failed to terminate session:', error)
      toast.error('Failed to terminate session')
      return false
    }
  }, [fetchDashboardStats])

  // Logs
  const fetchLogs = useCallback(async (level = 'INFO', limit = 100) => {
    try {
      const data = await adminService.getLogs(level, limit)
      setLogs(data.logs || [])
      return data
    } catch (error) {
      console.error('Failed to fetch logs:', error)
      toast.error('Failed to load logs')
      return null
    }
  }, [])

  // Auto-refresh functionality
  const startAutoRefresh = useCallback((interval = 30000) => {
    if (refreshInterval) {
      clearInterval(refreshInterval)
    }
    
    const intervalId = setInterval(() => {
      fetchDashboardStats()
    }, interval)
    
    setRefreshInterval(intervalId)
    return intervalId
  }, [refreshInterval, fetchDashboardStats])

  const stopAutoRefresh = useCallback(() => {
    if (refreshInterval) {
      clearInterval(refreshInterval)
      setRefreshInterval(null)
    }
  }, [refreshInterval])

  // Initial load
  useEffect(() => {
    const loadInitialData = async () => {
      setIsLoading(true)
      try {
        await Promise.all([
          fetchDashboardStats(),
          fetchSettings(),
          fetchUsers()
        ])
      } catch (error) {
        console.error('Failed to load initial admin data:', error)
      } finally {
        setIsLoading(false)
      }
    }

    loadInitialData()
  }, [])

  // Cleanup
  useEffect(() => {
    return () => {
      if (refreshInterval) {
        clearInterval(refreshInterval)
      }
    }
  }, [refreshInterval])

  return {
    // State
    stats,
    settings,
    users,
    logs,
    isLoading,
    
    // Dashboard
    fetchDashboardStats,
    startAutoRefresh,
    stopAutoRefresh,
    
    // Settings
    fetchSettings,
    updateSettings,
    
    // Knowledge Base
    refreshKnowledgeBase,
    addDocument,
    updateDocument,
    deleteDocument,
    
    // Users
    fetchUsers,
    createUser,
    updateUser,
    deleteUser,
    
    // Sessions
    terminateSession,
    
    // Logs
    fetchLogs
  }
}