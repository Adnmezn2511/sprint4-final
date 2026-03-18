// frontend/src/components/ModuleComparison/ModuleComparisonResult.jsx

import React from "react";

/**
 * Renders a labeled gene list section with a count badge.
 *
 * @param {object} props
 * @param {string} props.title - Section heading displayed above the list.
 * @param {string[]} props.genes - Array of gene names to display.
 * @param {string} [props.highlight] - Optional CSS class for visual emphasis.
 */
function GeneListSection({ title, genes, highlight }) {
    return (
        <div className={`gene-section ${highlight || ""}`}>
            <h4 className="gene-section-title">
                {title}
                <span className="gene-count-badge">{genes.length}</span>
            </h4>
            {genes.length === 0 ? (
                <p className="gene-empty-notice">No genes in this set.</p>
            ) : (
                <ul className="gene-list">
                    {genes.map((gene) => (
                        <li key={gene} className="gene-tag">
                            {gene}
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
}

/**
 * Full comparison result display component.
 *
 * Renders four sections:
 * - Intersection: genes shared by all patients
 * - Union: all genes across all patients
 * - Differences: per-patient genes absent from all others
 * - Discriminant genes: genes exclusive to exactly one patient
 *
 * @param {object} props
 * @param {object} props.result - Comparison result returned by the API.
 * @param {string[]} props.result.intersection
 * @param {string[]} props.result.union
 * @param {Object.<string, string[]>} props.result.differences
 * @param {Object.<string, string[]>} props.result.discriminant_genes
 * @param {number} props.result.patient_count
 * @param {object} props.result.summary
 */
function ModuleComparisonResult({ result }) {
    if (!result) return null;

    const { intersection, union, differences, discriminant_genes, summary } = result;

    return (
        <div className="comparison-result">

            {/* Summary banner */}
            <div className="comparison-summary">
                <span>
                    Patients compared : <strong>{result.patient_count}</strong>
                </span>
                <span>
                    Intersection : <strong>{summary.intersection_size}</strong> genes
                </span>
                <span>
                    Union : <strong>{summary.union_size}</strong> genes
                </span>
                <span>
                    Patients with discriminant genes :{" "}
                    <strong>{summary.patients_with_discriminant_genes}</strong>
                </span>
            </div>

            {/* Intersection */}
            <GeneListSection
                title="Intersection — shared by all patients"
                genes={intersection}
                highlight="section-intersection"
            />

            {/* Union */}
            <GeneListSection
                title="Union — present in at least one patient"
                genes={union}
                highlight="section-union"
            />

            {/* Per-patient differences */}
            <div className="differences-section">
                <h4 className="gene-section-title">Differences per patient</h4>
                {Object.entries(differences).map(([patientId, genes]) => (
                    <GeneListSection
                        key={patientId}
                        title={`Patient ${patientId} — not found in any other patient`}
                        genes={genes}
                    />
                ))}
            </div>

            {/* Discriminant genes */}
            <div className="discriminant-section">
                <h4 className="gene-section-title">
                    Discriminant genes — exclusive to one patient
                </h4>
                {Object.keys(discriminant_genes).length === 0 ? (
                    <p className="gene-empty-notice">No exclusive genes found.</p>
                ) : (
                    Object.entries(discriminant_genes).map(([patientId, genes]) => (
                        <GeneListSection
                            key={patientId}
                            title={`Patient ${patientId}`}
                            genes={genes}
                            highlight="section-discriminant"
                        />
                    ))
                )}
            </div>
        </div>
    );
}

export default ModuleComparisonResult;