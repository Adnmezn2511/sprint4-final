import networkx as nx
from typing import Dict, List, Any


class CommunityDetector:
    """
    Détecte les zones fortement connectées (communautés/modules) dans un graphe NetworkX.

    Deux algorithmes sont disponibles :
      - "louvain"      : détection de communautés par la méthode de Louvain (via networkx.algorithms.community)
      - "greedy"       : détection de communautés par modularité greedy (networkx natif)
      - "connected"    : composantes connexes du graphe (non dirigé)
      - "scc"          : composantes fortement connexes (graphe dirigé)
    """

    SUPPORTED_ALGORITHMS = ("louvain", "greedy", "connected", "scc")

    def __init__(self, G: nx.Graph, algorithm: str = "louvain"):
        """
        Initialise le détecteur.

        :param G: Graphe NetworkX (Graph ou DiGraph).
        :param algorithm: Algorithme à utiliser parmi SUPPORTED_ALGORITHMS.
        :raises ValueError: si l'algorithme n'est pas supporté ou le graphe est vide.
        """
        if algorithm not in self.SUPPORTED_ALGORITHMS:
            raise ValueError(
                f"Algorithme '{algorithm}' non supporté. "
                f"Choisissez parmi : {self.SUPPORTED_ALGORITHMS}"
            )
        if G is None or G.number_of_nodes() == 0:
            raise ValueError("Le graphe fourni est vide ou None.")

        self.G = G
        self.algorithm = algorithm

    def detect(self) -> List[List[Any]]:
        """
        Lance la détection de communautés selon l'algorithme choisi.

        :returns: Liste de communautés, chaque communauté étant une liste de nœuds.
        :raises RuntimeError: en cas d'échec interne de l'algorithme.
        """
        try:
            if self.algorithm == "louvain":
                return self._louvain()
            elif self.algorithm == "greedy":
                return self._greedy_modularity()
            elif self.algorithm == "connected":
                return self._connected_components()
            elif self.algorithm == "scc":
                return self._strongly_connected_components()
        except Exception as exc:
            raise RuntimeError(
                f"Erreur lors de la détection de communautés avec '{self.algorithm}' : {exc}"
            ) from exc

    # ── algorithmes privés ────────────────────────────────────────────────────

    def _louvain(self) -> List[List[Any]]:
        """Méthode de Louvain via networkx.algorithms.community."""
        undirected = self.G.to_undirected() if self.G.is_directed() else self.G
        communities = nx.algorithms.community.louvain_communities(undirected, seed=42)
        return [list(c) for c in communities]

    def _greedy_modularity(self) -> List[List[Any]]:
        """Modularité greedy (Clauset-Newman-Moore) via networkx natif."""
        undirected = self.G.to_undirected() if self.G.is_directed() else self.G
        communities = nx.algorithms.community.greedy_modularity_communities(undirected)
        return [list(c) for c in communities]

    def _connected_components(self) -> List[List[Any]]:
        """Composantes connexes pour graphe non dirigé."""
        undirected = self.G.to_undirected() if self.G.is_directed() else self.G
        return [list(c) for c in nx.connected_components(undirected)]

    def _strongly_connected_components(self) -> List[List[Any]]:
        """Composantes fortement connexes pour graphe dirigé."""
        directed = self.G if self.G.is_directed() else self.G.to_directed()
        return [list(c) for c in nx.strongly_connected_components(directed)]

    # ── utilitaires ───────────────────────────────────────────────────────────

    @staticmethod
    def communities_to_dict(communities: List[List[Any]]) -> Dict[str, Any]:
        """
        Convertit la liste de communautés en dictionnaire sérialisable (JSON-ready).

        :param communities: Liste de listes de nœuds.
        :returns: Dictionnaire avec métadonnées et liste des communautés.
        """
        return {
            "nb_communities": len(communities),
            "communities": [
                {
                    "id": idx,
                    "size": len(community),
                    "nodes": [str(n) for n in community],
                }
                for idx, community in enumerate(communities)
            ],
        }