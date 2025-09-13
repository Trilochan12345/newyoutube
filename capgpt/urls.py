# capgpt/urls.py
from django.urls import path
from .views import upload_and_generate

urlpatterns = [
    path("upload/", upload_and_generate, name="upload_generate"),
]
