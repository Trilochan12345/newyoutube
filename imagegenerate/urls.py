from django.contrib import admin
from django.urls import path
from .views import text_image, form_page

urlpatterns = [
    path("admin/", admin.site.urls),
    path("text-image/", text_image, name="text_image"),
    path("text", form_page, name="form_page"),
]
