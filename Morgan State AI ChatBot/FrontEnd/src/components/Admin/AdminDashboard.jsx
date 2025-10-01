import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FiDatabase, 
  FiRefreshCw, 
  FiTrash2, 
  FiDownload,
  FiUpload,
  FiActivity,
  FiUsers,
  FiSettings,
  FiLogOut,
  FiCheck,
  FiX,
  FiAlertTriangle,
  FiInfo,
  FiBarChart3,
  FiHardDrive,
  FiCpu,
  FiWifi
} from 'react-icons/fi';
import { apiService } from '../../services/api';
import './AdminDashboard.css';

const AdminDashboard = ({ onLogout }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [systemHealth, setSystemHealth] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [backups, setBackups] = useState([]);

  // Fetch system health on component mount
  useEffect(() => {
    fetchSystemHealth();
    fetchAnalytics();
    fetchBackups();
    
    // Set up periodic health checks
    const interval = setInterval(fetchSystemHealth, 30000); // Every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchSystemHealth = async () => {
    try {
      const health = await apiService.get('/api/admin/system-health');
      setSystemHealth(health.data || health);
    } catch (error) {
      console.error('Failed to fetch system health:', error);
      addNotification('Failed to fetch system health', 'error');
    }
  };

  const fetchAnalytics = async () => {
    try {
      const analyticsData = await apiService.get('/api/admin/analytics');
      setAnalytics(analyticsData.data || analyticsData);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    }
  };

  const fetchBackups = async () => {
    try {
      const backupsData = await apiService.get('/api/admin/backups');
      setBackups(backupsData.data?.backups || []);
    } catch (error) {
      console.error('Failed to fetch backups:', error);
    }
  };

  const addNotification = (message, type = 'info') => {
    const notification = {
      id: Date.now(),
      message,
      type,
      timestamp: new Date().toLocaleTimeString()
    };
    
    setNotifications(prev => [notification, ...prev.slice(0, 4)]); // Keep last 5
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== notification.id));
    }, 5000);
  };

  const handleRefreshKnowledge = async () => {
    setIsLoading(true);
    try {
      await apiService.post('/api/admin/refresh-knowledge', {
        force_refresh: true,
        backup_existing: true
      });
      addNotification('Knowledge base refresh started', 'success');
    } catch (error) {
      addNotification('Failed to refresh knowledge base', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearDatabase = async () => {
    if (!window.confirm('Are you sure? This will clear all vector embeddings and cannot be undone.')) {
      return;
    }
    
    setIsLoading(true);
    try {
      await apiService.post('/api/admin/clear-database');
      addNotification('Database clearing started', 'warning');
    } catch (error) {
      addNotification('Failed to clear database', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateBackup = async () => {
    setIsLoading(true);
    try {
      await apiService.post('/api/admin/backup', null, {
        params: {
          include_vectors: true,
          include_threads: true
        }
      });
      addNotification('Backup creation started', 'success');
      setTimeout(fetchBackups, 2000); // Refresh backup list
    } catch (error) {
      addNotification('Failed to create backup', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteBackup = async (backupName) => {
    if (!window.confirm(`Delete backup "${backupName}"?`)) return;
    
    try {
      await apiService.delete(`/api/admin/backups/${backupName}`);
      addNotification('Backup deleted successfully', 'success');
      fetchBackups();
    } catch (error) {
      addNotification('Failed to delete backup', 'error');
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy': return <FiCheck className="status-icon healthy" />;
      case 'degraded': return <FiAlertTriangle className="status-icon warning" />;
      case 'unhealthy': return <FiX className="status-icon error" />;
      default: return <FiInfo className="status-icon info" />;
    }
  };

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const tabVariants = {
    hidden: { opacity: 0, x: 20 },
    visible: { opacity: 1, x: 0, transition: { duration: 0.3 } }
  };

  return (
    <div className="admin-dashboard">
      {/* Header */}
      <div className="dashboard-header">
        <div className="header-content">
          <div className="header-left">
            <h1>Morgan AI Admin Dashboard</h1>
            <p>System Management & Control Panel</p>
          </div>
          <div className="header-right">
            <button 
              className="btn-secondary"
              onClick={fetchSystemHealth}
              disabled={isLoading}
            >
              <FiRefreshCw className={isLoading ? 'spinning' : ''} />
              Refresh
            </button>
            <button 
              className="btn-danger"
              onClick={onLogout}
            >
              <FiLogOut />
              Logout
            </button>
          </div>
        </div>
      </div>

      {/* Notifications */}
      <AnimatePresence>
        {notifications.length > 0 && (
          <div className="notifications">
            {notifications.map(notification => (
              <motion.div
                key={notification.id}
                className={`notification ${notification.type}`}
                initial={{ opacity: 0, y: -50 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -50 }}
              >
                <div className="notification-content">
                  <span className="message">{notification.message}</span>
                  <span className="timestamp">{notification.timestamp}</span>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </AnimatePresence>

      {/* Navigation Tabs */}
      <div className="dashboard-nav">
        <div className="nav-tabs">
          {[
            { id: 'overview', label: 'Overview', icon: FiActivity },
            { id: 'knowledge', label: 'Knowledge Base', icon: FiDatabase },
            { id: 'backups', label: 'Backups', icon: FiHardDrive },
            { id: 'analytics', label: 'Analytics', icon: FiBarChart3 },
            { id: 'settings', label: 'Settings', icon: FiSettings }
          ].map(tab => (
            <button
              key={tab.id}
              className={`nav-tab ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <tab.icon />
              <span>{tab.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div className="dashboard-content">
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            variants={tabVariants}
            initial="hidden"
            animate="visible"
            exit="hidden"
          >
            {activeTab === 'overview' && (
              <div className="overview-tab">
                <div className="metrics-grid">
                  {/* System Health */}
                  <div className="metric-card">
                    <div className="card-header">
                      <h3>System Health</h3>
                      {systemHealth && getStatusIcon(systemHealth.status)}
                    </div>
                    <div className="card-content">
                      {systemHealth ? (
                        <div className="health-details">
                          <div className="service-status">
                            {Object.entries(systemHealth.services || {}).map(([service, data]) => (
                              <div key={service} className="service-item">
                                <span className="service-name">{service}</span>
                                {getStatusIcon(data.status)}
                              </div>
                            ))}
                          </div>
                        </div>
                      ) : (
                        <div className="loading-placeholder">Loading health data...</div>
                      )}
                    </div>
                  </div>

                  {/* Quick Stats */}
                  {analytics && (
                    <div className="metric-card">
                      <div className="card-header">
                        <h3>Usage Statistics</h3>
                        <FiBarChart3 />
                      </div>
                      <div className="card-content">
                        <div className="stats-grid">
                          <div className="stat-item">
                            <span className="stat-label">Conversations</span>
                            <span className="stat-value">{analytics.total_conversations}</span>
                          </div>
                          <div className="stat-item">
                            <span className="stat-label">Messages</span>
                            <span className="stat-value">{analytics.total_messages}</span>
                          </div>
                          <div className="stat-item">
                            <span className="stat-label">Avg Response</span>
                            <span className="stat-value">{analytics.average_response_time}s</span>
                          </div>
                          <div className="stat-item">
                            <span className="stat-label">Uptime</span>
                            <span className="stat-value">{analytics.uptime_percentage}%</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Quick Actions */}
                  <div className="metric-card">
                    <div className="card-header">
                      <h3>Quick Actions</h3>
                      <FiSettings />
                    </div>
                    <div className="card-content">
                      <div className="quick-actions">
                        <button 
                          className="action-btn primary"
                          onClick={handleRefreshKnowledge}
                          disabled={isLoading}
                        >
                          <FiRefreshCw />
                          Refresh Knowledge Base
                        </button>
                        <button 
                          className="action-btn secondary"
                          onClick={handleCreateBackup}
                          disabled={isLoading}
                        >
                          <FiDownload />
                          Create Backup
                        </button>
                        <button 
                          className="action-btn danger"
                          onClick={handleClearDatabase}
                          disabled={isLoading}
                        >
                          <FiTrash2 />
                          Clear Database
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'knowledge' && (
              <div className="knowledge-tab">
                <div className="section-header">
                  <h2>Knowledge Base Management</h2>
                  <p>Manage the Morgan State CS department knowledge base and vector embeddings</p>
                </div>

                <div className="knowledge-actions">
                  <div className="action-card">
                    <div className="action-header">
                      <FiRefreshCw />
                      <h3>Refresh Knowledge Base</h3>
                    </div>
                    <p>Process training data and update vector embeddings. This may take 5-10 minutes.</p>
                    <button 
                      className="btn-primary"
                      onClick={handleRefreshKnowledge}
                      disabled={isLoading}
                    >
                      {isLoading ? 'Processing...' : 'Start Refresh'}
                    </button>
                  </div>

                  <div className="action-card">
                    <div className="action-header">
                      <FiUpload />
                      <h3>Upload Training Data</h3>
                    </div>
                    <p>Upload new training data files to expand the knowledge base.</p>
                    <input 
                      type="file" 
                      accept=".txt,.json,.csv"
                      className="file-input"
                    />
                    <button className="btn-secondary">Upload Files</button>
                  </div>

                  <div className="action-card danger">
                    <div className="action-header">
                      <FiTrash2 />
                      <h3>Clear Vector Database</h3>
                    </div>
                    <p>Remove all vector embeddings. This action cannot be undone.</p>
                    <button 
                      className="btn-danger"
                      onClick={handleClearDatabase}
                      disabled={isLoading}
                    >
                      Clear Database
                    </button>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'backups' && (
              <div className="backups-tab">
                <div className="section-header">
                  <h2>System Backups</h2>
                  <div className="header-actions">
                    <button 
                      className="btn-primary"
                      onClick={handleCreateBackup}
                      disabled={isLoading}
                    >
                      <FiDownload />
                      Create New Backup
                    </button>
                  </div>
                </div>

                <div className="backups-list">
                  {backups.length > 0 ? (
                    backups.map(backup => (
                      <div key={backup.backup_name} className="backup-item">
                        <div className="backup-info">
                          <h3>{backup.backup_name}</h3>
                          <div className="backup-meta">
                            <span>Created: {new Date(backup.created_at).toLocaleString()}</span>
                            <span>Size: {formatBytes(backup.file_size || 0)}</span>
                            <span className={`status ${backup.status}`}>{backup.status}</span>
                          </div>
                        </div>
                        <div className="backup-actions">
                          <button 
                            className="btn-danger small"
                            onClick={() => handleDeleteBackup(backup.backup_name)}
                          >
                            <FiTrash2 />
                          </button>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="empty-state">
                      <FiHardDrive size={48} />
                      <h3>No backups found</h3>
                      <p>Create your first backup to get started</p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {activeTab === 'analytics' && (
              <div className="analytics-tab">
                <div className="section-header">
                  <h2>Usage Analytics</h2>
                  <p>Monitor chatbot performance and user engagement</p>
                </div>

                {analytics ? (
                  <div className="analytics-content">
                    <div className="analytics-grid">
                      <div className="analytics-card">
                        <h3>Conversations</h3>
                        <div className="big-number">{analytics.total_conversations}</div>
                      </div>
                      <div className="analytics-card">
                        <h3>Messages</h3>
                        <div className="big-number">{analytics.total_messages}</div>
                      </div>
                      <div className="analytics-card">
                        <h3>Response Time</h3>
                        <div className="big-number">{analytics.average_response_time}s</div>
                      </div>
                      <div className="analytics-card">
                        <h3>Error Rate</h3>
                        <div className="big-number">{(analytics.error_rate * 100).toFixed(1)}%</div>
                      </div>
                    </div>

                    <div className="popular-questions">
                      <h3>Popular Questions</h3>
                      {analytics.popular_questions?.length > 0 ? (
                        <ul>
                          {analytics.popular_questions.map((q, index) => (
                            <li key={index}>{q.question} ({q.count} times)</li>
                          ))}
                        </ul>
                      ) : (
                        <p>No data available yet</p>
                      )}
                    </div>
                  </div>
                ) : (
                  <div className="loading-placeholder">Loading analytics...</div>
                )}
              </div>
            )}

            {activeTab === 'settings' && (
              <div className="settings-tab">
                <div className="section-header">
                  <h2>System Settings</h2>
                  <p>Configure Morgan AI chatbot settings</p>
                </div>

                <div className="settings-sections">
                  <div className="settings-card">
                    <h3>General Settings</h3>
                    <div className="setting-item">
                      <label>Max Response Length</label>
                      <input type="number" defaultValue="500" />
                    </div>
                    <div className="setting-item">
                      <label>Response Temperature</label>
                      <input type="range" min="0" max="1" step="0.1" defaultValue="0.7" />
                    </div>
                  </div>

                  <div className="settings-card">
                    <h3>Voice Settings</h3>
                    <div className="setting-item">
                      <label>
                        <input type="checkbox" defaultChecked />
                        Enable voice features
                      </label>
                    </div>
                    <div className="setting-item">
                      <label>Default TTS Voice</label>
                      <select defaultValue="alloy">
                        <option value="alloy">Alloy</option>
                        <option value="echo">Echo</option>
                        <option value="fable">Fable</option>
                        <option value="onyx">Onyx</option>
                        <option value="nova">Nova</option>
                        <option value="shimmer">Shimmer</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
};

export default AdminDashboard;