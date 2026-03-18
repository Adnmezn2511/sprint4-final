import '../css/MultiplexCHOICE.css';
import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';


function MultiplexCHOICE() {
    useEffect(() => {
      document.title = "GM | Multiplex's layer choice";
    }, []);

const navigate = useNavigate();
const location = useLocation();  
const { tsvDict } = location.state || {};
const [formData, setFormData] = useState({ coucheSelect: '' });
const [error, setError] = useState('');

const handleChange = (e) => {
  const value = e.target.value;
  setFormData({ coucheSelect: value });

};

const getFilesFromDict = (layer) => {
  console.log("getFileFromDict, layer : " + layer + ". Dict : " + tsvDict);
  if (tsvDict.hasOwnProperty(layer)) {
    return tsvDict[layer];
  }
  return [];  
}

const handleSubmit = (e) => {
  e.preventDefault();
  const value = formData.coucheSelect;

  if (!value) {
    setError('Please choose a layer before pursuing.');
  } else {
    setError('');
    const selectedFiles = getFilesFromDict(value);
    if (selectedFiles) {
      navigate(`/multiplex/${value}`, {
        state: { couche: value, tsvs: selectedFiles }
      });
    } else {
      setError('No file found.');
    }
  }
};

  return (
      <div className="m-form-container">
      <form className="m-form" onSubmit={handleSubmit}>
        <h2 className="m-form-title">Layer selection</h2>
        {error && <div className="error-message">{error}</div>}
        <div className="m-form-group">
          <select id="coucheSelect" value={formData.coucheSelect} onChange={handleChange}>
          <option value="">Layer</option>
            {Object.entries(tsvDict).map(([layer, files]) => (
              <option key={layer} value={layer}>{layer}</option>
            ))}
          </select>
        </div>
        <Link to="/multiplex" className="m-back">
          <i className="fas fa-chevron-left fa-xs"></i>
          <i className="fas fa-chevron-left fa-xs"></i>
          <i className="fas fa-chevron-left fa-xs"></i>
        </Link>
        <a onClick={handleSubmit} className="m-change-couche">
        <i className="fas fa-chevron-right fa-xs"></i>
        <i className="fas fa-chevron-right fa-xs"></i>
        <i className="fas fa-chevron-right fa-xs"></i></a>
      </form>
    </div>
  );
}

export default MultiplexCHOICE;
