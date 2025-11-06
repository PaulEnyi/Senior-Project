import React from 'react';
import { motion } from 'framer-motion';
import { 
  FaGraduationCap, 
  FaCalendarAlt, 
  FaClipboardList, 
  FaUsers,
  FaLaptopCode,
  FaBriefcase,
  FaQuestionCircle,
  FaMapMarkerAlt
} from 'react-icons/fa';

const QuickQuestions = ({ onSelect }) => {
  const questions = [
    {
      icon: <FaGraduationCap />,
      category: 'Courses',
      text: 'What are the prerequisites for COSC 211 Data Structures?',
      color: 'orange'
    },
    {
      icon: <FaCalendarAlt />,
      category: 'Registration',
      text: 'When does registration open for Spring 2025?',
      color: 'blue'
    },
    {
      icon: <FaClipboardList />,
      category: 'Requirements',
      text: 'What courses do I need to graduate with a CS degree?',
      color: 'green'
    },
    {
      icon: <FaUsers />,
      category: 'Advising',
      text: 'How do I schedule an appointment with my advisor?',
      color: 'purple'
    },
    {
      icon: <FaLaptopCode />,
      category: 'Resources',
      text: 'Where can I get tutoring for programming courses?',
      color: 'pink'
    },
    {
      icon: <FaBriefcase />,
      category: 'Career',
      text: 'What internship opportunities are available for CS students?',
      color: 'yellow'
    },
    {
      icon: <FaQuestionCircle />,
      category: 'General',
      text: 'What student organizations can I join as a CS major?',
      color: 'teal'
    },
    {
      icon: <FaMapMarkerAlt />,
      category: 'Location',
      text: 'Where is the Computer Science department office located?',
      color: 'red'
    }
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        type: 'spring',
        stiffness: 100
      }
    }
  };

  return (
    <div className="quick-questions">
      <h3 className="quick-questions-title">Quick Questions</h3>
      <motion.div
        className="questions-grid"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {questions.map((question, index) => (
          <motion.button
            key={index}
            variants={itemVariants}
            className={`question-card question-${question.color}`}
            onClick={() => onSelect(question.text)}
            whileHover={{ scale: 1.02, translateY: -2 }}
            whileTap={{ scale: 0.98 }}
          >
            <div className="question-icon">
              {question.icon}
            </div>
            <div className="question-content">
              <span className="question-category">{question.category}</span>
              <p className="question-text">{question.text}</p>
            </div>
          </motion.button>
        ))}
      </motion.div>
    </div>
  );
};

export default QuickQuestions;