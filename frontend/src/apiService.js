// frontend/src/apiService.js

const apiUrl = process.env.REACT_APP_API_URL;

/**
 * Get result graph of the itRWR
 * @url /graph
 * @param {[String]} seeds - The list of seeds
 * @param {int} nb_iterations - The numbers of iteration.
 * @param {int} top - The numbers of node show per layer.
 * @param {float} restart - The restart probability.
 * @param {String} user - The user name.
 * @param {String} title - The title of the graph.
 * @returns The graph of the result of itRWR in html format.
 */
async function GraphJson(seeds, steps, top, restart, user, title) {
    try {
        const response = await fetch(apiUrl + 'graph/', {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                seeds: seeds,
                steps: steps,
                top: top,
                restart: restart,
                user: user,
                title: title,
            }),
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error("Error fetching graph JSON:", error);
    }
}

/**
 * Get results graphs of the multi-patient itRWR
 * @url /graph/multipatient/
 * @param {{String: [String]}} seeds - The dictionary of seeds for each patient.
 * @param {int} nb_iterations - The numbers of iteration.
 * @param {int} top - The numbers of node show per layer.
 * @param {float} restart - The restart probability.
 * @param {String} user - The user name.
 * @returns The graph of the result of itRWR in html format.
 */
async function MultipatientGraphJson(seeds, steps, top, restart, user) {
    try {
        console.log("Calling MultipatientGraphJson with:" + JSON.stringify(seeds) + ", " + steps + ", " + top + ", " + restart + ", " + user);
        const response = await fetch(apiUrl + 'graph/multipatient/', {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                dico_patient_seeds: seeds,
                steps: steps,
                top: top,
                restart: restart,
                user: user,
            }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data;

    } catch (error) {
        console.error("Error fetching multipatient graph JSON:", error);
    }
}

// Simple function to test the API connection
async function testapi() {
    try {
        const response = await fetch(apiUrl + "test");
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        console.log("Django response:", data.test);
        return data.test;
    }
    catch (error) {
        console.error("Error:", error);
    }
}

/**
 * Upload a zip file to the backend
 * @url /upload-zip
 * @param {File} file - The zip file to upload.
 * @returns nothing
 */
async function uploadFile(file) {
    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch(apiUrl + "upload-zip", {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            throw new Error(`Upload failed: ${response.statusText}`);
        }

        return await response.json();
    } catch (error) {
        console.error("Error uploading file:", error);
        throw error;
    }
}

/**
 * Upload a TSV seeds file
 * @url /upload-seed
 * @param {File} file - The TSV file to upload.
 * @returns nothing
 */
async function uploadSeedFile(file) {
    const formData = new FormData();
    formData.append("file", file);
    try {
        const response = await fetch(apiUrl + "upload-seed", {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            throw new Error(`Upload failed: ${response.statusText}`);
        }

        return await response.json();
    } catch (error) {
        console.error("Error uploading seed file:", error);
        throw error;
    }
}

/**
 * Download a zip archive by graph history ID
 * @url /download-zip/<id>
 * @param {number} id - The ID of the graph history record.
 */
const downloadZip = async (id) => {
    try {
        const response = await fetch(apiUrl + `download-zip/${id}/`);

        if (!response.ok) {
            throw new Error('Fichier non trouvé');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `archive_${id}.zip`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);

    } catch (error) {
        console.error('Erreur de téléchargement:', error);
        throw error;
    }
};

/**
 * Get the history of the graphs
 * @url /graph-histories
 * @returns The list of information of the graphs
 */
async function getHistory() {
    try {
        const response = await fetch(apiUrl + 'graph-histories/');
        if (!response.ok) throw new Error('Erreur de chargement');
        const data = await response.json();
        return data;
    } catch (err) {
        console.error('Error:', err);
    }
}

/**
 * Delete a graph history record by ID
 * @url /graph/<id>/delete/
 * @param {number} id - The ID of the graph history record to delete.
 */
async function deleteGraph(id) {
    try {
        const response = await fetch(apiUrl + `graph/${id}/delete/`, {
            method: 'DELETE',
        });
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || 'Delete failed');
        }

        return await response.json();
    } catch (err) {
        console.error('Error:', err);
    }
}

/**
 * Fetch complete graph data by its ID
 * @url GET /api/graph-histories/<id>/
 * @param {number} id - The graph database ID
 * @returns {Object} Full graph JSON data (graph_json, parameters, title, etc.)
 */
async function getGraphById(id) {
    try {
        const response = await fetch(apiUrl + `graph-histories/${id}/`);
        if (!response.ok) throw new Error(`Graphe introuvable (id=${id})`);
        const data = await response.json();
        return data;
    } catch (err) {
        console.error('Erreur getGraphById:', err);
        throw err;
    }
}

/**
 * Send a module comparison request to the backend.
 *
 * Calls POST /modules/compare/ with a dict of patient IDs mapped to gene arrays.
 *
 * @param {Object.<string, string[]>} patientModules
 *   Dict mapping patient IDs to their gene lists.
 *   Example: { "P1": ["EGFR", "BRCA1"], "P2": ["BRCA1", "TP53"] }
 * @returns {Promise<object|null>}
 *   Comparison result from the API, or null on network failure.
 */
async function compareModules(patientModules) {
    try {
        const response = await fetch(apiUrl + "modules/compare/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ patients: patientModules }),
        });
        return await response.json();
    } catch (error) {
        console.error("compareModules error:", error);
        return null;
    }
}

export {
    GraphJson,
    MultipatientGraphJson,
    testapi,
    uploadFile,
    uploadSeedFile,
    downloadZip,
    getHistory,
    deleteGraph,
    getGraphById,
    compareModules,
};