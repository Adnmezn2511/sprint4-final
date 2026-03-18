import React, { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { GraphJson } from "../apiService";
import "../css/MultiplexMA.css";
import Alert from "./Alert";
function MultiplexMA() {
  useEffect(() => {
    document.title = "GM | Multiplex's seeds selection";
  }, []);

  const location = useLocation();
  const { couche, tsvs } = location.state || {};
  console.log("couche : " + couche);
  console.log("tsvs :" + tsvs);

  const [formData, setFormData] = useState({
    title: "",
    user: "",
    steps: 1,
    top: 10,
    restart: 0.7,
    seeds: "",
  });
  const [seedsData, setSeedsData] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [filteredSeeds, setFilteredSeeds] = useState([]);
  const [selectedSeeds, setSelectedSeeds] = useState([]);
  const [showAlert, setShowAlert] = useState(false);
  const [pannelSeeds, setPannelSeeds] = useState(false);
  const [graphData, setGraphData] = useState(null);
  const [loading, setLoading] = useState(false);

  const parseTsv = (tsvFiles) => {
    const nodes = [];
    tsvFiles.forEach((tsvFile) => {
      const rows = tsvFile.split("\n");
      rows.forEach((row) => {
        const [node1, node2] = row.split("\t");
        if (node1) {
          const n1 = node1.trim();
          if (!nodes.includes(n1)) nodes.push(n1);
        }
        if (node2) {
          const n2 = node2.trim();
          if (!nodes.includes(n2)) nodes.push(n2);
        }
      });
    });
    setSeedsData(nodes);
    console.log("Seeds Data:", nodes);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    if (name === "seeds") {
      if (value !== "") openPannelSeeds();
      // pb du trim()
      const seedsArray = value.split(",");
      setSelectedSeeds(seedsArray);
      console.log("seedsArray: " + seedsArray);
    }

    setFormData((prevFormData) => ({
      ...prevFormData,
      [name]: value,
    }));
  };

  const removeAllSeeds = () => {
    setSelectedSeeds([]);
    setPannelSeeds(false);
  };

  const closePannelSeeds = () => {
    const vSeeds = selectedSeeds.filter((seed) => seedsData.includes(seed));
    setSelectedSeeds(vSeeds);
    setFormData((prevFormData) => ({
      ...prevFormData,
      seeds: vSeeds,
    }));
    setPannelSeeds(false);
  };

  const openPannelSeeds = () => {
    setPannelSeeds(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log(
      "seeds : " +
        formData.seeds +
        ", steps : " +
        formData.steps +
        ", restart : " +
        formData.restart +
        ", user : " +
        formData.user +
        ", title :" +
        formData.title
    );

    if (
      selectedSeeds.length === 0 ||
      formData.title === "" ||
      formData.user === "" ||
      pannelSeeds
    ) {
      setShowAlert(true);
    } else {
      try {
        setLoading(true);

        // Appel à GraphJson pour obtenir les données du graphique
        const response = await GraphJson(
          formData.seeds,
          formData.steps,
          formData.top,
          formData.restart,
          formData.user,
          formData.title
        );
        setGraphData(response);

        // Ouvrir une nouvelle fenêtre pour afficher le graphique
        const newWindow = window.open("", "_blank");

        if (newWindow) {
          newWindow.document.write(
            '<html><head><title>Graph</title><script src="https://cdn.plot.ly/plotly-latest.min.js"></script></head><body>'
          );

          // Insérer un conteneur pour le graphique
          newWindow.document.write(
            '<div id="plotly-container" style="width: 100%; height: 100%;"></div>'
          );

          // Ajouter un script pour afficher le graphique
          newWindow.document.write(`
            <script>
              const plotData = ${JSON.stringify(response)};
              Plotly.newPlot('plotly-container', plotData.data, plotData.layout);
            </script>
          `);

          newWindow.document.write("</body></html>");
          newWindow.document.close();
        } else {
          console.error("Impossible d'ouvrir un nouvel onglet.");
        }
      } catch (error) {
        console.error("Erreur lors de l'appel à GraphJson:", error);
      } finally {
        setLoading(false);
      }
    }
  };

  const closeAlert = () => {
    setShowAlert(false);
  };

  const loadSeedsData = async () => {
    try {
      const response = await fetch("/seeds_740.txt");
      const txtText = await response.text();
      console.log("txt : " + txtText);
      setSeedsData(txtText);
    } catch (error) {
      console.error("Erreur lors du chargement du fichier .txt :", error);
    }
  };

  const handleClickOnSeed = (seed) => {
    if (selectedSeeds.includes(seed)) {
      setSelectedSeeds(selectedSeeds.filter((s) => s !== seed));
    } else {
      setSelectedSeeds([...selectedSeeds, seed]);
    }
    openPannelSeeds();
  };

  useEffect(() => {
    if (searchTerm) {
      const filtered = seedsData.filter((node) =>
        node.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredSeeds(filtered);
    } else {
      setFilteredSeeds([]);
    }
  }, [searchTerm, seedsData]);

  useEffect(() => {
    if (tsvs) parseTsv(tsvs);
  }, [tsvs]);

  useEffect(() => {
    setFormData((prevFormData) => ({
      ...prevFormData,
      seeds: selectedSeeds,
    }));
  }, [selectedSeeds]);

  return (
    <div>
      {loading ? (
        <div className="loading-container">
          <p>Executing the random walk...</p>
          <div className="spinner"></div>
        </div>
      ) : (
        <div>
          <div className="algo-options-container1">
            <form className="mma-form" onSubmit={handleSubmit}>
              <h2 className="mma-form-title">Random walk Algorithm</h2>

              <div className="mma-form-group">
                <label htmlFor="title">Title</label>
                <input
                  type="text"
                  name="title"
                  id="title"
                  value={formData.title}
                  onChange={handleChange}
                  placeholder="Title"
                  required
                />
              </div>
              <div className="mma-form-group">
                <label htmlFor="user">User</label>
                <input
                  type="text"
                  name="user"
                  id="user"
                  value={formData.user}
                  onChange={handleChange}
                  placeholder="User"
                  required
                />
              </div>
              <div className="mma-form-group">
                <label htmlFor="steps">Steps</label>
                <input
                  value={formData.steps}
                  onChange={handleChange}
                  min="1"
                  step="1"
                  type="number"
                  name="steps"
                  id="steps"
                  placeholder={formData.steps}
                />
              </div>
              <div className="mma-form-group">
                <label htmlFor="top">Top</label>
                <input
                  value={formData.top}
                  onChange={handleChange}
                  min="1"
                  step="1"
                  max="1000"
                  type="number"
                  name="top"
                  id="top"
                  placeholder={formData.top}
                />
              </div>
              <div className="mma-form-group">
                <label htmlFor="restart">Restarts</label>
                <input
                  value={formData.restart}
                  onChange={handleChange}
                  min="0.1"
                  step="0.1"
                  max="0.9"
                  type="number"
                  name="restart"
                  id="restart"
                  placeholder={formData.restart}
                />
              </div>
              <div className="mma-form-group">
                <label htmlFor="seeds">Seeds</label>
                <input
                  type="text"
                  name="seeds"
                  id="seeds"
                  value={formData.seeds}
                  onChange={handleChange}
                  placeholder="Label"
                  required
                />
              </div>
              {selectedSeeds.length > 0 && pannelSeeds && (
                <div
                  className={`${
                    selectedSeeds.some((line) => !seedsData.includes(line))
                      ? "popup-seeds-invalid"
                      : "popup-seeds-valid"
                  }`}
                  draggable="true"
                >
                  {selectedSeeds.map((line, index) => {
                    const included = filteredSeeds.includes(line);
                    const validS = seedsData.includes(line);
                    return (
                      <div
                        key={index}
                        className={`popup-seeds-sc`}
                        onClick={() => handleClickOnSeed(line)}
                      >
                        {!validS ? (
                          <p className="seed-invalid-atm">{line}</p>
                        ) : (
                          <p>{line}</p>
                        )}
                      </div>
                    );
                  })}
                  <i className="fas fa-times" onClick={removeAllSeeds}></i>
                  <i className="fas fa-check" onClick={closePannelSeeds}></i>
                </div>
              )}

              <button
                type="submit"
                className="mma-button"
                onClick={handleSubmit}
              >
                Start
              </button>

              {showAlert && !pannelSeeds && (
                <Alert
                  message="Every parameter needs to be filled before applying this algorithm."
                  onClose={closeAlert}
                />
              )}
              {showAlert && pannelSeeds && (
                <Alert
                  message="You must valid your selection before pursuing."
                  onClose={closeAlert}
                />
              )}

              <Link to="/multiplex/" className="mma-change-couche">
                <i className="fas fa-chevron-left fa-xs"></i>
                <i className="fas fa-chevron-left fa-xs"></i>
                <i className="fas fa-chevron-left fa-xs"></i>
              </Link>
            </form>
          </div>

          <div className="seeds-global-container1">
            <h2>
              Seeds available in the <strong>{couche}</strong> layer
            </h2>
            <div className="seeds-search-field">
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search seeds..."
                className="search-input"
              />
            </div>

            <div className="seeds-container">
              {seedsData
                .sort((a, b) => {
                  const isACorrect = filteredSeeds.includes(a);
                  const isBCorrect = filteredSeeds.includes(b);

                  if (isACorrect && !isBCorrect) return -1;
                  if (!isACorrect && isBCorrect) return 1;

                  return a.localeCompare(b, undefined, { sensitivity: "base" });
                })
                .map((line, index) => {
                  const included = filteredSeeds.includes(line);
                  return (
                    <div
                      key={index}
                      className={`seed-card ${
                        searchTerm ? (included ? "correct" : "opacity") : ""
                      } ${selectedSeeds.includes(line) ? "chosen" : ""}`}
                      onClick={() => handleClickOnSeed(line)}
                    >
                      <p>{line}</p>
                    </div>
                  );
                })}
            </div>
          </div>
        </div>
      )}
      <div className="MA-blank-container">
        {" "}
        <p> </p>
      </div>
    </div>
  );
}

export default MultiplexMA;
