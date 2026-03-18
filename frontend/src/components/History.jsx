// frontend/src/components/History.jsx

import React, { useEffect, useRef, useState } from "react";
import { deleteGraph, downloadZip, getGraphById, getHistory } from "../apiService";
import "../css/History.css";

function GraphHistoryTable() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedEntry, setSelectedEntry] = useState(null);
  const [loadingGraph, setLoadingGraph] = useState(false);
  const modalGraphRef = useRef(null);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const data = await getHistory();
        setHistory(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, []);

  // Inject Plotly into the modal each time a new entry is selected
  useEffect(() => {
    if (!selectedEntry || !modalGraphRef.current) return;
    const graphJson = selectedEntry.graph_json;
    if (!graphJson) return;

    if (window.Plotly) {
      window.Plotly.react(
        modalGraphRef.current,
        graphJson.data || [],
        {
          ...(graphJson.layout || {}),
          autosize: true,
          title: undefined,
        },
        { responsive: true }
      );
    }
  }, [selectedEntry]);

  // Format ISO date string to dd/mm/yyyy hh:mm
  const formatDate = (dateString) => {
    try {
      return new Date(dateString).toLocaleString("en-GB", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        hour12: false,
      });
    } catch (e) {
      return "Invalid date";
    }
  };

  const handleDownload = async (id) => {
    try {
      await downloadZip(id);
    } catch (err) {
      console.error(`Download failed: ${err.message}`);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this entry?")) return;
    try {
      await deleteGraph(id);
      setHistory((prev) => prev.filter((entry) => entry.id !== id));
      if (selectedEntry && selectedEntry.id === id) setSelectedEntry(null);
    } catch (err) {
      setError(err.message);
    }
  };

  // Fetch full graph data by id then open the modal
  const handleView = async (id) => {
    setLoadingGraph(true);
    try {
      const data = await getGraphById(id);
      setSelectedEntry(data);
    } catch (err) {
      setError(`Unable to load graph: ${err.message}`);
    } finally {
      setLoadingGraph(false);
    }
  };

  // Close modal and free Plotly memory
  const handleCloseModal = () => {
    if (modalGraphRef.current && window.Plotly) {
      window.Plotly.purge(modalGraphRef.current);
    }
    setSelectedEntry(null);
  };

  const formatParameterValue = (key, value) => {
    if (key === "Modules" && Array.isArray(value)) {
      if (value.length === 0) return "0 module";

      const moduleLabels = value
        .map((module) => {
          if (!module || typeof module !== "object") return null;
          const moduleId = module.module_id || "module";
          const size = module.size ?? "?";
          return `${moduleId} (taille ${size})`;
        })
        .filter(Boolean);

      return moduleLabels.length > 0
        ? moduleLabels.join(", ")
        : `${value.length} modules`;
    }

    if (Array.isArray(value)) {
      return value.join(", ");
    }

    if (value && typeof value === "object") {
      return JSON.stringify(value);
    }

    return String(value);
  };

  return (
    <div className="logs-container">
      <h2>Graph History</h2>

      {loading ? (
        <div>Loading...</div>
      ) : error ? (
        <div className="error">Error: {error}</div>
      ) : history && history.length > 0 ? (
        <div className="overflow-x-auto">
          <table className="log">
            <thead>
              <tr>
                <th>ID</th>
                <th>User</th>
                <th>Title</th>
                <th>Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {history.map((entry) => (
                <tr key={entry.id}>
                  <td>{entry.id}</td>
                  <td>{entry.user || "Anonymous"}</td>
                  <td>{entry.title}</td>
                  <td>{formatDate(entry.created_at)}</td>
                  <td>
                    <div className="action-buttons">
                      <div
                        className="download-btn"
                        onClick={() => handleDownload(entry.id)}
                        title="Download archive"
                      >
                        <i className="fas fa-download"></i>
                      </div>
                      <div
                        className="view-btn"
                        onClick={() => handleView(entry.id)}
                        title="View graph"
                      >
                        <i className="fas fa-eye"></i>
                      </div>
                      <div
                        className="delete-btn"
                        onClick={() => handleDelete(entry.id)}
                        title="Delete entry"
                      >
                        <i className="fas fa-times"></i>
                      </div>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="no-hist">No history available</div>
      )}

      {loadingGraph && (
        <div className="graph-modal-overlay">
          <div className="graph-modal-loading">Loading graph...</div>
        </div>
      )}

      {selectedEntry && !loadingGraph && (
        <div
          className="graph-modal-overlay"
          onClick={handleCloseModal}
          data-testid="graph-modal"
        >
          <div
            className="graph-modal-content"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="graph-modal-header">
              <h3 className="graph-modal-title">
                {selectedEntry.title || "Untitled graph"}
              </h3>
              <button
                className="graph-modal-close"
                onClick={handleCloseModal}
                aria-label="Fermer"
              >
                ✕
              </button>
            </div>

            {selectedEntry.parameters && (
              <div className="graph-modal-params">
                {Object.entries(selectedEntry.parameters).map(([key, val]) => (
                  <span key={key} className="graph-modal-param-badge">
                    <strong>{key}:</strong>{" "}
                    {formatParameterValue(key, val)}
                  </span>
                ))}
              </div>
            )}

            {/* Plotly target — populated via useEffect */}
            <div
              ref={modalGraphRef}
              className="graph-modal-plot"
              data-testid="plotly-container"
            />
          </div>
        </div>
      )}

      <div className="no-hist-b-c">
        <p></p>
      </div>
    </div>
  );
}

export default GraphHistoryTable;