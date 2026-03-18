import os
import subprocess
from .. import multixrank as mxk

from .file_utils import write_config_file, read_seeds, write_seeds
from .ranking_utils import *
from .sif_utils import correct_sif_order, filter_sif_file
from .constants import CONFIG_FILENAME

import json

class CommunityProcessor:
    """
    Handles community processing with the multixrank algorithm.
    
    Params:
      path: working directory.
      config_file: config filename.
      out_folder: output directory.
      seeds_file: seeds filename.
      nb_iterations: number of iterations.
      nb_nodes_per_layer: nodes per layer for final SIF.
    """
    def __init__(self, path: str, config_file: str, out_folder: str, seeds_file: str, nb_iterations: int, nb_nodes_per_layer: int):
        self.path = path
        self.config_file = config_file
        self.out_folder = out_folder
        self.seeds_file = seeds_file
        self.nb_iterations = nb_iterations
        self.nb_nodes_per_layer = nb_nodes_per_layer
        self.layer_max_scores = {}  # Store max scores per layer
        self.added_nodes = set()    # Track added seeds to avoid duplicates
        self.missing_seeds = []
    
    def run(self) -> None:
        
        subprocess.call(["cp", self.seeds_file, self.out_folder])
        
        write_config_file(self.config_file, self.out_folder)
        
        seeds_path = os.path.join(self.out_folder, self.seeds_file)
        seeds = read_seeds(seeds_path)  
        
        for i in range(self.nb_iterations):
            print(f"Iteration {i+1} of {self.nb_iterations}")
            iter_folder = os.path.join(self.out_folder, f"iteration_{i}")
            os.makedirs(iter_folder, exist_ok=True)
            
            multixrank_obj = mxk.Multixrank(config=os.path.join(self.out_folder, CONFIG_FILENAME), wdir=self.path)
            self.missing_seeds = sorted(set(self.missing_seeds) | set(multixrank_obj.seed_obj.missing_seeds))
            ranking = multixrank_obj.random_walk_rank()

            # ### test noreg
            # multixrank_obj1 = mxk.Multixrank(config=os.path.join(self.out_folder, CONFIG_FILENAME), wdir=self.path, old=True)
            # ranking1 = multixrank_obj1.random_walk_rank_old()
            # assert ranking.equals(ranking1)
            # ###

            ranking_df = multixrank_obj.write_ranking(ranking)
            ranking_files = get_multiplex_rankings_mem(ranking_df, iter_folder)

            update_layer_max_scores_vec(ranking, ranking_files, self.layer_max_scores)

            ### test opt non regression
            # multixrank_obj.write_ranking(ranking, path=iter_folder, aggregation="gmean_old")
            # ranking_files_noreg = get_multiplex_rankings(iter_folder)
            # layer_max_scores_noreg = {}
            # update_layer_max_scores(ranking, ranking_files_noreg, layer_max_scores_noreg)
            # assert sorted(layer_max_scores_noreg) == sorted(self.layer_max_scores)
            ###

            update_seeds_from_iteration(ranking_files, seeds, self.added_nodes)   
            write_seeds(seeds, os.path.join(iter_folder, self.seeds_file))
            write_seeds(seeds, os.path.join(self.out_folder, self.seeds_file))
        
        # Write normalized scores and final rankings
        max_scores_dir = os.path.join(self.out_folder, 'max_scores')
        write_normalized_scores(max_scores_dir, self.layer_max_scores)
        output_file = os.path.join(self.out_folder, 'ranking_final.sif')
        ranking_final = get_ranking_df_from_max_scores(max_scores_dir, self.nb_nodes_per_layer)
        ranking_final.to_csv(os.path.join(self.out_folder, 'ranking_final.csv'), sep='\t', index=False)
        
        # Create final SIF and clean up
        multixrank_obj.to_sif(ranking_final, path=output_file, top=self.nb_nodes_per_layer, top_type="layered")
        correct_sif_order(output_file, iter_folder)
        filter_sif_file(output_file, ranking_final)
