import networkx as nx
import pandas as pd

class MultiplexGraph:
    def __init__(self, sif_file: str, ranking_file: str = None):
        """ Initializes the multiplex graph from a SIF file and optionally a ranking file.

        :param sif_file: Path to the SIF file.
        :param ranking_file: Path to the ranking file (optional).
        """
        self.G = nx.Graph()
        self.layers = set()
        self.ranking_mapping = self._load_ranking_file(ranking_file) if ranking_file else {}
        self._load_sif_file(sif_file)
    
    def _load_ranking_file(self, ranking_file: str):
        ranking_df = pd.read_csv(ranking_file, sep='\t')
        ranking_df['multiplex'] = ranking_df['multiplex'].astype(str)
        ranking_df['node'] = ranking_df['node'].astype(str)
        mapping = {}
        for _, row in ranking_df.iterrows():
            key = (row['node'], row['multiplex'])
            mapping[key] = row['score']
        return mapping
    
    def _load_sif_file(self, sif_file: str):
        with open(sif_file, 'r', encoding='utf-8') as f:
            for line in f:
                self._process_line(line.strip())
    
    def _process_line(self, line: str):
        if not line or line.startswith("#"):
            return
        parts = line.split('\t')
        if len(parts) != 3:
            print(f"⚠ Format incorrect pour la ligne: {line}")
            return
        node1, relation, node2 = parts
        self._add_nodes_and_edges(node1, relation, node2)
    
    def _add_nodes_and_edges(self, node1: str, relation: str, node2: str):
        if relation.startswith("multiplex/"):
            try:
                layer = relation.split('/')[1]
            except IndexError:
                print(f"⚠ Erreur de parsing pour la relation: {relation}")
                return
            n1_id = (node1, layer)
            n2_id = (node2, layer)
            self.layers.add(layer)
        elif relation.startswith("bipartite/"):
            s = relation[len("bipartite/"):]
            if s.endswith(".tsv"):
                s = s[:-4]
            try:
                layer1, layer2 = s.split('_')
            except ValueError:
                print(f"⚠ Format bipartite incorrect pour la relation: {relation}")
                return
            n1_id = (node1, layer1)
            n2_id = (node2, layer2)
            self.layers.update([layer1, layer2])
        else:
            print(f"⚠ Relation inconnue: {relation}")
            return
        
        score1 = self.ranking_mapping.get((node1, n1_id[1]), 0)
        score2 = self.ranking_mapping.get((node2, n2_id[1]), 0)
        
        if n1_id not in self.G:
            self.G.add_node(n1_id, label=node1, layer=n1_id[1], score=score1)
        if n2_id not in self.G:
            self.G.add_node(n2_id, label=node2, layer=n2_id[1], score=score2)
        self.G.add_edge(n1_id, n2_id, relation=relation)
    
    def get_graph(self):
        """ Returns the constructed graph and the sorted list of layers.
        """
        return self.G, sorted(self.layers, key=lambda x: int(x))
