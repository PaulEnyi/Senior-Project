import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  FiUsers, 
  FiSettings, 
  FiDatabase, 
  FiActivity,
  FiRefreshCw,
  FiToggleLeft,
  FiToggleRight
} from 'react-icons/fi'
import toast from 'react-hot-toast'
import SettingsPanel from './SettingsPanel'
import { adminService } from '../../services/adminService'

const AdminDashboard = ({ user }) => {
  const [stats, setStats] = useState(null)
  const [settings, setSettings] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('overview')

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    setIsLoading(true)
    try {
      const [dashboardStats, systemSettings] = await Promise.all([
        adminService.getDashboardStats(),
        adminService.getSettings()
      ])
      
      setStats(dashboardStats)
      setSettings(systemSettings)
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
      toast.error('Failed to load dashboard data')
    } finally {
      setIsLoading(false)
    }
  }

  const handleRefreshKnowledgeBase = async () => {
    try {
      toast.loading('Refreshing knowledge base...')
      await adminService.refreshKnowledgeBase()
      toast.success('Knowledge base refreshed successfully!')
      fetchDashboardData()
    } catch (error) {
      toast.error('Failed to refresh knowledge base')
    }
  }

  const handleSettingsUpdate = async (newSettings) => {
    try {
      await adminService.updateSettings(newSettings)
      setSettings(newSettings)
      toast.success('Settings updated successfully!')
    } catch (error) {
      toast.error('Failed to update settings')
    }
  }

  if (isLoading) {
    return (
      <div className="admin-loading">
        <div className="loading-spinner" />
        <p>Loading dashboard...</p>
      </div>
    )
  }

  return (
    <div className="admin-dashboard">
      <div className="dashboard-header">
        <h1>Admin Dashboard</h1>
        <p>Welcome back, {user?.username}</p>
      </div>

      <div className="dashboard-tabs">
        <button
          className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          <FiActivity /> Overview
        </button>
        <button
          className={`tab ${activeTab === 'users' ? 'active' : ''}`}
          onClick={() => setActiveTab('users')}
        >
          <FiUsers /> Users
        </button>
        <button
          className={`tab ${activeTab === 'knowledge' ? 'active' : ''}`}
          onClick={() => setActiveTab('knowledge')}
        >
          <FiDatabase /> Knowledge Base
        </button>
        <button
          className={`tab ${activeTab === 'settings' ? 'active' : ''}`}
          onClick={() => setActiveTab('settings')}
        >
          <FiSettings /> Settings
        </button>
      </div>

      <div className="dashboard-content">
        {activeTab === 'overview' && (
          <motion.div
            className="overview-grid"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            {/* Statistics Cards */}
            <div className="stat-card">
              <div className="stat-icon users">
                <FiUsers />
              </div>
              <div className="stat-info">
                <h3>{stats?.total_users || 0}</h3>
                <p>Total Users</p>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon messages">
                <FiActivity />
              </div>
              <div className="stat-info">
                <h3>{stats?.total_messages || 0}</h3>
                <p>Total Messages</p>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon sessions">
                <FiUsers />
              </div>
              <div className="stat-info">
                <h3>{stats?.active_sessions || 0}</h3>
                <p>Active Sessions</p>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon knowledge">
                <FiDatabase />
              </div>
              <div className="stat-info">
                <h3>{stats?.knowledge_base?.total_documents || 0}</h3>
                <p>Knowledge Documents</p>
              </div>
            </div>

            {/* System Status */}
            <div className="status-card">
              <h3>System Status</h3>
              <div className="status-list">
                <div className="status-item">
                  <span>OpenAI API</span>
                  <span className={`status ${stats?.system_status?.openai === 'connected' ? 'online' : 'offline'}`}>
                    {stats?.system_status?.openai || 'Unknown'}
                  </span>
                </div>
                <div className="status-item">
                  <span>Pinecone DB</span>
                  <span className={`status ${stats?.system_status?.pinecone === 'connected' ? 'online' : 'offline'}`}>
                    {stats?.system_status?.pinecone || 'Unknown'}
                  </span>
                </div>
                <div className="status-item">
                  <span>Voice Services</span>
                  <span className={`status ${stats?.system_status?.voice_enabled ? 'online' : 'offline'}`}>
                    {stats?.system_status?.voice_enabled ? 'Enabled' : 'Disabled'}
                  </span>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {activeTab === 'users' && (
          <motion.div
            className="users-section"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            <h2>User Management</h2>
            <p>User management features coming soon...</p>
          </motion.div>
        )}

        {activeTab === 'knowledge' && (
          <motion.div
            className="knowledge-section"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            <h2>Knowledge Base Management</h2>
            <div className="knowledge-actions">
              <button
                className="action-button primary"
                onClick={handleRefreshKnowledgeBase}
              >
                <FiRefreshCw />
                Refresh Knowledge Base
              </button>
            </div>
            <div className="knowledge-stats">
              <p>Total Documents: {stats?.knowledge_base?.total_documents || 0}</p>
              <p>Last Updated: {stats?.knowledge_base?.last_updated || 'Unknown'}</p>
            </div>
          </motion.div>
        )}

        {activeTab === 'settings' && settings && (
          <SettingsPanel 
            settings={settings}
            onUpdate={handleSettingsUpdate}
          />
        )}
      </div>
    </div>
  )
}

export default AdminDashboard