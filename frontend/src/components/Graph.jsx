import React, { useEffect, useState } from "react";
import Plot from "react-plotly.js";
import Plotly from 'plotly.js/lib/core';
import '../css/Graph.css';
import { GraphJson } from "../apiService";

function PlotlyJsonComponent({ 
  seeds, 
  nb_iterations, 
  top, 
  restart, 
  user, 
  title 
}) {
  const [figData, setFigData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const json = await GraphJson(
          seeds, 
          nb_iterations, 
          top, 
          restart, 
          user,
          title
        );
        setFigData(json);
        setError(null);
      } catch (error) {
        console.error("Erreur lors de la récupération du graphique :", error);
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [seeds, nb_iterations, top, restart, user, title]);

  if (loading) {
    return <div>Loading ...</div>;
  }

  if (error) {
    return <div>Error : {error}</div>;
  }

  if (!figData) {
    return <div>No data</div>;
  }

  return (
    <div className="plotly-container">
      <div className="toolbar">
      </div>
      
      {loading && <div className="loading-message">Loading ...</div>}
      
      {error && (
        <div className="error-message">
          Erreur : {error}
        </div>
      )}

      {!loading && !error && figData && (
        <Plot
          className="plotly-graph"
          data={figData.data}
          layout={figData.layout}
          frames={figData.frames}
          config={{ responsive: true }}
        />
      )}
    </div>
  );
}

export default PlotlyJsonComponent;
