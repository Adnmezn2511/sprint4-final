import os
import zipfile
import yaml 

def generate_config(zip_path, nbIteration, seeds, restart, path):
    """ Generates a YAML config file, a seeds file, a results folder, and copies the multiplex and bipartite directories (from the ZIP archive) into the specified path.
    :param zip_path: Path to the ZIP archive containing multiplex and bipartite files.
    :param nbIteration: Number of iterations (used for naming the results folder).
    :param seeds: List of seeds to write in seeds.txt.
    :param path: Destination directory for the generated files.
    """
    os.makedirs(path, exist_ok=True)
    
    multiplex_files = {}
    bipartite_entries = []
    
    with zipfile.ZipFile(zip_path, 'r') as archive:
        for entry in archive.namelist():
            if entry.endswith('/'):
                continue

            if entry.startswith("multiplex/"):
                parts = entry.split('/')
                if len(parts) >= 3:
                    layer = parts[1]
                    multiplex_files.setdefault(layer, []).append(entry)
            
            elif entry.startswith("bipartite/"):
                parts = entry.split('/')
                if len(parts) == 2:
                    filename = parts[1]
                    if filename.endswith('.tst'):
                        config_filename = filename[:-4] + '.tsv'
                    else:
                        config_filename = filename
                    base = filename.rsplit('.', 1)[0]  
                    if '_' in base:
                        source, target = base.split('_')
                    else:
                        source, target = None, None
                    bipartite_entries.append((f"bipartite/{config_filename}", source, target))
    

    multiplex_config = {}
    for layer in sorted(multiplex_files.keys(), key=lambda x: int(x)):
        multiplex_config[int(layer)] = {
            "layers": sorted(multiplex_files[layer])
        }
    
    bipartite_config = {}
    for filepath, source, target in sorted(bipartite_entries, key=lambda x: x[0]):
        bipartite_config[filepath] = {
            "source": int(source) if source and source.isdigit() else source,
            "target": int(target) if target and target.isdigit() else target
        }
    
    config_dict = {
        "seed": f"seeds.txt",
        "r": restart,
        "multiplex": multiplex_config,
        "bipartite": bipartite_config
    }
    
    config_filepath = os.path.join(path, f"config.yml")
    seeds_filepath = os.path.join(path, f"seeds.txt")
    result_dir = os.path.join(path, f"result_{nbIteration}")
    
    with open(config_filepath, "w", encoding="utf-8") as config_file:
        yaml.dump(config_dict, config_file, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    os.makedirs(result_dir, exist_ok=True)
    
    with open(seeds_filepath, "w", encoding="utf-8") as seeds_file:
        seeds_file.write("\n".join(seeds))
    
    create_arborescence_from_zip(zip_path, path)
    print(f"Configuration générée dans '{config_filepath}', dossier '{result_dir}' créé et seeds écrits dans '{seeds_filepath}'.")


def create_arborescence_from_zip(zip_path, destination_path):
    """ Extracts the contents of the ZIP archive into the destination_path,
    recreating the directory structure from the archive.

    :param zip_path: Path to the ZIP archive.
    :param destination_path: Path to the directory where the contents will be extracted.
    """
    os.makedirs(destination_path, exist_ok=True)
    
    with zipfile.ZipFile(zip_path, 'r') as archive:
        archive.extractall(destination_path)
    
    print(f"Arborescence extraite avec succès dans '{destination_path}'.")


def get_layer_names(path):
    """ Reads the 'layer_name.tsv' file in the specified directory and returns a dictionary
    mapping layer IDs to their corresponding names.

    The 'layer_name.tsv' file must contain one layer ID and name per line, separated by a tab. Example:
    1 Compounds
    2 Diseases
    3 Genes
    4 Pathways

    :param path: Directory containing the 'layer_name.tsv' file.
    :return: Dictionary mapping layer IDs to layer names.
    """
    layer_names_path = os.path.join(path, "layer_name.tsv")
    layer_names = {}
    try:
        with open(layer_names_path, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split("\t")
                if len(parts) >= 2:
                    layer_names[parts[0]] = parts[1]
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"[get_layer_names] Erreur lors de la lecture de {layer_names_path}: {e}")
        return {}
    return layer_names


def get_layer_names_from_zip(zip_path):
    """Reads 'layer_name.tsv' directly from a ZIP archive (without extracting it).

    :param zip_path: Path to the ZIP archive.
    :return: Dictionary mapping layer IDs to layer names, or {} if not found.
    """
    try:
        with zipfile.ZipFile(zip_path, 'r') as archive:
            candidates = [n for n in archive.namelist() if n.endswith("layer_name.tsv")]
            if not candidates:
                return {}
            with archive.open(candidates[0]) as f:
                layer_names = {}
                for line in f.read().decode("utf-8").splitlines():
                    parts = line.strip().split("\t")
                    if len(parts) >= 2:
                        layer_names[parts[0]] = parts[1]
                return layer_names
    except Exception as e:
        print(f"[get_layer_names_from_zip] Erreur: {e}")
        return {}


