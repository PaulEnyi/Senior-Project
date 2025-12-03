import React from 'react';
import { motion } from 'framer-motion';
import './QuickQuestions.css';

const QuickQuestions = ({ onQuestionClick, isVisible }) => {
  const questionsByCategory = {
    "Department Information": [
      "Where is the Computer Science department located?",
      "Who are the faculty members in Computer Science?",
      "What are the department's office hours?",
      "How do I contact the CS department?"
    ],
    "Academic Support": [
      "What tutoring services are available for CS students?",
      "How do I get help with programming assignments?",
      "What study spaces are available for CS students?",
      "How do I form or join a study group for my CS classes?"
    ],
    "Career Resources": [
      "What internship programs are recommended?",
      "How do I prepare for technical interviews?",
      "What career resources are available through the department?",
      "How do I access NeetCode, LeetCode, and other prep resources?"
    ],
    "Student Organizations & Community": [
      "How do I join student organizations like WiCS or GDSC?",
      "What CS-related clubs and organizations can I join?",
      "Are there any upcoming hackathons I can participate in?",
      "How do I get involved with the CS student community?",
      "What networking events are available for CS majors?",
      "Are there coding competitions or programming contests?",
      "How can I connect with other CS majors for collaboration?"
    ],
    "Social & Events": [
      "What tech talks or guest speaker events happen in the CS department?",
      "Are there any CS study sessions or workshops?",
      "How do I find project partners for team assignments?",
      "What social events does the CS department host?",
      "How can I participate in code review sessions or peer programming?"
    ],
    "Advising & Registration": [
      "Who is my academic advisor and how do I contact them?",
      "How do I get an enrollment PIN for registration?",
      "What are the prerequisites for advanced CS courses?",
      "How do I submit an override request for a full class?"
    ]
  };

  if (!isVisible) return null;

  return (
    <motion.div 
      className="quick-questions-container"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 20 }}
      transition={{ duration: 0.3 }}
    >
      <div className="quick-questions-header">
        <h3>Quick Questions</h3>
        <p className="quick-questions-subtitle">Get started with common topics</p>
      </div>

      <div className="categories-grid">
        {Object.entries(questionsByCategory).map(([category, questions], categoryIndex) => (
          <motion.div 
            key={category}
            className="category-section"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: categoryIndex * 0.1 }}
          >
            <h4 className="category-title">{category}</h4>
            <div className="questions-list">
              {questions.map((question, questionIndex) => (
                <motion.button
                  key={questionIndex}
                  className="question-button"
                  onClick={() => onQuestionClick(question)}
                  whileHover={{ scale: 1.02, x: 5 }}
                  whileTap={{ scale: 0.98 }}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: (categoryIndex * 0.1) + (questionIndex * 0.05) }}
                >
                  <span className="question-icon">💬</span>
                  <span className="question-text">{question}</span>
                  <span className="question-arrow">→</span>
                </motion.button>
              ))}
            </div>
          </motion.div>
        ))}
      </div>

      <div className="quick-questions-footer">
        <p className="footer-hint">
          💡 Click any question to start a conversation, or type your own question below
        </p>
      </div>
    </motion.div>
  );
};

export default QuickQuestions;
