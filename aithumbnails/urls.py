from django.urls import path
from . import views

urlpatterns = [
    path("aigenerate_thumbnail/", views.generate_thumbnail, name="generate_thumbnail"),
]
