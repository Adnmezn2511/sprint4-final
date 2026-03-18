import { React, useEffect, useRef, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import "../css/Toolbar.css";
import Help from "./Help";
import Params from "./Params";

function Toolbar() {
  const location = useLocation();

  return (
      <div className="navbar">
        <div className="navbar-links">
          <>
          <Link to="/" className={location.pathname === "/" ? "active" : ""}><i className="fas fa-house"></i>          </Link>
          <Link to="/multiplex" className={location.pathname.includes("/multiplex") ? "active" : ""}>Multiplex</Link>
          <Link to="/logs" className={location.pathname === "/logs" ? "active" : ""}>Logs</Link>
          <Link to="/credits" className={location.pathname === "/credits" ? "active" : ""}>Credits</Link>

          </>
        </div>
          </div>
  );
}

export default Toolbar;
