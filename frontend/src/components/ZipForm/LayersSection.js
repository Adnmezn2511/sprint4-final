import React from "react";

function LayersSection({ layers, setLayers }) {
  const addLayer = () => {
    setLayers([...layers, { id: Date.now(), name: "", files: [] }]);
  };

  const handleLayerNameChange = (id, value) => {
    setLayers(
      layers.map((layer) =>
        layer.id === id ? { ...layer, name: value } : layer
      )
    );
  };

  const handleFileSelection = (id, event) => {
    const selectedFiles = Array.from(event.target.files);
    setLayers(
      layers.map((layer) =>
        layer.id === id
          ? { ...layer, files: [...layer.files, ...selectedFiles] }
          : layer
      )
    );
  };

  const handleRemoveFile = (layerId, fileIndex) => {
    setLayers(
      layers.map((layer) => {
        if (layer.id === layerId) {
          const updatedFiles = layer.files.filter(
            (_file, idx) => idx !== fileIndex
          );
          return { ...layer, files: updatedFiles };
        }
        return layer;
      })
    );
  };

  const handleRemoveLayer = (layerId) => {
    setLayers(layers.filter((layer) => layer.id !== layerId));
  };

  return (
    <div className="layers-container">
      <h4>Multiplex Layer</h4>
      {layers.map((layer) => (
        <div key={layer.id} className="layer-container">
          <div className="form-group">
            <label>Layer Name:</label>
            <input
              type="text"
              value={layer.name}
              onChange={(e) => handleLayerNameChange(layer.id, e.target.value)}
              placeholder="Layer Name"
            />
          </div>
          <div className="form-group">
            <label>TSV Files:</label>
            {/* Hidden file input */}
            <input
              type="file"
              accept=".tsv"
              multiple
              id={`file-input-${layer.id}`}
              style={{ display: "none" }}
              onChange={(e) => handleFileSelection(layer.id, e)}
            />
            {/* Trigger button */}
            <button
              type="button"
              onClick={() =>
                document.getElementById(`file-input-${layer.id}`).click()
              }
            >
              Select TSV Files
            </button>
            {/* Display selected files with delete option */}
            {layer.files && layer.files.length > 0 && (
              <ul className="file-list">
                {layer.files.map((file, index) => (
                  <li key={index}>
                    {file.name}{" "}
                    <button
                      type="button"
                      onClick={() => handleRemoveFile(layer.id, index)}
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
                  </li>
                ))}
              </ul>
            )}
          </div>
          {/* Layer delete button */}
          <button
            type="button"
            onClick={() => handleRemoveLayer(layer.id)}
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
            Delete Layer
          </button>
        </div>
      ))}
      <button type="button" onClick={addLayer}>
        Add Layer
      </button>
    </div>
  );
}

export default LayersSection;
