from django.urls import path
from . import views

urlpatterns = [
    path('thumbnail', views.generate_thumbnail, name='generate_thumbnail'),
    path('gallery/', views.thumbnail_gallery, name='thumbnail_gallery'),
    # urls.py
    path('thumbnail/delete/<int:id>/', views.delete_thumbnail, name='delete_thumbnail'),

]
