from django.urls import path
from . import views

app_name = "whitebox_plugin_map"

urlpatterns = [
    path("map/offline-tiles/", views.serve_offline_tile, name="serve-offline-tiles"),
]
