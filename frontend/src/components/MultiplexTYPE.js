import React, { useEffect } from "react";
import { useNavigate, useLocation  } from "react-router-dom";
import "../css/MultiplexTYPE.css";

function MultiplexTYPE() {
    useEffect(() => {
      document.title = "GM | Multiplex's type choice";
    }, []);

    const navigate = useNavigate();
    const location = useLocation();  
    const { tsvDict } = location.state || {};

    const goToNormalMultiplex = () => {
        navigate("/multiplex/couche", { state: { tsvDict } });
    };

    const goToMultiPatientMultiplex = () => {
        navigate("/multiplex/seed-load", { state: { tsvDict } });
    }

    return (
        <div className="multiplex-type-container">
            <h2 className="m-t-title">Choose the type of multiplex you want to create</h2>
            <div className="m-t-links-container">
                <button type="button" onClick={goToNormalMultiplex} className="m-t-link">
                One patient Multiplex
                </button>
                <button type="button" onClick={goToMultiPatientMultiplex} className="m-t-link">
                Multi-Patient Multiplex
                </button>
            </div>
        </div>
    );
}

export default MultiplexTYPE;