import React from 'react';
import { motion } from 'framer-motion';
import { FiCpu } from 'react-icons/fi';
import './TypingIndicator.css';

const TypingIndicator = ({ 
  message = "Morgan AI is thinking...", 
  showAvatar = true,
  variant = "default"
}) => {
  const dotVariants = {
    start: { y: 0 },
    end: { y: -10 }
  };

  const containerVariants = {
    hidden: { opacity: 0, y: 10, scale: 0.95 },
    visible: {
      opacity: 1,
      y: 0,
      scale: 1,
      transition: {
        duration: 0.3,
        ease: "easeOut"
      }
    }
  };

  const avatarVariants = {
    pulse: {
      scale: [1, 1.1, 1],
      opacity: [0.8, 1, 0.8],
      transition: {
        duration: 2,
        repeat: Infinity,
        ease: "easeInOut"
      }
    }
  };

  if (variant === "minimal") {
    return (
      <motion.div
        className="typing-indicator minimal"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        exit="hidden"
      >
        <div className="typing-dots minimal">
          {[0, 1, 2].map((i) => (
            <motion.div
              key={i}
              className="dot"
              variants={dotVariants}
              initial="start"
              animate="end"
              transition={{
                duration: 0.6,
                repeat: Infinity,
                repeatType: "reverse",
                delay: i * 0.2
              }}
            />
          ))}
        </div>
      </motion.div>
    );
  }

  if (variant === "compact") {
    return (
      <motion.div
        className="typing-indicator compact"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        exit="hidden"
      >
        <div className="typing-content">
          <div className="typing-dots">
            {[0, 1, 2].map((i) => (
              <motion.div
                key={i}
                className="dot"
                variants={dotVariants}
                initial="start"
                animate="end"
                transition={{
                  duration: 0.6,
                  repeat: Infinity,
                  repeatType: "reverse",
                  delay: i * 0.2
                }}
              />
            ))}
          </div>
          <span className="typing-text">{message}</span>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      className="typing-indicator default"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      exit="hidden"
    >
      {showAvatar && (
        <motion.div 
          className="typing-avatar"
          variants={avatarVariants}
          animate="pulse"
        >
          <div className="avatar-content">
            <FiCpu />
          </div>
        </motion.div>
      )}

      <div className="typing-message">
        <div className="typing-bubble">
          <div className="typing-content">
            <div className="typing-dots">
              {[0, 1, 2].map((i) => (
                <motion.div
                  key={i}
                  className="dot"
                  variants={dotVariants}
                  initial="start"
                  animate="end"
                  transition={{
                    duration: 0.6,
                    repeat: Infinity,
                    repeatType: "reverse",
                    delay: i * 0.2
                  }}
                />
              ))}
            </div>
            
            <span className="typing-text">{message}</span>
          </div>
          
          <div className="typing-progress">
            <motion.div
              className="progress-bar"
              initial={{ width: 0 }}
              animate={{ width: "100%" }}
              transition={{
                duration: 3,
                repeat: Infinity,
                ease: "easeInOut"
              }}
            />
          </div>
        </div>
        
        <div className="typing-timestamp">
          {new Date().toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
          })}
        </div>
      </div>
    </motion.div>
  );
};

export const EnhancedTypingIndicator = ({ 
  message = "Morgan AI is analyzing your question...",
  steps = [
    "Processing your question...",
    "Searching knowledge base...",
    "Generating response..."
  ],
  currentStep = 0,
  showProgress = true
}) => {
  const currentMessage = steps[currentStep] || message;
  const progress = ((currentStep + 1) / steps.length) * 100;

  return (
    <motion.div
      className="typing-indicator enhanced"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
    >
      <div className="enhanced-content">
        <div className="enhanced-avatar">
          <div className="avatar-base">
            <FiCpu />
          </div>
          <div className="activity-ring">
            <motion.div
              className="ring"
              animate={{ rotate: 360 }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: "linear"
              }}
            />
          </div>
        </div>

        <div className="enhanced-message">
          <div className="message-bubble">
            <div className="step-content">
              <motion.span
                key={currentStep}
                className="step-text"
                initial={{ opacity: 0, x: 10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -10 }}
                transition={{ duration: 0.3 }}
              >
                {currentMessage}
              </motion.span>
              
              <div className="inline-dots">
                {[0, 1, 2].map((i) => (
                  <motion.span
                    key={i}
                    className="inline-dot"
                    animate={{
                      opacity: [0.3, 1, 0.3]
                    }}
                    transition={{
                      duration: 1.2,
                      repeat: Infinity,
                      delay: i * 0.2
                    }}
                  >
                    •
                  </motion.span>
                ))}
              </div>
            </div>

            {showProgress && (
              <div className="step-progress">
                <motion.div
                  className="progress-fill"
                  initial={{ width: 0 }}
                  animate={{ width: `${progress}%` }}
                  transition={{ duration: 0.5, ease: "easeOut" }}
                />
                <div className="progress-text">
                  Step {currentStep + 1} of {steps.length}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export const PulseIndicator = () => (
  <motion.div
    className="pulse-indicator"
    initial={{ scale: 0.8, opacity: 0 }}
    animate={{ scale: 1, opacity: 1 }}
    exit={{ scale: 0.8, opacity: 0 }}
  >
    <motion.div
      className="pulse-circle"
      animate={{
        scale: [1, 1.5, 1],
        opacity: [1, 0.3, 1]
      }}
      transition={{
        duration: 1.5,
        repeat: Infinity,
        ease: "easeInOut"
      }}
    />
    <motion.div
      className="pulse-center"
      animate={{
        scale: [1, 1.2, 1]
      }}
      transition={{
        duration: 1.5,
        repeat: Infinity,
        ease: "easeInOut",
        delay: 0.2
      }}
    >
      <FiCpu />
    </motion.div>
  </motion.div>
);

export default TypingIndicator;