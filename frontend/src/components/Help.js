import React from 'react';
import '../css/Help.css'; 

const Help = ({ onClose }) => {
  return (
    <div className="help-container">
      <div className="help">
        <h2> Aide - Manuel utilisateur </h2>
        <p>Vous pouvez accéder aux anciens résultats dans l'onglet <strong>Logs</strong>.</p>
        <p>Vous pouvez au choix afficher ou télécharger le multiplex de sortie.</p>
        <p>Vous pouvez accéder aux détails concernant le format des données dans l'onglet <strong>Data</strong>.</p>

        <button onClick={onClose} className="close-help-button">
            <i className="fas fa-times"></i>    
        </button>
      </div>
    </div>
  );
};

export default Help;
