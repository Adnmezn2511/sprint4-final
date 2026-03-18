import React from 'react';
import '../css/Alert.css'; 

const Alert = ({ message, onClose }) => {
  return (
    <div className="alert-container">
      <div className="alert">
        <p>{message}</p>
        <button onClick={onClose} className="close-alert-button">
            <i className="fas fa-times"></i>    
        </button>
      </div>
    </div>
  );
};

export default Alert;
