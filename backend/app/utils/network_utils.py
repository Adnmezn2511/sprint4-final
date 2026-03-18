import os
import zipfile
from typing import Tuple, List, Dict

def _get_zip_file(zip_container_dir: str) -> str:
    """
    Recherche et retourne le chemin complet du fichier zip dans le dossier spécifié.
    Lève une erreur si aucun ou plusieurs fichiers zip sont trouvés.
    """
    zip_files = [f for f in os.listdir(zip_container_dir) if f.endswith('.zip')]
    if not zip_files:
        raise ValueError("Aucun fichier zip trouvé dans le dossier.")
    if len(zip_files) > 1:
        raise ValueError("Plusieurs fichiers zip trouvés dans le dossier. Veuillez n'en fournir qu'un seul.")
    return os.path.join(zip_container_dir, zip_files[0])

def _get_layer_mapping(zip_ref: zipfile.ZipFile) -> Tuple[List[str], Dict[str, str]]:
    """
    Lit le fichier 'layer_name.tsv' dans le zip et retourne :
      - une liste ordonnée des noms de couche,
      - un dictionnaire de mapping {nom_de_couche: id_de_couche}.
    """
    if "layer_name.tsv" not in zip_ref.namelist():
        raise ValueError("Le fichier 'layer_name.tsv' n'a pas été trouvé dans le zip.")
    
    content = zip_ref.read("layer_name.tsv").decode("utf-8")
    layer_names = []
    mapping = {}
    
    for line in content.splitlines():
        if line.strip():
            parts = line.split('\t')
            if len(parts) >= 2:
                layer_id = parts[0].strip()
                name = parts[1].strip()
                layer_names.append(name)
                mapping[name] = layer_id
    return layer_names, mapping

def list_multiplex_networks(zip_container_dir: str) -> List[str]:
    """
    Ouvre le zip dans le dossier spécifié et renvoie la liste ordonnée
    des noms des couches extraites du fichier 'layer_name.tsv'.
    """
    zip_path = _get_zip_file(zip_container_dir)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        layer_names, _ = _get_layer_mapping(zip_ref)
    return layer_names

def list_layers(zip_container_dir: str, layer_name: str) -> List[str]:
    """
    Renvoie la liste triée (ordre alphabétique) des noms de fichiers (sans extension)
    présents dans le dossier 'multiplex/<id_de_couche>' du zip pour la couche spécifiée.
    
    Le fichier 'layer_name.tsv' doit contenir l'id (première colonne) et le nom (deuxième colonne) de la couche.
    """
    zip_path = _get_zip_file(zip_container_dir)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        _, mapping = _get_layer_mapping(zip_ref)
        if layer_name not in mapping:
            raise ValueError(f"La couche '{layer_name}' n'a pas été trouvée dans 'layer_name.tsv'.")
        layer_id = mapping[layer_name]
        prefix = f"multiplex/{layer_id}/"
        file_names = [
            os.path.splitext(os.path.basename(file))[0]
            for file in zip_ref.namelist()
            if file.startswith(prefix) and file.endswith(".tsv") and not file.endswith("/")
        ]
    return sorted(file_names)

def list_unique_nodes(zip_container_dir: str, layer_name: str, specific_layer: str) -> List[str]:
    """
    Extrait et renvoie la liste triée des nœuds uniques présents dans le fichier spécifique
    (par exemple, "Compounds.tsv") situé dans le dossier 'multiplex/<id_de_couche>' du zip,
    pour la couche dont le nom est spécifié.
    
    Chaque ligne du fichier spécifique est supposée contenir une ou deux colonnes séparées par une tabulation.
    """
    zip_path = _get_zip_file(zip_container_dir)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        _, mapping = _get_layer_mapping(zip_ref)
        if layer_name not in mapping:
            raise ValueError(f"La couche '{layer_name}' n'a pas été trouvée dans 'layer_name.tsv'.")
        layer_id = mapping[layer_name]
        target_file_path = f"multiplex/{layer_id}/{specific_layer}.tsv"
        if target_file_path not in zip_ref.namelist():
            raise ValueError(f"Le fichier '{specific_layer}' n'a pas été trouvé dans 'multiplex/{layer_id}/' du zip.")
        
        content = zip_ref.read(target_file_path).decode("utf-8")
        unique_nodes = set()
        for line in content.splitlines():
            if line.strip():
                parts = line.split('\t')
                unique_nodes.add(parts[0])
                if len(parts) >= 2:
                    unique_nodes.add(parts[1])
    return sorted(unique_nodes)
