"""
Module de fusion de graphes patients.
Prend N graphes NetworkX individuels (issus de run_itRWR) et les fusionne en un seul
nx.Graph enrichi avec les attributs de fréquence multi-patient.
"""
import networkx as nx


def merge_patient_graphs(patient_graphs: dict) -> tuple:
    """
    Fusionne les graphes NetworkX de plusieurs patients en un seul graphe.

    Args:
        patient_graphs: dict {patient_id: (G, layers, seeds_list)}
            - G: nx.Graph issu de MultiplexGraph.get_graph()
            - layers: liste des couches
            - seeds_list: liste des seeds du patient

    Returns:
        tuple (nx.Graph, list):
            - G_merged: graphe fusionné avec attributs enrichis
            - layers: liste triée des couches (union de toutes les couches)

    Attributs des nœuds dans G_merged:
        - label (str): nom du gène/pathway/disease/compound
        - layer (str): identifiant de la couche
        - score (float): score RWR maximum parmi les patients (compatibilité GraphVisualizer)
        - freq (int): nombre de patients ayant ce nœud
        - max_score (float): = score
        - mean_score (float): score moyen parmi les patients qui l'ont
        - patient_scores (dict): {patient_id: score}
        - patient_seeds (set): patients pour lesquels ce nœud est une seed

    Attributs des arêtes dans G_merged:
        - relation (str): type de relation
        - freq (int): nombre de patients partageant cette arête
        - patients (set): ensemble des patient_id
    """
    G_merged = nx.Graph()
    all_layers = set()

    for patient_id, (G_patient, layers_patient, seeds_list) in patient_graphs.items():
        all_layers.update(layers_patient)

        # Fusionner les nœuds
        for node, data in G_patient.nodes(data=True):
            if node in G_merged:
                existing = G_merged.nodes[node]
                existing['freq'] += 1
                existing['patient_scores'][patient_id] = data.get('score', 0)
                existing['max_score'] = max(existing['max_score'], data.get('score', 0))
                existing['score'] = existing['max_score']
            else:
                score = data.get('score', 0)
                G_merged.add_node(node,
                    label=data.get('label', str(node)),
                    layer=data.get('layer', ''),
                    score=score,
                    freq=1,
                    max_score=score,
                    patient_scores={patient_id: score},
                    patient_seeds=set(),
                )

            # Tracker les seeds
            node_label = data.get('label', str(node))
            if node_label in seeds_list:
                G_merged.nodes[node]['patient_seeds'].add(patient_id)

        # Fusionner les arêtes
        for u, v, edge_data in G_patient.edges(data=True):
            if G_merged.has_edge(u, v):
                existing_edge = G_merged.edges[u, v]
                existing_edge['freq'] += 1
                existing_edge['patients'].add(patient_id)
            else:
                G_merged.add_edge(u, v,
                    relation=edge_data.get('relation', ''),
                    freq=1,
                    patients={patient_id},
                )

    # Calculer mean_score
    for node in G_merged.nodes():
        scores = G_merged.nodes[node]['patient_scores']
        G_merged.nodes[node]['mean_score'] = sum(scores.values()) / len(scores)

    sorted_layers = sorted(all_layers, key=lambda x: int(x))
    return G_merged, sorted_layers
