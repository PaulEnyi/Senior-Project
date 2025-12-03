import React from 'react'
import { motion } from 'framer-motion'
import clsx from 'clsx'

const Toggle = ({
  checked,
  onChange,
  disabled = false,
  label,
  size = 'medium',
  className
}) => {
  const sizeClasses = {
    small: 'toggle-sm',
    medium: 'toggle-md',
    large: 'toggle-lg'
  }

  return (
    <label
      className={clsx(
        'toggle-wrapper',
        { 'toggle-disabled': disabled },
        className
      )}
    >
      <div className={clsx('toggle', sizeClasses[size], { checked })}>
        <input
          type="checkbox"
          checked={checked}
          onChange={(e) => onChange(e.target.checked)}
          disabled={disabled}
          className="toggle-input"
        />
        <motion.div
          className="toggle-slider"
          animate={{ x: checked ? 24 : 0 }}
          transition={{ type: 'spring', stiffness: 300, damping: 30 }}
        />
      </div>
      {label && <span className="toggle-label">{label}</span>}
    </label>
  )
}

export default Toggle