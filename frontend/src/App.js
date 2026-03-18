import { React } from "react";
import { BrowserRouter as Router, Routes, Route, useLocation } from "react-router-dom";
import Toolbar from "./components/Toolbar";
import Home from "./components/Home";
import MultiplexLOAD from "./components/MultiplexLOAD";
import MultiplexCHOICE from "./components/MultiplexCHOICE";
import MultiplexMA from "./components/MultiplexMA";
import MultiplexTYPE from "./components/MultiplexTYPE";
import MultiplexSeedLOAD from "./components/MultiplexSeedLOAD";
import MultiplexMultipatientMA from "./components/MultiplexMultipatientMA";
import MultiplexMultipatientLIST from "./components/MultiplexMultipatientLIST";
import MAApplied from "./components/MAApplied";
import Logs from "./components/Logs";
import Credits from "./components/Credits";
import './App.css';
import Graph from "./components/Graph";
import TestApi from "./components/TestAPi";
import History from "./components/History";
import ParentComponent from "./components/Parent";

function App() {
 

  const location = useLocation();

  const hideSidebarRoutes = ["/testApi, /graph, /graph-viewer"];

  return (
    <div className="App">
      {!hideSidebarRoutes.includes(location.pathname) && <Toolbar />}

      <Routes>
        <Route
          path="/"
          element={
            <>
              <Home />
            </>
          }
        />
        <Route path="/multiplex/" element={<MultiplexLOAD />} />
        <Route path="/multiplex/type_choice" element={<MultiplexTYPE />} />
        <Route path="/multiplex/seed-load" element={<MultiplexSeedLOAD />} />
        <Route path="/multiplex/multipatient" element={<MultiplexMultipatientMA />} />
        <Route path="/multiplex/multipatient/list" element={<MultiplexMultipatientLIST />} />
        <Route path="/multiplex/couche" element={<MultiplexCHOICE />} />
        <Route path="/multiplex/:nomcouche" element={<MultiplexMA />} />
        <Route path="/logs" element={<History />} />
        <Route path="/credits" element={<Credits />} />
        <Route path="/graph" element={<ParentComponent />} />
        <Route path="/testApi" element={<TestApi />} />
      </Routes>
    </div>
  );
}

export default function Root() {
  return (
    <Router>
      <App />
    </Router>
  );
}
