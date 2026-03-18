import glob
import os
import re
import pandas as pd

def correct_sif_order(sif_file: str, multiplex_dir: str, output_file: str = None) -> None:
    """
    Corrects node order in a SIF file for bipartite relations and removes duplicates.
    
    Params:
      sif_file: Path to the input SIF file.
      multiplex_dir: Directory containing multiplex TSV files.
      output_file: Optional; output file path. Defaults to sif_file.
    """
    if output_file is None:
        output_file = sif_file

    # Load nodes from each multiplex TSV file, keyed by layer.
    multiplex_files = glob.glob(os.path.join(multiplex_dir, "multiplex_*.tsv"))
    multiplex_nodes = {}
    for file in multiplex_files:
        base = os.path.basename(file)
        match = re.search(r'multiplex_(\d+)\.tsv', base)
        if match:
            layer = match.group(1)
            try:
                df = pd.read_csv(file, sep="\t")
            except Exception as e:
                print(f"Error reading {file}: {e}")
                continue
            # Extract node set from file.
            if "node" in df.columns:
                nodes_set = set(df["node"].astype(str).str.strip())
            else:
                with open(file, 'r', encoding='utf-8') as f:
                    nodes_set = {line.strip() for line in f if line.strip()}
            multiplex_nodes[layer] = nodes_set

    # Process each line in the SIF file.
    corrected_lines = []
    seen = set()
    with open(sif_file, 'r', encoding='utf-8') as f:
        for line in f:
            original_line = line.strip()
            if not original_line:
                continue
            parts = original_line.split('\t')
            # If line format is unexpected, add if unique.
            if len(parts) != 3:
                if original_line not in seen:
                    corrected_lines.append(original_line)
                    seen.add(original_line)
                continue

            left_node, relation, right_node = parts
            if relation.startswith("bipartite/"):
                s = relation[len("bipartite/"):]
                if s.endswith(".tsv"):
                    s = s[:-4]
                try:
                    layer1, layer2 = s.split('_')
                except Exception as e:
                    if original_line not in seen:
                        corrected_lines.append(original_line)
                        seen.add(original_line)
                    continue
                nodes_layer1 = multiplex_nodes.get(layer1, set())
                # Swap nodes if left_node is not in layer1 but right_node is.
                if left_node not in nodes_layer1 and right_node in nodes_layer1:
                    left_node, right_node = right_node, left_node

            corrected_line = "\t".join([left_node, relation, right_node])
            if corrected_line not in seen:
                seen.add(corrected_line)
                corrected_lines.append(corrected_line)

    # Write the corrected lines to the output file.
    with open(output_file, 'w', encoding='utf-8') as out:
        for line in corrected_lines:
            out.write(line + "\n")


def filter_sif_file(sif_file: str, ranking_final: pd.DataFrame) -> None:
    """
    Filters a SIF file to keep only the lines where both nodes 
    (first and last column) exist in ranking_final.
    
    Params:
      sif_file: Path to the SIF file.
      ranking_final: DataFrame containing valid nodes.
    """
    # Build a set of valid nodes from the ranking DataFrame
    ranking_nodes = set(ranking_final['node'])
    filtered_lines = []
    
    # Read the SIF file line by line
    with open(sif_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split('\t')
            # Skip lines that don't have the expected format (at least 3 columns)
            if len(parts) < 3:
                continue
            left_node = parts[0]
            right_node = parts[-1]
            # Append the line if both nodes are in the ranking set
            if left_node in ranking_nodes and right_node in ranking_nodes:
                filtered_lines.append(line)
    
    # Overwrite the SIF file with the filtered lines
    with open(sif_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(filtered_lines))
    
    print(f"The file {sif_file} has been updated with {len(filtered_lines)} filtered lines.")
