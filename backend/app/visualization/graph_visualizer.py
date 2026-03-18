import networkx as nx
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import math
from itertools import combinations


# Bins de fréquence utilisés en mode fusionné.
# Nom → (freq_min, freq_max_inclus)
# Ces noms sont aussi utilisés dans assemble_figure pour construire
# les tableaux de visibilité des boutons updatemenus.
_FREQ_BINS = [
    ("1-2 patients", 1, 2),
    ("3-4 patients", 3, 4),
    ("5+ patients",  5, 9999),
]


class GraphVisualizer:
    def __init__(self, G: nx.Graph, layers: list):
        self.G = G
        self.layers = layers
        self.edge_colors = self.generate_edge_colors()
        self.inter_layer_colors = self.generate_inter_layer_colors()
        # Spring layout uniquement pour le graphe fusionné (nœuds avec attribut 'freq')
        # Graphes mono-patient : circular layout inchangé
        if any(G.nodes[n].get('freq') is not None for n in G.nodes()):
            self.pos = self.layered_spring_layout(layer_gap=6, scale=2)
        else:
            self.pos = self.layered_layout(layer_gap=6, scale=2)

    # ── couleurs ──────────────────────────────────────────────────────────────

    def generate_edge_colors(self):
        base_colors = px.colors.qualitative.Plotly
        return {layer: base_colors[i % len(base_colors)] for i, layer in enumerate(self.layers)}

    def generate_inter_layer_colors(self):
        inter_layer_pairs = list(combinations(sorted(self.layers), 2))
        palette = px.colors.qualitative.Dark2
        return {pair: palette[i % len(palette)] for i, pair in enumerate(inter_layer_pairs)}

    def _get_frequency_color(self, freq, max_freq):
        """Rampe gris → bleu → ambre → rouge clair → rouge foncé."""
        colors = [
            (211, 209, 199),
            (181, 212, 244),
            (249, 199, 117),
            (240, 149, 149),
            (226, 75,  74),
        ]
        if max_freq <= 1:
            idx = 0
        else:
            ratio = (freq - 1) / (max_freq - 1)
            idx = min(int(ratio * (len(colors) - 1)), len(colors) - 1)
        r, g, b = colors[idx]
        return f"rgb({r},{g},{b})"

    # ── layout ────────────────────────────────────────────────────────────────

    def layered_layout(self, layer_gap=6, scale=2):
        """
        Layout original (circular) — utilisé pour les graphes mono-patient.
        Comportement inchangé par rapport à la version initiale.
        """
        pos = {}
        for idx, layer in enumerate(self.layers):
            nodes_in_layer = [n for n in self.G.nodes() if self.G.nodes[n]['layer'] == layer]
            if nodes_in_layer:
                subG = self.G.subgraph(nodes_in_layer)
                sub_pos = nx.circular_layout(subG, scale=scale)
                xs = [p[0] for p in sub_pos.values()]
                ys = [p[1] for p in sub_pos.values()]
                centroid = (np.mean(xs), np.mean(ys))
                angle = idx * (math.pi / 6)
                cos_a, sin_a = math.cos(angle), math.sin(angle)
                for n in nodes_in_layer:
                    x, y = sub_pos[n]
                    x_c = x - centroid[0]
                    y_c = y - centroid[1]
                    pos[n] = (x_c * cos_a - y_c * sin_a,
                              x_c * sin_a + y_c * cos_a + idx * layer_gap)
        for n in self.G.nodes():
            if n not in pos:
                pos[n] = (0, 0)
        return pos

    def layered_spring_layout(self, layer_gap=6, scale=2):
        """
        Layout spring contraint par bande — utilisé uniquement pour le graphe fusionné.
        Spring_layout (Fruchterman-Reingold) sur le graphe complet pour aligner
        les nœuds connectés entre couches, puis Y forcé dans la bande de chaque couche.
        Réduit ~50 % des croisements interlayer par rapport au circular_layout.
        """
        if len(self.G.nodes()) == 0:
            return {}

        k_param = 1.5 / (len(self.G.nodes()) ** 0.5)
        global_pos = nx.spring_layout(
            self.G,
            k=k_param,
            iterations=80,
            scale=scale,
            seed=42,
        )

        pos = {}
        for idx, layer in enumerate(self.layers):
            nodes_in_layer = [n for n in self.G.nodes() if self.G.nodes[n]['layer'] == layer]
            if not nodes_in_layer:
                continue

            y_center = idx * layer_gap
            xs = [global_pos[n][0] for n in nodes_in_layer if n in global_pos]
            ys = [global_pos[n][1] for n in nodes_in_layer if n in global_pos]

            if not xs:
                for n in nodes_in_layer:
                    pos[n] = (0, y_center)
                continue

            x_min, x_max = min(xs), max(xs)
            y_min, y_max = min(ys), max(ys)
            x_range = x_max - x_min if x_max > x_min else 1
            y_range = y_max - y_min if y_max > y_min else 1

            for n in nodes_in_layer:
                if n not in global_pos:
                    pos[n] = (0, y_center)
                    continue
                gx, gy = global_pos[n]
                nx_ = ((gx - x_min) / x_range - 0.5) * 2 * scale
                ny_ = y_center + ((gy - y_min) / y_range - 0.5) * layer_gap * 0.3
                pos[n] = (nx_, ny_)

        for n in self.G.nodes():
            if n not in pos:
                pos[n] = (0, 0)

        return pos

    # ── fond + annotations couches ────────────────────────────────────────────

    def add_opacity(self, color, opacity):
        if color.startswith("#"):
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            return f"rgba({r}, {g}, {b}, {opacity})"
        if color.startswith("rgb("):
            inside = color[4:-1]
            parts = inside.split(",")
            if len(parts) == 3:
                return f"rgba({parts[0].strip()}, {parts[1].strip()}, {parts[2].strip()}, {opacity})"
        return color

    def generate_background_shapes_and_annotations(self, margin_x=0.8, margin_y=0.8, layer_names=None):
        centers = {}
        local_dims = {}
        for layer in self.layers:
            layer_positions = [self.pos[n] for n in self.G.nodes() if self.G.nodes[n]['layer'] == layer]
            if layer_positions:
                xs = [p[0] for p in layer_positions]
                ys = [p[1] for p in layer_positions]
                centers[layer] = (np.mean(xs), np.mean(ys))
                local_dims[layer] = (
                    (max(xs) - min(xs)) + 2 * margin_x,
                    (max(ys) - min(ys)) + 2 * margin_y,
                )

        # ── X global commun : toutes les bandes ont la même étendue horizontale ──
        all_xs = [self.pos[n][0] for n in self.G.nodes() if n in self.pos]
        if all_xs:
            x0_global = min(all_xs) - margin_x
            x1_global = max(all_xs) + margin_x
        else:
            x0_global, x1_global = -1, 1

        if local_dims:
            global_height = max(h for _, h in local_dims.values())
        else:
            global_height = 1

        background_shapes = []
        layer_annotations = []
        layer_rectangles  = {}

        for layer in self.layers:
            if layer in centers:
                _, cy = centers[layer]
                x0, x1 = x0_global, x1_global
                y0, y1 = cy - global_height / 2, cy + global_height / 2
                layer_rectangles[layer] = (x0, y0, x1, y1)
                background_shapes.append(dict(
                    type="rect", xref="x", yref="y",
                    x0=x0, y0=y0, x1=x1, y1=y1,
                    fillcolor="rgba(200,200,200,0.5)", opacity=0.5,
                    layer="below", line=dict(width=0),
                ))
                if layer_names is not None:
                    annotation_text = layer_names.get(str(layer), str(layer))
                else:
                    annotation_text = str(layer)
                layer_annotations.append(dict(
                    x=x1 + 0.05, y=(y0 + y1) / 2,
                    xref="x", yref="y",
                    text=f"<b>{annotation_text}</b>",
                    showarrow=False,
                    font=dict(size=13, color="#333"),
                    xanchor="left", yanchor="middle",
                    bgcolor="rgba(255,255,255,0.0)",
                ))

        return background_shapes, layer_annotations, layer_rectangles

    # ── arêtes ────────────────────────────────────────────────────────────────

    def group_edges_by_interaction(self, layer_names=None, bundled_paths=None):
        """
        Groupe les arêtes par type (intra/inter).
        Si bundled_paths est fourni, les arêtes interlayer sont tracées
        le long de leur chemin bundlé (N points) au lieu d'une ligne droite.
        """
        edge_groups       = {}
        edge_group_labels = {}
        edge_group_colors = {}

        for u, v, data in self.G.edges(data=True):
            if u[1] == v[1]:
                group_key   = f"intra_{u[1]}"
                group_label = (
                    f"Intra-layer interaction - {layer_names.get(str(u[1]), u[1])}"
                    if layer_names is not None
                    else f"Intra-layer interaction - Layer {u[1]}"
                )
                color = "darkgray"
            else:
                ls = sorted([u[1], v[1]], key=lambda x: int(x))
                group_key   = f"inter_{ls[0]}_{ls[1]}"
                group_label = (
                    f"Inter-layer interaction - "
                    f"{layer_names.get(str(ls[0]), ls[0])} and {layer_names.get(str(ls[1]), ls[1])}"
                    if layer_names is not None
                    else f"Inter-layer interaction - Layer {ls[0]} and Layer {ls[1]}"
                )
                color = self.inter_layer_colors.get((ls[0], ls[1]), "rgba(100,100,100,0.6)")

            if group_key not in edge_groups:
                edge_groups[group_key]       = {"x": [], "y": [], "hover": [], "freqs": []}
                edge_group_labels[group_key] = group_label
                edge_group_colors[group_key] = color

            edge_groups[group_key]["freqs"].append(data.get("freq", 1))

            # ── Coordonnées : bundlées ou droites ────────────────────────────
            path = None
            if bundled_paths:
                path = bundled_paths.get((u, v)) or bundled_paths.get((v, u))

            if path and len(path) > 2:
                # Arête interlayer bundlée : suivre le chemin point par point
                for px, py in path:
                    edge_groups[group_key]["x"].append(px)
                    edge_groups[group_key]["y"].append(py)
                edge_groups[group_key]["x"].append(None)
                edge_groups[group_key]["y"].append(None)
                # Hover sur le premier point seulement, None pour les suivants
                u_lbl = self.G.nodes[u]["label"]
                v_lbl = self.G.nodes[v]["label"]
                edge_groups[group_key]["hover"].append(f"{u_lbl} → {v_lbl}")
                edge_groups[group_key]["hover"].extend([None] * (len(path) - 1))
                edge_groups[group_key]["hover"].append(None)
            else:
                # Ligne droite (intralayer ou interlayer non-bundlée)
                x0, y0 = self.pos[u]
                x1, y1 = self.pos[v]
                edge_groups[group_key]["x"] += [x0, x1, None]
                edge_groups[group_key]["y"] += [y0, y1, None]
                edge_groups[group_key]["hover"] += [
                    (f"{self.G.nodes[u]['label']} (Layer "
                     f"{layer_names.get(str(self.G.nodes[u]['layer']), self.G.nodes[u]['layer'])})"
                     if layer_names
                     else f"{self.G.nodes[u]['label']} (Layer {self.G.nodes[u]['layer']})"),
                    (f"{self.G.nodes[v]['label']} (Layer "
                     f"{layer_names.get(str(self.G.nodes[v]['layer']), self.G.nodes[v]['layer'])})"
                     if layer_names
                     else f"{self.G.nodes[v]['label']} (Layer {self.G.nodes[v]['layer']})"),
                    None,
                ]

        return edge_groups, edge_group_labels, edge_group_colors

    def create_edge_traces(self, edge_groups, edge_group_labels, edge_group_colors):
        """
        - Épaisseur proportionnelle à la fréquence moyenne du groupe.
        - shape='spline' pour les arêtes interlayer (lisse les courbes bundlées).
        - shape='linear' pour les arêtes intralayer.
        """
        edge_traces = []
        for group_key, data_dict in edge_groups.items():
            freqs    = data_dict.get("freqs", [])
            avg_freq = sum(freqs) / len(freqs) if freqs else 1
            width    = max(0.8, min(0.5 + avg_freq * 0.4, 5))

            is_inter   = group_key.startswith("inter_")
            line_shape = "spline" if is_inter else "linear"

            trace = go.Scatter(
                x=data_dict["x"],
                y=data_dict["y"],
                mode="lines",
                line=dict(
                    width=width,
                    color=edge_group_colors[group_key],
                    shape=line_shape,
                    smoothing=0.8 if is_inter else 0,
                ),
                hoverinfo="text",
                text=data_dict["hover"],
                name=edge_group_labels[group_key],
                legendgroup=group_key,
                legendrank=1,
            )
            edge_traces.append(trace)
        return edge_traces

    # ── nœuds ─────────────────────────────────────────────────────────────────

    def _is_merged(self):
        return any(self.G.nodes[n].get("freq") is not None for n in self.G.nodes())

    def _max_freq(self):
        freqs = [self.G.nodes[n].get("freq", 1) for n in self.G.nodes()]
        return max(freqs) if freqs else 1

    def create_node_trace(self, base_size=10, scale_factor=20, seeds=None, layer_names=None):
        """
        Mode mono-patient : un seul trace, couleur fixe lightblue.
        Mode fusionné     : un seul trace, couleur par fréquence.
        (Utilisé en mono-patient. En mode fusionné, préférer create_node_traces_merged.)
        """
        is_merged = self._is_merged()
        max_freq  = self._max_freq() if is_merged else 1

        node_x, node_y, node_hover, node_sizes, node_symbols = [], [], [], [], []
        node_colors, node_borders = [], []

        for n in self.G.nodes():
            x, y = self.pos[n]
            node_x.append(x)
            node_y.append(y)
            label = self.G.nodes[n]["label"]
            layer = self.G.nodes[n]["layer"]
            score = self.G.nodes[n].get("score", 0)
            node_sizes.append(base_size + scale_factor * score)

            if is_merged:
                freq  = self.G.nodes[n].get("freq", 1)
                color = self._get_frequency_color(freq, max_freq)
                node_colors.append(color)
                node_borders.append("darkblue" if freq > 1 else "gray")

                patient_scores = self.G.nodes[n].get("patient_scores", {})
                patient_seeds  = self.G.nodes[n].get("patient_seeds", set())
                ps_lines = "<br>".join(
                    f"  {pid}: {s:.2f}" + (" (seed)" if pid in patient_seeds else "")
                    for pid, s in sorted(patient_scores.items())
                )
                neighbors = [
                    (f"{self.G.nodes[nb]['label']} (Layer "
                     f"{layer_names.get(str(self.G.nodes[nb]['layer']), self.G.nodes[nb]['layer'])}"
                     f", freq={self.G.nodes[nb].get('freq', 1)})"
                     if layer_names
                     else f"{self.G.nodes[nb]['label']} (Layer {self.G.nodes[nb]['layer']}"
                          f", freq={self.G.nodes[nb].get('freq', 1)})")
                    for nb in self.G.neighbors(n)
                ]
                neighbors_text = "<br>".join(f"• {nb}" for nb in neighbors) if neighbors else "Aucun"
                node_hover.append(
                    f"<b>{label}</b><br>Layer : {layer}<br>Score (max) : {score:.2f}"
                    f"<br>Mean score : {self.G.nodes[n].get('mean_score', score):.2f}"
                    f"<br>Freq : {freq}/{max_freq} patients"
                    f"<br><br>Scores par patient :<br>{ps_lines}"
                    f"<br><br>Neighbors :<br>{neighbors_text}"
                )
            else:
                node_colors.append("lightblue")
                node_borders.append("darkblue")
                neighbors = [
                    (f"{self.G.nodes[nb]['label']} (Layer "
                     f"{layer_names.get(str(self.G.nodes[nb]['layer']), self.G.nodes[nb]['layer'])})"
                     if layer_names
                     else f"{self.G.nodes[nb]['label']} (Layer {self.G.nodes[nb]['layer']})")
                    for nb in self.G.neighbors(n)
                ]
                neighbors_text = "<br>".join(f"• {nb}" for nb in neighbors) if neighbors else "Aucun"
                node_hover.append(
                    f"<b>{label}</b><br>Layer : {layer}<br>Score : {score:.2f}"
                    f"<br><br>Neighbors :<br>{neighbors_text}"
                )

            if seeds and any((seed == n) or (isinstance(seed, str) and seed == label) for seed in seeds):
                node_symbols.append("square")
            else:
                node_symbols.append("circle")

        return go.Scatter(
            x=node_x, y=node_y,
            mode="markers",
            hoverinfo="text",
            hovertext=node_hover,
            marker=dict(
                size=node_sizes,
                color=node_colors,
                line=dict(width=2, color=node_borders),
                symbol=node_symbols,
            ),
            name="Nœuds",
            showlegend=False,
        )

    def create_node_traces_merged(self, base_size=10, scale_factor=20, seeds=None, layer_names=None):
        """
        CORRECTIF 2 — Mode fusionné uniquement.
        Retourne UNE LISTE de go.Scatter, une par tranche de fréquence (_FREQ_BINS).
        Cela permet aux boutons updatemenus de cibler des traces spécifiques.
        """
        max_freq = self._max_freq()
        traces   = []

        for bin_label, freq_min, freq_max in _FREQ_BINS:
            bin_nodes = [
                n for n in self.G.nodes()
                if freq_min <= self.G.nodes[n].get("freq", 1) <= freq_max
            ]
            if not bin_nodes:
                continue

            nx_, ny_, hover_, sizes_, symbols_, colors_, borders_ = \
                [], [], [], [], [], [], []

            for n in bin_nodes:
                x, y = self.pos[n]
                nx_.append(x)
                ny_.append(y)

                label = self.G.nodes[n]["label"]
                layer = self.G.nodes[n]["layer"]
                score = self.G.nodes[n].get("score", 0)
                freq  = self.G.nodes[n].get("freq", 1)

                sizes_.append(base_size + scale_factor * score)
                colors_.append(self._get_frequency_color(freq, max_freq))
                borders_.append("darkblue" if freq > 1 else "gray")

                is_seed = seeds and any(
                    (seed == n) or (isinstance(seed, str) and seed == label)
                    for seed in seeds
                )
                patient_seeds = self.G.nodes[n].get("patient_seeds", set())
                symbols_.append("square" if (is_seed or patient_seeds) else "circle")

                # Hover enrichi
                patient_scores = self.G.nodes[n].get("patient_scores", {})
                ps_sorted = sorted(patient_scores.items(), key=lambda kv: kv[1], reverse=True)[:6]
                ps_lines  = "<br>".join(
                    f"  {pid}: {s:.3f}" + (" (seed)" if pid in patient_seeds else "")
                    for pid, s in ps_sorted
                )

                neighbors_info = sorted(
                    [
                        (
                            self.G.nodes[nb]["label"],
                            self.G.nodes[nb].get("freq", 1),
                            layer_names.get(str(self.G.nodes[nb]["layer"]), self.G.nodes[nb]["layer"])
                            if layer_names else self.G.nodes[nb]["layer"],
                        )
                        for nb in self.G.neighbors(n)
                    ],
                    key=lambda t: t[1],
                    reverse=True,
                )
                nb_lines = "<br>".join(
                    f"• {nl} ({nf} pat.) [{ls}]"
                    for nl, nf, ls in neighbors_info[:8]
                )
                if len(neighbors_info) > 8:
                    nb_lines += f"<br>  … +{len(neighbors_info) - 8} autres"

                seed_tag = " [SEED]" if (is_seed or patient_seeds) else ""
                layer_display = layer_names.get(str(layer), layer) if layer_names else layer

                hover_.append(
                    f"<b>{label}</b>{seed_tag}<br>"
                    f"Couche : {layer_display}<br>"
                    f"<b>Fréquence : {freq}/{max_freq} patients</b><br>"
                    f"Score max : {score:.3f}<br>"
                    f"<br><b>Scores par patient :</b><br>{ps_lines}<br>"
                    f"<br><b>Voisins ({len(neighbors_info)}) :</b><br>{nb_lines}"
                )

            traces.append(go.Scatter(
                x=nx_, y=ny_,
                mode="markers",
                hoverinfo="text",
                hovertext=hover_,
                marker=dict(
                    size=sizes_,
                    color=colors_,
                    line=dict(width=1.5, color=borders_),
                    symbol=symbols_,
                ),
                name=bin_label,
                legendgroup=f"freq_{bin_label}",
                legendrank=3,
                showlegend=True,
            ))

        return traces

    # ── assemblage final ──────────────────────────────────────────────────────

    def assemble_figure(self, edge_traces, node_traces, background_shapes, layer_annotations,
                        output_file, seeds=None, params=None, layer_names=None):
        """
        CORRECTIF 1 + 2 :
          - node_traces accepte un seul trace OU une liste (retro-compatible).
          - Labels : tous en mono-patient, seulement haute fréquence en mode fusionné.
          - Updatemenus : tableaux de visibilité construits après que toutes les traces
            sont ajoutées → les boutons filtrent vraiment.
        """
        if not isinstance(node_traces, list):
            node_traces = [node_traces]

        fig = go.Figure(data=edge_traces + node_traces)
        n_base_traces = len(fig.data)   # nb de traces avant seeds/params/légende

        # ── Seeds dummy trace ─────────────────────────────────────────────────
        if seeds:
            fig.add_trace(go.Scatter(
                x=[None], y=[None], mode="markers",
                marker=dict(size=12, symbol="square", color="lightblue",
                            line=dict(width=2, color="darkblue")),
                legendgroup="seeds", legendrank=1,
                showlegend=True, name="Seeds",
            ))

        # ── Paramètres dans la légende ────────────────────────────────────────
        if params:
            fig.add_trace(go.Scatter(
                x=[None], y=[None], mode="markers",
                marker=dict(size=0, color="white", opacity=0.0),
                showlegend=True, legendgroup="params", legendrank=2,
                name="<b>─── Parameters ───</b>",
            ))
            for key, value in params.items():
                if key.lower() == "seeds" and isinstance(value, (list, tuple)):
                    for i, seed in enumerate(value):
                        fig.add_trace(go.Scatter(
                            x=[None], y=[None], mode="markers",
                            marker=dict(size=0, color="white", opacity=0.0),
                            showlegend=True, legendgroup="params", legendrank=2,
                            name=f"• {key} : {seed}" if i == 0 else f"   {seed}",
                        ))
                else:
                    fig.add_trace(go.Scatter(
                        x=[None], y=[None], mode="markers",
                        marker=dict(size=0, color="white", opacity=0.0),
                        showlegend=True, legendgroup="params", legendrank=2,
                        name=f"• {key} : {value}",
                    ))

        # ── Couches manquantes ────────────────────────────────────────────────
        if layer_names is not None:
            existing = [str(l) for l in self.layers]
            for ml in [ly for ly in layer_names if ly not in existing]:
                fig.add_trace(go.Scatter(
                    x=[None], y=[None], mode="markers",
                    marker=dict(size=0, color="white", opacity=0.0),
                    showlegend=True, legendgroup="params", legendrank=2,
                    name=f"• {ml} (missing)",
                ))

        # ── Légende rampe de couleur (mode fusionné) ──────────────────────────
        is_merged = self._is_merged()
        max_freq  = self._max_freq() if is_merged else 1

        if is_merged:
            color_scale = [
                ("rgb(211,209,199)", "1 patient"),
                ("rgb(181,212,244)", "~25 %"),
                ("rgb(249,199,117)", "~50 %"),
                ("rgb(240,149,149)", "~75 %"),
                ("rgb(226,75,74)",   f"{max_freq} patients"),
            ]
            for color_rgb, label_text in color_scale:
                fig.add_trace(go.Scatter(
                    x=[None], y=[None], mode="markers",
                    marker=dict(size=10, color=color_rgb, line=dict(width=1, color="gray")),
                    showlegend=True, legendgroup="freq_legend", legendrank=4,
                    name=f"● {label_text}",
                ))

        # ── Updatemenus (CORRECTIF 2) ─────────────────────────────────────────
        updatemenus = []
        if is_merged:
            n_total     = len(fig.data)
            all_visible = [True] * n_total

            def _visibility(hide_bin_labels):
                vis = []
                for trace in fig.data:
                    name = trace.name or ""
                    vis.append(not any(bl in name for bl in hide_bin_labels))
                return vis

            updatemenus = [dict(
                type="buttons",
                direction="right",
                x=0.5, xanchor="center",
                y=1.0, yanchor="bottom",
                pad=dict(t=4, b=4),
                showactive=True,
                bgcolor="white",
                bordercolor="#999",
                font=dict(size=11),
                buttons=[
                    dict(label="All",
                         method="restyle",
                         args=[{"visible": all_visible}]),
                    dict(label="≥ 3 patients",
                         method="restyle",
                         args=[{"visible": _visibility(["1-2 patients"])}]),
                    dict(label="≥ 5 patients",
                         method="restyle",
                         args=[{"visible": _visibility(["1-2 patients", "3-4 patients"])}]),
                ],
            )]

        # ── Layout principal ──────────────────────────────────────────────────
        fig.update_layout(
            shapes=background_shapes,
            annotations=layer_annotations,
            updatemenus=updatemenus,
            title=dict(
                text="<b>Interactive Multiplex Graph</b>",
                x=0.5, xanchor="center",
                y=0.97, yanchor="top",
            ),
            hovermode="closest",
            autosize=True,
            margin=dict(b=50, t=110, l=50, r=120),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor="white",
            legend=dict(
                title="Types of interaction",
                bordercolor="Black",
                borderwidth=1,
                orientation="v",
                yanchor="top", y=1.0,
                xanchor="left", x=1.02,
            ),
        )

        # ── CORRECTIF 1 : labels des nœuds ────────────────────────────────────
        if is_merged:
            # Mode fusionné : labels uniquement pour les nœuds haute fréquence
            freq_threshold = max(2, int(max_freq * 0.6))
            for n in self.G.nodes():
                freq = self.G.nodes[n].get("freq", 1)
                if freq >= freq_threshold:
                    x, y  = self.pos[n]
                    label = self.G.nodes[n]["label"]
                    fig.add_annotation(dict(
                        x=x, y=y, xref="x", yref="y",
                        text=f"<b>{label}</b> ({freq})",
                        showarrow=False,
                        font=dict(color="black", size=10),
                        bgcolor="rgba(255,255,255,0.85)",
                        bordercolor="gray", borderwidth=0.5,
                        yshift=12,
                    ))

        # ── Légende d'encodage visuel (bas du graphe) ─────────────────────────
        if is_merged:
            fig.add_annotation(
                text=(
                    f"Couleur = fréquence (1 → {max_freq} patients) | "
                    f"Taille = score RWR | Épaisseur arête = partage | ■ = seed"
                ),
                xref="paper", yref="paper",
                x=0.0, y=-0.04,
                showarrow=False,
                font=dict(size=10, color="gray"),
                xanchor="left",
            )

        # ── Sauvegarde ────────────────────────────────────────────────────────
        fig.write_html(output_file, include_plotlyjs="cdn")
        fig.write_image(output_file.replace(".html", ".png"))
        print(f"Interactive graph successfully generated! Open '{output_file}' in a browser.")
        return fig

    # ── point d'entrée public ─────────────────────────────────────────────────

    def create_interactive_graph(self, output_file, seeds=None, params=None, layer_names=None):
        background_shapes, layer_annotations, _ = self.generate_background_shapes_and_annotations(
            layer_names=layer_names
        )

        # ── Edge-Path Bundling (mode fusionné uniquement) ─────────────────────
        bundled_paths = None
        if self._is_merged():
            try:
                from .edge_bundling import compute_bundled_paths
                bundled_paths = compute_bundled_paths(self.G, self.pos, k=2.0, d=2.0)
                n_bundled = sum(1 for p in bundled_paths.values() if len(p) > 2)
                print(f"[EPB] {n_bundled}/{len(bundled_paths)} arêtes interlayer bundlées")
            except Exception as e:
                print(f"[EPB] Bundling ignoré ({e}), lignes droites utilisées")
                bundled_paths = None

        edge_groups, edge_group_labels, edge_group_colors = self.group_edges_by_interaction(
            layer_names=layer_names,
            bundled_paths=bundled_paths,
        )
        edge_traces = self.create_edge_traces(edge_groups, edge_group_labels, edge_group_colors)

        if self._is_merged():
            node_traces = self.create_node_traces_merged(seeds=seeds, layer_names=layer_names)
        else:
            node_traces = [self.create_node_trace(seeds=seeds, layer_names=layer_names)]

        return self.assemble_figure(
            edge_traces,
            node_traces,
            background_shapes,
            layer_annotations,
            output_file,
            seeds=seeds,
            params=params,
            layer_names=layer_names,
        )
