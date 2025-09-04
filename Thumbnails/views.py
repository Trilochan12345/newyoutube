from django.http import HttpResponse
from django.shortcuts import render
from .models import Thumbnail
from django.core.files.base import ContentFile
from django.utils.crypto import get_random_string
from PIL import Image, ImageDraw, ImageFont
import os
import io
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def generate_thumbnail(request):
    if request.method == "POST":
        title = request.POST.get("title", "AI Is Taking Over!")
        background = request.FILES.get("background")
        logo = request.FILES.get("logo")

        # Load or create background
        if background:
            bg = Image.open(background).convert("RGB")
        else:
            bg = Image.new("RGB", (1280, 720), color=(30, 30, 30))

        width, height = bg.size
        draw = ImageDraw.Draw(bg)

        # Load font
        font_path = os.path.join(BASE_DIR, "fonts", "Anton-Regular.ttf")
        try:
            font = ImageFont.truetype(font_path, 100)
        except:
            font = ImageFont.load_default()

        try:
            bbox = draw.textbbox((0, 0), title, font=font)
            text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        except AttributeError:
            text_w, text_h = draw.textsize(title, font=font)

        padding = 30
        box_x = (width - text_w) // 2 - padding
        box_y = height // 3 - text_h // 2 - padding
        box_w = text_w + padding * 2
        box_h = text_h + padding * 2

        draw.rectangle(
            [box_x, box_y, box_x + box_w, box_y + box_h],
            fill="black"
        )

        shadow_offset = 2
        draw.text(
            ((width - text_w) // 2 + shadow_offset, box_y + padding + shadow_offset),
            title, font=font, fill="black"
        )

        draw.text(
            ((width - text_w) // 2, box_y + padding),
            title, font=font, fill="white"
        )

        if logo:
            logo_img = Image.open(logo).convert("RGBA")
            logo_size = (int(width * 0.15), int(height * 0.15))
            logo_img = logo_img.resize(logo_size, Image.LANCZOS)
            margin = 40
            logo_x = width - logo_size[0] - margin
            logo_y = height - logo_size[1] - margin
            bg.paste(logo_img, (logo_x, logo_y), logo_img)

        # Save image to memory
        output = io.BytesIO()
        bg.save(output, format="JPEG")
        output.seek(0)

        filename = f"thumbnail_{get_random_string(8)}.jpg"

        # Save model
        thumb = Thumbnail(title=title)
        if background:
            thumb.background = background
        if logo:
            thumb.logo = logo
        thumb.output.save(filename, ContentFile(output.read()), save=True)

        thumbnails = Thumbnail.objects.all().order_by('-created_at')

        return render(request, "thumbnail_gallery.html", {"thumbnails": thumbnails})


    return render(request, "generate_thumbnail.html")


def thumbnail_gallery(request):
    thumbnails = Thumbnail.objects.all().order_by('-created_at')
    return render(request, "thumbnail_gallery.html", {"thumbnails": thumbnails})

def delete_thumbnail(request, id):
    thumb = get_object_or_404(Thumbnail, id=id)
    thumb.output.delete(save=False)  # delete file
    thumb.delete()  # delete DB record
    messages.success(request, "Thumbnail deleted successfully.")
    return redirect('thumbnail_gallery')
