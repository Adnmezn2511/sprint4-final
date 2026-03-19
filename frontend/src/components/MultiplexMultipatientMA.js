import React, { useEffect, useState } from "react";
import { useNavigate, Link, useLocation } from "react-router-dom";
import { MultipatientGraphJson } from "../apiService";
import Alert from "./Alert";
import "../css/MultiplexMultipatientMA.css";

function MultiplexMultipatientMA() {
    useEffect(() => {
        document.title = "GM | Multipatient parameters selection";
        console.log("tsvDict:", tsvDict);
        console.log("seedDict:", seedDict);
    }, []);
    
    const navigate = useNavigate();
    const location = useLocation();
    const { tsvDict, seedDict } = location.state || {};

    const [formData, setFormData] = useState({
        user: "",
        steps: 5,
        top: 10,
        restart: 0.7,
        module_algorithm: "scc",
    });
    const [loading, setLoading] = useState(false);
    const [showAlert, setShowAlert] = useState(false);
    const [showBackendAlert, setShowBackendAlert] = useState(false);

    const closeAlert = () => setShowAlert(false);

    const handleChange = (e) => {
        const { name, value } = e.target;

        setFormData((prevData) => ({
            ...prevData,
            [name]: value,
        }));
    }

    const handleSubmit = async (e) => {
        e.preventDefault();
        console.log(
            "user : " +
            formData.user +
            ", steps : " +
            formData.steps +
            ", top : " +
            formData.top +
            ", restart : " +
            formData.restart
        );

        if (formData.user === "") {
            setShowAlert(true);
        } else {
            try {
                setLoading(true);
    
                const response = await MultipatientGraphJson(
                    seedDict,
                    formData.steps,
                    formData.top,
                    formData.restart,
                    formData.user,
                    formData.module_algorithm
                );

                if (response.error) {
                    console.error("Error from backend:", response.error);
                    setShowBackendAlert(true);
                    return;
                }

                console.log("Response from MultipatientGraphJson:", response);

                navigate("/multiplex/multipatient/list", {
                    state: {
                        graphData: response,
                    },
                });

            } catch (error) {
                console.error("Erreur lors de l'appel à MultipatientGraphJson", error);
                setShowBackendAlert(true);
            } finally {
                setLoading(false);
            }
        }
    };

    return (
        <div>
            {loading ? (
                <div className="loading-container">
                    <p>Executing the random walk...</p>
                    <div className="spinner"></div>
                </div>
            ) : (
                <div>
                    <div className="algo-options-container-multipatient">
                        <form className="mmma-form" onSubmit={handleSubmit}>
                            <h2 className="mmma-form-title">Multi-patient Random walk Algorithm</h2>

                            <div className="mmma-form-group">
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
                            <div className="mmma-form-group">
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
                            <div className="mmma-form-group">
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
                            <div className="mmma-form-group">
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

                            <div className="mmma-form-group">
                                <label htmlFor="module_algorithm">Module detection (US-C2)</label>
                                <select
                                    name="module_algorithm"
                                    id="module_algorithm"
                                    value={formData.module_algorithm}
                                    onChange={handleChange}
                                >
                                    <option value="scc">SCC (zones fortement connectées)</option>
                                    <option value="louvain">Louvain</option>
                                    <option value="greedy">Greedy modularity</option>
                                    <option value="connected">Connected components</option>
                                </select>
                            </div>

                            <button
                                type="submit"
                                className="mmma-button"
                            >
                                Start
                            </button>

                            {showAlert && (
                                <Alert
                                    message="Every parameter needs to be filled before applying this algorithm."
                                    onClose={closeAlert}
                                />
                            )}

                            {showBackendAlert && (
                                <Alert
                                    message="An error occurred while processing your request. Please try again."
                                    onClose={() => setShowBackendAlert(false)}
                                />
                            )}

                            <Link to="/multiplex/" className="mmma-back-button">
                                <i className="fas fa-chevron-left fa-xs"></i>
                                <i className="fas fa-chevron-left fa-xs"></i>
                                <i className="fas fa-chevron-left fa-xs"></i>
                            </Link>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}

export default MultiplexMultipatientMA;