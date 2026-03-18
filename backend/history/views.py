from django.shortcuts import get_object_or_404, render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import GraphHistory
import plotly.io as pio
from rest_framework import generics
from rest_framework.views import APIView
from .serializers import GraphHistorySerializer
from django.http import FileResponse, Http404
import json
import os
from app.utils.misc import delete_zip_file
from django.conf import settings
import plotly.graph_objects as go


current_dir = os.path.dirname(os.path.abspath(__file__))
program_dir = os.path.dirname(current_dir)
input_dir = os.path.join(program_dir, "samples")
log_zip_dir = os.path.join(input_dir, 'log_zip')


def display_graph(request, graph_id):
    graph_record = get_object_or_404(GraphHistory, pk=graph_id)
    fig = go.Figure(graph_record.graph_json)
    graph_html = fig.to_html(full_html=False)
    context = {
        'graph_html': graph_html,
        'graph_record': graph_record,
    }
    return render(request, 'display_graph.html', context)

@api_view(['GET'])
def list_graphs(request):
    graph_records = GraphHistory.objects.all()
    figures = []
    for record in graph_records:
        if record.graph_json:
            fig = go.Figure(record.graph_json)
            figures.append(fig.to_dict())
    return Response(figures)

class GraphHistoryList(generics.ListAPIView):
    queryset = GraphHistory.objects.all().order_by('-created_at')
    serializer_class = GraphHistorySerializer

class GraphHistoryDetail(generics.RetrieveAPIView):
    """
    Vue API pour récupérer un graphe unique par son ID.
    
    Méthode : GET /api/graph-histories/<id>/
    Retourne : les données JSON complètes du graphe (graph_json, parameters, etc.)
    Erreur 404 si l'ID n'existe pas.
    """
    queryset = GraphHistory.objects.all()
    serializer_class = GraphHistorySerializer

# Fonction pour supprimer un fichier zip spécifique
def delete_zip_file(zip_dir, filename):
    zip_path = os.path.join(zip_dir, filename)
    if os.path.isfile(zip_path):
        os.remove(zip_path)

@api_view(['DELETE'])
def delete_graph(request, graph_id):
    # Résout le chemin absolu vers le dossier "backend/samples/log_zip"
    log_zip_dir = os.path.join(settings.BASE_DIR, 'samples', 'log_zip')

    if not os.path.isdir(log_zip_dir):
        raise Http404("Le dossier des fichiers ZIP n'existe pas")

    # Recherche tous les fichiers ZIP contenant '#graph_id.zip'
    matched_files = [
        f for f in os.listdir(log_zip_dir)
        if f.endswith(f"#{graph_id}.zip")
    ]

    if not matched_files:
        raise Http404("Aucun fichier ZIP correspondant trouvé")

    # Suppression de tous les fichiers correspondants
    for matched_file in matched_files:
        delete_zip_file(log_zip_dir, matched_file)

    # Suppression de l'objet GraphHistory
    graph_record = get_object_or_404(GraphHistory, pk=graph_id)
    graph_record.delete()

    return Response({'message': 'GraphHistory et fichier(s) ZIP supprimés avec succès'}, status=200)