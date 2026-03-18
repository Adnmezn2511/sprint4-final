import zipfile
import os
import logging

def create_zip(source_folder, zip_filename, output_dir):
    """Compresse un dossier dans un fichier ZIP
    
    Args:
        source_folder (str): Chemin du dossier à compresser
        zip_filename (str): Nom du fichier ZIP (sans extension)
        output_dir (str): Répertoire de destination (créé si inexistant)
    """
    # Crée le répertoire de sortie si nécessaire
    os.makedirs(output_dir, exist_ok=True)
    
    # Création du chemin complet du ZIP
    full_zip_path = os.path.join(output_dir, f"{zip_filename}.zip")
    
    with zipfile.ZipFile(full_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_folder):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, start=source_folder)
                zipf.write(file_path, arcname)
    
    print(f"✅ Compression réussie : {full_zip_path}")
    return full_zip_path

def delete_zip_file(path: str, name: str):
    """
    Supprime un fichier ZIP spécifié par son nom et chemin
    
    Args:
        path (str): Chemin du dossier contenant le fichier
        name (str): Nom du fichier ZIP (avec ou sans extension .zip)
    
    Returns:
        bool: True si suppression réussie, False sinon
    """
    try:
        # Construit le chemin complet
        full_path = os.path.join(path, name)
        
        # Vérifie l'extension .zip
        if not full_path.lower().endswith('.zip'):
            full_path += '.zip'

        # Vérifie l'existence du fichier
        if not os.path.isfile(full_path):
            logging.warning(f"Le fichier {full_path} n'existe pas")
            return False

        # Suppression du fichier
        os.remove(full_path)
        logging.info(f"Fichier {full_path} supprimé avec succès")
        return True

    except Exception as e:
        logging.error(f"Erreur lors de la suppression : {str(e)}")
        return False
