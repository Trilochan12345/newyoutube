from django.urls import path
from . import views

urlpatterns = [
    path('', views.publish_to_youtube_view, name='publish_to_youtube'),
    path('modify/', views.modify_view, name='modify'),
]
