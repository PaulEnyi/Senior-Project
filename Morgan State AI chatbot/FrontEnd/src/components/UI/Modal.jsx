import React, { useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiX, FiInfo, FiCheck, FiAlertTriangle } from 'react-icons/fi';
import './Modal.css';

const Modal = ({
  isOpen = false,
  onClose,
  title,
  children,
  size = 'medium', // 'small', 'medium', 'large', 'fullscreen'
  showCloseButton = true,
  closeOnBackdropClick = true,
  closeOnEscape = true,
  className = '',
  headerActions = null,
  footerActions = null
}) => {
  const modalRef = useRef(null);
  const previousActiveElement = useRef(null);

  // Handle escape key
  useEffect(() => {
    const handleEscape = (event) => {
      if (event.key === 'Escape' && closeOnEscape && isOpen) {
        onClose();
      }
    };

    if (isOpen && closeOnEscape) {
      document.addEventListener('keydown', handleEscape);
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen, closeOnEscape, onClose]);

  // Focus management for accessibility
  useEffect(() => {
    if (isOpen) {
      // Store the previously focused element
      previousActiveElement.current = document.activeElement;
      
      // Focus the modal
      if (modalRef.current) {
        modalRef.current.focus();
      }
      
      // Prevent body scroll
      document.body.style.overflow = 'hidden';
    } else {
      // Restore focus to the previously focused element
      if (previousActiveElement.current) {
        previousActiveElement.current.focus();
      }
      
      // Restore body scroll
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  // Handle backdrop click
  const handleBackdropClick = (event) => {
    if (event.target === event.currentTarget && closeOnBackdropClick) {
      onClose();
    }
  };

  // Animation variants
  const backdropVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1 }
  };

  const modalVariants = {
    hidden: { 
      opacity: 0, 
      scale: 0.8,
      y: -50
    },
    visible: { 
      opacity: 1, 
      scale: 1,
      y: 0,
      transition: {
        type: "spring",
        stiffness: 300,
        damping: 30
      }
    },
    exit: {
      opacity: 0,
      scale: 0.8,
      y: -50,
      transition: {
        duration: 0.2
      }
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          className="modal-backdrop"
          variants={backdropVariants}
          initial="hidden"
          animate="visible"
          exit="hidden"
          onClick={handleBackdropClick}
        >
          <motion.div
            ref={modalRef}
            className={`modal modal-${size} ${className}`}
            variants={modalVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
            role="dialog"
            aria-modal="true"
            aria-labelledby={title ? "modal-title" : undefined}
            tabIndex={-1}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            {(title || showCloseButton || headerActions) && (
              <div className="modal-header">
                <div className="modal-header-content">
                  {title && (
                    <h2 id="modal-title" className="modal-title">
                      {title}
                    </h2>
                  )}
                  
                  <div className="modal-header-actions">
                    {headerActions}
                    {showCloseButton && (
                      <button
                        className="modal-close-button"
                        onClick={onClose}
                        aria-label="Close modal"
                        type="button"
                      >
                        <FiX />
                      </button>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Modal Body */}
            <div className="modal-body">
              {children}
            </div>

            {/* Modal Footer */}
            {footerActions && (
              <div className="modal-footer">
                {footerActions}
              </div>
            )}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

// Confirmation Modal - Specialized component for confirmations
export const ConfirmationModal = ({
  isOpen,
  onClose,
  onConfirm,
  title = "Confirm Action",
  message,
  confirmText = "Confirm",
  cancelText = "Cancel",
  variant = "default", // 'default', 'danger', 'warning'
  isLoading = false
}) => {
  const handleConfirm = () => {
    onConfirm();
  };

  const footerActions = (
    <div className="confirmation-actions">
      <button
        className="btn secondary"
        onClick={onClose}
        disabled={isLoading}
      >
        {cancelText}
      </button>
      <button
        className={`btn ${variant === 'danger' ? 'danger' : 'primary'}`}
        onClick={handleConfirm}
        disabled={isLoading}
      >
        {isLoading ? (
          <>
            <span className="spinner"></span>
            Processing...
          </>
        ) : (
          confirmText
        )}
      </button>
    </div>
  );

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={title}
      size="small"
      footerActions={footerActions}
      className={`confirmation-modal ${variant}`}
    >
      <div className="confirmation-content">
        <p>{message}</p>
      </div>
    </Modal>
  );
};

// Alert Modal - For displaying important messages
export const AlertModal = ({
  isOpen,
  onClose,
  title,
  message,
  type = "info", // 'info', 'success', 'warning', 'error'
  buttonText = "OK"
}) => {
const getIcon = () => {
  switch (type) {
    case 'success': return <FiCheck size={32} />;
    case 'warning': return <FiAlertTriangle size={32} />;
    case 'error': return <FiX size={32} />;
    default: return <FiInfo size={32} />;
  }
};

  const footerActions = (
    <button className="btn primary" onClick={onClose}>
      {buttonText}
    </button>
  );

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={title}
      size="small"
      footerActions={footerActions}
      className={`alert-modal ${type}`}
    >
      <div className="alert-content">
        <div className="alert-icon">{getIcon()}</div>
        <p>{message}</p>
      </div>
    </Modal>
  );
};

// Loading Modal - For showing loading states
export const LoadingModal = ({
  isOpen,
  title = "Loading...",
  message = "Please wait while we process your request.",
  showProgress = false,
  progress = 0
}) => {
  return (
    <Modal
      isOpen={isOpen}
      onClose={() => {}} // No close function for loading modals
      title={title}
      size="small"
      showCloseButton={false}
      closeOnBackdropClick={false}
      closeOnEscape={false}
      className="loading-modal"
    >
      <div className="loading-content">
        <div className="loading-spinner">
          <div className="spinner large"></div>
        </div>
        <p className="loading-message">{message}</p>
        
        {showProgress && (
          <div className="progress-container">
            <div className="progress-bar">
              <div 
                className="progress-fill"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
            <span className="progress-text">{progress}%</span>
          </div>
        )}
      </div>
    </Modal>
  );
};

export default Modal;