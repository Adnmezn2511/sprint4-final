# backend/app/urls.py

from django.urls import path
from .views import (
    test_itRWR,
    multiplex_list,
    layers_list,
    unique_nodes,
    upload_zip,
    upload_seed,
    getGraph,
    getMultipatientGraph,
    test_api,
    download_zip,
    compare_modules_view,
)

urlpatterns = [
    path('test-itRWR/', test_itRWR, name='test_itRWR'),
    path('api/multiplexes/', multiplex_list, name='multiplex_list'),
    path('api/multiplexes/<str:multiplex_name>/layers/', layers_list, name='layers_list'),
    path(
        'api/multiplexes/<str:multiplex_name>/layers/<str:layer_name>/nodes/',
        unique_nodes,
        name='unique_nodes',
    ),
    path("upload-zip", upload_zip, name="upload_zip"),
    path("upload-seed", upload_seed, name="upload_seed"),
    path("graph/", getGraph),
    path("graph/multipatient/", getMultipatientGraph, name="get_multipatient_graph"),
    path("test/", test_api),
    path('download-zip/<int:id>/', download_zip, name='download_zip'),
    # US-D2: module comparison endpoint
    path("modules/compare/", compare_modules_view, name="compare_modules"),
]