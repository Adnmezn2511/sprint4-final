import JSZip from "jszip";
import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { uploadFile } from "../apiService";
import "../css/MultiplexLOAD.css";
import Alert from "./Alert";
import GenerateZipForm from "./ZipForm/GenerateZipForm";

function MultiplexLOAD() {
  useEffect(() => {
    document.title = "GM | Multiplex uploading";
  }, []);

  const navigate = useNavigate();

  // États pour l'upload du fichier .zip
  const [file, setFile] = useState(null);
  const [fileName, setFileName] = useState("");
  const [showAlert, setShowAlert] = useState(false);
  // Contrôle de l'affichage du formulaire modale "Generate Zip"
  const [showGenerateZip, setShowGenerateZip] = useState(false);

  const closeAlert = () => setShowAlert(false);

  const fileSelect = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setFileName(selectedFile.name);
    }
  };

  const extractZipFiles = (zipFile) => {
    const zip = new JSZip();
    return zip.loadAsync(zipFile).then((contents) => {
      const tsvDict = {}; 
  
      const tsvNamesFile = contents.files["layer_name.tsv"];
      if (tsvNamesFile) {
        return tsvNamesFile.async("text").then((tsvNamesFileContent) => {
          const tsvNamesMapping = {};
          const tsvNamesLines = tsvNamesFileContent.split("\n");
  
          tsvNamesLines.forEach((line) => {
            const [id, name] = line.split("\t");
            if (id && name) {
              tsvNamesMapping[id] = name;
              if (!tsvDict[name]) {
                tsvDict[name] = []; 
              }
            }
          });
  
          // Extraction des fichiers .tsv dans les sous-dossiers de multiplex
          const promises = Object.keys(contents.files)
            .map((filename) => {
              const parts = filename.split("/");
              if (parts.length === 3 && parts[0] === "multiplex" && parts[1].match(/^\d+$/)) {
                const layerId = parts[1];
                const categoryName = tsvNamesMapping[layerId]; 
                if (categoryName && filename.endsWith(".tsv")) {
                  return contents.files[filename].async("text").then((fileContent) => {
                    tsvDict[categoryName].push(fileContent);
                  });
                }
              }
              return null;
            })
            .filter((promise) => promise !== null);
  
          return Promise.all(promises).then(() => ({ tsvDict }));
        });
      } else {
        return Promise.resolve({ tsvDict });
      }
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!file) {
      setShowAlert(true);
    } else {
      try {
        // Upload du fichier ZIP vers le backend Django
        const response = await uploadFile(file);
        console.log("Upload successful!", response);

        const { tsvDict } = await extractZipFiles(file);
        console.log("dict:", tsvDict);

        navigate("/multiplex/type_choice", {
          state: { tsvDict: tsvDict },
        });
      } catch (error) {
        console.error("Erreur lors de l'extraction du fichier ZIP", error);
      }
    }
  };

  const rmFile = () => {
    setFile(null);
    setFileName("");  
    document.getElementById("m-l-import").value = "";
  };

  const handleGenerateZip = async (data) => {
    console.log("Generating zip with data: ", data);
    const zip = new JSZip();

    // Création des dossiers principaux
    const multiplexFolder = zip.folder("multiplex");
    const bipartiteFolder = zip.folder("bipartite");

    // Mapping des couches avec id séquentiel (1, 2, ...)
    const layerMapping = data.layers.map((layer, index) => ({
      id: index + 1,
      name: layer.name,
      files: layer.files,
    }));

    // Création du fichier layer_name.tsv à la racine du zip
    let layerNameTsv = "";
    layerMapping.forEach((layer) => {
      layerNameTsv += `${layer.id}\t${layer.name}\n`;
    });
    zip.file("layer_name.tsv", layerNameTsv);

    // Ajout des fichiers dans le dossier "multiplex"
    for (const layer of layerMapping) {
      const folder = multiplexFolder.folder(String(layer.id));
      for (const file of layer.files) {
        // Lecture du contenu du fichier sous forme de ArrayBuffer
        const fileContent = await file.arrayBuffer();
        folder.file(file.name, fileContent);
      }
    }

    // Traitement des bipartites
    for (const bip of data.bipartites) {
      // Recherche des couches correspondantes via le nom
      const layer1Obj = layerMapping.find((l) => l.name === bip.layer1);
      const layer2Obj = layerMapping.find((l) => l.name === bip.layer2);
      if (layer1Obj && layer2Obj && bip.file) {
        // Renommage du fichier : "<idCouche1>_<idCouche2>.tsv"
        const newFileName = `${layer1Obj.id}_${layer2Obj.id}.tsv`;
        const fileContent = await bip.file.arrayBuffer();
        bipartiteFolder.file(newFileName, fileContent);
      }
    }

    // Génération et téléchargement du fichier ZIP
    const content = await zip.generateAsync({ type: "blob" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(content);
    link.download = data.zipName.endsWith(".zip")
      ? data.zipName
      : `${data.zipName}.zip`;
    link.click();
  };

  return (
    <div className="multiplex-load-container">
      <div className="m-l-form-container">
        <form className="m-l-form" onSubmit={handleSubmit}>
          <h2 className="m-l-form-title">Load your Multiplex</h2>
          <p>(.zip only)</p>

          {/* Bouton Generate Zip placé juste au-dessus du bouton Dépôt fichier */}
          <a className="gen-text" onClick={() => setShowGenerateZip(true)}>
            Generate Zip
          </a>

          {/* Bouton Dépôt fichier */}
          <label
            htmlFor="m-l-import"
            className={`m-l-import ${fileName ? "active" : ""}`}
          >
            {fileName ? fileName : "File Deposit"}
            {file && (
              <div className="m-l-rm-file" onClick={rmFile}>
                <i className="fas fa-times"></i>
              </div>
            )}
          </label>
          <input
            type="file"
            id="m-l-import"
            accept=".zip"
            onChange={fileSelect}
          />
          <a onClick={handleSubmit} className="m-l-change-couche">
            <i className="fas fa-chevron-right fa-xs"></i>
            <i className="fas fa-chevron-right fa-xs"></i>
            <i className="fas fa-chevron-right fa-xs"></i>
          </a>
        </form>
        {showAlert && (
          <Alert
            message="Veuillez déposer un multiplex au format .zip avant de continuer"
            onClose={closeAlert}
          />
        )}
      </div>

      {/* Affichage du formulaire Generate Zip dans une modale */}
      {showGenerateZip && (
        <GenerateZipForm
          onGenerateZip={handleGenerateZip}
          onClose={() => setShowGenerateZip(false)}
        />
      )}
    </div>
  );
}

export default MultiplexLOAD;
