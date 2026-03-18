from django.urls import path
from .views import display_graph, list_graphs, delete_graph, GraphHistoryDetail, GraphHistoryList
from . import views

urlpatterns = [
    path('graph/<int:graph_id>/', display_graph, name='display_graph'),
    path('graphs/', list_graphs, name='list_graphs'),
    path('graph-histories/', views.GraphHistoryList.as_view()),
    path('graph-histories/<int:pk>/', GraphHistoryDetail.as_view(), name='graph_history_detail'),
    path('graph/<int:graph_id>/delete/', delete_graph, name='delete_graph'),
]

