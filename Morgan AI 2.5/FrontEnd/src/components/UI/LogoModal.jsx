import React from "react";
import "./logoModal.css";

const LogoModal = ({ show, onClose }) => {
  if (!show) return null;
  return (
    <div className="logo-modal-overlay" onClick={onClose}>
      <div className="logo-modal-content" onClick={e => e.stopPropagation()}>
        <img src="/assets/morgan-logo/morgan-logo.png" alt="Morgan Logo" className="logo-modal-img" />
        <button className="logo-modal-close" onClick={onClose}>Close</button>
      </div>
    </div>
  );
};

export default LogoModal;
