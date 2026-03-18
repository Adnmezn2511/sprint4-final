import os
from .constants import CONFIG_FILENAME

def write_config_file(config_file: str, out_folder: str) -> None:
    """
    Copies the config file to the output folder, updating the seed file path.
    
    Params:
      config_file: Original config file path.
      out_folder: Output directory.
    """
    config_out = os.path.join(out_folder, CONFIG_FILENAME)
    with open(config_file, 'r') as infile, open(config_out, 'w') as outfile:
        for i, line in enumerate(infile):
            if i == 0:
                # Replace the first line with the new seed file path.
                seed_line = f"seed: {os.path.join(out_folder, f'seeds.txt')}\n"
                outfile.write(seed_line)
            else:
                outfile.write(line)

def read_seeds(seeds_filepath: str) -> set:
    """
    Reads the seeds file and returns the set of seeds.
    
    Params:
      seeds_filepath: Path to the seeds file.
      
    Returns:
      A set of seeds.
    """
    with open(seeds_filepath, 'r') as file:
        return {line.rstrip('\n') for line in file}

def write_seeds(seeds: set, seeds_filepath: str) -> None:
    """
    Writes seeds to the specified file, one per line.
    
    Params:
      seeds: Set of seeds.
      seeds_filepath: Path where seeds will be written.
    """
    with open(seeds_filepath, 'w') as file:
        for seed in seeds:
            file.write(f"{seed}\n")
