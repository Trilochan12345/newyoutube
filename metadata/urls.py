from django.urls import path
from . import views

urlpatterns = [
    path('metadata', views.generate_metadata_view, name='generate_metadata'),
]
