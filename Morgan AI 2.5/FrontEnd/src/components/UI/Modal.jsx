import React from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { FiX } from 'react-icons/fi'
import clsx from 'clsx'

const Modal = ({
  isOpen,
  onClose,
  title,
  children,
  size = 'medium',
  className,
  showCloseButton = true,
  closeOnOverlayClick = true
}) => {
  const sizeClasses = {
    small: 'modal-sm',
    medium: 'modal-md',
    large: 'modal-lg',
    full: 'modal-full'
  }

  const handleOverlayClick = (e) => {
    if (closeOnOverlayClick && e.target === e.currentTarget) {
      onClose()
    }
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            className="modal-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={handleOverlayClick}
          >
            <motion.div
              className={clsx('modal', sizeClasses[size], className)}
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              transition={{ type: 'spring', stiffness: 300, damping: 30 }}
              onClick={(e) => e.stopPropagation()}
            >
              {(title || showCloseButton) && (
                <div className="modal-header">
                  {title && <h2 className="modal-title">{title}</h2>}
                  {showCloseButton && (
                    <button
                      onClick={onClose}
                      className="modal-close"
                      aria-label="Close modal"
                    >
                      <FiX />
                    </button>
                  )}
                </div>
              )}
              
              <div className="modal-content">
                {children}
              </div>
            </motion.div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}

export default Modal