from django.shortcuts import render

# Create your views here.
# capgpt/views.py
from django.shortcuts import render
from django.conf import settings
import os
from .forms import UploadImageForm
from .utils import generate_3d_image

def upload_and_generate(request):
    generated_path = None
    if request.method == "POST":
        form = UploadImageForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded = form.cleaned_data["image"]
            save_path = os.path.join(settings.MEDIA_ROOT, "uploads", uploaded.name)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, "wb+") as dest:
                for chunk in uploaded.chunks():
                    dest.write(chunk)

            # Run AI generator
            generated_path = generate_3d_image(save_path)
            rel_path = generated_path.replace(settings.MEDIA_ROOT + os.sep, "")
            return render(request, "capgpt/result.html", {"gen_image": rel_path})

    else:
        form = UploadImageForm()
    return render(request, "capgpt/upload.html", {"form": form})
