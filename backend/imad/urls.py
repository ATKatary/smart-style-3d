"""
imad url patterns
"""
from . import views
from django.urls import path

urlpatterns = [
    path("fetch", views.fetch, name = "fetch"),
    path("stylize", views.stylize, name = "stylize"),
]