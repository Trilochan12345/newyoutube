from django.urls import path
from . import views

urlpatterns = [
   
    path("modify-video/", views.modify_video_with_audio, name="modify_video_with_audio"),

]
