import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FiExternalLink, 
  FiBook, 
  FiUsers, 
  FiCalendar, 
  FiFileText,
  FiGlobe,
  FiMail,
  FiPhone,
  FiMapPin,
  FiChevronDown,
  FiChevronRight
} from 'react-icons/fi';


const ResourceLinks = ({ isCompact = false, showCategories = true }) => {
  const [expandedCategory, setExpandedCategory] = useState(null);

  // Morgan State University links organized by category
  const linkCategories = {
    academic: {
      title: "Academic Resources",
      icon: <FiBook />,
      color: "#FF9100",
      links: [
        {
          title: "Computer Science Department",
          url: "https://www.morgan.edu/scmns/computerscience",
          description: "CS Department homepage with programs and faculty info"
        },
        {
          title: "Course Catalog",
          url: "https://www.morgan.edu/academics/academic-catalog",
          description: "Official course descriptions and requirements"
        },
        {
          title: "Academic Calendar",
          url: "https://www.morgan.edu/academic-calendar",
          description: "Important dates, deadlines, and academic schedule"
        },
        {
          title: "Library Services",
          url: "https://www.morgan.edu/library",
          description: "Earl S. Richardson Library resources and services"
        },
        {
          title: "Canvas LMS",
          url: "https://morganstate.instructure.com/login/ldap",
          description: "Learning management system for courses"
        }
      ]
    },
    student: {
      title: "Student Services",
      icon: <FiUsers />,
      color: "#001B3A",
      links: [
        {
          title: "WebSIS",
          url: "https://lbpsso.morgan.edu/authenticationendpoint/login.do?Name=PreLoginRequestProcessor&TARGET=https%3A%2F%2Fgateway.morgan.edu%2Fcasban%2F",
          description: "Student information system for registration and grades"
        },
        {
          title: "Office of the Registrar",
          url: "https://www.morgan.edu/office-of-the-registrar",
          description: "Registration, transcripts, and academic records"
        },
        {
          title: "Financial Aid",
          url: "https://www.morgan.edu/student-success/financial-aid",
          description: "Scholarships, grants, loans, and financial assistance"
        },
        {
          title: "Student Life",
          url: "https://www.morgan.edu/student-success/student-life",
          description: "Campus activities, organizations, and events"
        },
        {
          title: "Career Center",
          url: "https://www.morgan.edu/student-success/career-center",
          description: "Career counseling, job search, and internship opportunities"
        }
      ]
    },
    department: {
      title: "CS Department",
      icon: <FiFileText />,
      color: "#FF9100",
      links: [
        {
          title: "Faculty and Staff",
          url: "https://www.morgan.edu/computer-science/faculty-and-staff",
          description: "CS faculty profiles, research areas, and contact info"
        },
        {
          title: "Degree Programs",
          url: "https://www.morgan.edu/scmns/computerscience/programs",
          description: "BS, MS degree requirements and curriculum"
        },
        {
          title: "Research Opportunities",
          url: "https://www.morgan.edu/scmns/computerscience/research",
          description: "Undergraduate and graduate research programs"
        },
        {
          title: "Student Organizations",
          url: "https://www.morgan.edu/scmns/computerscience/student-organizations",
          description: "WiCS, GDSC, SACS, and other CS student groups"
        }
      ]
    },
    resources: {
      title: "Online Resources",
      icon: <FiGlobe />,
      color: "#001B3A",
      links: [
        {
          title: "NeetCode",
          url: "https://neetcode.io",
          description: "Coding interview preparation platform",
          external: true
        },
        {
          title: "LeetCode",
          url: "https://leetcode.com",
          description: "Programming practice and coding challenges",
          external: true
        },
        {
          title: "ColorStack",
          url: "https://colorstack.org",
          description: "Community for underrepresented students in tech",
          external: true
        },
        {
          title: "CodePath",
          url: "https://codepath.org",
          description: "Technical interview prep and career development",
          external: true
        },
        {
          title: "GitHub Student Pack",
          url: "https://education.github.com/pack",
          description: "Free developer tools and resources for students",
          external: true
        }
      ]
    }
  };

  const toggleCategory = (categoryKey) => {
    setExpandedCategory(expandedCategory === categoryKey ? null : categoryKey);
  };

  const handleLinkClick = (url, title) => {
    // Track link clicks for analytics (if implemented)
    console.log(`Morgan Link clicked: ${title} - ${url}`);
    window.open(url, '_blank', 'noopener,noreferrer');
  };

  if (isCompact) {
    // Compact view - just show important links
    const quickLinks = [
      { title: "WebSIS", url: linkCategories.student.links[0].url },
      { title: "Canvas", url: linkCategories.academic.links[4].url },
      { title: "CS Dept", url: linkCategories.academic.links[0].url },
      { title: "Academic Calendar", url: linkCategories.academic.links[2].url }
    ];

    return (
      <div className="morgan-links compact">
        <h4 className="links-title">Quick Links</h4>
        <div className="quick-links-grid">
          {quickLinks.map((link, index) => (
            <motion.button
              key={index}
              className="quick-link-btn"
              onClick={() => handleLinkClick(link.url, link.title)}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <span>{link.title}</span>
              <FiExternalLink size={14} />
            </motion.button>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="morgan-links">
      <div className="links-header">
        <h3 className="links-title">Morgan State Resources</h3>
        <p className="links-subtitle">Quick access to university services and tools</p>
      </div>

      {showCategories ? (
        <div className="links-categories">
          {Object.entries(linkCategories).map(([categoryKey, category]) => (
            <motion.div
              key={categoryKey}
              className="link-category"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: Object.keys(linkCategories).indexOf(categoryKey) * 0.1 }}
            >
              <motion.button
                className="category-header"
                onClick={() => toggleCategory(categoryKey)}
                whileHover={{ backgroundColor: '#f8f9fa' }}
                whileTap={{ scale: 0.98 }}
              >
                <div className="category-info">
                  <div 
                    className="category-icon"
                    style={{ color: category.color }}
                  >
                    {category.icon}
                  </div>
                  <span className="category-title">{category.title}</span>
                  <span className="link-count">({category.links.length})</span>
                </div>
                <motion.div
                  className="expand-icon"
                  animate={{ rotate: expandedCategory === categoryKey ? 90 : 0 }}
                  transition={{ duration: 0.2 }}
                >
                  <FiChevronRight />
                </motion.div>
              </motion.button>

              <AnimatePresence>
                {expandedCategory === categoryKey && (
                  <motion.div
                    className="category-links"
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    {category.links.map((link, linkIndex) => (
                      <motion.div
                        key={linkIndex}
                        className="link-item"
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: linkIndex * 0.05 }}
                      >
                        <button
                          className="link-button"
                          onClick={() => handleLinkClick(link.url, link.title)}
                        >
                          <div className="link-content">
                            <div className="link-header">
                              <span className="link-title">{link.title}</span>
                              <div className="link-icons">
                                {link.external && (
                                  <span className="external-badge">External</span>
                                )}
                                <FiExternalLink size={16} className="external-icon" />
                              </div>
                            </div>
                            <p className="link-description">{link.description}</p>
                          </div>
                        </button>
                      </motion.div>
                    ))}
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          ))}
        </div>
      ) : (
        // Flat view - all links in one list
        <div className="all-links">
          {Object.entries(linkCategories).map(([categoryKey, category]) => (
            <div key={categoryKey} className="category-section">
              <h4 className="section-title" style={{ color: category.color }}>
                {category.icon}
                {category.title}
              </h4>
              <div className="section-links">
                {category.links.map((link, linkIndex) => (
                  <button
                    key={linkIndex}
                    className="flat-link-button"
                    onClick={() => handleLinkClick(link.url, link.title)}
                  >
                    <span className="link-title">{link.title}</span>
                    <FiExternalLink size={14} />
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Contact Information */}
      <div className="contact-info">
        <h4 className="contact-title">CS Department Contact</h4>
        <div className="contact-details">
          <div className="contact-item">
            <FiMapPin className="contact-icon" />
            <span>Science Complex, Room 325</span>
          </div>
          <div className="contact-item">
            <FiPhone className="contact-icon" />
            <span>(443) 885-3130</span>
          </div>
          <div className="contact-item">
            <FiMail className="contact-icon" />
            <span>computer.science@morgan.edu</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResourceLinks;