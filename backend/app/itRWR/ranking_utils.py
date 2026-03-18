import glob
import os
import pandas as pd
from .constants import SCORE_HEADER

def extract_multiplex_value(layer: str) -> str:
    """
    Extracts the multiplex value from a string like 'multiplex/3/genes_interactions.tsv'.
    
    Returns:
      The multiplex value (e.g., '3').
    """
    parts = layer.split('/')
    return parts[1] if len(parts) > 1 else ""

def get_multiplex_rankings(iteration_folder: str) -> list:
    """
    Retrieves all multiplex ranking files from the specified folder.
    
    Parameters:
      iteration_folder: Path to the folder with ranking files.
    
    Returns:
      A list of pandas DataFrames.
    """
    multiplex_rankings = []
    for file in glob.glob(os.path.join(iteration_folder, 'multiplex*')):
        print(file)
        df = pd.read_csv(file, sep='\t')
        df['node'] = df['node'].astype(str)
        multiplex_rankings.append(df)
    return multiplex_rankings

def get_multiplex_rankings_mem(ranking_df: pd.DataFrame, outdir: str = None) -> pd.DataFrame:
    """
    Retrieves all multiplex ranking "files" from the specified DataFrame.
    
    Parameters:
      outdir: (optional) Path to export ranking files.
    
    Returns:
      A list of pandas DataFrames.
    """

    res = []
    for multiplex in sorted(ranking_df.multiplex.unique()):
        out_i_df = ranking_df.loc[ranking_df.multiplex == multiplex]
        if outdir != None:
          multiplex_tsv_path = os.path.join(outdir, "multiplex_" + str(multiplex) + ".tsv")
          out_i_df.to_csv(multiplex_tsv_path, sep='\t', index=False, header=True, na_rep='NA')
        res.append(out_i_df)

    return res

def update_layer_max_scores_vec(ranking: pd.DataFrame, ranking_files: list, layer_max_scores: dict) -> None:
    """
    Updates layer_max_scores with the maximum score for each node per layer using vectorized operations.
    Result of asking deepseek to vectorize update_layer_max_scores as df.iterrows is not recommanded and was the bottleneck
    
    Params:
      ranking: DataFrame with initial ranking data.
      ranking_files: List of DataFrames from ranking files.
      layer_max_scores: Dictionary to update with max scores.
    """
    
    # Create a mapping from node to layer using the initial ranking data
    node_layer_map = (
        ranking[['node', 'layer']]
        .drop_duplicates(subset='node', keep='first')
        .set_index('node')['layer']
        .to_dict()
    )
    
    processed_dfs = []
    for df in ranking_files:
        
        # Get default layer from the current dataframe's multiplex column
        default_layer = df['multiplex'].iloc[0]
        
        # Create a temporary dataframe with node and score, then determine layers
        temp_df = df[['node', 'score']].copy()
        temp_df['layer'] = (
            temp_df['node']
            .map(node_layer_map)
            .fillna(default_layer)
        )
        
        processed_dfs.append(temp_df)
    
    # Combine all processed dataframes and compute max scores per (layer, node)
    combined_df = pd.concat(processed_dfs, ignore_index=True)
    max_scores = (
        combined_df
        .groupby(['layer', 'node'])['score']
        .max()
        .to_dict()
    )
    
    # Update layer_max_scores with computed maximums
    for (layer, node), score in max_scores.items():
        layer_dict = layer_max_scores.setdefault(layer, {})# = layer_max_scores[node_layer]
        layer_dict[node] = max(layer_dict.get(node, float("-inf")), score)

def update_layer_max_scores(ranking: pd.DataFrame, ranking_files: list, layer_max_scores: dict) -> None:
    """
    Updates layer_max_scores with the maximum score for each node per layer.
    
    Params:
      ranking: DataFrame with initial ranking data.
      ranking_files: List of DataFrames from ranking files.
      layer_max_scores: Dictionary to update with max scores.
    """

    temp_df = ranking[['node', 'layer']].copy()
    temp_df = temp_df.drop_duplicates(subset='node', keep='first')
    node_layer_map = temp_df.set_index('node')['layer'].to_dict()

    for df in ranking_files:
        #new bottlneck: iterrows
        for _, row in df.iterrows():
            node = row['node']
            score = row['score']

            # Get the layer for the node from the ranking DataFrame
            node_layer = node_layer_map.get(node, df['multiplex'].iloc[0])

            if node_layer not in layer_max_scores:
                layer_max_scores[node_layer] = {node: score}
                continue
            
            last_score = layer_max_scores[node_layer].get(node, score)
            layer_max_scores[node_layer][node] = max(score, last_score)



def update_seeds_from_iteration(ranking_files: list, seeds: set, added_nodes: set) -> None:
    """
    Adds the first node from the first ranking file that is not already in seeds.
    
    Params:
      ranking_files: List of ranking DataFrames.
      seeds: Set of current seeds.
      added_nodes: Set tracking newly added nodes.
    """
    if ranking_files:
        df = ranking_files[0]
        for node in df['node']:
            if node not in seeds:
                seeds.add(node)
                added_nodes.add(node)
                break

def write_normalized_scores(max_scores_dir: str, layer_max_scores: dict) -> None:
    """
    Normalizes scores per layer (by dividing by the max score) and writes them to a file.
    
    Params:
      max_scores_dir: Directory to save normalized score files.
      layer_max_scores: Dictionary with raw max scores.
    """
    os.makedirs(max_scores_dir, exist_ok=True)
    for layer, scores_dict in layer_max_scores.items():
        max_score = max(scores_dict.values()) if scores_dict else 1
        if max_score == 0:
            max_score = 1  
        normalized_scores = {node: (score / max_score) for node, score in scores_dict.items()}
        multiplex_value = extract_multiplex_value(layer)
        output_file_layer = os.path.join(max_scores_dir, f"{multiplex_value}_max_scores.tsv")
        with open(output_file_layer, 'w') as f:
            f.write(SCORE_HEADER)
            for node, norm_score in normalized_scores.items():
                f.write(f"{multiplex_value}\t{node}\t{layer}\t{norm_score}\n")




def get_ranking_df_from_max_scores(max_scores_dir: str, nb_nodes_per_layer: int) -> pd.DataFrame:
    """
    Get a ranking DataFrame from normalized score files.
    
    Parameters:
      max_scores_dir: Directory containing normalized score files.
      nb_nodes_per_layer: Number of top nodes to retain per layer.
    
    Returns:
      A DataFrame with the top-ranked nodes from each file.
    """
    ranking_df = pd.DataFrame()
    for file_path in glob.glob(os.path.join(max_scores_dir, "*.tsv")):
        df = pd.read_csv(file_path, sep='\t')
        df_sorted = df.sort_values(by="score", ascending=False)
        df_top = df_sorted.head(nb_nodes_per_layer)
        ranking_df = pd.concat([ranking_df, df_top], ignore_index=True)
    return ranking_df
