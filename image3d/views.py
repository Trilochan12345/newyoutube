# image3d/views.py
import os
from django.shortcuts import render, redirect
from django.conf import settings
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from .forms import GenerateForm
from .models import GenerationRequest, GeneratedImage

# import local generator
from . import generate_figurine

@require_http_methods(["GET"])
def index(request):
    form = GenerateForm(initial={"prompt": generate_figurine.PROMPT_DEFAULT})
    return render(request, "image3d/index.html", {"form": form})

@require_http_methods(["POST"])
def generate_view(request):
    form = GenerateForm(request.POST)
    if not form.is_valid():
        return render(request, "image3d/index.html", {"form": form})

    # Save request
    data = form.cleaned_data
    gen_req = GenerationRequest.objects.create(
        prompt=data["prompt"],
        negative_prompt=data.get("negative_prompt", ""),
        num_images=data["num_images"],
        guidance=data["guidance"],
        steps=data["steps"],
    )

    # Prepare output dir under MEDIA_ROOT
    out_dir = os.path.join(settings.MEDIA_ROOT, "figurines")
    os.makedirs(out_dir, exist_ok=True)

    # load pipeline (this may take time)
    pipe = generate_figurine.load_pipeline()

    # generate images
    seed = data.get("seed")
    seed_start = int(seed) if seed else None

    results = generate_figurine.generate_images(
        pipe=pipe,
        prompt=data["prompt"],
        negative_prompt=data.get("negative_prompt", generate_figurine.NEGATIVE_PROMPT_DEFAULT),
        out_dir=out_dir,
        num_images=data["num_images"],
        steps=data["steps"],
        guidance_scale=data["guidance"],
        height=data["height"],
        width=data["width"],
        seed_start=seed_start
    )

    # Save DB GeneratedImage objects pointing to MEDIA files
    saved_images = []
    for path, seed_val in results:
        filename = os.path.basename(path)
        rel_path = os.path.join("figurines", filename)  # relative to MEDIA_ROOT
        gi = GeneratedImage.objects.create(
            request=gen_req,
            image=rel_path,
            seed=seed_val
        )
        saved_images.append(gi)

    # show results
    return render(request, "image3d/results.html", {"request_obj": gen_req, "images": saved_images})
