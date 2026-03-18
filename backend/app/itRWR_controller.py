from .itRWR.communityProcessor import *
from .graph.multiplex_graph import MultiplexGraph
from .graph.graph_merger import merge_patient_graphs
from .visualization.graph_visualizer import GraphVisualizer
from history.models import GraphHistory
from .utils.misc import create_zip
import os
import tempfile
from django.conf import settings
from .utils.multixrank_config import generate_config, get_layer_names, get_layer_names_from_zip
import networkx as nx


from time import perf_counter
from datetime import timedelta, datetime
from zoneinfo import ZoneInfo
import shutil

import cProfile


def extract_modules_from_graph(graph):
  """Return strongly connected components (modules) from a graph.

  For undirected graphs, conversion to DiGraph keeps edges in both directions,
  so SCCs are equivalent to connected components.
  """
  if graph is None or graph.number_of_nodes() == 0:
    return []

  directed_graph = graph if graph.is_directed() else nx.DiGraph(graph)
  components = list(nx.strongly_connected_components(directed_graph))
  components = sorted(components, key=lambda comp: len(comp), reverse=True)

  modules = []
  for index, component in enumerate(components, start=1):
    labels = sorted(
      {
        directed_graph.nodes[node].get("label", node[0] if isinstance(node, tuple) else str(node))
        for node in component
      }
    )
    modules.append(
      {
        "module_id": f"M{index}",
        "size": len(component),
        "nodes": labels,
      }
    )

  return modules

def run_itRWR(log_zip_dir, input_zip_path, result_dir, liste_seeds, nb_iterations, nb_nodes_per_layer, restart, user, title):
    """
    Runs the itRWR algorithm on a multiplex.
    
    Params:
      liste_seeds: List of seed nodes.
      nb_iterations: Number of iterations.
      nb_nodes_per_layer: Nodes per layer for the final graph.
      
    Returns:
      An interactive graph created from the results.
    """
    sample_name = datetime.now(ZoneInfo("Europe/Paris")).strftime("%d-%m-%Y_%H-%M-%S")
    output_dir = os.path.join(result_dir,sample_name)
    
    if not os.path.exists(output_dir): os.makedirs(output_dir)

    os.chdir(output_dir)

    config_filename = f"config.yml"
    seeds_filename = f"seeds.txt"

    dir_result_name = f"result_{nb_iterations}"
    interactive_graph_path= os.path.join(dir_result_name, "interactive_graph.html")

    # ### profiler
    # pr = cProfile.Profile()
    # pr.enable()
    # ###

    generate_config(input_zip_path, nb_iterations, liste_seeds, restart, output_dir)
    processorCommunity = CommunityProcessor(
            path=output_dir,
            config_file=config_filename,
            out_folder=dir_result_name,
            seeds_file=seeds_filename,
            nb_iterations=nb_iterations,
            nb_nodes_per_layer=nb_nodes_per_layer
        )
    
    processorCommunity.run()
    missing_seeds = processorCommunity.missing_seeds
    
    sif_file = os.path.join(output_dir, dir_result_name, "ranking_final.sif")
    ranking_file = os.path.join(output_dir, dir_result_name, "ranking_final.csv")
    
    # Construction du graphe multiplex
    multiplex_graph = MultiplexGraph(sif_file, ranking_file)
    G, layers = multiplex_graph.get_graph()
    node_count = G.number_of_nodes()
    edge_count = G.number_of_edges()
    
    # Création et sauvegarde du graphe interactif
    visualizer = GraphVisualizer(G, layers)
    modules = extract_modules_from_graph(G)

    display_params = {
        "Iterations": nb_iterations,
        "Number of nodes per layer": nb_nodes_per_layer,
        "Number of nodes": node_count,
        "Number of edges": edge_count,
        "Seeds": liste_seeds,
        "Missing seeds": missing_seeds,
      "Restart (%)": restart,
      "Modules Count": len(modules),
    }

    saved_params = {
      **display_params,
      "Modules": modules,
    }

    layer_names = get_layer_names(output_dir)

    # Création de la figure interactive Plotly
    fig = visualizer.create_interactive_graph(
      interactive_graph_path,
      seeds=liste_seeds,
      params=display_params,
      layer_names=layer_names,
    )
    
    # Convertir la figure en JSON pour stocker toute sa configuration
    fig_json = fig.to_dict()


    # Sauvegarde de la configuration du graphe dans la base de données
    graph_record = GraphHistory.objects.create(
      user=user,
      title=title,
      graph_json=fig_json,
      parameters=saved_params,
      result_folder=sample_name
    )
    print(f"GraphHistory record created with ID: {graph_record.id}")

    new_output_dir_name = f"{sample_name}#{graph_record.id}"


    create_zip(
      source_folder=output_dir,
      zip_filename=new_output_dir_name,
      output_dir=log_zip_dir
    )


    if os.path.exists(result_dir):
        try:
            shutil.rmtree(result_dir)
            print(f"Dossier result_dir supprimé : {result_dir}")
        except Exception as e:
            print(f"Erreur lors de la suppression de result_dir : {e}")
    
    # pr.disable()
    # # dump fichier utilisable par snakeviz
    # pr.dump_stats("cProfile.prof")
   

    return fig, G, layers, modules

def run_itRWR_multipatient(log_zip_dir, input_zip_path, result_dir, dico_patient_seeds, nb_iterations, nb_nodes_per_layer, restart, user):
    """
    Runs the itRWR algorithm on a multiplex for multiple patients, then merges all graphs.

    Params:
      log_zip_dir: Directory to save the zip file containing logs and results.
      input_zip_path: Path to the input multiplex zip file.
      result_dir: Directory to save intermediate results.
      dico_patient_seeds: Dictionnary patient -> list of seeds {str: [str]}.
      nb_iterations: Number of iterations.
      nb_nodes_per_layer: Nodes per layer for the final graph.
      restart: Restart probability.
      user: User identifier.

    Returns:
      tuple (dict, plotly.Figure or None):
          - figs: {patient_id: plotly_fig}
          - merged_fig: plotly figure of the merged graph, or None if < 2 patients
    """
    figs = {}
    patient_graph_data = {}

    if not dico_patient_seeds or not isinstance(dico_patient_seeds, dict):
        raise ValueError("No patient seeds provided.")

    for patient, seeds in dico_patient_seeds.items():
        if not isinstance(seeds, list) or len(seeds) == 0:
            print(f"Warning: patient {patient} has no seeds and will be skipped.")
            continue

        print(
            f"Running itRWR for patient: {patient} with seeds: {seeds} "
            f"nb_iterations: {nb_iterations} nb_nodes_per_layer: {nb_nodes_per_layer} restart: {restart}"
        )
        fig, G, layers, modules = run_itRWR(
            log_zip_dir,
            input_zip_path,
            result_dir,
            seeds,
            nb_iterations,
            nb_nodes_per_layer,
            restart,
            user,
            f"patient_{patient}",
        )
        fig.update_layout(title=f"Patient {patient}")
        figs[patient] = {
            "figure": fig,
            "modules": modules,
        }
        patient_graph_data[patient] = (G, layers, seeds)

    if len(figs) == 0:
        raise ValueError("No patients with seeds provided.")

    # Générer le graphe fusionné
    merged_fig = None
    if len(patient_graph_data) >= 2:
        G_merged, merged_layers = merge_patient_graphs(patient_graph_data)

        visualizer = GraphVisualizer(G_merged, merged_layers)

        all_seeds = list(set(
            seed for seeds in dico_patient_seeds.values() for seed in seeds
        ))

        merged_params = {
            "Type": "Merged graph",
            "Patients": len(patient_graph_data),
            "Iterations": nb_iterations,
            "Number of nodes per layer": nb_nodes_per_layer,
            "Number of nodes": G_merged.number_of_nodes(),
            "Number of edges": G_merged.number_of_edges(),
            "Restart (%)": restart,
        }

        # Fichier temporaire pour create_interactive_graph (qui exige un output_file)
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as tmp:
            merged_output_path = tmp.name

        # Récupérer les layer_names directement depuis le ZIP d'entrée
        layer_names = get_layer_names_from_zip(input_zip_path)

        merged_fig = visualizer.create_interactive_graph(
            merged_output_path,
            seeds=all_seeds,
            params=merged_params,
            layer_names=layer_names,
        )
        merged_fig.update_layout(
            title=dict(
                text="<b>Merged graph — All patients</b>",
                x=0.5, xanchor="center",
                y=0.97, yanchor="top",
            ),
        )

        # Nettoyer les fichiers temporaires
        for path in [merged_output_path, merged_output_path.replace('.html', '.png')]:
            if os.path.exists(path):
                os.remove(path)

    return figs, merged_fig

    
