import React from "react";
import PlotlyJsonComponent from "../components/Graph";

function ParentComponent() {
  // Exemple de paramètres - à adapter selon vos besoins
  const graphParams = {
    seeds: ["Vapreotide", "Terlipressin"],
    nb_iterations: 1,
    top: 10,
    restart: 0.7,
    user: "user",
    title: "test"
  };

  return (
    <div className="app-container">
      <div className="graph-container">
        <PlotlyJsonComponent
          seeds={graphParams.seeds}
          nb_iterations={graphParams.nb_iterations}
          top={graphParams.top}
          restart={graphParams.restart}
          user={graphParams.user}
          title={graphParams.title}
        />
      </div>
    </div>
  );
}

export default ParentComponent;