# backend/app/views.py

from django.http import JsonResponse, HttpResponseBadRequest
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.http import JsonResponse, HttpResponse, Http404, FileResponse
from django.conf import settings
import json
import plotly.express as px
import os
from django.shortcuts import render
from django.conf import settings
from .itRWR_controller import run_itRWR, run_itRWR_multipatient
from .utils.multixrank_config import generate_config
from .utils.network_utils import *
from app.services.module_comparison_service import compare_modules

from time import perf_counter
from datetime import timedelta
import shutil


current_dir = os.path.dirname(os.path.abspath(__file__))
program_dir = os.path.dirname(current_dir)

input_dir = os.path.join(program_dir, "samples")
output_dir = ""
result_dir = os.path.join(input_dir, "result")

current_zip_dir = os.path.join(settings.BASE_DIR, "samples/current_zip")
input_zip_path = os.path.join(current_zip_dir, "input.zip")
log_zip_dir = os.path.join(input_dir, 'log_zip')


def test_itRWR(request):
    """
    View to execute the itRWR algorithm with hardcoded arguments and display a result.
    """
    start_time = perf_counter()
    liste_seeds = ["GAS2L3", "ABCC9", "AKAP2"]
    nb_nodes_per_layer = 10
    nb_iterations = 1
    restart = 0.1
    user = "leo"
    title = "Titre"

    res_fig, _, _, _modules = run_itRWR(
        log_zip_dir, input_zip_path, result_dir,
        liste_seeds, nb_iterations, nb_nodes_per_layer,
        restart, user, title
    )

    end_time = perf_counter()
    print("elapsed time: ", timedelta(seconds=end_time - start_time))

    res_fig.show(config={'responsive': True})

    if os.path.exists(result_dir):
        try:
            shutil.rmtree(result_dir)
            print(f"Dossier result_dir supprime : {result_dir}")
        except Exception as e:
            print(f"Erreur lors de la suppression de result_dir : {e}")

    return JsonResponse({"status": "itRWR executed successfully"})


def multiplex_list(request):
    """
    View returning the list of available multiplex network names.
    """
    multiplexes = list_multiplex_networks(current_zip_dir)
    return JsonResponse({'multiplexes': multiplexes})


def layers_list(request, multiplex_name):
    """
    View returning the list of available layers for a given multiplex.
    """
    layers = list_layers(current_zip_dir, multiplex_name)
    return JsonResponse({'layers': layers})


def unique_nodes(request, multiplex_name, layer_name):
    """
    View returning the list of unique nodes present in the specified layer.
    """
    nodes = list_unique_nodes(current_zip_dir, multiplex_name, layer_name)
    return JsonResponse({'nodes': nodes})


@api_view(["POST"])
def upload_zip(request):
    """
    Uploads a ZIP file to the current_zip_dir directory.

    :param request: POST request containing a .zip file.
    :return: 200 on success, 400 if the file is missing or not a ZIP.
    """
    if 'file' not in request.FILES:
        return JsonResponse({"error": "A file is required"}, status=400)

    zip_file = request.FILES['file']

    if not zip_file.name.endswith(".zip"):
        return JsonResponse({"error": "Only ZIP files are allowed"}, status=400)

    new_filename = "input.zip"
    destination_path = os.path.join(current_zip_dir, new_filename)

    with open(destination_path, "wb") as f:
        f.write(zip_file.read())

    return JsonResponse({"message": "File uploaded successfully"}, status=200)


@api_view(["POST"])
def upload_seed(request):
    """
    Uploads a TSV seed file to the current_zip_dir directory.

    :param request: POST request containing a .tsv or .txt file.
    :return: 200 on success, 400 if the file is missing or has an invalid extension.
    """
    if 'file' not in request.FILES:
        return JsonResponse({"error": "A file is required"}, status=400)

    seed_file = request.FILES['file']

    if not seed_file.name.endswith((".tsv", ".txt")):
        return JsonResponse({"error": "Only TSV and TXT files are allowed"}, status=400)

    new_filename = "seeds.tsv"
    seeds_path = os.path.join(current_zip_dir, new_filename)

    with open(seeds_path, "wb") as f:
        f.write(seed_file.read())

    return JsonResponse({"message": "Seed file uploaded successfully"}, status=200)


@api_view(["POST"])
def getGraph(request):
    """
    Receives parameters, runs the itRWR algorithm, and returns the resulting graph.

    Expected POST body fields:
    - seeds (list[str]): seed gene list
    - steps (int): number of iterations
    - top (int): number of nodes per layer
    - restart (float): restart probability
    - user (str): username
    - title (str): graph title
    """
    data = request.data
    liste_seeds = data.get("seeds", [""])
    nb_iterations = data.get("steps", 1)
    nb_nodes_per_layer = data.get("top", 10)
    restart = data.get("restart", 0.7)
    user = data.get("user", "user")
    title = data.get("title", "title")

    sample_name = "0"

    try:
        nb_iterations = int(nb_iterations)
        nb_nodes_per_layer = int(nb_nodes_per_layer)
        restart = float(restart)
    except ValueError:
        return Response({"error": "Invalid parameters"}, status=400)

    fig, _, _, _modules = run_itRWR(
        log_zip_dir, input_zip_path, result_dir,
        liste_seeds, nb_iterations, nb_nodes_per_layer,
        restart, user, title
    )

    print("Done !")

    return Response(fig.to_dict())


@api_view(['GET'])
def test_api(request):
    return Response({"test": "Hello from Django!"})


@api_view(['POST'])
def getMultipatientGraph(request):
    """
    Receives parameters, runs itRWR for multiple patients, and returns the resulting graphs.

    Expected POST body fields:
    - dico_patient_seeds (dict[str, list[str]]): mapping of patient ID to seed gene list
    - steps (int): number of iterations
    - top (int): number of nodes per layer
    - restart (float): restart probability
    - user (str): username
    """
    data = request.data
    dico_patient_seeds = data.get("dico_patient_seeds", {})
    nb_iterations = data.get("steps", 5)
    nb_nodes_per_layer = data.get("top", 10)
    restart = data.get("restart", 0.7)
    user = data.get("user", "user")

    if not isinstance(dico_patient_seeds, dict) or len(dico_patient_seeds) == 0:
        return Response(
            {"error": "dico_patient_seeds must be a non-empty object {patient: [seeds]}"},
            status=400,
        )

    for patient, seeds in dico_patient_seeds.items():
        if not isinstance(patient, str) or not patient.strip():
            return Response({"error": "Each patient identifier must be a non-empty string"}, status=400)

        if not isinstance(seeds, list) or len(seeds) == 0:
            return Response(
                {"error": f"Patient '{patient}' must have a non-empty seed list"},
                status=400,
            )

        if not all(isinstance(seed, str) and seed.strip() for seed in seeds):
            return Response(
                {"error": f"Patient '{patient}' contains invalid seed values"},
                status=400,
            )

    try:
        nb_iterations = int(nb_iterations)
        nb_nodes_per_layer = int(nb_nodes_per_layer)
        restart = float(restart)
    except (TypeError, ValueError):
        return Response({"error": "steps, top and restart must be numeric"}, status=400)

    if nb_iterations < 1:
        return Response({"error": "steps must be >= 1"}, status=400)

    if nb_nodes_per_layer < 1:
        return Response({"error": "top must be >= 1"}, status=400)

    if restart <= 0 or restart >= 1:
        return Response({"error": "restart must be between 0 and 1 (exclusive)"}, status=400)

    if not isinstance(user, str) or not user.strip():
        return Response({"error": "user must be a non-empty string"}, status=400)

    # Run the itRWR algorithm and set the result to interactive Plotly figures
    try:
        figs, merged_fig, merged_modules_fig = run_itRWR_multipatient(
            
            log_zip_dir,
            input_zip_path,
            result_dir,
           
            dico_patient_seeds,
            nb_iterations,
            nb_nodes_per_layer,
           
            restart,
            user,
        
        )
    except ValueError as exc:
        return Response({"error": str(exc)}, status=400)
    except Exception:
        return Response({"error": "Unexpected error while generating multipatient graphs"}, status=500)

    print("Done !")

    payload = []
    for entry in figs.values():
        fig = entry.get("figure") if isinstance(entry, dict) else entry
        modules = entry.get("modules", []) if isinstance(entry, dict) else []

        fig_dict = fig.to_dict()
        fig_dict["_modules"] = modules
        payload.append(fig_dict)

    result = payload
    if merged_fig is not None:
        result.append(merged_fig.to_dict())

    if merged_modules_fig is not None:
        result.append(merged_modules_fig.to_dict())

    return Response(result)


def download_zip(request, id):
    """
    Downloads the ZIP archive associated with the given graph history ID.

    :param id: Graph history ID used to locate the corresponding ZIP file.
    :return: ZIP file as a FileResponse, or 404 if not found.
    """
    if not os.path.exists(log_zip_dir):
        raise Http404("Le dossier de fichiers n'existe pas")

    matched_file = None
    for filename in os.listdir(log_zip_dir):
        if filename.endswith(f"#{id}.zip"):
            matched_file = filename
            break

    if not matched_file:
        raise Http404("Le fichier ZIP correspondant n'a pas ete trouve")

    zip_path = os.path.join(log_zip_dir, matched_file)

    try:
        response = FileResponse(open(zip_path, 'rb'))
        response['Content-Type'] = 'application/zip'
        response['Content-Disposition'] = f'attachment; filename="{matched_file}"'
        return response
    except IOError:
        raise Http404("Erreur lors de l'acces au fichier ZIP")


@api_view(["POST"])
def compare_modules_view(request):
    """
    API endpoint to compare gene module lists across multiple patients.

    Expected POST body (JSON):
    {
        "patients": {
            "patient_id_1": ["GENE1", "GENE2"],
            "patient_id_2": ["GENE1", "GENE3"]
        }
    }

    Returns:
        200: Comparison result with intersection, union, differences,
             discriminant_genes, patient_count, and summary.
        400: Error message if input is missing, malformed, or invalid.
    """
    data = request.data
    patient_modules = data.get("patients", None)

    if patient_modules is None:
        return Response(
            {"error": "Missing 'patients' field in request body."},
            status=400,
        )

    if not isinstance(patient_modules, dict):
        return Response(
            {
                "error": (
                    "'patients' must be an object mapping "
                    "patient IDs to gene lists."
                )
            },
            status=400,
        )

    try:
        result = compare_modules(patient_modules)
    except ValueError as exc:
        return Response({"error": str(exc)}, status=400)

    return Response(result, status=200)