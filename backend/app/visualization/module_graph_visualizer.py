import math
from typing import Dict, List, Optional, Tuple

import networkx as nx
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from app.graph.community_detector import CommunityDetector
from .edge_bundling import compute_bundled_paths


def _extract_modules_with_mapping(
    G: nx.Graph,
    algorithm: str = "scc",
) -> Tuple[List[Dict], Dict]:
    """
    Extrait les modules via l'US-C2 (CommunityDetector) et renvoie :
    - modules (liste sérialisable)
    - node_to_module_id (mapping node_id -> module_id)
    """
    if G is None or G.number_of_nodes() == 0:
        return [], {}

    detector = CommunityDetector(G, algorithm=algorithm)
    communities = detector.detect()
    communities = sorted(communities, key=lambda comp: len(comp), reverse=True)

    modules: List[Dict] = []
    node_to_module_id: Dict = {}

    for index, community in enumerate(communities, start=1):
        module_id = f"M{index}"

        # Mapping node_id -> module_id
        for node in community:
            node_to_module_id[node] = module_id

        labels = sorted(
            {
                G.nodes[node].get("label", node[0] if isinstance(node, tuple) else str(node))
                for node in community
            }
        )

        modules.append(
            {
                "module_id": module_id,
                "size": len(community),
                "nodes": labels,
            }
        )

    return modules, node_to_module_id


def _dominant_patient(module_patient_scores: Dict[str, float]) -> Optional[str]:
    if not module_patient_scores:
        return None
    # Top patient by aggregated score; deterministic tie-break by patient_id
    return sorted(module_patient_scores.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]


def _build_module_graph(
    G_merged: nx.Graph,
    node_to_module_id: Dict,
    algorithm: str = "scc",
) -> Tuple[nx.Graph, List[Dict]]:
    """
    Construit un graphe des modules :
    - nœuds = modules (US-C2 / CommunityDetector)
    - arêtes entre modules si au moins une arête existe entre leurs nœuds membres
    """
    modules, _ = _extract_modules_with_mapping(G_merged, algorithm=algorithm)

    H = nx.Graph()

    # Pré-calc : pour chaque module, agrège les scores patients
    module_patient_scores_sum: Dict[str, Dict[str, float]] = {}
    module_node_sizes: Dict[str, int] = {}

    for node in G_merged.nodes():
        module_id = node_to_module_id.get(node)
        if module_id is None:
            continue
        module_node_sizes[module_id] = module_node_sizes.get(module_id, 0) + 1
        module_patient_scores_sum.setdefault(module_id, {})
        for pid, score in (G_merged.nodes[node].get("patient_scores", {}) or {}).items():
            module_patient_scores_sum[module_id][pid] = (
                module_patient_scores_sum[module_id].get(pid, 0.0) + float(score)
            )

    for module_id, size in module_node_sizes.items():
        dominant_pid = _dominant_patient(module_patient_scores_sum.get(module_id, {}))
        # Astuce : layer unique par module pour forcer l’inter-module bundling
        # (compute_bundled_paths ne bundle que si layer(u) != layer(v)).
        H.add_node(
            module_id,
            label=module_id,
            module_id=module_id,
            size=size,
            patient_scores_sum=module_patient_scores_sum.get(module_id, {}),
            dominant_patient=dominant_pid,
            layer=str(module_id),
        )

    # Arêtes modules
    for u, v, data in G_merged.edges(data=True):
        mu = node_to_module_id.get(u)
        mv = node_to_module_id.get(v)
        if mu is None or mv is None or mu == mv:
            continue

        freq = int(data.get("freq", 1))
        if H.has_edge(mu, mv):
            H.edges[mu, mv]["freq"] += freq
        else:
            H.add_edge(mu, mv, freq=freq)

    return H, modules


def create_fused_modules_interactive_graph(
    G_merged: nx.Graph,
    merged_layers: List[str],
    node_positions: Dict,
    active_patients: List[str],
    output_file: str,
    k: float = 2.0,
    d: float = 2.0,
    layer_gap: float = 6.0,
    module_algorithm: str = "scc",
) -> Tuple[go.Figure, List[Dict]]:
    """
    Génère la figure Plotly affichant les modules fusionnés avec :
    - edge-path bundling (sur le graphe des modules)
    - couleurs des modules par patient dominant
    """
    modules, node_to_module_id = _extract_modules_with_mapping(
        G_merged,
        algorithm=module_algorithm,
    )
    if not modules:
        fig = go.Figure()
        return fig, []

    H, modules_from_graph = _build_module_graph(
        G_merged,
        node_to_module_id,
        algorithm=module_algorithm,
    )

    # --- Couleurs patients
    palette = px.colors.qualitative.Plotly
    patient_to_color = {
        pid: palette[i % len(palette)] for i, pid in enumerate(sorted(active_patients))
    }

    # --- Positions modules (centroid des nœuds membres)
    module_positions: Dict[str, Tuple[float, float]] = {}
    max_x = -math.inf
    min_x = math.inf
    max_y = -math.inf
    min_y = math.inf

    # Reconstitue la liste des nœuds membres par module
    module_to_nodes: Dict[str, List] = {}
    for node, mid in node_to_module_id.items():
        module_to_nodes.setdefault(mid, []).append(node)

    for module_id in H.nodes():
        members = module_to_nodes.get(module_id, [])
        xs = [node_positions[n][0] for n in members if n in node_positions]
        ys = [node_positions[n][1] for n in members if n in node_positions]

        if not xs:
            cx, cy = 0.0, 0.0
        else:
            cx, cy = float(np.mean(xs)), float(np.mean(ys))

        module_positions[module_id] = (cx, cy)
        max_x = max(max_x, cx)
        min_x = min(min_x, cx)
        max_y = max(max_y, cy)
        min_y = min(min_y, cy)

    # --- Background rectangles (par "layers" modules)
    module_layer_ids = sorted([str(n) for n in H.nodes()])
    # Hauteur approximative des bandes (évite le "0 height" si graphe plat)
    denom = max(1, len(module_layer_ids))
    approx_band_height = max(1.0, (max_y - min_y) / denom if max_y > min_y else layer_gap)
    band_height = approx_band_height * 0.9

    # x-extent pour les rectangles
    x_range = max_x - min_x if max_x > min_x else 1.0
    x0_global = min_x - 0.12 * x_range
    x1_global = max_x + 0.12 * x_range

    background_shapes = []
    layer_annotations = []
    for idx, ml in enumerate(module_layer_ids):
        # Centrage vertical sur la position réelle du module si possible
        module_id = ml
        _, cy = module_positions.get(module_id, (0.0, idx * layer_gap))
        y0 = cy - band_height / 2.0
        y1 = cy + band_height / 2.0

        background_shapes.append(
            dict(
                type="rect",
                xref="x",
                yref="y",
                x0=x0_global,
                y0=y0,
                x1=x1_global,
                y1=y1,
                fillcolor="rgba(200,200,200,0.5)",
                opacity=0.5,
                layer="below",
                line=dict(width=0),
            )
        )
        layer_annotations.append(
            dict(
                x=x1_global + 0.05,
                y=(y0 + y1) / 2.0,
                xref="x",
                yref="y",
                text=f"<b>Module {module_id}</b>",
                showarrow=False,
                font=dict(size=12, color="#333"),
                xanchor="left",
                yanchor="middle",
                bgcolor="rgba(255,255,255,0.0)",
            )
        )

    # --- Edge-path bundling sur le graphe des modules
    pos_for_bundling = {mid: module_positions[mid] for mid in H.nodes() if mid in module_positions}
    bundled_paths = None
    try:
        bundled_paths = compute_bundled_paths(H, pos_for_bundling, k=k, d=d)
    except Exception:
        bundled_paths = None

    # --- Traces arêtes (groupées par bins de fréquence)
    edges_data = list(H.edges(data=True))
    if not edges_data:
        edges_traces: List[go.Scatter] = []
    else:
        # bins -> (label, min_inclusive, max_inclusive)
        freq_bins = [("1", 1, 1), ("2-4", 2, 4), ("5+", 5, 999999)]
        bin_to_edges = {label: [] for (label, _, __) in freq_bins}

        for u, v, data in edges_data:
            freq = int(data.get("freq", 1))
            chosen_label = freq_bins[-1][0]
            for label, fmin, fmax in freq_bins:
                if fmin <= freq <= fmax:
                    chosen_label = label
                    break
            bin_to_edges[chosen_label].append((u, v, freq))

        edges_traces = []
        for label, fmin, fmax in freq_bins:
            edges_in_bin = bin_to_edges.get(label, [])
            if not edges_in_bin:
                continue

            # Epaisseur & couleur cohérentes
            if label == "1":
                width = 1.2
                color = "rgba(120,120,120,0.55)"
            elif label == "2-4":
                width = 2.0
                color = "rgba(90,90,90,0.65)"
            else:
                width = 3.2
                color = "rgba(70,70,70,0.75)"

            x_arr = []
            y_arr = []
            hover_arr = []

            for u, v, freq in edges_in_bin:
                if bundled_paths:
                    path = bundled_paths.get((u, v)) or bundled_paths.get((v, u))
                else:
                    path = None

                if path and len(path) > 2:
                    pts = path
                else:
                    pts = [module_positions[u], module_positions[v]]

                # Points
                for i, (px_, py_) in enumerate(pts):
                    x_arr.append(px_)
                    y_arr.append(py_)
                    if i == 0:
                        hover_arr.append(f"{u} ↔ {v}<br>edge freq: {freq}")
                    else:
                        hover_arr.append(None)

                x_arr.append(None)
                y_arr.append(None)
                hover_arr.append(None)

            edges_traces.append(
                go.Scatter(
                    x=x_arr,
                    y=y_arr,
                    mode="lines",
                    line=dict(width=width, color=color, shape="spline", smoothing=0.8),
                    hoverinfo="text",
                    text=hover_arr,
                    name="Inter-module edges",
                    showlegend=False,
                )
            )

    # --- Traces nœuds (modules) : couleur = dominant patient
    max_module_size = max((H.nodes[n].get("size", 1) for n in H.nodes()), default=1)
    base_size = 10
    scale_factor = 20

    node_x = []
    node_y = []
    node_sizes = []
    node_colors = []
    node_borders = []
    node_hover = []

    for mid in H.nodes():
        x, y = module_positions[mid]
        size = int(H.nodes[mid].get("size", 1))
        dominant_pid = H.nodes[mid].get("dominant_patient")
        patient_color = patient_to_color.get(dominant_pid, "lightblue") if dominant_pid else "lightblue"

        node_x.append(x)
        node_y.append(y)
        node_sizes.append(base_size + scale_factor * (size / max_module_size))
        node_colors.append(patient_color)
        node_borders.append("darkblue")

        patient_scores_sum = H.nodes[mid].get("patient_scores_sum", {}) or {}
        ps_sorted = sorted(patient_scores_sum.items(), key=lambda kv: kv[1], reverse=True)
        top_ps = ps_sorted[:5]
        ps_lines = "<br>".join([f"{pid}: {score:.3f}" for pid, score in top_ps]) if top_ps else "N/A"

        node_hover.append(
            f"<b>{mid}</b><br>Module size: {size}<br>"
            f"Dominant patient: {dominant_pid or 'N/A'}<br><br>"
            f"<b>Scores agrégés par patient (top)</b><br>{ps_lines}"
        )

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers",
        hoverinfo="text",
        hovertext=node_hover,
        marker=dict(
            size=node_sizes,
            color=node_colors,
            line=dict(width=2, color=node_borders),
            symbol="circle",
        ),
        name="Modules",
        showlegend=False,
    )

    # --- Légende patients (dummies)
    patient_legend_traces = []
    for pid in sorted(active_patients):
        patient_legend_traces.append(
            go.Scatter(
                x=[None],
                y=[None],
                mode="markers",
                marker=dict(size=10, color=patient_to_color.get(pid, "lightblue"), line=dict(width=1, color="gray")),
                showlegend=True,
                name=f"Patient {pid}",
                legendgroup="patients",
            )
        )

    fig = go.Figure(data=edges_traces + patient_legend_traces + [node_trace])
    fig.update_layout(
        shapes=background_shapes,
        annotations=layer_annotations,
        title=dict(
            text="<b>Merged modules - All patients</b>",
            x=0.5,
            xanchor="center",
            y=0.97,
            yanchor="top",
        ),
        hovermode="closest",
        autosize=True,
        margin=dict(b=50, t=110, l=50, r=120),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor="white",
        legend=dict(
            title="Patients (module color)",
            bordercolor="Black",
            borderwidth=1,
            orientation="v",
            yanchor="top",
            y=1.0,
            xanchor="left",
            x=1.02,
        ),
    )

    # Sauvegarde (cohérente avec GraphVisualizer)
    fig.write_html(output_file, include_plotlyjs="cdn")
    # write_image peut nécessiter kaleido (déjà présent pour GraphVisualizer)
    fig.write_image(output_file.replace(".html", ".png"))

    return fig, modules_from_graph

