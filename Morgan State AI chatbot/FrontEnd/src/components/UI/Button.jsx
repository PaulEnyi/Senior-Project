import React, { forwardRef } from 'react';
import { motion } from 'framer-motion';
import './Button.css';

const Button = forwardRef(({
  children,
  variant = 'primary',
  size = 'medium',
  disabled = false,
  loading = false,
  icon = null,
  iconPosition = 'left',
  fullWidth = false,
  onClick,
  type = 'button',
  className = '',
  ariaLabel,
  tooltip,
  ...props
}, ref) => {
  
  // Build CSS classes
  const baseClass = 'morgan-button';
  const variantClass = `morgan-button--${variant}`;
  const sizeClass = `morgan-button--${size}`;
  const disabledClass = disabled ? 'morgan-button--disabled' : '';
  const loadingClass = loading ? 'morgan-button--loading' : '';
  const fullWidthClass = fullWidth ? 'morgan-button--full-width' : '';
  const iconOnlyClass = icon && !children ? 'morgan-button--icon-only' : '';
  
  const buttonClasses = [
    baseClass,
    variantClass,
    sizeClass,
    disabledClass,
    loadingClass,
    fullWidthClass,
    iconOnlyClass,
    className
  ].filter(Boolean).join(' ');

  // Handle click events
  const handleClick = (e) => {
    if (disabled || loading) {
      e.preventDefault();
      return;
    }
    if (onClick) {
      onClick(e);
    }
  };

  // Animation variants
  const buttonVariants = {
    hover: {
      scale: disabled || loading ? 1 : 1.02,
      transition: { duration: 0.2 }
    },
    tap: {
      scale: disabled || loading ? 1 : 0.98,
      transition: { duration: 0.1 }
    }
  };

  // Loading spinner component
  const LoadingSpinner = () => (
    <div className="morgan-button__spinner" aria-hidden="true">
      <div className="spinner-circle"></div>
    </div>
  );

  // Render icon
  const renderIcon = () => {
    if (!icon) return null;
    
    return (
      <span 
        className={`morgan-button__icon morgan-button__icon--${iconPosition}`}
        aria-hidden="true"
      >
        {icon}
      </span>
    );
  };

  // Button content
  const buttonContent = (
    <>
      {loading && <LoadingSpinner />}
      {!loading && iconPosition === 'left' && renderIcon()}
      {children && (
        <span className="morgan-button__text">
          {children}
        </span>
      )}
      {!loading && iconPosition === 'right' && renderIcon()}
    </>
  );

  return (
    <motion.button
      ref={ref}
      type={type}
      className={buttonClasses}
      onClick={handleClick}
      disabled={disabled || loading}
      aria-label={ariaLabel || (typeof children === 'string' ? children : undefined)}
      aria-busy={loading}
      title={tooltip}
      variants={buttonVariants}
      whileHover="hover"
      whileTap="tap"
      {...props}
    >
      {buttonContent}
    </motion.button>
  );
});

// Set display name for debugging
Button.displayName = 'Button';

// Button variants for easy access
Button.variants = {
  PRIMARY: 'primary',
  SECONDARY: 'secondary',
  GHOST: 'ghost',
  DANGER: 'danger',
  SUCCESS: 'success',
  WARNING: 'warning',
  LINK: 'link'
};

Button.sizes = {
  SMALL: 'small',
  MEDIUM: 'medium',
  LARGE: 'large'
};

export default Button;