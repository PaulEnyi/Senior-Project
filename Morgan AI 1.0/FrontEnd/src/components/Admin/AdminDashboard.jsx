import React, { useState, useEffect } from 'react';
import {
  FiBarChart2,
  FiUsers,
  FiMessageSquare,
  FiDatabase,
  FiSettings,
  FiDownload,
  FiRefreshCw,
  FiAlertCircle,
  FiCheckCircle,
  FiArrowLeft,
  FiTrash2,
  FiEdit
} from 'react-icons/fi';
import { apiService } from '../../services/api';
import './AdminDashboard.css';

const AdminDashboard = ({ onBack }) => {
  const [stats, setStats] = useState({
    totalChats: 0,
    totalMessages: 0,
    totalUsers: 0,
    knowledgeBaseSize: 0
  });
  const [threads, setThreads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [statsData, threadsData] = await Promise.all([
        apiService.getAdminStats(),
        apiService.getThreads()
      ]);

      setStats(statsData);
      setThreads(threadsData);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
      setError('Failed to load dashboard data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    loadDashboardData();
  };

  const handleExportData = async () => {
    try {
      const data = await apiService.exportData();
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `morgan-ai-data-${new Date().toISOString()}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Failed to export data:', err);
      setError('Failed to export data. Please try again.');
    }
  };

  const handleDeleteThread = async (threadId) => {
    if (!confirm('Are you sure you want to delete this thread?')) return;

    try {
      await apiService.deleteThread(threadId);
      setThreads(threads.filter(t => t.id !== threadId));
    } catch (err) {
      console.error('Failed to delete thread:', err);
      setError('Failed to delete thread. Please try again.');
    }
  };

  if (loading) {
    return (
      <div className="admin-dashboard loading">
        <div className="loading-spinner">
          <FiRefreshCw size={48} className="spin" />
          <p>Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-dashboard">
      <div className="dashboard-header">
        <button onClick={onBack} className="back-button">
          <FiArrowLeft size={20} />
          Back to Chat
        </button>
        <h1>Admin Dashboard</h1>
        <div className="header-actions">
          <button onClick={handleRefresh} className="icon-button" title="Refresh">
            <FiRefreshCw size={20} />
          </button>
          <button onClick={handleExportData} className="icon-button" title="Export Data">
            <FiDownload size={20} />
          </button>
        </div>
      </div>

      {error && (
        <div className="error-banner">
          <FiAlertCircle size={20} />
          <span>{error}</span>
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}

      <div className="dashboard-tabs">
        <button
          className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          <FiBarChart2 size={18} />
          Overview
        </button>
        <button
          className={`tab ${activeTab === 'threads' ? 'active' : ''}`}
          onClick={() => setActiveTab('threads')}
        >
          <FiMessageSquare size={18} />
          Chat Threads
        </button>
        <button
          className={`tab ${activeTab === 'knowledge' ? 'active' : ''}`}
          onClick={() => setActiveTab('knowledge')}
        >
          <FiDatabase size={18} />
          Knowledge Base
        </button>
        <button
          className={`tab ${activeTab === 'settings' ? 'active' : ''}`}
          onClick={() => setActiveTab('settings')}
        >
          <FiSettings size={18} />
          Settings
        </button>
      </div>

      <div className="dashboard-content">
        {activeTab === 'overview' && (
          <div className="overview-tab">
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-icon">
                  <FiMessageSquare size={32} color="#FF9100" />
                </div>
                <div className="stat-info">
                  <h3>Total Chats</h3>
                  <p className="stat-value">{stats.totalChats}</p>
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-icon">
                  <FiUsers size={32} color="#001B3A" />
                </div>
                <div className="stat-info">
                  <h3>Total Messages</h3>
                  <p className="stat-value">{stats.totalMessages}</p>
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-icon">
                  <FiDatabase size={32} color="#FF9100" />
                </div>
                <div className="stat-info">
                  <h3>Knowledge Base</h3>
                  <p className="stat-value">{stats.knowledgeBaseSize} docs</p>
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-icon">
                  <FiCheckCircle size={32} color="#4CAF50" />
                </div>
                <div className="stat-info">
                  <h3>System Status</h3>
                  <p className="stat-value">Healthy</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'threads' && (
          <div className="threads-tab">
            <h2>Recent Chat Threads</h2>
            {threads.length === 0 ? (
              <p className="empty-message">No chat threads yet.</p>
            ) : (
              <div className="threads-list">
                {threads.map(thread => (
                  <div key={thread.id} className="thread-item">
                    <div className="thread-info">
                      <h4>{thread.title || 'Untitled Thread'}</h4>
                      <p className="thread-meta">
                        {thread.messageCount} messages • Created {new Date(thread.createdAt).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="thread-actions">
                      <button className="icon-button" title="View">
                        <FiEdit size={18} />
                      </button>
                      <button 
                        className="icon-button danger" 
                        title="Delete"
                        onClick={() => handleDeleteThread(thread.id)}
                      >
                        <FiTrash2 size={18} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'knowledge' && (
          <div className="knowledge-tab">
            <h2>Knowledge Base Management</h2>
            <p>Knowledge base management features coming soon...</p>
          </div>
        )}

        {activeTab === 'settings' && (
          <div className="settings-tab">
            <h2>System Settings</h2>
            <p>Settings panel coming soon...</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminDashboard;