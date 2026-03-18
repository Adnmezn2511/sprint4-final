import '../css/MAApplied.css';
import React, { useState, useEffect } from 'react';
import { Link, useLocation, useParams } from 'react-router-dom';
import { Line } from 'react-chartjs-2'; 
import Papa from 'papaparse'; 
import { Chart as ChartJS, Title, Tooltip, Legend, LineElement, PointElement, CategoryScale, LinearScale } from 'chart.js';

ChartJS.register(Title, Tooltip, Legend, LineElement, PointElement, CategoryScale, LinearScale);

function MAApplied() {
  useEffect(() => {
        document.title = "GM | Random walk results";
      }, []);

  const location = useLocation();
  const { steps, seeds } = location.state || {};  
  console.log("steps: " + steps);
  console.log("seeds: " + seeds);
  const { nomcouche, seed} = useParams(); 
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({steps: '0', seeds: '0', graine: ''});
  const [seedsData, setSeedsData] = useState(''); 
  const [searchTerm, setSearchTerm] = useState(''); 
  const [filteredSeeds, setFilteredSeeds] = useState([]); 
  const [selectedSeed, setSelectedSeed] = useState(null);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');
  };

  return (
    <div>
      <div className="options-container">
        <h2>Random walk Algorithm applied on seeds : {seed}</h2>
        <div className="params-chosen">
        <h4> Chosen parameters</h4>
        <p> Steps</p>
        <p> {steps}</p>
        <p> Restarts</p>
        <p> {seeds}</p>
        </div>
        <Link to={`/multiplex/${nomcouche}`} className="mmapplied-return">
            <i className="fas fa-chevron-left fa-xs"></i>
            <i className="fas fa-chevron-left fa-xs"></i>
            <i className="fas fa-chevron-left fa-xs"></i>
        </Link>
      </div>
    </div>
  );
}

export default MAApplied;
