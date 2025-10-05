import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FiRefreshCw, 
  FiDatabase, 
  FiTrash2, 
  FiDownload,
  FiUpload,
  FiAlertTriangle,
  FiCheck,
  FiX,
  FiClock,
  FiInfo
} from 'react-icons/fi';
import { apiService } from '../../services/api';
import './DataManager.css';

const DataManager = ({ onStatusChange }) => {
  const [refreshStatus, setRefreshStatus] = useState('idle'); // idle, loading, success, error
  const [clearStatus, setClearStatus] = useState('idle');
  const [backupStatus, setBackupStatus] = useState('idle');
  const [systemHealth, setSystemHealth] = useState(null);
  const [lastRefresh, setLastRefresh] = useState(null);
  const [showConfirmDialog, setShowConfirmDialog] = useState(null);
  const [operationProgress, setOperationProgress] = useState(null);

  // Fetch system health on component mount
  useEffect(() => {
    fetchSystemHealth();
    // Check for last refresh info
    const lastRefreshTime = localStorage.getItem('lastKnowledgeRefresh');
    if (lastRefreshTime) {
      setLastRefresh(new Date(lastRefreshTime));
    }
  }, []);

  const fetchSystemHealth = async () => {
    try {
      const health = await apiService.getSystemHealth();
      setSystemHealth(health);
      if (onStatusChange) {
        onStatusChange(health.status);
      }
    } catch (error) {
      console.error('Failed to fetch system health:', error);
    }
  };

  const handleRefreshKnowledge = async (forceRefresh = false) => {
    setRefreshStatus('loading');
    setOperationProgress({
      type: 'refresh',
      message: 'Initializing knowledge base refresh...',
      progress: 10
    });

    try {
      const response = await apiService.refreshKnowledgeBase({
        force_refresh: forceRefresh,
        backup_existing: true
      });

      setOperationProgress({
        type: 'refresh',
        message: 'Processing training data and generating embeddings...',
        progress: 50
      });

      // Simulate progress updates (in real implementation, you might poll status)
      setTimeout(() => {
        setOperationProgress({
          type: 'refresh',
          message: 'Uploading to vector database...',
          progress: 80
        });
      }, 2000);

      setTimeout(() => {
        setRefreshStatus('success');
        setOperationProgress(null);
        setLastRefresh(new Date());
        localStorage.setItem('lastKnowledgeRefresh', new Date().toISOString());
        
        // Refresh system health
        fetchSystemHealth();
        
        // Auto-hide success state
        setTimeout(() => setRefreshStatus('idle'), 3000);
      }, 4000);

    } catch (error) {
      setRefreshStatus('error');
      setOperationProgress(null);
      console.error('Knowledge refresh failed:', error);
      
      // Auto-hide error state
      setTimeout(() => setRefreshStatus('idle'), 5000);
    }
  };

  const handleClearDatabase = async () => {
    setClearStatus('loading');
    setOperationProgress({
      type: 'clear',
      message: 'Clearing vector database...',
      progress: 50
    });

    try {
      await apiService.clearVectorDatabase();
      
      setTimeout(() => {
        setClearStatus('success');
        setOperationProgress(null);
        fetchSystemHealth();
        
        // Auto-hide success state
        setTimeout(() => setClearStatus('idle'), 3000);
      }, 2000);

    } catch (error) {
      setClearStatus('error');
      setOperationProgress(null);
      console.error('Database clear failed:', error);
      
      setTimeout(() => setClearStatus('idle'), 5000);
    }
  };

  const handleCreateBackup = async () => {
    setBackupStatus('loading');
    setOperationProgress({
      type: 'backup',
      message: 'Creating system backup...',
      progress: 30
    });

    try {
      const response = await apiService.createBackup({
        include_vectors: true,
        include_threads: true
      });

      setOperationProgress({
        type: 'backup',
        message: 'Compressing backup archive...',
        progress: 80
      });

      setTimeout(() => {
        setBackupStatus('success');
        setOperationProgress(null);
        
        setTimeout(() => setBackupStatus('idle'), 3000);
      }, 2000);

    } catch (error) {
      setBackupStatus('error');
      setOperationProgress(null);
      console.error('Backup creation failed:', error);
      
      setTimeout(() => setBackupStatus('idle'), 5000);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'loading': return <FiRefreshCw className="spin" />;
      case 'success': return <FiCheck className="success-icon" />;
      case 'error': return <FiX className="error-icon" />;
      default: return null;
    }
  };

  const getHealthStatusColor = (status) => {
    switch (status) {
      case 'healthy': return '#4CAF50';
      case 'degraded': return '#FF9800';
      case 'unhealthy': return '#F44336';
      default: return '#9E9E9E';
    }
  };

  return (
    <div className="data-manager">
      <div className="data-manager-header">
        <h2>Data Management</h2>
        <p>Manage knowledge base, vector database, and system backups</p>
      </div>

      {/* System Health Status */}
      <div className="health-status-card">
        <div className="health-header">
          <h3>System Health</h3>
          <button 
            className="refresh-health-btn"
            onClick={fetchSystemHealth}
            title="Refresh health status"
          >
            <FiRefreshCw />
          </button>
        </div>
        
        {systemHealth && (
          <div className="health-grid">
            <div className="health-item">
              <span className="health-label">Overall Status</span>
              <div className="health-value">
                <div 
                  className="health-indicator"
                  style={{ backgroundColor: getHealthStatusColor(systemHealth.status) }}
                />
                <span className="health-text">{systemHealth.status}</span>
              </div>
            </div>
            
            {systemHealth.services && Object.entries(systemHealth.services).map(([service, info]) => (
              <div key={service} className="health-item">
                <span className="health-label">{service}</span>
                <div className="health-value">
                  <div 
                    className="health-indicator"
                    style={{ backgroundColor: getHealthStatusColor(info.status) }}
                  />
                  <span className="health-text">{info.status}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Operation Progress */}
      <AnimatePresence>
        {operationProgress && (
          <motion.div
            className="operation-progress"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
          >
            <div className="progress-content">
              <div className="progress-header">
                <span className="progress-type">
                  {operationProgress.type === 'refresh' && 'Knowledge Refresh'}
                  {operationProgress.type === 'clear' && 'Database Clear'}
                  {operationProgress.type === 'backup' && 'Backup Creation'}
                </span>
                <span className="progress-percentage">{operationProgress.progress}%</span>
              </div>
              <div className="progress-bar">
                <motion.div
                  className="progress-fill"
                  initial={{ width: 0 }}
                  animate={{ width: `${operationProgress.progress}%` }}
                  transition={{ duration: 0.5 }}
                />
              </div>
              <p className="progress-message">{operationProgress.message}</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Action Cards */}
      <div className="action-cards">
        {/* Knowledge Base Refresh */}
        <div className="action-card">
          <div className="card-header">
            <div className="card-icon refresh-icon">
              <FiRefreshCw />
            </div>
            <div className="card-title">
              <h3>Refresh Knowledge Base</h3>
              <p>Update embeddings and reload training data</p>
            </div>
          </div>
          
          {lastRefresh && (
            <div className="last-operation">
              <FiClock />
              <span>Last refresh: {lastRefresh.toLocaleString()}</span>
            </div>
          )}
          
          <div className="card-actions">
            <button
              className={`action-btn primary ${refreshStatus === 'loading' ? 'loading' : ''}`}
              onClick={() => handleRefreshKnowledge(false)}
              disabled={refreshStatus === 'loading'}
            >
              {getStatusIcon(refreshStatus)}
              <span>Quick Refresh</span>
            </button>
            
            <button
              className={`action-btn secondary ${refreshStatus === 'loading' ? 'loading' : ''}`}
              onClick={() => setShowConfirmDialog('force-refresh')}
              disabled={refreshStatus === 'loading'}
            >
              <FiRefreshCw />
              <span>Force Refresh</span>
            </button>
          </div>
          
          <div className="card-info">
            <FiInfo />
            <span>Quick refresh updates existing data. Force refresh rebuilds everything.</span>
          </div>
        </div>

        {/* Vector Database Management */}
        <div className="action-card">
          <div className="card-header">
            <div className="card-icon database-icon">
              <FiDatabase />
            </div>
            <div className="card-title">
              <h3>Vector Database</h3>
              <p>Manage Pinecone vector storage</p>
            </div>
          </div>
          
          <div className="card-actions">
            <button
              className={`action-btn danger ${clearStatus === 'loading' ? 'loading' : ''}`}
              onClick={() => setShowConfirmDialog('clear-database')}
              disabled={clearStatus === 'loading'}
            >
              {getStatusIcon(clearStatus)}
              <FiTrash2 />
              <span>Clear Database</span>
            </button>
          </div>
          
          <div className="card-warning">
            <FiAlertTriangle />
            <span>Warning: This will permanently delete all vector embeddings</span>
          </div>
        </div>

        {/* Backup Management */}
        <div className="action-card">
          <div className="card-header">
            <div className="card-icon backup-icon">
              <FiDownload />
            </div>
            <div className="card-title">
              <h3>System Backup</h3>
              <p>Create and manage data backups</p>
            </div>
          </div>
          
          <div className="card-actions">
            <button
              className={`action-btn primary ${backupStatus === 'loading' ? 'loading' : ''}`}
              onClick={handleCreateBackup}
              disabled={backupStatus === 'loading'}
            >
              {getStatusIcon(backupStatus)}
              <FiDownload />
              <span>Create Backup</span>
            </button>
            
            <button className="action-btn secondary">
              <FiUpload />
              <span>View Backups</span>
            </button>
          </div>
          
          <div className="card-info">
            <FiInfo />
            <span>Includes knowledge base, conversations, and vector data</span>
          </div>
        </div>
      </div>

      {/* Confirmation Dialogs */}
      <AnimatePresence>
        {showConfirmDialog && (
          <motion.div
            className="dialog-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setShowConfirmDialog(null)}
          >
            <motion.div
              className="confirmation-dialog"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              onClick={(e) => e.stopPropagation()}
            >
              <div className="dialog-header">
                <h3>
                  {showConfirmDialog === 'force-refresh' && 'Force Refresh Knowledge Base'}
                  {showConfirmDialog === 'clear-database' && 'Clear Vector Database'}
                </h3>
              </div>
              
              <div className="dialog-content">
                {showConfirmDialog === 'force-refresh' && (
                  <p>
                    This will completely rebuild the knowledge base from scratch. 
                    It may take 5-10 minutes and will backup existing data first.
                  </p>
                )}
                
                {showConfirmDialog === 'clear-database' && (
                  <div className="warning-content">
                    <FiAlertTriangle className="warning-icon" />
                    <p>
                      This will permanently delete ALL vector embeddings from the database. 
                      This action cannot be undone. You will need to refresh the knowledge 
                      base afterwards to restore functionality.
                    </p>
                  </div>
                )}
              </div>
              
              <div className="dialog-actions">
                <button
                  className="dialog-btn secondary"
                  onClick={() => setShowConfirmDialog(null)}
                >
                  Cancel
                </button>
                <button
                  className="dialog-btn danger"
                  onClick={() => {
                    if (showConfirmDialog === 'force-refresh') {
                      handleRefreshKnowledge(true);
                    } else if (showConfirmDialog === 'clear-database') {
                      handleClearDatabase();
                    }
                    setShowConfirmDialog(null);
                  }}
                >
                  Confirm
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default DataManager;