import React, { useEffect, useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { uploadSeedFile } from "../apiService";
import "../css/MultiplexSeedLOAD.css";
import Alert from "./Alert";

function MultiplexSeedLOAD() {
    useEffect(() => {
        document.title = "GM | Seed upload";
    }, []);

    const navigate = useNavigate();
    const location = useLocation();  
    const { tsvDict } = location.state || {};
    const [file, setFile] = useState(null);
    const [fileName, setFileName] = useState("");
    const [showAlert, setShowAlert] = useState(false);

    const closeAlert = () => setShowAlert(false);

    const fileSelect = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile) {
            setFile(selectedFile);
            setFileName(selectedFile.name);
        }
    };


    const rmFile = () => {
        setFile(null);
        setFileName("");  
        document.getElementById("m-s-l-import").value = "";
    };

    /**
     * Parse the file content into a seed dictionnary with {patient: [seed1, ...]} structure
     * @param {File} file The file to read
     * @returns The file parsed into a dictionnary
     */
    const readSeedFile = async (file) => {
        const dict = {};
        const content = await file.text();
        const lines = content.split(/\r?\n/).filter(Boolean);
        const linesWithoutHeader = lines.slice(1); // Remove header line

        linesWithoutHeader.forEach((line) => {
            const [col1, col2] = line.split("\t").map((value) => value?.trim());

            // Ignore les lignes incomplètes.
            if (!col1 || !col2) {
                return;
            }

            if (!dict[col1]) {
                dict[col1] = [];
            }
            dict[col1].push(col2);
        });

        return dict;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (!file) {
            setShowAlert(true);
        } else {
            try {
                // Upload du fichier TSV vers le backend Django
                const response = await uploadSeedFile(file);
                console.log("Upload Successful!");

                const seedDict = await readSeedFile(file);
                console.log("dict:", seedDict);

                navigate("/multiplex/multipatient", {
                    state: { tsvDict: tsvDict, seedDict: seedDict },
                });
                
            } catch (error) {
                console.error("Erreur lors de l'extraction du fichier TSV", error);
            }
        }
    }

    return (
        <div className="multiplex-seed-load-container">
            <form className="m-s-l-form" onSubmit={handleSubmit}>
                <h2>Load your seed file</h2>
                <p>(.tsv only)</p>
                {/* Bouton Dépôt fichier */}
                <label
                    htmlFor="m-s-l-import"
                    className={`m-s-l-import ${fileName ? "active" : ""}`}
                >
                    {fileName ? fileName : "File Deposit"}
                    {file && (
                    <div className="m-s-l-rm-file" onClick={rmFile}>
                        <i className="fas fa-times"></i>
                    </div>
                    )}
                </label>

                <input
                    type="file"
                    id="m-s-l-import"
                    accept=".tsv,.txt"
                    onChange={fileSelect}
                />

                <button type="submit" className="m-s-l-seed">
                    <i className="fas fa-chevron-right fa-xs"></i>
                    <i className="fas fa-chevron-right fa-xs"></i>
                    <i className="fas fa-chevron-right fa-xs"></i>
                </button>

                <Link to="/multiplex" className="m-back">
                    <i className="fas fa-chevron-left fa-xs"></i>
                    <i className="fas fa-chevron-left fa-xs"></i>
                    <i className="fas fa-chevron-left fa-xs"></i>
                </Link>
            </form>

            {showAlert && (
                <Alert
                    message="Veuillez déposer une seed au format tsv avant de continuer"
                    onClose={closeAlert}
                />
            )}
        </div>
    )
}

export default MultiplexSeedLOAD;