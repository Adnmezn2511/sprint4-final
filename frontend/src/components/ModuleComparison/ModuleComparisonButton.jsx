// frontend/src/components/ModuleComparison/ModuleComparisonButton.jsx

import React from "react";

/**
 * Button that opens the module comparison modal.
 *
 * Disabled automatically when fewer than 2 patients have modules available.
 * Displays a tooltip explaining why the button is disabled in that case.
 *
 * @param {object} props
 * @param {boolean} props.disabled - Disables the button when true.
 * @param {function} props.onClick - Callback invoked when the button is clicked.
 */
function ModuleComparisonButton({ disabled, onClick }) {
    return (
        <button
            className="module-comparison-btn"
            onClick={onClick}
            disabled={disabled}
            title={
                disabled
                    ? "At least 2 patient modules are required to compare"
                    : "Compare patient modules"
            }
        >
            Compare modules
        </button>
    );
}

export default ModuleComparisonButton;