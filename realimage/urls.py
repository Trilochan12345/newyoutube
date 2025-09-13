from django.urls import path
from .views import generate_sd_image, image_form,generate_video

urlpatterns = [
    path("generate-image/", generate_sd_image, name="generate_sd_image"),
    path("image-form/", image_form, name="image_form"),
    path("generate-video/", generate_video, name="generate_video"),
   
]
