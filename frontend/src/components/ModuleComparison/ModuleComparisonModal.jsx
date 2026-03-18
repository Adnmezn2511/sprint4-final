// frontend/src/components/ModuleComparison/ModuleComparisonModal.jsx

import React, { useState } from "react";
import { compareModules } from "../../apiService";
import ModuleComparisonResult from "./ModuleComparisonResult";
import "../../css/ModuleComparison/ModuleComparison.css";

/**
 * Modal component for triggering and displaying module comparison results.
 *
 * Workflow:
 * 1. User opens the modal via ModuleComparisonButton.
 * 2. The modal displays the number of loaded patients.
 * 3. User clicks "Run comparison" to call the API.
 * 4. Results are rendered via ModuleComparisonResult.
 * 5. Errors are displayed in a banner.
 *
 * @param {object} props
 * @param {Object.<string, string[]>} props.patientModules
 *   Dict mapping patient IDs to their gene arrays.
 * @param {function} props.onClose - Callback invoked to close the modal.
 */
function ModuleComparisonModal({ patientModules, onClose }) {
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    /**
     * Calls the comparison API and updates local state with the result or error.
     */
    async function handleCompare() {
        setLoading(true);
        setError(null);
        setResult(null);

        try {
            const data = await compareModules(patientModules);

            if (!data) {
                setError("No response received from the server. Please try again.");
                return;
            }

            if (data.error) {
                setError(data.error);
                return;
            }

            setResult(data);
        } catch (err) {
            setError("An unexpected error occurred during comparison.");
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="comparison-modal-container" role="dialog" aria-modal="true">
            <div className="comparison-modal">

                {/* Header */}
                <h2 className="comparison-modal-title">Module comparison</h2>
                <button
                    className="close-comparison-button"
                    onClick={onClose}
                    aria-label="Close modal"
                >
                    <i className="fas fa-times"></i>
                </button>

                {/* Body */}
                <div className="comparison-modal-body">
                    <p>
                        Patients loaded :{" "}
                        <strong>{Object.keys(patientModules).length}</strong>
                    </p>

                    {/* Error banner */}
                    {error && (
                        <div className="comparison-error-banner" role="alert">
                            {error}
                        </div>
                    )}

                    {/* Run button — hidden once results are displayed */}
                    {!result && (
                        <button
                            className="run-comparison-button"
                            onClick={handleCompare}
                            disabled={loading}
                        >
                            {loading ? "Computing..." : "Run comparison"}
                        </button>
                    )}

                    {/* Results */}
                    {result && <ModuleComparisonResult result={result} />}
                </div>
            </div>
        </div>
    );
}

export default ModuleComparisonModal;