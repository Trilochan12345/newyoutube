# tts/urls.py
from django.urls import path
from .views import tts_api, tts_form_view

urlpatterns = [
    path('speech/', tts_form_view, name='speech'),      # Renders form
    path('api/tts/', tts_api, name='tts_api'),     # Handles TTS generation
]