import React, { useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { getHistory } from "../apiService";
import "../css/MultiplexMultipatientLIST.css";

function MultiplexMultipatientLIST() {
    useEffect(() => {
        document.title = "GM | Multipatient Graph List";
    }, []);

    const navigate = useNavigate();
    const location = useLocation();
    const [historyGraphs, setHistoryGraphs] = useState([]);
    const [loadingHistory, setLoadingHistory] = useState(false);

  const { graphData } = location.state || {};
  const graphList = useMemo(() => {
    if (Array.isArray(graphData) && graphData.length > 0) {
      return graphData;
    }
    return historyGraphs;
  }, [graphData, historyGraphs]);

  useEffect(() => {
    if (Array.isArray(graphData) && graphData.length > 0) {
      return;
    }

    const loadHistory = async () => {
      try {
        setLoadingHistory(true);
        const history = await getHistory();
        const list = Array.isArray(history) ? history : [];

        const multipatientGraphs = list
          .filter((entry) => typeof entry?.title === "string" && entry.title.startsWith("patient_"))
          .map((entry) => ({
            ...(entry.graph_json || {}),
            _modules: Array.isArray(entry?.parameters?.Modules) ? entry.parameters.Modules : [],
          }))
          .filter(Boolean);

        setHistoryGraphs(multipatientGraphs);
      } catch (error) {
        console.error("Error loading multipatient history:", error);
      } finally {
        setLoadingHistory(false);
      }
    };

    loadHistory();
  }, [graphData]);

  console.log("Received graph data:", graphData);
  console.log("Graph list:", graphList);


  /**
   * This function extract a value searched from a list conaining the metricLabel
   * @param {List} data The list search
   * @param {String} metricLabel The value to find
   * @returns The value found
   */
  const extractMetricValue = (data, metricLabel) => {
    const metricTrace = data.find((trace) => {
      const traceName = trace?.name;
      return (
        typeof traceName === "string" &&
        traceName.toLowerCase().includes(metricLabel.toLowerCase())
      );
    });

    if (!metricTrace || typeof metricTrace.name !== "string") {
      return "N/A";
    }

    const value = metricTrace.name.split(":").pop()?.trim();
    return value || "N/A";
  };

  const openGraphInNewTab = (graph, index) => {
    const newWindow = window.open("", "_blank");

    if (!newWindow) {
      console.error("Impossible d'ouvrir un nouvel onglet.");
      return;
    }

    const title = graph?.layout?.title?.text || `Graph ${index + 1}`;

    newWindow.document.write(
      `<html><head><title>${title}</title><script src="https://cdn.plot.ly/plotly-latest.min.js"></script></head><body>`
    );
    newWindow.document.write(
      '<div id="plotly-container" style="width: 100%; height: 100vh;"></div>'
    );
    newWindow.document.write(`
      <script>
        const plotData = ${JSON.stringify(graph)};
        Plotly.newPlot('plotly-container', plotData.data, plotData.layout);
      </script>
    `);
    newWindow.document.write("</body></html>");
    newWindow.document.close();
  };

  const getModules = (graph) => {
    const modules = graph?._modules;
    return Array.isArray(modules) ? modules : [];
  };

  const mergedGraph = graphList.find((graph) =>
    graph?.layout?.title?.text?.includes("Merged graph")
  );
  const patientGraphs = graphList.filter((graph) =>
    !graph?.layout?.title?.text?.includes("Merged graph")
  );

  if (loadingHistory) {
    return (
      <div>
        <div className="mml-container">
          <h2 className="mml-title">Loading graphs...</h2>
        </div>
      </div>
    );
  }

  if (!graphList.length) {
    return (
      <div>
        <div className="mml-container">
          <h2 className="mml-title">No graph available</h2>
          <p>Launch the multipatient random walk first.</p>
          <button
            type="button"
            className="mml-button"
            onClick={() => navigate("/multiplex/multipatient")}
          >
            Back to parameters
          </button>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="mml-container">
        <h2 className="mml-title">Generated graphs</h2>

        {mergedGraph && (
          <div className="mml-merged-section">
            <button
              type="button"
              className="mml-button mml-merged-button"
              onClick={() => openGraphInNewTab(mergedGraph, -1)}
            >
              Open merged graph (all patients)
            </button>
          </div>
        )}

        <ul className="mml-list">
          {patientGraphs.map((graph, index) => {
            const graphTitle = graph?.layout?.title?.text || `Graph ${index + 1}`;
            const modules = getModules(graph);

            return (
              <li
                key={index}
                className="mml-graph-line"
              >
                <div>
                  <span>{graphTitle}</span>
                  <div className="mml-graph-metrics">
                    <p className="mml-graph-data">
                      Number of Nodes: {extractMetricValue(graph?.data, "• number of nodes : ")}
                    </p>
                    <p className="mml-graph-data">
                      Number of Edges: {extractMetricValue(graph?.data, "• number of edges : ")}
                    </p>
                  </div>
                  <p>
                    Modules détectés: <strong>{modules.length}</strong>
                  </p>
                  {modules.length > 0 && (
                    <details>
                      <summary>Voir la liste des modules</summary>
                      <ul>
                        {modules.map((module) => (
                          <li key={module.module_id}>
                            <strong>{module.module_id}</strong> (taille {module.size}) - {module.nodes.join(", ")}
                          </li>
                        ))}
                      </ul>
                    </details>
                  )}
                </div>
                <button
                  type="button"
                  className="mml-button"
                  onClick={() => openGraphInNewTab(graph, index)}
                >
                  Open
                </button>
              </li>
            );
          })}
        </ul>
      </div>
    </div>
  );
}

export default MultiplexMultipatientLIST;
