import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FiBriefcase,
  FiMapPin,
  FiClock,
  FiDollarSign,
  FiExternalLink,
  FiCalendar,
  FiUser,
  FiMail,
  FiPhone,
  FiFilter,
  FiSearch,
  FiStar,
  FiBookmark,
  FiTrendingUp
} from 'react-icons/fi';
import '../../styles/career.css';

const InternshipsPage = ({ user }) => {
  const [internships, setInternships] = useState([]);
  const [filteredInternships, setFilteredInternships] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState('all');
  const [selectedLocation, setSelectedLocation] = useState('all');
  const [sortBy, setSortBy] = useState('newest');
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [totalCount, setTotalCount] = useState(0);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Fetch internships from API
  const fetchInternships = async (autoUpdate = true) => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      if (!token) {
        console.log('No auth token found');
        setLoading(false);
        return;
      }

      const params = new URLSearchParams({
        limit: '100',
        offset: '0',
        auto_update: autoUpdate.toString()
      });

      const response = await fetch(`http://localhost:8000/api/internships/list?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setInternships(data.internships || []);
        setFilteredInternships(data.internships || []);
        setTotalCount(data.total || 0);
        setLastUpdate(data.last_update);
        console.log(`Loaded ${data.total} internships from API`);
      } else {
        console.error('Failed to fetch internships:', response.status);
        // Fallback to sample data if API fails
        setInternships(sampleInternships);
        setFilteredInternships(sampleInternships);
      }
    } catch (error) {
      console.error('Error fetching internships:', error);
      // Fallback to sample data if API fails
      setInternships(sampleInternships);
      setFilteredInternships(sampleInternships);
    } finally {
      setLoading(false);
    }
  };

  // Manual refresh function
  const handleRefresh = async () => {
    try {
      setIsRefreshing(true);
      const token = localStorage.getItem('token');
      
      if (!token) {
        return;
      }

      // Trigger immediate update
      const response = await fetch('http://localhost:8000/api/internships/update-now', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        // Fetch updated data
        await fetchInternships(false);
        console.log('Internships refreshed successfully');
      }
    } catch (error) {
      console.error('Error refreshing internships:', error);
    } finally {
      setIsRefreshing(false);
    }
  };

  // Fetch on component mount and user login
  useEffect(() => {
    fetchInternships(true);
  }, [user]); // Re-fetch when user changes (login/logout)

  // Auto-refresh every 5 minutes
  useEffect(() => {
    const interval = setInterval(() => {
      fetchInternships(true);
    }, 5 * 60 * 1000); // 5 minutes

    return () => clearInterval(interval);
  }, []);

  // Sample internship data - fallback only
  const sampleInternships = [
    {
      id: 1,
      title: 'Software Engineering Intern',
      company: 'Microsoft',
      location: 'Redmond, WA',
      type: 'Software Development',
      duration: '12 weeks',
      salary: '$7,000/month',
      deadline: '2024-03-15',
      postedDate: '2024-01-20',
      description: 'Work on cutting-edge cloud technologies and collaborate with senior engineers on Azure platform development.',
      requirements: ['Computer Science major', 'Proficiency in C# or Java', 'Strong problem-solving skills'],
      benefits: ['Housing stipend', 'Transportation', 'Mentorship program', 'Full-time offer potential'],
      applyUrl: 'https://careers.microsoft.com/students',
      featured: true
    },
    {
      id: 2,
      title: 'Data Science Intern',
      company: 'Google',
      location: 'Mountain View, CA',
      type: 'Data Science',
      duration: '10-12 weeks',
      salary: '$8,500/month',
      deadline: '2024-02-28',
      postedDate: '2024-01-15',
      description: 'Analyze large datasets to derive insights for product improvements and user experience optimization.',
      requirements: ['Statistics or CS background', 'Python/R proficiency', 'Machine learning knowledge'],
      benefits: ['Housing support', 'Gym access', 'Free meals', 'Networking events'],
      applyUrl: 'https://careers.google.com/jobs',
      featured: true
    },
    {
      id: 3,
      title: 'Cybersecurity Intern',
      company: 'JPMorgan Chase',
      location: 'New York, NY',
      type: 'Cybersecurity',
      duration: '10 weeks',
      salary: '$6,500/month',
      deadline: '2024-04-01',
      postedDate: '2024-01-25',
      description: 'Support the cybersecurity team in threat analysis, vulnerability assessments, and security protocol development.',
      requirements: ['Cybersecurity or CS major', 'Understanding of network security', 'Security+ certification preferred'],
      benefits: ['Financial planning sessions', 'Professional development', 'Return offer opportunities'],
      applyUrl: 'https://jpmorgan.com/careers',
      featured: false
    },
    {
      id: 4,
      title: 'Mobile App Development Intern',
      company: 'Apple',
      location: 'Cupertino, CA',
      type: 'Mobile Development',
      duration: '12 weeks',
      salary: '$8,000/month',
      deadline: '2024-03-10',
      postedDate: '2024-01-18',
      description: 'Develop iOS applications and contribute to the next generation of mobile experiences.',
      requirements: ['Swift programming experience', 'iOS development knowledge', 'Portfolio of mobile apps'],
      benefits: ['Apple products discount', 'Fitness center', 'Commuter benefits', 'Innovation workshops'],
      applyUrl: 'https://jobs.apple.com/en-us/search',
      featured: false
    },
    {
      id: 5,
      title: 'Cloud Computing Intern',
      company: 'Amazon Web Services',
      location: 'Seattle, WA',
      type: 'Cloud Computing',
      duration: '12 weeks',
      salary: '$7,500/month',
      deadline: '2024-03-20',
      postedDate: '2024-01-22',
      description: 'Work with AWS services and help build scalable cloud solutions for enterprise customers.',
      requirements: ['Cloud computing knowledge', 'Linux/Unix experience', 'AWS certification preferred'],
      benefits: ['Relocation assistance', 'Career mentoring', 'Technical training', 'Full-time conversion'],
      applyUrl: 'https://amazon.jobs/en/business_categories/student-programs',
      featured: false
    },
    {
      id: 6,
      title: 'AI Research Intern',
      company: 'NVIDIA',
      location: 'Santa Clara, CA',
      type: 'Artificial Intelligence',
      duration: '12-16 weeks',
      salary: '$9,000/month',
      deadline: '2024-02-15',
      postedDate: '2024-01-10',
      description: 'Conduct research in machine learning and AI technologies, working alongside leading researchers.',
      requirements: ['PhD or Masters student', 'Deep learning experience', 'Published research preferred'],
      benefits: ['Research publication opportunities', 'Conference attendance', 'GPU access', 'Flexible schedule'],
      applyUrl: 'https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite',
      featured: true
    }
  ];

  // Remove old useEffect that set sample data
  // Filter internships based on search and filters

  useEffect(() => {
    let filtered = internships;

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(internship =>
        internship.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        internship.company.toLowerCase().includes(searchTerm.toLowerCase()) ||
        internship.type.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Filter by type
    if (selectedType !== 'all') {
      filtered = filtered.filter(internship => internship.type === selectedType);
    }

    // Filter by location (simplified)
    if (selectedLocation !== 'all') {
      filtered = filtered.filter(internship => 
        internship.location.includes(selectedLocation)
      );
    }

    // Sort internships
    switch (sortBy) {
      case 'newest':
        filtered.sort((a, b) => new Date(b.postedDate) - new Date(a.postedDate));
        break;
      case 'deadline':
        filtered.sort((a, b) => new Date(a.deadline) - new Date(b.deadline));
        break;
      case 'salary':
        filtered.sort((a, b) => {
          const salaryA = parseInt(a.salary.replace(/[^0-9]/g, ''));
          const salaryB = parseInt(b.salary.replace(/[^0-9]/g, ''));
          return salaryB - salaryA;
        });
        break;
      case 'company':
        filtered.sort((a, b) => a.company.localeCompare(b.company));
        break;
      default:
        break;
    }

    setFilteredInternships(filtered);
  }, [searchTerm, selectedType, selectedLocation, sortBy, internships]);

  const getUniqueValues = (key) => {
    return [...new Set(internships.map(item => item[key]))];
  };

  const formatDeadline = (deadline) => {
    const date = new Date(deadline);
    const now = new Date();
    const diffTime = date - now;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays < 0) return 'Expired';
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Tomorrow';
    return `${diffDays} days left`;
  };

  const getDeadlineColor = (deadline) => {
    const date = new Date(deadline);
    const now = new Date();
    const diffTime = date - now;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays < 0) return '#6B7280';
    if (diffDays <= 7) return '#EF4444';
    if (diffDays <= 14) return '#F59E0B';
    return '#10B981';
  };

  return (
    <div className="internships-container">
      <div className="internships-header">
        <div className="header-content">
          <div className="title-section">
            <div className="title-with-icon">
              <FiBriefcase className="page-icon" />
              <h1 className="page-title">Internship Opportunities</h1>
            </div>
            <p className="page-subtitle">
              Discover amazing internship opportunities to boost your career in Computer Science
              {lastUpdate && (
                <span className="last-update"> • Last updated: {new Date(lastUpdate).toLocaleString()}</span>
              )}
            </p>
          </div>
          
          <div className="header-stats">
            <div className="stat-card">
              <FiTrendingUp className="stat-icon" />
              <div className="stat-info">
                <span className="stat-number">{totalCount > 0 ? totalCount : internships.length}</span>
                <span className="stat-label">Available Positions</span>
              </div>
            </div>
            <div className="stat-card">
              <FiStar className="stat-icon" />
              <div className="stat-info">
                <span className="stat-number">{internships.filter(i => i.featured).length}</span>
                <span className="stat-label">Featured</span>
              </div>
            </div>
            <button
              className="refresh-button"
              onClick={handleRefresh}
              disabled={isRefreshing}
              title="Refresh internship data"
            >
              <FiTrendingUp className={isRefreshing ? 'spinning' : ''} />
              {isRefreshing ? 'Refreshing...' : 'Refresh'}
            </button>
          </div>
        </div>
      </div>

      <div className="internships-content">
        <div className="filters-section">
          <div className="search-bar">
            <FiSearch className="search-icon" />
            <input
              type="text"
              placeholder="Search internships by title, company, or type..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
          </div>
          
          <div className="filter-controls">
            <div className="filter-group">
              <label htmlFor="type-filter">Type:</label>
              <select
                id="type-filter"
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
                className="filter-select"
              >
                <option value="all">All Types</option>
                {getUniqueValues('type').map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>
            
            <div className="filter-group">
              <label htmlFor="location-filter">Location:</label>
              <select
                id="location-filter"
                value={selectedLocation}
                onChange={(e) => setSelectedLocation(e.target.value)}
                className="filter-select"
              >
                <option value="all">All Locations</option>
                <option value="CA">California</option>
                <option value="WA">Washington</option>
                <option value="NY">New York</option>
              </select>
            </div>
            
            <div className="filter-group">
              <label htmlFor="sort-by">Sort By:</label>
              <select
                id="sort-by"
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="filter-select"
              >
                <option value="newest">Newest First</option>
                <option value="deadline">Deadline</option>
                <option value="salary">Salary (High to Low)</option>
                <option value="company">Company Name</option>
              </select>
            </div>
          </div>
        </div>

        <div className="internships-grid">
          {loading ? (
            <div className="loading-state">
              <div className="spinner"></div>
              <p>Loading internships...</p>
            </div>
          ) : (
            <AnimatePresence>
              {filteredInternships.map((internship, index) => (
              <motion.div
                key={internship.id}
                className={`internship-card ${internship.featured ? 'featured' : ''}`}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
                layout
              >
                {internship.featured && (
                  <div className="featured-badge">
                    <FiStar />
                    Featured
                  </div>
                )}
                
                <div className="card-header">
                  <div className="company-info">
                    <h3 className="internship-title">{internship.title}</h3>
                    <p className="company-name">{internship.company}</p>
                  </div>
                  <button className="bookmark-btn" title="Save for later">
                    <FiBookmark />
                  </button>
                </div>
                
                <div className="card-details">
                  <div className="detail-item">
                    <FiMapPin className="detail-icon" />
                    <span>{internship.location}</span>
                  </div>
                  <div className="detail-item">
                    <FiClock className="detail-icon" />
                    <span>{internship.duration}</span>
                  </div>
                  <div className="detail-item">
                    <FiDollarSign className="detail-icon" />
                    <span>{internship.salary}</span>
                  </div>
                  <div className="detail-item">
                    <FiCalendar className="detail-icon" />
                    <span 
                      className="deadline-text"
                      style={{ color: getDeadlineColor(internship.deadline) }}
                    >
                      {formatDeadline(internship.deadline)}
                    </span>
                  </div>
                </div>
                
                <div className="internship-type">
                  <span className="type-badge">{internship.type}</span>
                </div>
                
                <p className="internship-description">
                  {internship.description}
                </p>
                
                <div className="requirements-section">
                  <h4 className="section-title">Key Requirements:</h4>
                  <ul className="requirements-list">
                    {internship.requirements.slice(0, 2).map((req, idx) => (
                      <li key={idx}>{req}</li>
                    ))}
                    {internship.requirements.length > 2 && (
                      <li className="more-requirements">
                        +{internship.requirements.length - 2} more
                      </li>
                    )}
                  </ul>
                </div>
                
                <div className="card-footer">
                  <div className="benefits-preview">
                    <span className="benefits-label">Benefits: </span>
                    <span className="benefits-text">
                      {internship.benefits.slice(0, 2).join(', ')}
                      {internship.benefits.length > 2 && '...'}
                    </span>
                  </div>
                  
                  <a
                    href={internship.applyUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="apply-btn"
                  >
                    Apply Now
                    <FiExternalLink />
                  </a>
                </div>
              </motion.div>
            ))}
            </AnimatePresence>
          )}
        </div>

        {filteredInternships.length === 0 && (
          <div className="no-results">
            <FiBriefcase className="no-results-icon" />
            <h3>No internships found</h3>
            <p>Try adjusting your search criteria or filters</p>
          </div>
        )}
      </div>

      {/* Resources Section */}
      <div className="resources-section">
        <h2 className="resources-title">Career Resources</h2>
        <div className="resources-grid">
          <div className="resource-card">
            <FiUser className="resource-icon" />
            <h3>Career Services</h3>
            <p>Get help with resume reviews, interview prep, and career counseling</p>
            <a href="mailto:career@morgan.edu" className="resource-link">
              <FiMail />
              career@morgan.edu
            </a>
          </div>
          
          <div className="resource-card">
            <FiPhone className="resource-icon" />
            <h3>Career Center</h3>
            <p>Schedule an appointment for personalized career guidance</p>
            <a href="tel:443-885-3130" className="resource-link">
              <FiPhone />
              (443) 885-3130
            </a>
          </div>
          
          <div className="resource-card">
            <FiExternalLink className="resource-icon" />
            <h3>LinkedIn Learning</h3>
            <p>Access free courses to build in-demand skills</p>
            <a 
              href="https://linkedin.com/learning" 
              target="_blank" 
              rel="noopener noreferrer"
              className="resource-link"
            >
              <FiExternalLink />
              Start Learning
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InternshipsPage;