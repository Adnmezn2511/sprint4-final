import React, { useState } from "react";
import "../../css/ZipForm/GenerateZipForm.css";
import BipartiteSection from "./BipartiteSection";
import LayersSection from "./LayersSection";

function GenerateZipForm({ onGenerateZip, onClose }) {
  const [zipName, setZipName] = useState("");
  const [layers, setLayers] = useState([]);
  const [bipartites, setBipartites] = useState([]);
  const [error, setError] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    setError("");

    if (!zipName.trim()) {
      setError("Please enter the zip name.");
      return;
    }
    if (!layers.length) {
      setError("Please add at least one layer.");
      return;
    }
    for (const layer of layers) {
      if (!layer.name.trim()) {
        setError("Each layer must have a name.");
        return;
      }
      if (!layer.files || layer.files.length === 0) {
        setError(
          `Please attach at least one TSV file to the layer ${layer.name}.`
        );
        return;
      }
      for (const file of layer.files) {
        if (!file.name.toLowerCase().endsWith(".tsv")) {
          setError(
            `The file ${file.name} is not a TSV file for the layer ${layer.name}.`
          );
          return;
        }
      }
    }
    for (const bip of bipartites) {
      if (!bip.layer1 || !bip.layer2) {
        setError("Please select both layers for each bipartite.");
        return;
      }
      if (!bip.file) {
        setError(
          `Please attach a TSV file for the bipartite between ${bip.layer1} and ${bip.layer2}.`
        );
        return;
      }
      if (!bip.file.name.toLowerCase().endsWith(".tsv")) {
        setError(
          `The file ${bip.file.name} is not a TSV file for the bipartite between ${bip.layer1} and ${bip.layer2}.`
        );
        return;
      }
    }

    onGenerateZip({ zipName, layers, bipartites });
    onClose();
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <button className="modal-close" onClick={onClose}>
          ×
        </button>
        <h3>Generate Zip</h3>
        <form onSubmit={handleSubmit} className="generate-zip-form">
          <div className="form-group">
            <label>Zip Name:</label>
            <input
              type="text"
              value={zipName}
              onChange={(e) => setZipName(e.target.value)}
              placeholder="Enter the zip name"
              required
            />
          </div>
          <LayersSection layers={layers} setLayers={setLayers} />
          <BipartiteSection
            bipartites={bipartites}
            setBipartites={setBipartites}
            layers={layers}
          />
          {error && <div className="error-message">{error}</div>}
          <button type="submit" className="submit-button">
            Generate Zip
          </button>
        </form>
      </div>
    </div>
  );
}

export default GenerateZipForm;
