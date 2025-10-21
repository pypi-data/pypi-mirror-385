import requests

from django.http import HttpResponse, Http404
from django.views.decorators.cache import cache_control


@cache_control(max_age=3600)
def serve_offline_tile(request):
    try:
        z = int(request.GET.get("z"))
        x = int(request.GET.get("x"))
        y = int(request.GET.get("y"))
    except (TypeError, ValueError):
        raise Http404("Invalid tile coordinates")

    tile_url = f"http://tileserver:8080/styles/basic-preview/{z}/{x}/{y}.png"
    response = requests.get(tile_url, timeout=5)
    if response.status_code == 200:
        return HttpResponse(response.content, content_type="image/png")
    else:
        raise Http404("Tile not found")
