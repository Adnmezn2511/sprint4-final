"""
edge_bundling.py
----------------
Edge-Path Bundling pour arêtes interlayer uniquement.

Basé sur Wallinger et al. (2021) "Edge-Path Bundling: A Less Ambiguous
Edge Bundling Approach" et (2023) "Faster Edge-Path Bundling through
Graph Spanners".

Algorithme :
  1. Triangulation de Delaunay sur les positions 2D de TOUS les nœuds
  2. Construction du graphe de proximité pondéré par distance^d
  3. Pour chaque arête INTERLAYER : plus court chemin dans le graphe de proximité
  4. Si chemin ≤ k × distance directe → router le long du chemin (bundling)
  5. Sinon → garder la ligne droite
  6. Lisser les chemins avec la subdivision de Chaikin

Les arêtes INTRALAYER ne sont pas bundlées (courtes, peu de croisements).
"""

import numpy as np
import networkx as nx
from scipy.spatial import Delaunay


def compute_bundled_paths(G: nx.Graph, pos: dict, k: float = 2.0, d: float = 2.0) -> dict:
    """
    Calcule les chemins bundlés pour les arêtes interlayer.

    Args:
        G   : graphe multiplex (nœuds avec attribut 'layer')
        pos : dict {node_id: (x, y)} depuis layered_layout
        k   : seuil de détour (défaut 2.0)
              Si longueur_chemin > k × distance_directe → ligne droite
        d   : exposant de pondération des arêtes Delaunay (défaut 2.0)
              Plus d est élevé, plus les chemins convergent vers les mêmes troncs

    Returns:
        dict {(u, v): list[(x, y)]}
          - arête intralayer          → [(x_u, y_u), (x_v, y_v)]   droite
          - arête interlayer bundlée  → [(x0,y0), ..., (xn,yn)]    courbe lissée
          - arête interlayer non-bundlée → [(x_u,y_u), (x_v,y_v)]  droite
    """
    nodes = [n for n in G.nodes() if n in pos]

    # Pas assez de nœuds pour Delaunay
    if len(nodes) < 4:
        return {(u, v): [pos[u], pos[v]] for u, v in G.edges() if u in pos and v in pos}

    points      = np.array([pos[n] for n in nodes])
    node_to_idx = {n: i for i, n in enumerate(nodes)}
    idx_to_node = nodes  # liste indexée

    # ── 1. Triangulation de Delaunay ─────────────────────────────────────────
    try:
        tri = Delaunay(points)
    except Exception:
        return {(u, v): [pos.get(u, (0, 0)), pos.get(v, (0, 0))] for u, v in G.edges()}

    # ── 2. Graphe de proximité pondéré ────────────────────────────────────────
    proximity = nx.Graph()
    proximity.add_nodes_from(nodes)

    for simplex in tri.simplices:
        for i in range(len(simplex)):
            for j in range(i + 1, len(simplex)):
                n1 = idx_to_node[simplex[i]]
                n2 = idx_to_node[simplex[j]]
                if not proximity.has_edge(n1, n2):
                    dist = float(np.linalg.norm(points[simplex[i]] - points[simplex[j]]))
                    proximity.add_edge(n1, n2, weight=dist ** d if dist > 0 else 1e-9)

    # ── 3. Bundling des arêtes ────────────────────────────────────────────────
    bundled = {}

    for u, v in G.edges():
        if u not in pos or v not in pos:
            bundled[(u, v)] = [(0.0, 0.0), (0.0, 0.0)]
            continue

        u_layer = G.nodes[u].get("layer", "")
        v_layer = G.nodes[v].get("layer", "")

        # Intralayer → ligne droite, pas de bundling
        if u_layer == v_layer:
            bundled[(u, v)] = [pos[u], pos[v]]
            continue

        # Interlayer → chercher le chemin dans le graphe de proximité
        p_u = np.array(pos[u])
        p_v = np.array(pos[v])
        direct_dist = float(np.linalg.norm(p_u - p_v))

        if direct_dist < 1e-6:
            bundled[(u, v)] = [pos[u], pos[v]]
            continue

        if u not in proximity or v not in proximity:
            bundled[(u, v)] = [pos[u], pos[v]]
            continue

        try:
            path_nodes = nx.shortest_path(proximity, u, v, weight="weight")

            # Longueur euclidienne du chemin trouvé
            path_length = sum(
                float(np.linalg.norm(
                    np.array(pos[path_nodes[i]]) - np.array(pos[path_nodes[i + 1]])
                ))
                for i in range(len(path_nodes) - 1)
            )

            # Critère de bundling : le détour ne doit pas dépasser k × distance directe
            if path_length > k * direct_dist or len(path_nodes) <= 2:
                bundled[(u, v)] = [pos[u], pos[v]]
            else:
                control_pts = [pos[n] for n in path_nodes]
                bundled[(u, v)] = _smooth_chaikin(control_pts, iterations=2)

        except (nx.NetworkXNoPath, nx.NodeNotFound):
            bundled[(u, v)] = [pos[u], pos[v]]

    return bundled


def _smooth_chaikin(points: list, iterations: int = 2) -> list:
    """
    Lissage par subdivision de Chaikin (corner cutting).
    Transforme une polyligne anguleuse en courbe lisse tout en
    conservant les extrémités exactes (source et destination).

    Args:
        points     : liste de tuples (x, y)
        iterations : nombre de passes (2 = bon équilibre lisibilité / fidélité)

    Returns:
        liste de tuples (float, float) lissés
    """
    if len(points) <= 2:
        return list(points)

    pts = [np.array(p, dtype=float) for p in points]

    for _ in range(iterations):
        new_pts = [pts[0]]                    # garder le point de départ exact
        for i in range(len(pts) - 1):
            q = 0.75 * pts[i] + 0.25 * pts[i + 1]
            r = 0.25 * pts[i] + 0.75 * pts[i + 1]
            new_pts.extend([q, r])
        new_pts.append(pts[-1])               # garder le point d'arrivée exact
        pts = new_pts

    return [(float(p[0]), float(p[1])) for p in pts]
