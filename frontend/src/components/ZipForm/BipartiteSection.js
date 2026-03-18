import React from "react";

function BipartiteSection({ bipartites, setBipartites, layers }) {
  const addBipartite = () => {
    setBipartites([
      ...bipartites,
      { id: Date.now(), layer1: "", layer2: "", file: null },
    ]);
  };

  const handleBipartiteChange = (id, field, value) => {
    setBipartites(
      bipartites.map((b) => (b.id === id ? { ...b, [field]: value } : b))
    );
  };

  // Handle TSV file selection for a bipartite
  const handleFileSelection = (id, event) => {
    const selectedFile = event.target.files[0];
    handleBipartiteChange(id, "file", selectedFile);
  };

  // Remove the selected file from the bipartite
  const handleRemoveFile = (id) => {
    handleBipartiteChange(id, "file", null);
  };

  // Remove a bipartite entry
  const handleRemoveBipartite = (id) => {
    setBipartites(bipartites.filter((bip) => bip.id !== id));
  };

  return (
    <div className="bipartite-container">
      <h4>Bipartite</h4>
      {bipartites.map((bip) => (
        <div key={bip.id} className="bipartite-item">
          <div className="form-group">
            <label>Layer 1:</label>
            <select
              value={bip.layer1}
              onChange={(e) =>
                handleBipartiteChange(bip.id, "layer1", e.target.value)
              }
            >
              <option value="">Select a layer</option>
              {layers.map((layer) => (
                <option key={layer.id} value={layer.name}>
                  {layer.name || `Layer ${layer.id}`}
                </option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>Layer 2:</label>
            <select
              value={bip.layer2}
              onChange={(e) =>
                handleBipartiteChange(bip.id, "layer2", e.target.value)
              }
            >
              <option value="">Select a layer</option>
              {layers.map((layer) => (
                <option key={layer.id} value={layer.name}>
                  {layer.name || `Layer ${layer.id}`}
                </option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>TSV File:</label>
            {/* Hidden file input */}
            <input
              type="file"
              accept=".tsv"
              id={`tsv-input-${bip.id}`}
              style={{ display: "none" }}
              onChange={(e) => handleFileSelection(bip.id, e)}
            />
            {/* Trigger button */}
            <button
              type="button"
              onClick={() =>
                document.getElementById(`tsv-input-${bip.id}`).click()
              }
            >
              Select a TSV file
            </button>
            {/* Display the selected file with delete option */}
            {bip.file && (
              <div className="file-display" style={{ marginTop: "10px" }}>
                <span>{bip.file.name}</span>
                <button
                  type="button"
                  onClick={() => handleRemoveFile(bip.id)}
                  style={{
                    marginLeft: "10px",
                    background: "transparent",
                    border: "none",
                    color: "#d9534f",
                    cursor: "pointer",
                  }}
                >
                  Delete
                </button>
              </div>
            )}
          </div>
          {/* Delete bipartite button */}
          <button
            type="button"
            onClick={() => handleRemoveBipartite(bip.id)}
            style={{
              background: "#d9534f",
              color: "#fff",
              border: "none",
              padding: "5px 10px",
              borderRadius: "4px",
              cursor: "pointer",
              marginTop: "10px",
            }}
          >
            Delete Bipartite
          </button>
        </div>
      ))}
      <button type="button" onClick={addBipartite}>
        Add Bipartite
      </button>
    </div>
  );
}

export default BipartiteSection;
