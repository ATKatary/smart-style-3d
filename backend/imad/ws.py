"""
imad ws patterns
"""
from . import consumers
from django.urls import re_path

websocket_urlpatterns = [
    re_path(r'^ws/api/imad/upload/$', consumers.MeshConsumer.as_asgi(), name="mesh"),
]