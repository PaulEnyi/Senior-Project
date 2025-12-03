import React, { useState, useEffect } from 'react';
import degreeWorksService from '../../services/degreeWorksService';
import '../../styles/degree-works.css';

const DegreeWorks = () => {
  const [analysis, setAnalysis] = useState(null);
  const [versions, setVersions] = useState([]);
  const [selectedVersion, setSelectedVersion] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showUpload, setShowUpload] = useState(false);
  const [showVersions, setShowVersions] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [analysisResponse, versionsResponse] = await Promise.all([
        degreeWorksService.getLatestAnalysis().catch(() => null),
        degreeWorksService.listVersions().catch(() => null)
      ]);
      
      // Extract actual data from API responses
      const analysisData = analysisResponse?.analysis || analysisResponse;
      const versionsData = versionsResponse?.versions || versionsResponse || [];
      
      console.log('Loaded analysis:', analysisData);
      console.log('Loaded versions:', versionsData);
      
      setAnalysis(analysisData);
      setVersions(Array.isArray(versionsData) ? versionsData : []);
      setError(null);
    } catch (err) {
      console.error('Failed to load degree works data:', err);
      setError('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    if (file.type !== 'application/pdf') {
      setError('Please upload a PDF file');
      return;
    }

    try {
      setUploading(true);
      setError(null);
      
      console.log('📤 Uploading file:', file.name);
      const result = await degreeWorksService.uploadDegreeWorks(file);
      console.log('✅ Upload result:', result);
      
      // Reload data to show new version and updated analysis
      console.log('🔄 Reloading data...');
      await loadData();
      setShowUpload(false);
      
      // Show success message
      alert(`✅ Degree Works uploaded successfully!\n${result.diff ? degreeWorksService.summarizeDiff(result.diff) : ''}`);
    } catch (err) {
      console.error('❌ Upload failed:', err);
      setError(err.message || 'Failed to upload file');
    } finally {
      setUploading(false);
      event.target.value = ''; // Reset file input
    }
  };

  const handleDeleteVersion = async (versionId) => {
    if (!confirm('Are you sure you want to delete this Degree Works version?')) {
      return;
    }

    try {
      await degreeWorksService.deleteVersion(versionId);
      await loadData(); // Reload to update list
      
      if (selectedVersion?.id === versionId) {
        setSelectedVersion(null);
      }
    } catch (err) {
      console.error('Delete failed:', err);
      setError('Failed to delete version');
    }
  };

  const handleDeleteAll = async () => {
    if (!confirm('⚠️ This will delete ALL your Degree Works data. Are you sure?')) {
      return;
    }

    try {
      await degreeWorksService.deleteAllDegreeWorks();
      setAnalysis(null);
      setVersions([]);
      setSelectedVersion(null);
    } catch (err) {
      console.error('Delete all failed:', err);
      setError('Failed to delete all data');
    }
  };

  const handleViewVersion = async (versionId) => {
    try {
      const versionData = await degreeWorksService.getVersion(versionId);
      setSelectedVersion(versionData);
      setShowVersions(false);
    } catch (err) {
      console.error('Failed to load version:', err);
      setError('Failed to load version');
    }
  };

  const renderCourseList = (courses, status) => {
    if (!courses || courses.length === 0) {
      return <p className="no-courses">No {status} courses</p>;
    }

    const statusIcons = {
      completed: '✓',
      'in_progress': '⏳',
      remaining: '📝'
    };

    return (
      <div className="course-list">
        {courses.map((course, index) => (
          <div key={index} className={`course-card ${status}`}>
            <div className="course-header">
              <span className="course-icon">{statusIcons[status]}</span>
              <span className="course-code">{course.course_code}</span>
              {course.grade && <span className={`course-grade grade-${course.grade}`}>{course.grade}</span>}
              <span className="course-credits">{course.credits} cr</span>
            </div>
            <div className="course-name">{course.course_name}</div>
            {course.term && <div className="course-term">{course.term}</div>}
          </div>
        ))}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="degree-works-container">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading Degree Works...</p>
        </div>
      </div>
    );
  }

  const displayData = selectedVersion || analysis;

  return (
    <div className="degree-works-container">
      {/* Header */}
      <div className="dw-header">
        <div className="dw-title">
          <div className="dw-icon">🎓</div>
          <div>
            <h1>Degree Works Analyzer</h1>
            <p className="dw-subtitle">Computer Science Academic Progress</p>
          </div>
        </div>
        
        <div className="dw-actions">
          <button 
            className="btn-primary"
            onClick={() => setShowUpload(!showUpload)}
            disabled={uploading}
          >
            {uploading ? 'Uploading...' : '📤 Upload New PDF'}
          </button>
          
          {versions.length > 0 && (
            <>
              <button 
                className="btn-secondary"
                onClick={() => setShowVersions(!showVersions)}
              >
                📚 Versions ({versions.length})
              </button>
              
              <button 
                className="btn-danger"
                onClick={handleDeleteAll}
              >
                🗑️ Delete All
              </button>
            </>
          )}
        </div>
      </div>

      {error && (
        <div className="error-banner">
          ⚠️ {error}
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}

      {/* Upload Section */}
      {showUpload && (
        <div className="upload-section">
          <div className="upload-box">
            <input
              type="file"
              accept=".pdf"
              onChange={handleFileUpload}
              disabled={uploading}
              id="pdf-upload"
              className="file-input"
            />
            <label htmlFor="pdf-upload" className="upload-label">
              <div className="upload-icon">📄</div>
              <p className="upload-text">
                {uploading ? 'Uploading and analyzing...' : 'Click to select PDF or drag and drop'}
              </p>
              <p className="upload-hint">Maximum file size: 10MB</p>
            </label>
          </div>
        </div>
      )}

      {/* Versions List */}
      {showVersions && versions.length > 0 && (
        <div className="versions-panel">
          <h3>📚 Upload History</h3>
          <div className="versions-list">
            {versions.map((version) => (
              <div key={version.id} className="version-card">
                <div className="version-info">
                  <div className="version-date">
                    {new Date(version.uploaded_at).toLocaleString()}
                  </div>
                  <div className="version-meta">
                    {version.student_name && <span>👤 {version.student_name}</span>}
                    <span>GPA: {version.gpa || 'N/A'}</span>
                    <span>{version.completed_credits || 0} credits</span>
                  </div>
                </div>
                <div className="version-actions">
                  <button 
                    className="btn-view"
                    onClick={() => handleViewVersion(version.id)}
                  >
                    👁️ View
                  </button>
                  <button 
                    className="btn-delete"
                    onClick={() => handleDeleteVersion(version.id)}
                  >
                    🗑️
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Main Content */}
      {displayData ? (
        <div className="dw-content">
          {selectedVersion && (
            <div className="version-banner">
              📅 Viewing version from {new Date(selectedVersion.uploaded_at).toLocaleString()}
              <button onClick={() => setSelectedVersion(null)}>← Back to Latest</button>
            </div>
          )}

          {/* Student Info Card */}
          {displayData.student_info && (
            <div className="info-card student-card">
              <h2>Student Information</h2>
              <div className="info-grid">
                <div className="info-item">
                  <span className="info-label">Name:</span>
                  <span className="info-value">{displayData.student_info.name || 'N/A'}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Student ID:</span>
                  <span className="info-value">{displayData.student_info.student_id || 'N/A'}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Major:</span>
                  <span className="info-value">{displayData.student_info.major || 'Computer Science'}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Degree:</span>
                  <span className="info-value">{displayData.student_info.degree || 'B.S.'}</span>
                </div>
              </div>
            </div>
          )}

          {/* Academic Summary */}
          {displayData.academic_summary && (
            <div className="summary-grid">
              <div className="stat-card classification">
                <div className="stat-icon">🎓</div>
                <div className="stat-content">
                  <div className="stat-label">Classification</div>
                  <div className="stat-value">{displayData.academic_summary.classification || 'N/A'}</div>
                </div>
              </div>

              <div className="stat-card gpa">
                <div className="stat-icon">📊</div>
                <div className="stat-content">
                  <div className="stat-label">Current GPA</div>
                  <div className="stat-value">{displayData.academic_summary.gpa?.toFixed(3) || 'N/A'}</div>
                </div>
              </div>

              <div className="stat-card credits-completed">
                <div className="stat-icon">✅</div>
                <div className="stat-content">
                  <div className="stat-label">Credits Completed</div>
                  <div className="stat-value">{displayData.academic_summary.completed_credits || 0}</div>
                </div>
              </div>

              <div className="stat-card credits-progress">
                <div className="stat-icon">⏳</div>
                <div className="stat-content">
                  <div className="stat-label">In Progress</div>
                  <div className="stat-value">{displayData.academic_summary.in_progress_credits || 0}</div>
                </div>
              </div>

              <div className="stat-card credits-total">
                <div className="stat-icon">🎯</div>
                <div className="stat-content">
                  <div className="stat-label">Total Required</div>
                  <div className="stat-value">{displayData.academic_summary.total_credits_required || 120}</div>
                </div>
              </div>

              <div className="stat-card credits-remaining">
                <div className="stat-icon">📝</div>
                <div className="stat-content">
                  <div className="stat-label">Remaining</div>
                  <div className="stat-value">{displayData.academic_summary.remaining_credits || 0}</div>
                </div>
              </div>
            </div>
          )}

          {/* Progress Bar */}
          {displayData.academic_summary && (
            <div className="progress-section">
              <h3>Degree Progress</h3>
              <div className="progress-bar-container">
                <div 
                  className="progress-bar-fill"
                  style={{
                    width: `${Math.min(100, (displayData.academic_summary.completed_credits / displayData.academic_summary.total_credits_required) * 100)}%`
                  }}
                >
                  <span className="progress-text">
                    {Math.round((displayData.academic_summary.completed_credits / displayData.academic_summary.total_credits_required) * 100)}%
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Courses Sections */}
          {displayData.courses && (
            <>
              <div className="courses-section">
                <h2>✓ Completed Courses ({displayData.courses.completed?.length || 0})</h2>
                {renderCourseList(displayData.courses.completed, 'completed')}
              </div>

              <div className="courses-section">
                <h2>⏳ In Progress ({displayData.courses.in_progress?.length || 0})</h2>
                {renderCourseList(displayData.courses.in_progress, 'in_progress')}
              </div>

              {displayData.courses.remaining?.length > 0 && (
                <div className="courses-section">
                  <h2>📝 Remaining Required ({displayData.courses.remaining.length})</h2>
                  {renderCourseList(displayData.courses.remaining, 'remaining')}
                </div>
              )}
            </>
          )}
        </div>
      ) : (
        <div className="empty-state">
          <div className="empty-icon">📄</div>
          <h2>No Degree Works Data</h2>
          <p>Upload your Degree Works PDF to see your academic progress analysis</p>
          <button 
            className="btn-primary btn-large"
            onClick={() => setShowUpload(true)}
          >
            📤 Upload Your First PDF
          </button>
        </div>
      )}
    </div>
  );
};

export default DegreeWorks;
