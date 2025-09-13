# image3d/urls.py
from django.urls import path
from . import views

app_name = "image3d"

urlpatterns = [
    path("generate3d/", views.index, name="generate3d"),
    path("generateview/", views.generate_view, name="generate"),
]
